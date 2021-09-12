# $Id: BaudExpressJson.py 525 2021-06-18 16:34:25Z nasinha $
import ast
import datetime
import json
import logging
import os
import socket
import sys
import threading
import time

import paho.mqtt.client as mqtt
from ProcessSequence.SLXBoxes import SLXOS
from pymongo import MongoClient

from MoveTable import MoveTable
from ProcessSequence.AsBuildFeed import AsBuiltFeed
from ProcessSequence.Sequences import CommandSequence
from TelnetAcessorLib.TelnetAccessor import TelnetAccessor
from config import ConfigItems


# noinspection SpellCheckingInspection


class BaudExpress(object):
    """
    BuadExpress: Baudexpress takes in SN# and looks up actions
    """

    def __init__(self, mqttclient=None, mongodb=None, logexport=None):
        '''
        Constructor for CExpress Core
        '''
        logging.info("CExpress Core")
        dbase = '127.0.0.1'
        if mongodb:
            # Connect to database
            dbase = mongodb
            logging.info("Connecting to Mongo Instance at %s" % (dbase))
            self.client = MongoClient(dbase, 27017)
            database = self.client['baudexpress']
            self.dbcol = database['logs']


        if mqttclient:
            self.mqttclient = mqttclient
        else:
            # MQTT mqttclient
            logging.info("MQTT logging started")
            self.mqttclient = mqtt.Client()
            self.mqttclient.on_connect = self.on_mqttconnect
            self.mqttclient.on_message = self.on_mqttmessage

            self.mqttclient.connect(ConfigItems.mqtt['mqttserver']['server'],
                                    ConfigItems.mqtt['mqttserver']['port'],
                                    60)
            logging.info("MQTT Connection started")

            h_name = socket.gethostname()
            self.ipaddress = socket.gethostbyname(h_name)
            logging.info("Host IP is {}".format(self.ipaddress))
            print("HOSTIP: {}".format(self.ipaddress))
            self.t1 = threading.Thread(target=self.runserver)
            self.t1.start()

        self.loglocation = os.path.join(os.getcwd())
        if logexport:
            self.loglocation = logexport




    def on_mqttconnect(self, client, userdata, flags, rc):
        """
        MQTT Connect
        """
        logging.info("MQTT conenction established")


    def on_mqttmessage(self, client, userdata, msg):
        """
        MSG
        """
        logging.info("Topic: %s, Rxd: %s" % (msg.topic, msg.payload))

        t2 = None
        # Command Switcher
        if 'bdexp/cmd' in msg.topic:
            print("Cmd: %s" % (msg.payload))
            print(type(msg.payload))
            pload = msg.payload
            cmdobj = ast.literal_eval(msg.payload.decode("utf-8", "ignore"))
            print(type(pload))
            print(type(cmdobj))
            print("CmdObj: %s" % (cmdobj))
            for key, value in cmdobj.items():
                print("CommandObj: %s, %s" % (key, value))

            # response

            #rsp = {'progress': True, 'Done': False}
            #self.mqttclient.publish(topic="trex/rsp",
            #                        payload=json.dumps(rsp))

    def runserver(self):
        """
        Run MQTT Loop in a thread
        """
        # MQTT Loop
        self.mqttclient.subscribe(topic="bexp/cmd")
        logging.info("Started MQTT subscription")
        self.mqttclient.loop(timeout=20, max_packets=10)
        self.mqttclient.loop_forever()

    def shutdown(self):
        """

        :return:
        """
        if self.t1.is_alive():
            logging.info("Thread[{}] is alive. Shutting down".format(self.t1.name))
            self.mqttclient.disconnect()
            logging.info("Disconnecting MQTT from client")
            self.t1.join()
            time.sleep(2)

            if self.t1.is_alive():
                logging.info("Thread[{}] is still alive.".format(self.t1.name))


            logging.info("Performing a clean shutdown")
            time.sleep(2)




    def baudoperation2(self, mqttid, console, serialnumber=None):
        """

        :return:
        """
        self.movetable = MoveTable()
        movedetails = self.movetable.getMoveEnteries(serialNum=serialnumber)
        omove = self.movetable.getOpenMoves(serialNum=serialnumber)
        print("MovepartNum: {}".format(omove))


        tsession = TelnetAccessor(mqtt_id=mqttid, debugFlag=True,
                                  mqttClient=self.mqttclient)
        tsession.open_console(console)
        slxos = SLXOS(tsession=tsession, mqttid=mqttid, mqttclient=self.mqttclient, logger=logging)
        slxos.loginHandler()
        slxos.extarctChassis()
        slxos.extarctVersion()
        slxos.extarctPSU()
        slxos.extarctFAN()

    def getDateTime(self):
        """
        Get TimeStamp
        """
        now = datetime.datetime.now()

        dt = {"date": "%s-%02d-%02d" % (now.year, now.month, now.day),
              "time": "%02d-%02d-%02d" % (now.hour, now.minute, now.second)}

        return dt

    def epoch(self):
        """
        Returns the current EPOCH time
        """
        millis = int(round(time.time() * 1000))
        return millis


    def initLogging(self, serialnumber=None, tstamp=None ):
        """
        Initialize Logging
        :return:
        """

        logdir = os.path.join(self.loglocation, 'sessionlogs')

        os.makedirs(logdir, exist_ok=True)
        print("=== Log Path: {}".format(logdir) )
        self.logpath = os.path.join(logdir, '{}_{}.log'.format(serialnumber, tstamp) )
        self.flog = open(self.logpath, 'w')
        versionarr = ConfigItems.svnrevid.split('Id:')[1]
        self.scriptversion = versionarr.strip().split(" ")
        self.logappend("BaudExpress Rev-{}, Last updated {}".format(self.scriptversion[1], self.scriptversion[2]))


    def logappend(self, msg=None, mtype=None):
        """
        Append log
        :param msg:
        :return:
        """
        tstamp = datetime.datetime.now().time()
        mstype = 'INFO'
        if mtype:
            mstype = mtype

        self.flog.write("[{}, {}] : {}\n".format(mstype, tstamp, msg))

    def logclose(self, status):
        """

        :return:
        """
        print("Status: {}".format(status))
        statusfl = status['status']
        self.flog.close()
        nfname = "{}".format(self.flog.name)
        nfname = nfname.replace('.log', '-{}.log'.format(statusfl))
        logging.info("Renaming log file to {}".format(nfname))
        os.rename(self.flog.name, nfname)




    def baudoperation(self, mqttid=None, console=None, partnumber = None,serialnumber=None, scandata=None):
        """
        Baudoperation providing a PN# and SN#
        :param mqttid:
        :param console:
        :param serialnumber:
        :param scandata:
        :return:
        """
        self.starttime = self.getDateTime()
        startdt = '{}_{}'.format(self.starttime['date'], self.starttime['time'])

        self.initLogging(serialnumber=serialnumber, tstamp=startdt)
        self.logappend(msg="Starting BaudOperation for {}/{}/{}".format(serialnumber, partnumber, console))
        #self.movetable = MoveTable()
        #movedetails = self.movetable.getMoveEnteries(serialNum=serialnumber)
        #omove = self.movetable.getOpenMoves(serialNum=serialnumber)
        #print("MovepartNum: {} / {}".format(omove, movedetails))
        partnum = 'SLX9150-48XT-6C-AC-F'
        if partnumber:
            partnum = partnumber


        uutid = {'SerialNumber' : serialnumber, 'PartNumber': partnum,
                 'startdatetime': startdt, 'startepoch': self.epoch()}


        tsession = TelnetAccessor(mqtt_id=mqttid, debugFlag=True,
                                  mqttClient=self.mqttclient)

        self.logappend(msg="Trying to establish connection with telnet console {}".format(console))
        tsession.open_console(console)
        self.logappend(msg="Successfully established connection with telnet console {}".format(console))
        matchlist = ["SLX.*#"]



        sysmodel = {}

        scanlist = self.generateScanList(scandata=scandata)
        print("Scanned Data: {}".format(scandata))
        logging.info("Scanned Data: {}".format(json.dumps(scanlist, indent=2)))
        self.logappend(msg="Scanned Info: {}".format(json.dumps(scanlist, indent=2)))

        if partnum in CommandSequence:
            cmdefs =CommandSequence[partnum]['commandset']
            parseobj = CommandSequence[partnum]['parseobj']
            asbfdef = CommandSequence[partnum]['AsBuiltFeedMap']

            for el in parseobj.getkeys():
                sysmodel[el] = None

            buff = ''
            for cmobj in cmdefs:
                logging.info("Sending command: {} ".format(cmobj))
                self.logappend(msg='{}'.format(cmobj['cmd']), mtype='CMD')
                resp = tsession.sendexpect(data=cmobj['cmd'],
                                           matchlist=cmobj['prompt'],
                                           timeout=cmobj['timeout'])
                buff += resp['buffer']
                print("Resp: {}".format(resp['buffer']))
                dbobj = {'UnitIdentifier' : uutid, 'console' : resp['buffer'] ,
                         'cmddef' : cmobj, 'timeout' :  resp['timeout_occured']}

                if (resp['timeout_occured']):
                   self.logappend(msg='TIMEOUT {}'.format(cmobj['timeout']), mtype='RSP')

                self.logappend(msg='{}'.format(resp['buffer']), mtype='RSP')

                if self.dbcol:
                    self.dbcol.insert(dbobj)

            logging.info("Clossing session: {}".format(console))
            tsession.close_console()

            expkeys = parseobj.get_expect_keys()
            logging.info("Expect Dict: {}\n===".format(expkeys))

            val_stat = {'serial': serialnumber, 'status': 'FAILED', 'msg': None}
            for pkey in parseobj.getkeys():
                poutx = parseobj.extract(buffstring=buff, keys=[pkey] )
                if poutx[pkey]:
                    valx = poutx[pkey].strip()
                    sysmodel[pkey] = valx


            dbobj = {'UnitIdenfitier': uutid, 'systemmodel' : sysmodel, 'scandata' : json.loads(scandata)}
            self.dbcol.insert(dbobj)

            self.logappend(msg="====\n\n\n")
            msgx = None
            fail = False
            for pkey, valx in  sysmodel.items():
                evalx = None
                print("SystemModel {} : {}".format(pkey, valx))
                if pkey in expkeys:
                    evalx = expkeys[pkey]
                    logging.info("Checking Expected Values {} : {}/ {}".format(pkey, valx, evalx))
                    self.logappend(msg="Checking Expected Values {} : {}/ {}".format(pkey, valx, evalx))
                    val_stat = {'serial': serialnumber, 'status': 'FAILED', 'msg': None}
                    #valx = sysmodel[pkey]

                    expName = pkey
                    expVal  = expkeys[pkey]

                    if isinstance(evalx, list):
                       logging.info("Expected value is a list")
                       if valx in expVal:
                            val_stat['status'] = "PASSED"
                            logging.info("Expected value matched list")
                    else:
                        if evalx.startswith('scan'):
                            scankey = evalx.split('.')[1]
                            scanval = scanlist[scankey]
                            print("Scankeys : {}/{}".format(scankey, scanlist[scankey]) )
                            expVal = scanlist[scankey]

                        if expVal == valx:
                            val_stat['status'] = "PASSED"
                        elif valx in expVal:
                            val_stat['status'] = "PASSED"


                    msgx = "{}: Expected {}/Found {}".format(expName, expVal,
                                                             valx)
                    val_stat['msg'] = msgx

                    self.endtime = self.getDateTime()
                    enddt = '{}_{}'.format(self.endtime['date'], self.endtime['time'])
                    self.mqttclient.publish('{}/status'.format(mqttid), json.dumps(val_stat))
                    self.logappend(msg="{} {} ".format(val_stat['status'], msgx))

                    uutid['enddatetime'] = enddt
                    uutid['endepoch']  = self.epoch()

                    dbobj = {'UnitIdentifier': uutid, 'systemmodel': sysmodel,
                             'scandata': json.loads(scandata),
                             'mqttid' : mqttid, 'status': val_stat}

                    if 'FAILED' in val_stat['status']:
                        logging.info("Halting execution")
                        self.logappend(msg="Terminating execution")
                        break

                    self.dbcol.insert(dbobj)
            statusx = {'status': 'PASSED'}
            #self.mqttclient.publish('{}/status'.format(mqttid), json.dumps(statusx))
            # self.mqttclient.publish(mqttid, json.dumps(resp['buffer']))

            self.logappend(msg="Writing ASBF file")
            asbf = AsBuiltFeed(outputloc=os.path.join(self.loglocation, 'asbf'))
            asbf.generateTag(systemModel=sysmodel, scandata=scanlist,
                             asbfdefs=asbfdef )
            asbf.writeXML()


            self.logappend(msg="Completed, exiting from threads")
            self.logclose(val_stat)
            self.opsstatusfile(status=val_stat, scanlist=scanlist, systemmodel=sysmodel)

        else:
            statusx = {'status': 'NOTFOUND', 'msg': 'ProcessSequence for {} was not found'.format(partnum)}
            logging.info("ProcessSequence for {} not found".format(partnum))
            self.mqttclient.publish('{}/status'.format(mqttid), json.dumps(statusx))


        #close database at end
        logging.info("Starting, shutting down MQTT connection")
        self.client.close()
        logging.info("Finsished, Shutting down MQTT connection")
        logging.shutdown()

        return sysmodel

    def opsstatusfile(self, status=None, scanlist=None, systemmodel=None):
        """

        :param status:
        :return:
        """
        logdir = os.path.join(self.loglocation, 'status')
        os.makedirs(logdir, exist_ok=True)
        print("=== Status File: {} === ".format(logdir))
        statuspath = os.path.join(logdir, '{}_{}_{}_{}.log'.format(status['serial'], self.starttime['date'],
                                                                self.starttime['time'],
                                                                status['status']))

        h_name = socket.gethostname()
        self.ipaddr = socket.gethostbyname(h_name)
        print("HOSTIP: {}".format(self.ipaddr))
        statfile = open(statuspath,  'w')
        statfile.write("{}\n".format(os.path.basename(statuspath))) #Log file
        statfile.write("{}\n".format(statuspath)) #Log file with full-path
        statfile.write("{}\n".format("Product Conversion")) #Conversion
        statfile.write("{}/{}\n".format(systemmodel['chassis_pn'], systemmodel['chassis_type']))  #ProductName
        statfile.write("TestStationIP: {}, ConsoleIP: {}\n".format(self.ipaddr, scanlist['iconsole']))  #TestStation
        statfile.write("{}\n".format("Tester"))  #Tester
        statfile.write("{}\n".format("NA"))  #New Product conversion
        statfile.write("{}\n".format(systemmodel['chassis_pn']))  #New Product PN
        statfile.write("{}\n".format(status['status']))  #Product Check Pass/Fail
        statfile.write("{}\n".format(status['serial']))  #Product Serial
        statfile.write("{}\n".format(status['status']))  #Product Serial Check Pass/Fail
        statfile.write("{}\n".format(systemmodel['mac']))  #MAC
        statfile.write("{}\n".format(status['status']))  #MAC
        statfile.write("{}\n".format("Revision"))  #Revision
        statfile.write("{}\n".format("NA"))  #DVA
        statfile.write("{}\n".format(self.scriptversion))  #Test Script Revision
        statfile.write("{}\n".format("NA"))  #Aspect Start Menu Rev
        statfile.write("{}\n".format("NA"))  #Customer
        statfile.write("{}\n".format("NA"))  #Program Comments
        statfile.write("{}\n".format(systemmodel['swversion']))  #Primary Firmware
        statfile.write("{}\n".format("NA"))  #Secondary Firmware
        statfile.write("{}\n".format("NA"))  #Config File
        statfile.write("{}\n".format(status['status']))  #Status Overall
        statfile.write("{}_{}\n".format(self.starttime['date'], self.starttime['time']))  #Time Started
        statfile.write("{}_{}\n".format(self.endtime['date'], self.endtime['time']))  #Time Started
        statfile.write("{}\n".format("NA"))  #Schneider FW
        statfile.write("{}\n".format("NA"))  #Schneider REV
        statfile.write("{}\n".format("NA"))  #Schneider PN
        statfile.write("{}\n".format("NA"))  #Bundler Serial#

        statfile.close()







    
    def generateScanList(self, scandata=None):
        """

        :return:
        """
        scanlist = None
        if scandata:
            scanlist = {}
            scanlistobj = json.loads(scandata)
            print("ScanData[Bexp]: {}".format(scanlistobj))
            for scanlistx in scanlistobj:
                # print("ScanList: {}".format(scanlistx))
                for skey, scanobj in scanlistx.items():
                    # print('Scanned: {}, {}'.format(skey, scanobj))
                    scanlist[scanobj['id']] = scanobj['value']


        return scanlist

# main code section
if __name__ == '__main__':

    logpath = os.path.join(os.getcwd(), 'log', 'baudexpress.log')
    logdir = os.path.dirname(logpath)
    if not os.path.exists(logdir):
        print("Log directory does not exist, creating %s" % (logdir))
        os.makedirs(logdir)

    logging.basicConfig(filename=logpath, level=logging.DEBUG, format='%(asctime)s %(message)s')
    handler = logging.StreamHandler(sys.stdout)
    logging.getLogger().addHandler(handler)

    bcode = BaudExpress(mongodb='10.24.114.242')
    scandata = {

            }
    #bcode.baudoperation(serialnumber='1908Q-20179', mqttid='console1', console='10.31.221.215:3010')
    bcode.baudoperation(serialnumber='1908Q-20179', mqttid='console1', console='134.141.248.18:5008')
    #bcode.baudoperation(serialnumber='1938Q-20011', mqttid='1938Q-20011', console='10.31.221.216:3002')




    bcode.shutdown()
