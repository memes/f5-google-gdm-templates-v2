# Copyright 2021 F5 Networks All rights reserved.
#
# Version 0.1.0


"""Creates full stack for POC"""
COMPUTE_URL_BASE = 'https://www.googleapis.com/compute/v1/'

def generate_name(prefix, suffix):
    """ Generate unique name """
    return prefix + "-" + suffix

def create_network_deployment(context):
    """ Create network module deployment """
    network_config = {}
    network_config_array = []
    for nics in range(context.properties['numNics']):
        if nics is 0:
            net_name = 'mgmt'
            subnet_name = 'mgmt'
            subnet_description = 'Subnetwork used for management traffic'
        elif context.properties['numNics'] is not 1 and nics is 1:
            net_name = 'external'
            subnet_name = 'external'
            subnet_description = 'Subnetwork used for external traffic'
        else:
            net_name = 'internal' + str(nics)
            subnet_name = 'internal' + str(nics)
            subnet_description = 'Subnetwork used for internal traffic'
        subnet_config = [{
            'description': subnet_description,
            'name': subnet_name,
            'region': context.properties['region'],
            'ipCidrRange': '10.0.' + str(nics) + '.0/24'
        }]
        if nics + 1 is context.properties['numNics']:
            app_subnet_config = {
                'description': 'Subnetwork used for POC application.',
                'name': 'app',
                'region': context.properties['region'],
                'ipCidrRange': '10.0.' + str(nics + 1) + '.0/24'
            }
            subnet_config.append(app_subnet_config)
        network_config = {
            'name': 'network' + str(nics),
            'type': '../modules/network/network.py',
            'properties': {
                'name': net_name,
                'provisionPublicIp': True,
                'uniqueString': context.properties['uniqueString'],
                'subnets': subnet_config
            }
        }
        network_config_array.append(network_config)
    return network_config_array

def create_bigip_deployment(context):
    """ Create bigip-standalone module deployment """
    interface_config_array = []
    depends_on_array = []
    prefix = context.properties['uniqueString']
    for nics in range(context.properties['numNics']):
        access_config = {}
        if context.properties['numNics'] is not 1 and nics is 0:
            net_name = generate_name(prefix, 'external-network')
            subnet_name = generate_name(prefix, 'external-subnet')
            interface_description = 'Interface used for external traffic'
            access_config = {
                'accessConfigs': [{ 'name': 'External NAT', 'type': 'ONE_TO_ONE_NAT' }]
            }
        elif nics is 0:
            net_name = generate_name(prefix, 'mgmt-network')
            subnet_name = generate_name(prefix, 'mgmt-subnet')
            interface_description = 'Interface used for management traffic'
            access_config = {
                'accessConfigs': [{ 'name': 'Management NAT', 'type': 'ONE_TO_ONE_NAT' }]
            }
        elif nics is 1:
            net_name = generate_name(prefix, 'mgmt-network')
            subnet_name = generate_name(prefix, 'mgmt-subnet')
            interface_description = 'Interface used for management traffic'
            access_config = {
                'accessConfigs': [{ 'name': 'Management NAT', 'type': 'ONE_TO_ONE_NAT' }]
            }
        else:
            net_name = generate_name(prefix, 'internal' + str(nics) + '-network')
            subnet_name = generate_name(prefix, 'internal' + str(nics) + '-subnet')
            interface_description = 'Interface used for internal traffic'
        interface_config = {
            'description': interface_description,
            'network': '$(ref.' + net_name + '.selfLink)',
            'subnetwork': '$(ref.' + subnet_name + '.selfLink)'
        }
        interface_config.update(access_config)
        depends_on_array.append(net_name)
        depends_on_array.append(subnet_name)
        interface_config_array.append(interface_config)
    bigip_config = [{
        'name': 'bigip-standalone',
        'type': '../modules/bigip-standalone/bigip_standalone.py',
        'properties': {
            'bigIpRuntimeInitConfig': context.properties['bigIpRuntimeInitConfig'],
            'bigIpRuntimeInitPackageUrl': context.properties['bigIpRuntimeInitPackageUrl'],
            'imageName': context.properties['imageName'],
            'instanceType': context.properties['instanceType'],
            'name': 'bigip1',
            'networkInterfaces': interface_config_array,
            'region': context.properties['region'],
            'tags': {
                'items': [
                    generate_name(prefix, 'mgmt-fw'),
                    generate_name(prefix, 'app-vip-fw'),
                    generate_name(prefix, 'app-int-fw'),
                    generate_name(prefix, 'app-int-vip-fw')
                ]
            },
            'uniqueString': context.properties['uniqueString'],
            'zone': context.properties['zone']
        },
        'metadata': {
            'dependsOn': depends_on_array
        }
    }]
    return bigip_config


def create_application_deployment(context):
    """ Create application module deployment """
    prefix = context.properties['uniqueString']
    subnet_name = generate_name(prefix, 'app-subnet')
    if context.properties['numNics'] is 1:
        net_name = generate_name(prefix, 'mgmt-network')
    elif context.properties['numNics'] is 2:
        net_name = generate_name(prefix, 'external-network')
    else:
        net_name = generate_name(prefix, 'internal' + \
            str(context.properties['numNics'] - 1) + '-network')
    depends_on_array = []
    depends_on_array.append(net_name)
    depends_on_array.append(subnet_name)
    application_config = [{
      'name': 'application',
      'type': '../modules/application/application.py',
      'properties': {
        'appContainerName': context.properties['appContainerName'],
        'application': context.properties['application'],
        'availabilityZone': context.properties['zone'],
        'createAutoscaleGroup': False,
        'cost': context.properties['cost'],
        'environment': context.properties['environment'],
        'group': context.properties['group'],
        'hostname': generate_name(context.properties['uniqueString'], \
            'app1.c.' + context.env['project'] + '.internal'),
        'instanceTemplateVersion': 1,
        'instanceType': 'n1-standard-1',
        'networkSelfLink': '$(ref.' + net_name + '.selfLink)',
        'subnetSelfLink': '$(ref.' + subnet_name + '.selfLink)',
        'uniqueString': context.properties['uniqueString'],
      },
      'metadata': {
        'dependsOn': depends_on_array
      }
    }]
    return application_config

def create_dag_deployment(context):
    """ Create dag module deployment """
    prefix = context.properties['uniqueString']
    mgmt_net_name = generate_name(prefix, 'mgmt-network')
    ext_net_name = generate_name(prefix, 'external-network')
    int_net_name = generate_name(prefix, 'internal2-network')
    if context.properties['numNics'] is 1:
        app_net_name = generate_name(prefix, 'mgmt-network')
    elif context.properties['numNics'] is 2:
        app_net_name = generate_name(prefix, 'external-network')
    else:
        app_net_name = generate_name(prefix, 'internal' + \
            str(context.properties['numNics'] - 1) + '-network')
    depends_on_array = []
    depends_on_array.append(mgmt_net_name)
    mgmt_port = 8443
    if context.properties['numNics'] > 1:
        depends_on_array.append(ext_net_name)
        mgmt_port = 443
    if context.properties['numNics'] > 2:
        depends_on_array.append(int_net_name)
    if context.properties['numNics'] > 3:
        depends_on_array.append(app_net_name)
    dag_configuration = [{
      'name': 'dag',
      'type': '../modules/dag/dag.py',
      'properties': {
        'application': context.properties['application'],
        'applicationPort': '80 443',
        'applicationVipPort': '80 443',
        'cost': context.properties['cost'],
        'environment': context.properties['environment'],
        'group': context.properties['group'],
        'guiPortMgmt': mgmt_port,
        'networkSelfLinkApp': '$(ref.' + app_net_name + '.selfLink)',
        'networkSelfLinkExternal': '$(ref.' + ext_net_name + '.selfLink)',
        'networkSelfLinkInternal': '$(ref.' + int_net_name + '.selfLink)',
        'networkSelfLinkMgmt': '$(ref.' + mgmt_net_name + '.selfLink)',
        'numberOfForwardingRules': 0,
        'numberOfInternalForwardingRules': 0,
        'numberOfNics': context.properties['numNics'],
        'owner': context.properties['owner'],
        'region': context.properties['region'],
        'restrictedSrcAddressApp': context.properties['restrictedSrcAddressApp'],
        'restrictedSrcAddressAppInternal': context.properties['restrictedSrcAddressAppInternal'],
        'restrictedSrcAddressMgmt': context.properties['restrictedSrcAddressMgmt'],
        'uniqueString': context.properties['uniqueString']
      },
      'metadata': {
        'dependsOn': depends_on_array
      }
    }]
    return dag_configuration

def generate_config(context):
    """ Entry point for the deployment resources. """

    name = context.properties.get('name') or \
           context.env['name']
    deployment_name = generate_name(context.properties['uniqueString'], name)

    resources = create_network_deployment(context) + create_bigip_deployment(context) \
    + create_application_deployment(context) + create_dag_deployment(context)

    outputs = [
        {
            'name': 'deploymentName',
            'value': deployment_name
        }
    ]

    return {
        'resources':
            resources,
        'outputs':
            outputs
    }