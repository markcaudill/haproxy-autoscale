from boto.ec2 import EC2Connection
from boto.ec2.securitygroup import SecurityGroup
import logging
from mako.template import Template
import urllib2

def get_self_instance_id():
    '''
    Get this instance's id.
    '''
    logging.debug('get_self_instance_id()')
    response = urllib2.urlopen('http://169.254.169.254/1.0/meta-data/instance-id')
    instance_id = response.read()
    return instance_id


def steal_elastic_ip(access_key=None, secret_key=None, ip=None):
    '''
    Assign an elastic IP to this instance.
    '''
    logging.debug('steal_elastic_ip()')
    instance_id = get_self_instance_id()
    conn = EC2Connection(aws_access_key_id=access_key,
                         aws_secret_access_key=secret_key)
    conn.associate_address(instance_id=instance_id, public_ip=ip)


def get_running_instances(access_key=None, secret_key=None, group=None):
    '''
    Get all running instances that have a tag that matches
    'haproxy-autoscale-group' => group.
    '''
    logging.debug('get_running_instances()')
    instances = []
    # Get all the regions.
    conn = EC2Connection(aws_access_key_id=access_key,
                         aws_secret_access_key=secret_key)
    ec2_region_list = conn.get_all_regions()
    # Check each region for running instances.
    for index, region in enumerate(ec2_region_list):
        conn = EC2Connection(aws_access_key_id=access_key,
                             aws_secret_access_key=secret_key,
                             region=ec2_region_list[index])
        for reservation in conn.get_all_instances():
            for instance in reservation.instances:
                if instance.state == 'running':
                    if 'haproxy-autoscale-group' in instance.tags:
                        if instance.tags['haproxy-autoscale-group'] == group:
                            instances.append(instance)
    return instances


def file_contents(filename=None, content=None):
    '''
    Just return the contents of a file as a string or write if content
    is specified. Returns the contents of the filename either way.
    '''
    logging.debug('file_contents()')
    if content:
        f = open(filename, 'w')
        f.write(content)
        f.close()

    try:
        f = open(filename, 'r')
        text = f.read()
        f.close()
    except:
        text = None

    return text


def generate_haproxy_config(template=None, instances=None):
    '''
    Generate an haproxy configuration based on the template and instances list.
    '''
    return Template(filename=template).render(instances=instances)
