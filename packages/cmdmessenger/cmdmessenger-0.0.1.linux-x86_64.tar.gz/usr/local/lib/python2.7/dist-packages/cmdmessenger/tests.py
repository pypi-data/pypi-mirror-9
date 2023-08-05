#!/usr/bin/env python

import serial

from . import messenger

cmds = [
    {'name': 'kCommError'},
    {'name': 'kComment'},
    {'name': 'kAcknowledge'},
    {'name': 'kAreYouReady'},
    {'name': 'kError'},
    {'name': 'kAskIfReady'},
    {'name': 'kYouAreReady'},
    {'name': 'kValuePing'},
    {'name': 'kValuePong'},
    {'name': 'kMultiValuePing'},
    {'name': 'kMultiValuePong'},
    {'name': 'kRequestReset'},
    {'name': 'kRequestResetAcknowledge'},
    {'name': 'kRequestSeries'},
    {'name': 'kReceiveSeries'},
    {'name': 'kDoneReceiveSeries'},
    {'name': 'kPrepareSendSeries'},
    {'name': 'kSendSeries'},
    {'name': 'kAckSendSeries'},
]


def setup(port='/dev/ttyUSB0'):
    s = serial.Serial(port, 115200)
    return messenger.Messenger(s, cmds)


def run(m):
    pass


def test():
    m = setup()
    run(m)
