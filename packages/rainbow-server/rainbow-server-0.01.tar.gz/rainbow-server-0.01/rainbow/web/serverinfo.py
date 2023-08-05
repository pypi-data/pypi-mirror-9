# encoding=utf-8

import traceback
import logging as log
import json
import commands
import os

import tornado

from webhandler import ClusterWebHandler
from wshandler import serverinfo


def process_info():
    pid = os.getpid()
    ps_command = "/bin/ps aux | /usr/bin/awk '$2==%d'" % pid
    log.info(ps_command)
    l = commands.getstatusoutput(ps_command)
    log.info(l)
    l = l[1]
    log.info(l)
    l = l.split()
    log.info(l)
    info = {'user': l[0],
            'pid': l[1],
            'cpu': l[2],
            'mem': l[3],
            }
    return info


class ServerInfoHandler(ClusterWebHandler):

    def prepare(self):
        self.need_sign = False
        return super(ClusterWebHandler, self).prepare()

    @tornado.web.asynchronous
    def get(self):
        try:
            self.cluster_init()
            if not self.get_query_argument('cluster', ''):
                self.cluster = False
                self.cluster_send_get(uri='serverinfo')
            else:
                self.cluster = True

            self.data = {}
            self.data['serverinfo'] = []

            data = serverinfo()
            data['status'] = 0
            data['process'] = process_info()
            self.handler_return(data)
        except Exception, e:
            self.exception_finish(e, traceback.format_exc())

    def handler_return(self, data):
        log.debug('ServerInfoHandler data = %s' % data)
        self.server_rsp_cnt = self.server_rsp_cnt + 1

        if self.cluster:
            self.data = data
        else:
            if data['status'] == 0:
                self.data['serverinfo'].append(data)

        if self.server_rsp_cnt == self.server_cnt:
            self.send_finish()

    def sort_by_host(self, item):
        return item['server']

    def send_finish(self):
        log.debug('self.data = %s' % self.data)
        try:
            if self.cluster:
                self.finish(json.dumps(self.data))
            else:
                self.data['serverinfo'] = sorted(
                    self.data['serverinfo'], key=self.sort_by_host)
                self.render('serverinfo.html', data=self.data)
        except Exception, e:
            self.exception_finish(e, traceback.format_exc())
