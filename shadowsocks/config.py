import logging

#BIND IP
#if you want bind ipv4 and ipv6 '[::]'
#if you want bind all of ipv4 if '0.0.0.0'
#if you want bind all of if only '4.4.4.4'
SS_BIND_IP = "::"
SS_METHOD = 'chacha20'

#local udp
manager_address = '/tmp/shadowsocks_main_manager.sock'

#shadowsocks config
tunnel_remote = "208.67.222.222"
dns_server = ["208.67.222.222", "8.8.4.4"]
fast_open = False
timeout = 300

#DB config
DBHOST = "127.0.0.1"
DBUSER = "root"
DBPASS = "root"
DBNAME = "shadowsocks"


#Other
CHECKTIME = 15
SYNCTIME=10
#LOG CONFIG
LOG_ENABLE = False
LOG_LEVEL = logging.CRITICAL
LOG_FILE = '/tmp/shadowsocks.log'

