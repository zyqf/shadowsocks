#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2015 mengskysama
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
# --manager-address /var/run/shadowsocks-manager.sock -c tests/server-multi-passwd.json

import sys
import os
import logging
import thread
import config
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))
from dbtransfer import DBbase
from shadowsocks import shell, daemon, eventloop, tcprelay, udprelay, \
    asyncdns, manager



if config.LOG_ENABLE:                                                                                     
    logging.basicConfig(format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',     
                        datefmt='%Y, %b %d %a %H:%M:%S', filename=config.LOG_FILE, level=config.LOG_LEVEL)
else:
    logging.basicConfig(format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%Y, %b %d %a %H:%M:%S', level=logging.DEBUG)

def handler_SIGQUIT():
    return


def main():
    configer = {
        'server': config.SS_BIND_IP,
        "local_port": 1080,
        "server_port":1081,
        "port_password": {
            "1234": "1223"

        },
        "timeout": config.timeout,
        'manager_address': config.manager_address,
        'method': '%s' % config.SS_METHOD,
        "local_address": "127.0.0.1",
        "fast_open": config.fast_open,
        "tunnel_remote": config.tunnel_remote,
        "dns_server": config.dns_server,
        'verbose': 2
    }
    adduser = DBbase()
    updateuser = DBbase()

    os.system('rm -rf %s'%config.manager_address)
    os.system("rm -rf /tmp/shadowsock_traffic.sock")
    os.system("rm -rf /tmp/client_manager.sock")


    t = thread.start_new_thread(manager.run, (configer,))
    time.sleep(1)
    t = thread.start_new_thread(adduser.push_all_user, ())
    time.sleep(1)
    t = thread.start_new_thread(updateuser.update_shadowsock_traffic(), ())

    while True:
        time.sleep(100)


if __name__ == '__main__':
    main()
