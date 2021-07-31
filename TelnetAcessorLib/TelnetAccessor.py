"""
Created on Mar 23, 2017

@author: smcochra

3/27/2017 - edited by smcochra
"""

#import TelnetDriver
import time
import telnetlib
import time
import datetime
import re
import paho.mqtt.client as mqtt
import copy
import json
import config.ConfigItems as server


#BROKER_ADD = 'broker.mqttdashboard.com'
BROKER_ADD = server.mqtt['mqttserver']['server']
# BROKER_ADD = '10.130.41.48'
BROKER_PORT = server.mqtt['mqttserver']['port']



class TelnetAccessor(object):
    """
    Encompasses Send, Expect, SendExpect, Logging to DB with Timestamp
    """
    matchobj = None

    def __init__(self, mqtt_id=None, qos=1, debugFlag=False, mqttClient=None):
        """
        Instantiate TelnetDriver Class
        + mqtt_id - identifier for MQTT client to launch
                  - if None, no Client will launch
        + qos - Quality of service for mqtt range int([0, 2])
        + loc - string location of test being executed. e.g. 'SAN JOSE'
        + debugFlag - enable debug messaging
        """
        self.t = TelnetDriver(mqtt_id=mqtt_id, debugFlag=debugFlag, mqttClient=mqttClient)

    def open_console(self, console):
        self.t.open(console)


    def close_console(self):
        self.t.close()

    def send(self, data):
        """
        Sends data to open console
        + data - string to push to socket
        """
        data = data.encode('ascii')
        self.t.debug('Sending: %r' % data)
        self.t.send(data)

    def getlastmatchobj(self):
        """
        Returns last RE match object
        """
        return self.matchobj

    def setmatchobj(self, matchobj):
        """
        Set RE match object for query
        """
        self.matchobj = matchobj

    def expect(self, matchlist, timeout=5):
        """
        Arguments -
        + matchlist - regex or list of regex's to match against
        + timeout - seconds before timeout occurs
        Returns tupple dictionary with following keys:
        + 'matchidx' - index of item matched from argument matchlist
        + 'matchobj' - MatchObject; see documentation re.MatchObject
        + 'matchtext' - raw string that pattern matched against
        + 'buffer' - buffer captured between start of expect call and timeout/match
        + 'bufobj' - list of dictionaries ordered with key timestamp and value list
                    of lines associated with timestamp
                    [{time1: [buffer_line_1, buffer_line_2]},
                     {time2: [buffer_line_1, buffer_line_2, ...],
                     ...,
                     ]
        + 'timeout_occured' - True or False
        + 'xtime' - execution time for expect to match

        """
        returndict = {}
        buffer = ''

        expobj = self.t.expect(matchlist, timeout)

        for dict in expobj['buffer']:
            for timestamp, line in dict.items():
                buffer += '\n'.join(line)
                buffer += '\n'

        # remove last new line that was applied in excess above
        buffer = buffer[:-1]

        timeout = True
        mtext = None
        if expobj['midx'] != -1:
            timeout = False
            # fetch entire match
            mtext = expobj['mobj'].group(0)

        self.setmatchobj(expobj['mobj'])

        returndict['matchidx'] = expobj['midx']
        # returndict['matchobj'] = expobj['mobj']
        returndict['matchtext'] = mtext
        returndict['buffer'] = buffer
        returndict['bufobj'] = expobj['buffer']
        returndict['xtime'] = expobj['xtime']
        returndict['timeout_occured'] = timeout

        return returndict

    def sendexpect(self, data, matchlist, timeout=5, debug=False):
        """
        Combined send, expect;
        """
        self.send(data )
        result = self.expect(matchlist, timeout=timeout)

        if debug:
            self.__debug_expect(result)

        return result

    def sendexpect_list(self, data_list, matchlist, timeout=5, debug=False):
        """
        accepts list of commands to execute assuming same matchlist;
        returns True after successful execution
        + data_list - list of commands to run - '\r' will be appended to each command
        + matchlist - regex or list of regex's to match against
        + timeout - seconds before timeout occurs
        + debug - print out expect return values 
        """
        returnobj = []
        for data in data_list:
            result = self.sendexpect(data + '\r', matchlist, timeout, debug)
            returnobj.append(result)

        return returnobj

    def __debug_expect(self, exp_retrn_dict):
        """
        Print out expect return values
        """
        self.t.set_debug_flag(True)
        self.t.debug('------------------------------')
        for key, value in exp_retrn_dict.iteritems():
            self.t.debug('%s: %r' % (key, value))
        self.t.debug('------------------------------')

    def print_log_with_timestamps(self, expect_obj_list):
        """
        Takes list of expect return objects and prints log
        with timestamps
        """
        lastline = ''
        buflist = []
        for result in expect_obj_list:
            buflist.append(result['bufobj'])

        for cmd_dict_list in buflist:
            # connect cmd sequence lastline w/ firstline
            cmd_dict_list[0].values()[0][0] = lastline + \
                cmd_dict_list[0].values()[0][0]
            # get lastline of cmd sequence to tie to first line of next
            # sequence
            lastline = cmd_dict_list[-1].values()[0].pop()

            for bufobj in cmd_dict_list:
                for timestamp, buf_list in bufobj.iteritems():
                    for idx in range(len(buf_list)):
                        print ('%s\t%r' % (timestamp, buf_list[idx]))

        # don't forget to print lastline that we are storing
        print('%s\t%r' % (timestamp, lastline))


def logmsg(msg):
    """
    Logs msg to TBD location
    """
    time = gettimestamp()
    print ('%s\tlogmsg: %s' % (time, msg))


def usermsg(msg):
    """
    Logs msg to TBD location
    """
    time = gettimestamp()
    print ('%s\tusermsg: %s' % (time, msg))


def gettimestamp():
    """
    Returns int of epoch in milliseconds
    """
    # return datetime.datetime.now()
    return int(time.time() * 1000)


def test(console='10.31.248.147:3009'):
    usermsg('Testing User Message!')
    logmsg('Testing log Message!')

    # prints output of all expect return values
    # to provide support for debugging
    debugFlag = False
    data_list = ['exit', 'en', 'skip', 'show version']

#     session = TelnetAccessor(debugFlag=debugFlag)
#     session.open_console(console)
#  
#     logmsg('Testing sendexpect_list...')
#  
#     results = session.sendexpect_list(
#         data_list, ['not_a_match', 'Router', 'NetIron\sCE[SR]\s2024[CF].4X'], timeout=15, debug=debugFlag)
#  
#     session.print_log_with_timestamps(results)
#  
#     session.close_console()
# 
#     """
#     Testing MQTT integration now with same series
#     """
#     print '###############################################################'
#     print '#                  STARTING A TIMEOUT TEST                         #'
#     print '###############################################################'
# 
#     session = TelnetAccessor(debugFlag=debugFlag)
#     session.open_console(console)
#  
#     logmsg('Testing sendexpect_list assuming timeouts...')
#  
#     results = session.sendexpect_list(
#         data_list, ['not_a_match', 'Router'], timeout=10, debug=debugFlag)
#  
#     session.print_log_with_timestamps(results)
#  
#     session.close_console()

    """
    Testing MQTT integration now with same series
    """
    print ('###############################################################')
    print ('#                  STARTING MQTT TEST                         #')
    print ('###############################################################')

    session = TelnetAccessor(mqtt_id='ABC123', qos=1, debugFlag=debugFlag)
    session.open_console(console)

    logmsg('Testing sendexpect_list...')

    for i in range(20):
        results = session.sendexpect_list(
            data_list, ['not_a_match', 'Router', 'NetIron\sCE[SR]\s2024[CF].4X'], timeout=15, debug=debugFlag)
        time.sleep(3)

    # session.print_log_with_timestamps(results)

    session.close_console()

    usermsg('Done!')
    logmsg('Done!')



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

    def __init__(self, mqtt_id=None, qos=0, debugFlag=False, mqttClient=None):
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

        self.mqtt_client = None
        if mqttClient:
            print("Live MQTT Client")
            self.mqtt_client = mqttClient
            self.mqtt_client.publish('{}/status'.format(self.mqtt_id), json.dumps({ 'serial': self.mqtt_id,
                                                                                  'epoch': self.get_time(),
                                                                         'status' : 'RESET'}) )

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

        self.debug("Attempting to open connection with IP: '%s' Port: '%s'" % (
            self._ip, self._port))
        self.t.open(self._ip, self._port)
        self.debug("Session opened!")
        print("MQTT: {}".format(self.mqtt_id))
        print("Session Opened")
        #self.init_mqtt(console)
        resp = self.expect(matchlist=['login:'], timeout=5)
        if resp:
            if 'mobj' in resp:
                if resp['mobj']:
                    print("Telnet Connect: {}".format(resp['mobj'][0]))
                    if 'login:' in resp['mobj'][0]:
                        portx = "port{}".format(str(self._port)[-1:])
                        print("Ports: {}".format(portx))
                        self.send("{}\n".format(portx))
                        self.send("pass\n")

    def init_mqtt(self, console):
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
        if isinstance(data, str):
            #print("Found String: {}".format(data))
            data = data.encode('ascii')

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
                if not isinstance(buf, str):
                    buf = buf.decode('ascii')

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
        if running_buf:
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
        print("Pushing MQTT: {} {}".format(self.topic, json.dumps(payload)))
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


if __name__ == "__main__":
    test()
