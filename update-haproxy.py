import argparse 
import subprocess
import logging
import sys
import time
from haproxy_autoscale import get_running_instances, file_contents, generate_haproxy_config, restart_haproxy

def parse_args():
    # Parse up the command line arguments.
    parser = argparse.ArgumentParser(description='Update haproxy to use all instances running in a security group.')
    parser.add_argument('--security-group', required=True, nargs='+', type=str)
    parser.add_argument('--access-key', required=True)
    parser.add_argument('--secret-key', required=True)
    parser.add_argument('--output', default='haproxy.cfg',
                        help='Defaults to ./haproxy.cfg if not specified.')
    parser.add_argument('--template', default='templates/haproxy.tpl',
                        help="the template you want to use for generating the HAproxys config file")
    parser.add_argument('--servicename', default="haproxy", 
                        help='The OS service name to restart (Ubuntu only)')
    parser.add_argument('--haproxy', default=None,
                        help='The haproxy binary to call. Defaults to haproxy if not specified.\n\
                        Not needed if --servicename is used')
    parser.add_argument('--pid', default='/var/run/haproxy.pid',
                        help='The pid file for haproxy. Defaults to /var/run/haproxy.pid.\n\
                        Not needed if --servicename is used')
    parser.add_argument('--sleep', default=False, type=int,
                        help='If specified this script will go in a continous loop, sleeping this amount between runs.')
    
    args = parser.parse_args()
    
    # syntax checking
    if args.servicename != "haproxy" and args.haproxy:
        logging.fatal("you must supply either \"--servicename\" OR \"--haproxy\", dont know what to restart now")
        sys.exit(2)
    
    if args.servicename == "haproxy" and not args.haproxy:
        logging.info("no \"--servicename\" OR \"--haproxy\" arguments found, defaulting to restarting service haproxy")
    
    return args
    
def main(args):    
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
    old_configuration = file_contents(filename=args.output)
    
    if new_configuration != old_configuration:
        logging.info('Existing configuration is outdated.')
        
        # Overwite the existing config file.
        logging.info('Writing new configuration.')
        file_contents(filename=args.output,
                      content=generate_haproxy_config(template=args.template,
                                                      instances=instances    ))
        
        restart_haproxy(args)
        
    else:
        logging.info('Configuration unchanged. Skipping restart.')
    
if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    args = parse_args()
    
    if args.sleep: #continous runs
        logging.info("continous mode, sleeping %i seconds between runs\n" % args.sleep)
        while True:
            main(args)
            time.sleep(args.sleep)
    
    else: #standard, onetime run
        main(args)
