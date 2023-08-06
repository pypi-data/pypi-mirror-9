#!/usr/bin/env python
""" Elliptics test server
Based on https://github.com/reverbrain/historydb/blob/master/test/misc.py
"""
import os
import sys
import signal
import random
import logging
import json
from subprocess import Popen
from shutil import rmtree
from time import sleep


log = logging.getLogger(__name__)

ELLIPTICS_CONF_TEMPLATE = {
    "loggers": {
        "type": "/dev/stderr",
        "level": 1
    },
    "options": {
        "join": True,
        "flags": 20,
        "remote": [
            "{elliptics_addr}"
        ],
        "address": [
            "{elliptics_addr}"
        ],
        "wait_timeout": 30,
        "check_timeout": 50,
        "io_thread_num": 4,
        "nonblocking_io_thread_num": 4,
        "net_thread_num": 4,
        "daemon": False,
        "auth_cookie": "unique_storage_cookie",
        "bg_ionice_class": 3,
        "bg_ionice_prio": 0,
        "server_net_prio": 1,
        "client_net_prio": 6,
        "cache": {
            "size": 0
        },
        "indexes_shard_count": 2,
        "monitor": {
            "port": 20000,
            "call_tree_timeout": 0
        }
    },
    "backends": [
        {
            "backend_id": 1,
            "type": "blob",
            "group": 1,
            "history": "/var/blob",
            "data": "/var/blob/data",
            "sync": "-1",
            "blob_flags": "2",
            "blob_size": "1G",
            "records_in_blob": "1000000",
            "periodic_timeout": 15
        }
    ]
}

HISTORYDB_THEVOID_TEMPLATE = """{{
    "endpoints": [
        "{thevoid_addr}"
    ],
    "daemon": {{
        "monitor-port": 20001
    }},
    "backlog": 128,
    "threads": 2,
    "application": {{
        "loglevel": 5,
        "logfile": "{directory}/historydb-test.log",
        "remotes": [
            "{elliptics_addr}"
        ],
        "groups": [
            1
        ]
    }}
}}"""


class EllipticsRunner(object):
    def __init__(self, root_dir, elliptics_addr="localhost:2025:2", thevoid_addr="127.0.0.1:8089", kill_timeout=5):
        self.ellitptics_addr = elliptics_addr
        self.thevoid_addr = thevoid_addr
        self.root_dir = root_dir
        self.kill_timeout = kill_timeout
        self.tmp_dir = None
        self.ioserv = None
        self.thevoid = None
        self.is_running = False

    def output_configs(self, directory):
        kwargs = dict(directory=directory,
                      elliptics_addr=self.ellitptics_addr,
                      thevoid_addr=self.thevoid_addr,)
        ELLIPTICS_CONF_TEMPLATE["options"]["remote"] = [self.ellitptics_addr]
        ELLIPTICS_CONF_TEMPLATE["options"]["address"] = [self.ellitptics_addr]
        ELLIPTICS_CONF_TEMPLATE["backends"][0]["history"] = directory
        ELLIPTICS_CONF_TEMPLATE["backends"][0]["data"] = os.path.join(directory, "data")
        ELLIPTICS_CONF_TEMPLATE["loggers"]["type"] = os.path.join(directory, "elliptics.log")
        with open(os.path.join(directory, "elliptics.conf"), "w+") as f:
            f.write(json.dumps(ELLIPTICS_CONF_TEMPLATE))
        with open(os.path.join(directory, "historydb.json"), "w+") as f:
            f.write(HISTORYDB_THEVOID_TEMPLATE.format(**kwargs))

    def start(self, tmp_dir=None):
        if tmp_dir:
            self.tmp_dir = tmp_dir
        else:
            self.tmp_dir = tmp_dir = os.path.join(self.root_dir, "historydb-test-" + hex(random.randint(0, sys.maxint))[2:])
        if not os.path.exists(self.tmp_dir):
            try:
                os.makedirs(self.tmp_dir, 0755)
            except Exception as e:
                raise ValueError("Directory: {0} does not exist and could not be created: {1}".format(self.tmp_dir, e))
        else:
            try:
                os.remove(os.path.join(self.tmp_dir, "data.lock"))
            except Exception:
                pass
        self.output_configs(tmp_dir)
        log.info("Starting in %s ...", tmp_dir)
        self.ioserv = Popen(["dnet_ioserv", "-c", os.path.join(tmp_dir, "elliptics.conf")])
        try:
            self.thevoid = Popen(["historydb-thevoid", "-c", os.path.join(tmp_dir, "historydb.json")])
        except OSError:
            log.error("historydb-thevoid unavailable")
            pass
        self.wait_elliptics_start()
        log.info("Server started")
        self.is_running = True

    def stop_app(self, app):
        if not app:
            return
        log.info("Stoping %s", app.pid)
        app.send_signal(signal.SIGINT)
        if app.poll():
            sleep(self.kill_timeout)
            if app.poll():
                log.info("Killing %s after %s seconds", app.pid, self.kill_timeout)
                try:
                    app.kill()
                except OSError:
                    pass
        # ensure killed
        try:
            app.kill()
        except OSError:
            pass

    def stop(self, leave_files=False):
        self.stop_app(self.ioserv)
        self.stop_app(self.thevoid)

        if not leave_files:
            rmtree(self.tmp_dir, True)
        self.is_running = False

    def wait_elliptics_start(self):
        from historydb import Provider
        import elliptics
        n_tries = 10

        for i in range(n_tries):
            try:
                Provider([self.ellitptics_addr], [1])
                break
            except elliptics.Error:
                sleep(0.3)

    def print_logs(self):
        with open(os.path.join(self.tmp_dir, "historydb-elliptics.log")) as f:
            print f.read()
