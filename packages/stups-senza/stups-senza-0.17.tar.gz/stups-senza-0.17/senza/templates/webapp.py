'''
HTTP app with auto scaling, ELB and DNS
'''

import click
from clickclick import Action, warning, error
import pystache
import yaml
from senza.aws import get_security_group
import boto.ec2
import boto.vpc

TEMPLATE = '''
# basic information for generating and executing this definition
SenzaInfo:
  StackName: {{application_id}}
  Parameters:
    - ImageVersion:
        Description: "Docker image version of {{ application_id }}."

# a list of senza components to apply to the definition
SenzaComponents:

  # this basic configuration is required for the other components
  - Configuration:
      Type: Senza::StupsAutoConfiguration # auto-detect network setup

  # will create a launch configuration and auto scaling group with scaling triggers
  - AppServer:
      Type: Senza::TaupageAutoScalingGroup
      InstanceType: {{ instance_type }}
      SecurityGroups:
        - app-{{application_id}}
      ElasticLoadBalancer: AppLoadBalancer
      TaupageConfig:
        runtime: Docker
        source: "{{ docker_image }}:{{=<% %>=}}{{Arguments.ImageVersion}}<%={{ }}=%>"
        ports:
          {{http_port}}: {{http_port}}

  # creates an ELB entry and Route53 domains to this ELB
  - AppLoadBalancer:
      Type: Senza::WeightedDnsElasticLoadBalancer
      HTTPPort: {{http_port}}
      HealthCheckPath: {{http_health_check_path}}
      SecurityGroups:
        - app-{{application_id}}-lb
'''


def prompt(variables: dict, var_name, *args, **kwargs):
    if var_name not in variables:
        variables[var_name] = click.prompt(*args, **kwargs)


def check_security_group(sg_name, rules, region):
    rules_missing = set()
    for rule in rules:
        rules_missing.add(rule)

    with Action('Checking security group {}..'.format(sg_name)):
        sg = get_security_group(region, sg_name)
        if sg:
            for rule in sg.rules:
                # NOTE: boto object has port as string!
                for proto, port in rules:
                    if rule.ip_protocol == proto and rule.from_port == str(port):
                        rules_missing.remove((proto, port))

    if sg:
        return rules_missing
    else:
        create_sg = click.confirm('Security group {} does not exist. Do you want Senza to create it now?'.format(
                                  sg_name), default=True)
        if create_sg:
            vpc_conn = boto.vpc.connect_to_region(region)
            vpcs = vpc_conn.get_all_vpcs()
            ec2_conn = boto.ec2.connect_to_region(region)
            sg = ec2_conn.create_security_group(sg_name, 'Application security group', vpc_id=vpcs[0].id)
            sg.add_tags({'Name': sg_name})
            for proto, port in rules:
                sg.authorize(ip_protocol=proto, from_port=port, to_port=port, cidr_ip='0.0.0.0/0')
        return set()


def gather_user_variables(variables, region):
    prompt(variables, 'application_id', 'Application ID', default='hello-world')
    prompt(variables, 'docker_image', 'Docker image', default='stups/hello-world')
    prompt(variables, 'http_port', 'HTTP port', default=8080, type=int)
    prompt(variables, 'http_health_check_path', 'HTTP health check path', default='/')
    prompt(variables, 'instance_type', 'EC2 instance type', default='t2.micro')

    http_port = variables['http_port']

    sg_name = 'app-{}'.format(variables['application_id'])
    rules_missing = check_security_group(sg_name, [('tcp', 22), ('tcp', http_port)], region)

    if ('tcp', 22) in rules_missing:
        warning('Security group {} does not allow SSH access, you will not be able to ssh into your servers'.format(
            sg_name))

    if ('tcp', http_port) in rules_missing:
        error('Security group {} does not allow inbound TCP traffic on the specified HTTP port ({})'.format(
            sg_name, http_port
        ))

    rules_missing = check_security_group(sg_name + '-lb', [('tcp', 443)], region)

    if rules_missing:
        error('Load balancer security group {} does not allow inbound HTTPS traffic'.format(sg_name))

    return variables


def generate_definition(variables):
    definition_yaml = pystache.render(TEMPLATE, variables)
    definition = yaml.safe_load(definition_yaml)
    return definition
