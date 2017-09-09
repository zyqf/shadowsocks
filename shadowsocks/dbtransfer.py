# /usr/bin/python2
# yum install MySQL-python
# ALTER TABLE `user` ADD `pass` VARCHAR(20) NOT NULL AFTER `id`;
import MySQLdb
import MySQLdb.cursors
import os
import sys
import config
import logging
import copy
import time

if config.LOG_ENABLE:
    logging.basicConfig(format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%Y, %b %d %a %H:%M:%S', filename=config.LOG_FILE, level=config.LOG_LEVEL)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))
from shadowsocks import common, shell


class DBbase(object):
    def __init__(self, host=config.DBHOST, user=config.DBUSER, passwd=config.DBPASS, database=config.DBNAME, port=3306,
                 charset='utf8'):
        import socket
        super(DBbase, self).__init__()
        self.host = host
        self.user = user
        self.passwd = passwd
        self.database = database
        self.port = port
        self.charset = charset
        self.connectDB()
        self.old_user = {}

    def connectDB(self):
        try:
            db = MySQLdb.connect(
                host=self.host,
                user=self.user,
                passwd=self.passwd,
                db=self.database,
                port=self.port,
                charset=self.charset,
                cursorclass=MySQLdb.cursors.DictCursor
            )
            return db
        except Exception as e:
            raise e

    def return_port_ip(self, port, users):

        if type(port) is not int:
            print("the type must be int")
            return
        for user in users:
            # print(user)
            if user['port'] == port:
                return user['id']

    def flush_user(self, mcli):
        new_user = self.toFilter()
        old_user = self.old_user
        for user in old_user:
            if not new_user.has_key(user):
                logging.debug("remove %s" % user)
                mcli.send(b'remove: {"server_port":%s}' % user)

        for user in new_user:
            if not old_user.has_key(user):
                self.add_user(new_user[user], mcli)
                continue
            if new_user[user]["passwd"] != old_user[user]["passwd"] or new_user[user]["method"] != old_user[user][
                "method"]:
                # change user passwd or method
                mcli.send(b'remove: {"server_port":%s}' % user)
                time.sleep(0.2)
                self.add_user(new_user[user], mcli)

        self.old_user = copy.deepcopy(new_user)
        new_user = None

    def add_user(self, data, mcli):
        port = data["port"]
        passwd = data["passwd"]
        method = data["method"]
        mcli.send(b'add: {"server_port":%s, "password":"%s" ,"method":"%s"}' % (port, passwd, method))
        time.sleep(0.2)

    def toFilter(self):
        data = {}
        db = self.connectDB()
        cursor = db.cursor()
        cursor.execute('select * from user')
        users = cursor.fetchall()
        db.close
        for user in users:
            if user["enable"] == 0:
                continue
            if user["d"] > user["transfer_enable"]:
                continue
            id = user["id"]
            port = user["port"]
            ssmethod = user['pass']
            passwd = user["passwd"]
            if len(ssmethod) < 1:
                ssmethod = config.SS_METHOD
            data[str(port)] = {"port": port, "passwd": passwd, "method": ssmethod}

        return data

    def commit_traffic_info(self, data):
        db = self.connectDB()
        cursor = db.cursor()
        cursor.execute('select * from user')
        users = cursor.fetchall()
        for port in data.iterkeys():
            port_id = self.return_port_ip(int(port), users)
            datasize = data[port]
            logging.critical("==> id: %s port: %s size: %s <==" % (port_id, port, datasize))
            sql = "UPDATE `shadowsocks`.`user` SET `t`= '%s',`d`= `d` + '%s' WHERE `id`= '%s' and`port`='%s';" % (
                str(int(time.time())), str(datasize), str(port_id), str(port))
            cursor.execute(sql)
        db.commit()
        db.close()


    def update_shadowsock_traffic(self):
        import socket
        socket.setdefaulttimeout(30)
        cli = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        cli.bind('/tmp/shadowsock_traffic.sock')  # address of the client
        cli.connect(config.manager_address)
        cli.send(b'ping')
        data = cli.recv(1506)
        logging.debug(data)
        cli.send(b'remove: {"server_port":1234}')
        logging.debug(cli.recv(1506))

        while True:
            try:
                data = cli.recv(1506)
                if "stat: " not in data:
                    logging.critical(data)
                    continue
                data = common.to_str(data)
                data = data.split('stat: ')[1]
                stats = shell.parse_json_in_str(data)
                self.commit_traffic_info(stats)
            except Exception as e:
                cli.send(b'ping')



    def push_all_user(self):
        import time
        import socket
        socket.setdefaulttimeout(1)
        mcli = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        mcli.bind('/tmp/client_manager.sock')
        mcli.connect(config.manager_address)
        while True:
            logging.info('db Manager user')
            try:
                self.flush_user(mcli)
                time.sleep(5)
            except Exception as e:
                import traceback
                traceback.print_exc()
                logging.warn('db thread except:%s' % e)
            finally:
                time.sleep(config.SYNCTIME)


if __name__ == '__main__':
    pass
