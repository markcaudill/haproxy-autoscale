global  
    daemon
    maxconn 256

defaults
    mode http
    timeout connect 5000ms
    timeout client 5000ms
    timeout server 5000ms

frontend www *:80
    mode http
    maxconn 50000
    default_backend servers

backend servers
    mode http
    balance roundrobin
    % for instance in instances['security-group-1']:
    server ${ instance.id } ${ instance.private_dns_name }
    % endfor

frontend java *:8080,*:8443
    mode http
    maxconn 50000
    default_backend java_servers

backend java_servers
    mode http
    balance roundrobin
    % for instance in instances['security-group-2']:
    server ${ instance.id } ${ instance.private_dns_name }
    % endfor
