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


def get_running_instances(access_key=None, secret_key=None, security_group=None):
    '''
    Get all running instances. Only within a security group if specified.
    '''
    logging.debug('get_running_instances()')

    instances_all_regions_list = []
    conn = EC2Connection(aws_access_key_id=access_key,
                         aws_secret_access_key=secret_key)
    ec2_region_list = conn.get_all_regions()

    if security_group:
        for index, region in enumerate(ec2_region_list):
            conn = EC2Connection(aws_access_key_id=access_key,
                                 aws_secret_access_key=secret_key,
                                 region=ec2_region_list[index])
            running_instances = []
            for s in conn.get_all_security_groups():
               if s.name == security_group:
                   running_instances = [i for i in s.instances() if i.state == 'running']
            if running_instances:
                for instance in running_instances:
                    instances_all_regions_list.append(instance)
    else:
        for index, region in enumerate(ec2_region_list):
            conn = EC2Connection(aws_access_key_id=access_key,
                                 aws_secret_access_key=secret_key,
                                 region=ec2_region_list[index])
            reserved_instances = conn.get_all_instances()
            if reserved_instances:
                for reservation in reserved_instances:
                    for instance in reservation.instances:
                        if instance.stat == 'running':
                            instances_all_regions_list.append(instance)
    return instances_all_regions_list


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
