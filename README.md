# haproxy-autoscale #

## Description ##
I had a project I was working on where I needed a private load balancer to use
on Amazon Web Services. Unfortunately, AWS Elastic Load Balancers do not
support private listeners so I needed to make my own load balancer using
Linux.

Making a load balancer is pretty straight forward. The challenge was that the
instances under it were auto-scaling and there was no built-in mechanism for
the load balancer to know to send traffic to new instances and to stop sending
traffic to deleted instances.

Enter haproxy-autoscale. This is a wrapper of sorts that will automatically add
all instances in a security group that are currently in a running state to the
haproxy configuration. It then restarts haproxy in a manner which gracefully
terminates connections so there is no downtime. Also, haproxy will only be
restarted if there are changes. If there are no changes in the isntances that
should be sent traffic then it just exits.

I've actually bundled the haproxy binary with this repo to make things easier
when getting started.

The update-haproxy.py script does a good job with basic setups using the
default options but as things get more complex you may want to get more
specific with the paramters. For instance, if you decide to run multiple
instances at the same time then you should probably specifify different
templates, outputs and pid files for each.

## Installation ##
Run `sudo python setup.py install` and if everything goes well you're ready to
configure (if you have complex needs) and run the update-haproxy.py command.

## Configuration ##
Most of the configuration is done via command line options. The only
configuration that may need to be done is the haproxy.cfg template. You can
customize it to suit your needs or you can specify a different on on the
command line. Make sure to read the existing template to see what variables
will be available to use.

## Usage ##
haproxy-autoscale was designed to be run from the load balancer itself as a cron
job. Ideally it would be run every minute.

    update-haproxy.py [-h] --security-group SECURITY_GROUP --access-key
                      ACCESS_KEY --secret-key SECRET_KEY [--output OUTPUT]
                      [--template TEMPLATE] [--haproxy HAPROXY] [--pid PID]
    
    optional arguments:
      -h, --help            show this help message and exit
      --security-group SECURITY_GROUP
      --access-key ACCESS_KEY
      --secret-key SECRET_KEY
      --output OUTPUT       Defaults to haproxy.cfg.
      --template TEMPLATE   Defaults to templates/haproxy.cfg.
      --haproxy HAPROXY     The haproxy binary to call. Defaults to haproxy.
      --pid PID             The pid file for haproxy. Defaults to
                            /var/run/haproxy.pid.

Example:

    /usr/bin/python update-haproxy.py --access-key='SOMETHING' --secret-key='SoMeThInGeLsE' --security-group='webheads'

