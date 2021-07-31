from TelnetAcessorLib.TelnetAccessor import TelnetAccessor
import ast, threading
import paho.mqtt.client as mqtt
from pymongo import MongoClient
from BExpress.AutomationSequence import ParseEngine
import json, re

class SystemModel(object):
    """
    Defines place Holder for Systen defintions
    """

    def __init__(self):
        return False




class SLXOS(object):
    """
    SLX OS Object which defines the sequence
    """

    system_model = {
                    'chassis' : {'PartNumber' : None, 'SerialNumber' : None} ,
                    'version' : None,
                    'MAC' : None,
                    'Ports' : None,
                    'PowerSupply' : None,
                    'Fans' : None
                    }

    _logincmds = [
            {'cmd': "\n", 'prompt': ["SLX.*login"], 'timeout': 10},
            {'cmd': "admin\n", 'prompt': ["Password:"], 'timeout': 10},
            {'cmd': "password\n", 'prompt': ["SLX.*#"], 'timeout': 10},
            {'cmd': "term len 0\n", 'prompt': ["SLX.*#"], 'timeout': 10}
            ]

    _chassis = [
                {'cmd': "term len 0\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                {'cmd': "show chassis\n", 'prompt': ["SLX.*#"], 'timeout': 10}
            ]




    def __init__(self, tsession, logger, mqttclient, mqttid):

        """
        Intialzes class with a terminal server session, a logger object
        and a mqttclient
        :rtype: object
        :param tsession:
        :param logger:
        :param mqttclient:
        :param mqttid:
        """

        self.tsession = tsession
        self.logger = logger
        self.mqttclient = mqttclient
        self.mqttid = mqttid

        self.parseengine = ParseEngine(key='version', regex='Firmware.name:(.*)')
        self.parseengine.addparser(key='chassis_pn', regex='Factory.Part.Num:(.*)')
        self.parseengine.addparser(key='chassis_sn', regex='Factory.Serial.Num:(.*)')
        self.parseengine.addparser(key='chassis_type', regex='Chassis.Name:(.*)')
        self.parseengine.addparser(key='psu_id', regex='ID:(.*)')
        self.parseengine.addparser(key='psu_pn', regex='Part.Num:(.*)')
        self.parseengine.addparser(key='psu_sn', regex='Serial.Num:(.*)')


        return None




    def loginHandler(self):
        """
        Handles Login into the unit
        :return:
        """
        for cmobj in self._logincmds:
            print("Sending command: {} ".format(cmobj))
            resp = self.tsession.sendexpect(data=cmobj['cmd'],
                                       matchlist=cmobj['prompt'],
                                       timeout=cmobj['timeout'])
            print("Resp: {}".format(resp['buffer']))
            if resp['timeout_occured']:
                print("Timeout Occured..")
                statusx = {'status': 'FAILED', 'timeout': True}
                if 'SLX#' in resp['buffer']:
                    print("Found prompt")
                    break
            else:
                statusx = {'status': 'PASSED', 'timeout' : False}

            self.mqttclient.publish('{}/status'.format(self.mqttid), json.dumps(statusx))
        # self.mqttclient.publish(mqttid, json.dumps(resp['buffer']))


    def reboot(self, writeerase=False):
        """
        Reboots SLX box
        :return:
        """
        cmdobj_arr = []
        if writeerase:
            cmdobj_arr.append({'cmd': 'write erase\n', 'prompt': ['SLX#'], 'timeout': 5})

        cmdobj_arr.append({'cmd': 'reload\n', 'prompt': ['reload.*n.:'], 'timeout': 2})
        cmdobj_arr.append({'cmd': 'y\n', 'prompt': ['SLX:.*login'], 'timeout': 120})

        for cmdobj in cmdobj_arr:
            resp = self.tsession.sendexpect(data=cmdobj['cmd'],
                                        matchlist=cmdobj['prompt'],
                                        timeout=cmdobj['timeout'])

            print("Resp: {}".format(resp['buffer']))
            if resp['timeout_occured']:
                statusx = {'status': 'FAILED', 'timeout': True}
            else:
                statusx = {'status': 'PASSED', 'timeout': False}


    def extarctChassis(self):
        """
        Extract Chassis info and check if config matches
        :return:
        """
        cmdobj = {'cmd' : 'show chassis\n', 'prompt' : ['SLX#'], 'timeout' : 10}
        print("Sending command: {} ".format(cmdobj))
        resp = self.tsession.sendexpect(data=cmdobj['cmd'],
                                        matchlist=cmdobj['prompt'],
                                        timeout=cmdobj['timeout'])
        print("Resp: {}".format(resp['buffer']))
        if resp['timeout_occured']:
            statusx = {'status': 'FAILED', 'timeout': True}
        else:
            resp = self.parseengine.extract(resp['buffer'], keys=['chassis_pn', 'chassis_sn', 'chassis_type',
                                                                  'psu_id', 'psu_sn', 'psu_pn'] )
            print(resp)
            for ch_key, ch_item in resp.items():
                if ch_item:
                    ch_item = ch_item.strip()
                    print("\t== {} : {}".format(ch_key, ch_item))

            statusx = {'status': 'PASSED', 'timeout': False}

        self.mqttclient.publish('{}/status'.format(self.mqttid), json.dumps(statusx))

    def extarctVersion(self):
        """
        Extracts Version info
        :return:
        """
        cmdobj = {'cmd' : 'show version\n', 'prompt' : ['SLX#'], 'timeout' : 10}
        print("Sending command: {} ".format(cmdobj))
        resp = self.tsession.sendexpect(data=cmdobj['cmd'],
                                        matchlist=cmdobj['prompt'],
                                        timeout=cmdobj['timeout'])
        print("Resp: {}".format(resp['buffer']))
        if resp['timeout_occured']:
            statusx = {'status': 'FAILED', 'timeout': True}
        else:
            statusx = {'status': 'PASSED', 'timeout': False}

        self.mqttclient.publish('{}/status'.format(self.mqttid), json.dumps(statusx))


    def extarctPSU(self):
        """
        Extract  PSU info and check if config matches
        :return:
        """
        cmdobj = {'cmd' : 'show env power \n', 'prompt' : ['SLX#'], 'timeout' : 10}
        print("Sending command: {} ".format(cmdobj))
        resp = self.tsession.sendexpect(data=cmdobj['cmd'],
                                        matchlist=cmdobj['prompt'],
                                        timeout=cmdobj['timeout'])
        print("Resp: {}".format(resp['buffer']))
        if resp['timeout_occured']:
            statusx = {'status': 'FAILED', 'timeout': True}
        else:
            statusx = {'status': 'PASSED', 'timeout': False}

        self.mqttclient.publish('{}/status'.format(self.mqttid), json.dumps(statusx))



    def extarctFAN(self):
        """
        Extract  PSU info and check if config matches
        :return:
        """
        cmdobj = {'cmd' : 'show env fan \n', 'prompt' : ['SLX#'], 'timeout' : 10}
        print("Sending command: {} ".format(cmdobj))
        resp = self.tsession.sendexpect(data=cmdobj['cmd'],
                                        matchlist=cmdobj['prompt'],
                                        timeout=cmdobj['timeout'])
        print("Resp: {}".format(resp['buffer']))
        if resp['timeout_occured']:
            statusx = {'status': 'FAILED', 'timeout': True}
        else:
            statusx = {'status': 'PASSED', 'timeout': False}

        self.mqttclient.publish('{}/status'.format(self.mqttid), json.dumps(statusx))



class SLX9150(object):
    """
    BuadExpress: Baudexpress takes in SN# and looks up actions
    """

    def __init__(self, mqttclient):
        """

        :param mqttclient:
        """
        print("Test")