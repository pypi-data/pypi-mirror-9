# Copyright (C) PyZMQ Developers
# Distributed under the terms of the Modified BSD License.

import sys
from unittest import TestCase

class TestImports(TestCase):
    """Test Imports - the quickest test to ensure that we haven't
    introduced version-incompatible syntax errors."""

    def test_toplevel(self):
        """test toplevel import"""
        import appdynamics_bindeps.zmq

    def test_core(self):
        """test core imports"""
        from appdynamics_bindeps.zmq import Context
        from appdynamics_bindeps.zmq import Socket
        from appdynamics_bindeps.zmq import Poller
        from appdynamics_bindeps.zmq import Frame
        from appdynamics_bindeps.zmq import constants
        from appdynamics_bindeps.zmq import device, proxy
        from appdynamics_bindeps.zmq import Stopwatch
        from appdynamics_bindeps.zmq import (
            zmq_version,
            zmq_version_info,
            pyzmq_version,
            pyzmq_version_info,
        )

    def test_devices(self):
        """test device imports"""
        import appdynamics_bindeps.zmq.devices
        from appdynamics_bindeps.zmq.devices import basedevice
        from appdynamics_bindeps.zmq.devices import monitoredqueue
        from appdynamics_bindeps.zmq.devices import monitoredqueuedevice

    def test_log(self):
        """test log imports"""
        import appdynamics_bindeps.zmq.log
        from appdynamics_bindeps.zmq.log import handlers

    def test_eventloop(self):
        """test eventloop imports"""
        import appdynamics_bindeps.zmq.eventloop
        from appdynamics_bindeps.zmq.eventloop import ioloop
        from appdynamics_bindeps.zmq.eventloop import zmqstream
        from appdynamics_bindeps.zmq.eventloop.minitornado.platform import auto
        from appdynamics_bindeps.zmq.eventloop.minitornado import ioloop

    def test_utils(self):
        """test util imports"""
        import appdynamics_bindeps.zmq.utils
        from appdynamics_bindeps.zmq.utils import strtypes
        from appdynamics_bindeps.zmq.utils import jsonapi



