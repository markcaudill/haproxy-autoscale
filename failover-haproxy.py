import argparse
import logging
from haproxy_autoscale import steal_elastic_ip
import urllib2

def main():
    # Parse up the command line arguments.
    parser = argparse.ArgumentParser(description='Update haproxy to use all instances running in a security group.')
    parser.add_argument('--access-key', required=True)
    parser.add_argument('--secret-key', required=True)
    parser.add_argument('--eip',
                        help='The Elastic IP to bind to when VIP seems unhealthy.')
    parser.add_argument('--health-check-url',
                        help='The URL to check. Assigns EIP to self if health check fails.')
    args = parser.parse_args()
    
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
                                 ip=args.eip )

    except:
        pass

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    main()    