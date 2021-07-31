"""
Created on Mar 23, 2017

@author: smcochra

3/27/2017 - edited by smcochra 
"""

import telnetlib
import time
import datetime
import re
import paho.mqtt.client as mqtt
import copy
import json

#BROKER_ADD = 'broker.mqttdashboard.com'
BROKER_ADD = '10.6.47.88'
# BROKER_ADD = '10.130.41.48'
BROKER_PORT = 1883


class TelnetDriver(object):
    '''
    Wrapper for telnetlib. Shouldn't be called directly, use TelnetAccessor
    '''
    _ip = None
    _port = None
    mqtt_client = None
    mqtt_id = None
    qos = None
    topic = None

    def __init__(self, mqtt_id=None, qos=0, debugFlag=False):
        '''
        Pass console, return telnet session
        + console - (optional) format <ip>:<port> e.g. '192.168.1.1:3003'
        + qos - Quality of service for mqtt range int([0, 2])
        + mqtt_id - identifier for MQTT client to launch on 'open' call
                  - if None, no Client will launch
        + loc - string location of test being executed. e.g. 'SAN JOSE'
        + debugFlag - enables debug messaging
        '''
        self.debugFlag = debugFlag
        self.debug('Hello (telnet) World')

        self.mqtt_id = mqtt_id
        self.qos = qos
        self.topic = '%s/console' % mqtt_id

    def _on_message(self, client, userdata, msg):
        # not expecting to receive any messages 
        pass

    def set_debug_flag(self, flag):
        """
        Enable/Disable debug messaging
        + flag - True/False
        """
        self.debugFlag = flag

    def open(self, console):
        self.t = telnetlib.Telnet()

        self._ip = console.split(':')[0]
        self._port = int(console.split(':')[1])

        self.init_mqtt(console)

        self.debug("Attempting to open connection with IP: '%s' Port: '%s'" % (
            self._ip, self._port))
        self.t.open(self._ip, self._port)
        self.debug("Session opened!")


    def init_mqtt(self, console):
        print("Initializing MQTT for console\n====\n")
        if self.mqtt_id:
            userdata = {'process_id': self.mqtt_id,
                        'console_ip': console,
                        'timezone': time.strftime("%z", time.gmtime()),
                        'start_time': self.get_time()}
            self.mqtt_client = mqtt.Client(userdata=userdata)
            self.mqtt_client.on_connect = self._on_connect
            self.mqtt_client.on_message = self._on_message

            self.mqtt_client.connect(BROKER_ADD, BROKER_PORT)

    def _on_connect(client, userdata, rc):
        print("MQTT Client [%s] connected with result code %s" % (
                userdata['process_id'], str(rc)))

    def _on_message(client, userdata, msg):
        print('Received message! [Thread: %s] %s' % (msg.topic, msg.payload))

    def send(self, data):
        """
        + data - string to push to socket
        """
        self.t.write(data)

    def expect_old(self, matchlist, timeout=5):
        """
        Returns tupple (idx, mtext, buf, timeout)
        + idx - index of matched expr in matchlist; -1 if timeout occurs
        + mtext - matchobject; if match, mtext.group(idx) returns actual matched text, else returns None
        + buf - buffer from time of expect starts to timeout/match
        """
        self.t.cookedq = ''

        if not isinstance(matchlist, list):
            matchlist = [matchlist]

        idx, mtext, buf = self.t.expect(matchlist, timeout=timeout)

        return (idx, mtext, buf)

    def expect(self, matchlist, timeout=5):
        """
        Accepts:
        + matchlist - list of values to match against
        + timeout - seconds before function should return if match is not met

        Returns dictionary:
        + 'buffer' - list of dictionaries in format:
                [{time1: [buffer_line_1, buffer_line_2]},
                 {time2: [buffer_line_1, buffer_line_2, ...],
                 ...,
                 ]
        + 'xtime' - execution time
        + 'midx' - index of item matched in argument matchlist; -1 if no match found
        + 'mobj' - match object returned by re.search; None if no match found
        """
        if not isinstance(matchlist, list):
            matchlist = list(matchlist)

        # convert timeout to milliseconds
        timeout *= 1000

        # define list of dictionaries;
        # list insures order is perserved rather than
        # sorting down the road...
        running_buf = []
        # remember last line of buffer to append to first line of next buf
        last_line_buf = ''

        # matchidx initialized to 0
        midx = -1
        # index of timestamp we are iterating with
        tidx = 0
        timestamp = self.get_time()

        # compile regex's once to save processing
        compiled_regex = []
        for regex in matchlist:
            compiled_regex.append(re.compile(regex))

        start_time = self.get_time()
        while self.get_time() - start_time < timeout:
            buf = self.t.read_very_eager()
            if buf:
                # create list of lines associated with buffer
                buf = buf.replace('\r', '')
                buf_list = buf.split('\n')

                # first line is really cut off part from last line
                last_idx = len(buf_list) - 1
                buf_list[0] = last_line_buf + buf_list[0]
                last_line_buf = buf_list[last_idx]

                # buffer to remember
                timestamp = self.get_time()
                running_buf.append({timestamp: []})

                # send to MQTT - format {'epoch': timestamp, 'console': payload}
                payload = copy.deepcopy(buf_list)
                payload.pop()
                self.mqtt_publish({'epoch': timestamp, 'console': payload})
                # search each line in most recent buf for regex match
                # don't search last line because it is incomplete,
                # last line is appended to start of first line of next buf
                for i in range(len(buf_list)):
                    # don't append last item
                    if i < last_idx:
                        running_buf[tidx][timestamp].append(buf_list[i])
                    # iterate thru matchlist to look for matches in this line
                    for idx in range(len(compiled_regex)):
                        # compute regex
                        mobj = re.search(compiled_regex[idx], buf_list[i])
                        if mobj:
                            # don't forget to append last line we were saving
                            running_buf[tidx][timestamp].append(last_line_buf)
                            # don't forget to 'send' last line over mqtt
                            self.mqtt_publish({'epoch': timestamp, 'console': [last_line_buf]})

                            return {'buffer': running_buf,
                                    'xtime': self.get_time() - start_time,
                                    'midx': idx,
                                    'mobj': mobj}

                tidx += 1

        # if we get here, we have a TIMEOUT
        # don't forget to append last line we were saving;
        # tidx was over incremented above
        tidx -= 1
        running_buf[tidx][timestamp].append(last_line_buf)

        self.mqtt_publish({'epoch': timestamp, 'console': [last_line_buf]})

        return {'buffer': running_buf,
                'xtime': self.get_time() - start_time,
                'midx': midx,
                'mobj': None}

    def mqtt_publish(self, payload):
        """
        Push payload over defined mqtt client/thread in json format
        """
        print("Pushing on {}/{}".format(self.topic, json.dumps(payload)))
        if self.mqtt_client:
            self.mqtt_client.publish(self.topic, json.dumps(payload), self.qos)

    def close(self):
        """
        Close opened session
        """
        self.t.close()

    def get_time(self):
        """
        Returns integer time in milliseconds
        """
        return int(time.time() * 1000)

    def debug(self, msg):
        """
        Dump debug info - can be changed easily from here...
        """
        if self.debugFlag:
            print(msg)
