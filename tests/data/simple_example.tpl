global
    log 127.0.0.1 local0 debug# see /etc/rsyslog.d/10-haproxy
    maxconn 2048
    user haproxy
    group haproxy
    daemon
    stats socket /tmp/haproxy.sock

defaults
    log global
    mode http
    option httplog
    option dontlognull
    option redispatch
    retries 3
    contimeout 5000
    clitimeout 50000
    srvtimeout 20000

frontend http-in
    mode http
    bind 0.0.0.0:80
    option http-server-close

frontend haproxyconfig
    mode http
    bind 0.0.0.0:8080
    option http-server-close
    default_backend haproxyconfig
    
backend haproxyconfig
    mode http
    option httpclose
    #errorfile 503 /etc/haproxy/haproxy.cfg
    
frontend haproxytemplate
    mode http
    bind 0.0.0.0:8081
    option http-server-close
    default_backend haproxytemplate

backend haproxytemplate
    mode http
    option httpclose
    #errorfile 503 /etc/haproxy/templates/example.tpl

backend simple_exampletpl
    mode http
    % for instance in instances['example_sg_1']:
    server ${ instance.id } ${ instance.private_dns_name }:80 cookie ${ instance.id }
    % endfor
    option httpclose
