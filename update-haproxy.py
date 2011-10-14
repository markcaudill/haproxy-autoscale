from boto.ec2.connection import EC2Connection
from boto.ec2.securitygroup import SecurityGroup
from boto.ec2.instance import Instance
from mako.template import Template
import argparse
import os
import subprocess
import logging


def main():
    # Parse up the command line arguments.
    parser = argparse.ArgumentParser(description='Update haproxy to use all instances running in a security group.')
    parser.add_argument('--security-group', required=True)
    parser.add_argument('--access-key', required=True)
    parser.add_argument('--secret-key', required=True)
    parser.add_argument('--output', default='haproxy.cfg',
                        help='Defaults to haproxy.cfg if not specified.')
    parser.add_argument('--template', default='templates/haproxy.tpl')
    parser.add_argument('--haproxy', default='./haproxy',
                        help='The haproxy binary to call. Defaults to haproxy if not specified.')
    parser.add_argument('--pid', default='/var/run/haproxy.pid',
                        help='The pid file for haproxy. Defaults to /var/run/haproxy.pid.')
    args = parser.parse_args()

    # Wrap everytihg in a try block. Any exceptions and exit without changing
    # anything just to be safe.
    new_configuration = None
    try:
        # Create a connection to EC2.
        logging.debug('Connecting to EC2.')
        conn = EC2Connection(aws_access_key_id=args.access_key,
                             aws_secret_access_key=args.secret_key)
    
        # Get the security group.
        logging.debug('Fetching security group (%s).' % args.security_group)
        sg = SecurityGroup(connection=conn, name=args.security_group)
    
        # Fetch a list of all the instances in this security group.
        logging.debug('Getting instance.')
        instances = [i for i in sg.instances() if i.state == 'running']
    
        # Load in the existing config file contents.
        logging.debug('Locading existing configuration.')
        f = open(args.output, 'r')
        old_configuration = f.read()
        f.close()
    
        # Generate the new config from the template.
        logging.debug('Generating configuration for haproxy.')
        new_configuration = Template(filename=args.template).render(instances=instances)
    except:
        logging.error('Something went wrong! Exiting without making changes.')
        return False

    # See if this new config is different. If it is then restart using it.
    # Otherwise just delete the temporary file and do nothing.
    logging.debug('Comparing to existing configuration.')
    if old_configuration != new_configuration:
        logging.debug('Existing configuration is outdated.')

        # Overwite the real config file.
        logging.debug('Writing new configuration.')
        output = open(args.output, 'w')
        output.write(Template(filename=args.template).render(instances=instances))
        output.close()

        # Get PID if haproxy is already running.
        logging.debug('Fetching PID from %s.' % args.pid)
        pid = ''
        try:
            pidfile = open(args.pid, 'r')
            pid = pidfile.read()
            pidfile.close()
        except:
            logging.warn('Unable to read from %s. haproxy may not be running already.')

        # Restart haproxy.
        logging.debug('Restarting haproxy.')
        command = '''%s -p %s -f %s -sf %s''' % (args.haproxy, args.pid, args.output, pid)
        logging.debug('Executing: %s' % command)
        subprocess.call(command, shell=True)
    else:
        logging.debug('Existing configuration is up-to-date.')


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.ERROR)
    main()
