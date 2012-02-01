import boto.ec2.connection
from boto.ec2.connection import EC2Connection
from boto.ec2.securitygroup import SecurityGroup
from boto.ec2.instance import Instance
from mako.template import Template
import argparse
import os
import subprocess
import logging
from haproxy_autoscale import get_running_instances, file_contents, generate_haproxy_config, steal_elastic_ip
import urllib2


def main():
    # Parse up the command line arguments.
    parser = argparse.ArgumentParser(description='Update haproxy to use all instances running in a security group.')
    parser.add_argument('--security-group', required=True, nargs='+', type=str)
    parser.add_argument('--access-key', required=True)
    parser.add_argument('--secret-key', required=True)
    parser.add_argument('--output', default='haproxy.cfg',
                        help='Defaults to haproxy.cfg if not specified.')
    parser.add_argument('--template', default='templates/haproxy.tpl')
    parser.add_argument('--haproxy', default='./haproxy',
                        help='The haproxy binary to call. Defaults to haproxy if not specified.')
    parser.add_argument('--pid', default='/var/run/haproxy.pid',
                        help='The pid file for haproxy. Defaults to /var/run/haproxy.pid.')
    parser.add_argument('--eip',
                        help='The Elastic IP to bind to when VIP seems unhealthy.')
    parser.add_argument('--health-check-url',
                        help='The URL to check. Assigns EIP to self if health check fails.')
    args = parser.parse_args()

    # Fetch a list of all the instances in these security groups.
    instances = {}
    for security_group in args.security_group:
        logging.info('Getting instances for %s.' % security_group)
        instances[security_group] = get_running_instances(access_key=args.access_key,
                                                          secret_key=args.secret_key,
                                                          security_group=security_group)
    # Generate the new config from the template.
    logging.info('Generating configuration for haproxy.')
    new_configuration = generate_haproxy_config(template=args.template,
                                                instances=instances)
    # See if this new config is different. If it is then restart using it.
    # Otherwise just delete the temporary file and do nothing.
    logging.info('Comparing to existing configuration.')
    logging.info('Existing configuration is outdated.')

    # Overwite the real config file.
    logging.info('Writing new configuration.')
    file_contents(filename=args.output,
                  content=generate_haproxy_config(template=args.template,
                                                  instances=instances    ))

    # Get PID if haproxy is already running.
    logging.info('Fetching PID from %s.' % args.pid)
    pid = file_contents(filename=args.pid)

    # Restart haproxy.
#   logging.info('Restarting haproxy.')
#   command = '''%s -p %s -f %s -sf %s''' % (args.haproxy, args.pid, args.output, pid or '')
#   logging.info('Executing: %s' % command)
#   subprocess.call(command, shell=True)

    # Do a health check on the url if specified.
    try:
        if args.health_check_url and args.eip:
            logging.info('Performing health check.')
            try:
                logging.info('Checking %s' % args.health_check_url)
                response = urllib2.urlopen(args.health_check_url)
                logging.info('Response: %s' % response.read())
            except:
                # Assign the EIP to self.
                logging.warn('Health check failed. Assigning %s to self.' % args.eip)
                steal_elastic_ip(access_key=args.access_key,
                                 secret_key=args.secret_key,
                                 ip=args.eip                )
    except:
        pass



if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    main()
