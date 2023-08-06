import os, sys
sys.path.insert(0, os.path.abspath('..'))

from tests.server_runner import EllipticsRunner
from historydb import Provider

import logging



class BaseTestWithServers(object):

    runner = None
    elliptics_addr = None
    leave_files = False
    tmp_dir = None
    root_dir = os.path.expanduser("~/elliptics-tests")
    print_test_name_in_setup = True

    @classmethod
    def setUpClass(cls):
        cls.elliptics_addr = "localhost:1026:2"
        cls.thevoid_addr = "127.0.0.1:8089"
        #return
        cls.runner = EllipticsRunner(cls.root_dir, cls.elliptics_addr, cls.thevoid_addr)
        tmp_dir = None
        if cls.tmp_dir:
            tmp_dir = os.path.join(cls.root_dir, cls.tmp_dir)
        cls.runner.start(tmp_dir)

    @classmethod
    def tearDownClass(cls):
        if cls.runner:
            cls.runner.stop(cls.leave_files)

    @classmethod
    def create_provider(cls, **kwargs):
        return Provider(**cls.provider_kwargs(**kwargs))

    @classmethod
    def provider_kwargs(cls, **additional):
        kwargs = {"servers": [cls.elliptics_addr], "groups": [1]}
        kwargs.update(additional)
        return kwargs

    def setUp(self):
        if self.print_test_name_in_setup:
            logging.info("!!! Starting: {}".format(self))
