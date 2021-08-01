# $Id: BEXPServer.py 532 2021-06-29 16:33:45Z nasinha $


import argparse
import ast
import json
import logging
import os
import sys
import threading
import time

import cherrypy as HttpServer
import paho.mqtt.client as mqtt
from pymongo import MongoClient

from BExpress.BaudExpress import BaudExpress
from config import ConfigItems


# from MoveTable import MoveTable
# from ProcessSequence.Sequences import CommandSequence


class BEXPServer(object):
    '''
    classdocs
    '''

    staticdir = None


    def __init__(self, staticdir=None, database=None, logexport=None):
        '''
        Constructor
        '''

        self.staticdir = os.path.join(os.getcwd(), 'ui_www')
        if staticdir:
            self.staticdir = staticdir

        logging.info("Static directory for web-content: %s" % self.staticdir)

        # Intializing the upload directory
        uploaddir = os.path.join(self.staticdir, '..', 'uploads')
        if uploaddir:
            self.uploaddir = uploaddir


        #setup log export
        self.logexport = os.getcwd()
        if logexport:
            self.logexport = logexport

        # Setup Database IP
        dbip = '127.0.0.1'
        port = 27017
        if database:
            dbip = database

            ## there is a port notation embedded
            if ':' in database:
                dbip, port = database.split(':')
                port = int(port)

            self.dbloc = "{}:{}".format(dbip, port)
            self.client = MongoClient(dbip, port)

            database = self.client['baudexpress']
            self.dblog = database['logs']
            self.dbreg = database['sntable']
            self.dbseq = database['sequences']

        # MQTT mqttclient
        logging.info("MQTT logging started, {}".format(ConfigItems.mqtt['mqttserver']))
        self.mqttclient = mqtt.Client()
        self.mqttclient.on_connect = self.on_mqttconnect
        self.mqttclient.on_message = self.on_mqttmessage

        self.mqttclient.username_pw_set("apiuser", "millionchamps")
        self.mqttclient.connect(ConfigItems.mqtt['mqttserver']['server'],
                                ConfigItems.mqtt['mqttserver']['port'],
                                60)

        logging.info("MQTT Connection started")

        self.t1 = threading.Thread(target=self.runserver)
        self.t1.start()


    @HttpServer.expose
    def index(self):
        """
        Sources the index file
        :return: raw index file
        """

        return open(os.path.join(self.staticdir, "index.html"))



    @HttpServer.expose
    def oobaview(self):
        """
        Sources the index file
        :return: raw index file
        """

        return open(os.path.join(self.staticdir, "ooba.html"))




    @HttpServer.expose
    def getscanlist(self, partnumber=None):
        """
        Returns Scanlist for the partnumber

        :param partnumnber:
        :return:
        """
        robj = None
        logging.info("ScanList Query: {}".format(partnumber))
        if partnumber:
            if partnumber in CommandSequence:
                robj = CommandSequence[partnumber]['scanlist']
                logging.info("ScanList for {} is {}".format(partnumber, robj))

        return json.dumps(robj)


    @HttpServer.expose
    def getproducts(self):
        """
        Returns list of supported products
        :return:
        """

        prods = []
        products = list(self.dbseq.distinct('sku'))
        logging.info("Products: {}".format(products))
        for prod in products:
            pobj = self.dbseq.find_one({'sku': prod}, {'_id': 0})
            logging.info("SequenceObj: {}".format(pobj))
            prods.append({'product' : prod, 'scanlist' : pobj['scanlist'], 'about' : pobj['about']})

        #for key in CommandSequence.keys():
        #    dobj = {}
        #    dobj['product'] =  key
        #    dobj['scanlist'] = CommandSequence[key]['scanlist']
        #    dobj['about'] =  CommandSequence[key]['about']

        #    prods.append(dobj)






        return json.dumps(prods)


    @HttpServer.expose
    def getinspections(self):
        """
        Returns list of supported products and inspection elements
        :return:
        """


        prods = []
        products = list(self.dbseq.distinct('sku'))
        logging.info("Products: {}".format(products))
        for prod in products:
            pobj = self.dbseq.find_one({'sku': prod}, {'_id': 0})
            logging.info("SequenceObj: {}".format(pobj))
            if 'inspection' in pobj:
                prods.append({'product' : prod, 'scanlist' : pobj['scanlist'], 'about' : pobj['about']})
            else:
                logging.info("Inspection objs not defined for SKU: {}".format(prod) )


        #prods = []
        #for key in CommandSequence.keys():
        #    dobj = {}
        #    dobj['product'] =  key
        #    if 'inspection' in CommandSequence[key]:
        #        dobj['inspection'] =  CommandSequence[key]['inspection']

         #   if 'about' in CommandSequence[key]:
         #       dobj['about'] =  CommandSequence[key]['about']

         #   prods.append(dobj)

        return json.dumps(prods)



    @HttpServer.expose
    def getlogtable(self):
        """
        Get Log Table
        :return:
        """
        recds = []
        endtimelist = list(self.dblog.distinct('UnitIdentifier.enddatetime'))
        endtimelist.reverse()

        for rec in endtimelist:
            print("log: {}".format(rec))
            query = { 'UnitIdentifier.enddatetime': rec}
            statlg = self.dblog.find_one(query, {'_id': 0} )
            print(statlg)

            recds.append({'SerialNumber' : statlg['UnitIdentifier']['SerialNumber'],
                          'startdatetime' : statlg['UnitIdentifier']['startdatetime'],
                          'status' : statlg['status']})

            if len(recds) > 25:
                break

        print("LogTable:\n{}".format(recds))
        return json.dumps(recds)


    @HttpServer.expose
    def getlogsforserial(self, serialnum=None):
        """
        Get Log Table
        :return:
        """
        recds = []
        if serialnum:
            endtimelist = self.dblog.distinct('UnitIdentifier')
            for rec in endtimelist:
                if rec['SerialNumber'] == serialnum:
                    if 'enddatetime' in rec:
                        #print("Rec: {}".format(rec))
                        query = {'UnitIdentifier.SerialNumber': rec['SerialNumber'],
                                 'UnitIdentifier.enddatetime': rec['enddatetime']}
                        statlg = self.dblog.find_one(query, {'_id': 0, 'status' : 1})
                        rec['status'] = statlg['status']
                        recds.append(rec)

        return json.dumps(recds)


    @HttpServer.expose
    def gettestlog(self, serialnum=None, startdatetime=None):
        """
        Get test Log
        :param serialnum:
        :param startdatetime:
        :return:
        """
        tlog = []
        query = { 'UnitIdentifier.SerialNumber' : serialnum, 'UnitIdentifier.startdatetime' : startdatetime}
        tlogs = self.dblog.find(query, {'_id' : 0, 'cmddef' : 1,'console' : 1 })

        for lgel in tlogs:
            if 'cmdef' in lgel:
                print("Cmd: {}".format(lgel['cmddef']['cmd']) )
            if 'console' in lgel:
                print("Log: {}".format(lgel['console']))
                tlog.append(lgel['console'].replace('\n', '<BR/>'))

        return json.dumps(tlog)


    @HttpServer.expose
    def getbackenddata(self):
        """
        Returns backenddata model
        :return:
        """

        jsondata = {}
        jsondata['products'] = json.loads(self.getproducts())
        jsondata['inspections'] = json.loads(self.getinspections())
        #jsondata['movetable'] = json.loads(self.getmovetable())
        jsondata['logtable'] = json.loads(self.getlogtable())

        return json.dumps(jsondata)

    @HttpServer.expose
    def baudoperation(self, console=None, serialnumber=None, partnumber=None, scandata=None):
        """
        Perform BExpress Operation
        :return:
        """
        logging.info("BaudExp request for PN:{}/ SN:{} on Console:{}".format(partnumber, serialnumber, console) )
        logging.info("BaudExp Scandata:  {}".format(scandata) )
        consolex = None
        serialNumberScan = None
        if scandata:
            for scanitem in json.loads(scandata):
                #print("ScanItem: {}".format(scanitem))
                for scanName, scanObj in scanitem.items():
                    print("\tScanLoad: {}/{}".format(scanName, scanObj))
                    if  'telnet' in scanObj:
                        if scanObj['telnet']:
                            consolex = scanObj['value']

                    if 'SerialNumber' in scanObj:
                        if scanObj['SerialNumber']:
                            serialNumberScan = scanObj['value']

        self.operationRegister(console=consolex, serialnum=serialNumberScan)

        baudopTherad = threading.Thread(target=self.baudexpThread(serialnumber=serialNumberScan,
                                                                  partnumber=partnumber, console=consolex,
                                                                  scandata=scandata))

        # Register stattus on BaudExp Register

        #baudopTherad.start()
        robj = {'mqttid' : "{}/status".format(serialNumberScan), 'starttime' : self.epoch() ,  'status' : "TERMINATED"}
        return (json.dumps(robj))


    def operationRegister(self, console=None, serialnum=None):
        """

        :return:
        """
        query = {'console' : console, 'serialnum' : serialnum}
        sntbl = list(self.dbreg.find(query, {'_id' : 0} ))

        if len(sntbl):
            print(sntbl)
            for sn in sntbl:
                print("SN: {}/Tbl: {}".format(serialnum, console))
        else:
            print("{}/{} was not found".format(console, serialnum))

        robj = False

        return robj



    def epoch(self):
        """
        Returns the current EPOCH time
        """
        millis = int(round(time.time() * 1000))
        return millis

    def baudexpThread(self, mqttid=None, console=None, partnumber = None, serialnumber=None, scandata=None):
        """
        BaudThread
        :param mqttid:
        :param console:
        :param serialnumber:
        :return:
        """
        boper = BaudExpress(mqttclient=self.mqttclient, mongodb=self.dbloc, logexport=self.logexport)
        sysmodel = boper.baudoperation(mqttid=serialnumber, console=console,
                                       serialnumber=serialnumber,
                                       partnumber=partnumber,
                                       scandata=scandata)





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

            # self.mqttclient.publish(topic="trex/rsp",
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
        if self.t1.isAlive():
            logging.info("Thread[{}] is alive. Shutting down".format(self.t1.name))
            self.mqttclient.disconnect()
            logging.info("Disconnecting MQTT from client")
            self.t1.join()
            time.sleep(2)

        if self.t1.isAlive():
            logging.info("Thread[{}] is still alive.".format(self.t1.name))

        logging.info("Performing a clean shutdown")
        time.sleep(2)





# main code section
if __name__ == '__main__':
    port = 9009
    www = os.path.join(os.getcwd(), 'ui_www')
    ipaddr = '0.0.0.0'
    dbip = 'data.sinhamobility.com:28018'

    logpath = os.path.join(os.getcwd(), 'log', 'baudexpress-server.log')
    logdir = os.path.dirname(logpath)
    os.makedirs(logdir, exist_ok=True)

    cascPath = os.path.abspath(os.getcwd())

    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--port", required=False, default=9005,
                    help="Port number to start HTTPServer." )

    ap.add_argument("-i", "--ipaddress", required=False, default='127.0.0.1',
                help="IP Address to start HTTPServer")

    ap.add_argument("-d", "--dbaddress", required=False, default=dbip,
                    help="Database Address to start HTTPServer")

    ap.add_argument("-s", "--static", required=False, default=www,
                help="Static directory where WWW files are present")

    ap.add_argument("-c", "--cascpath", required=False, default=cascPath,
                    help="Directory where cascase files are found, defaults to %s" % (cascPath))

    ap.add_argument("-f", "--logfile", required=False, default=logpath,
                    help="Directory where application logs shall be stored, defaults to %s" % (logpath) )

    ap.add_argument("-o", "--sessionlogs", required=False, default=os.getcwd(),
                    help="Directory where application logs are stored,   %s" % (logpath) )

    # Parse Arguments
    logexport = os.getcwd()

    args = vars(ap.parse_args())
    if args['port']:
        portnum = int(args["port"])

    if args['ipaddress']:
        ipadd = args["ipaddress"]

    if args['dbaddress']:
        dbip= args["dbaddress"]

    if args['static']:
        staticwww = os.path.abspath(args['static'])

    if args['logfile']:
        logpath = os.path.abspath(args['logfile'])
    else:
        if not os.path.exists(logdir):
            print("Log directory does not exist, creating %s" % (logdir))
            os.makedirs(logdir)

    if args['cascpath']:
        cascPath = args['cascpath']


    if args['sessionlogs']:
        logexport = args['sessionlogs']


    logging.basicConfig(filename=logpath, level=logging.DEBUG, format='%(asctime)s %(message)s')
    handler = logging.StreamHandler(sys.stdout)
    logging.getLogger().addHandler(handler)

    HttpServer.config.update({'server.socket_host': ipadd,
                           'server.socket_port': portnum,
                           'server.socket_timeout': 60,
                           'server.thread_pool': 8,
                           'server.max_request_body_size': 0
                           })

    logging.info("Static dir: %s " % (staticwww))
    conf = { '/': {
            'tools.sessions.on': True,
            'tools.staticdir.on': True,
            'tools.staticdir.dir': staticwww}
            }

    HttpServer.quickstart(BEXPServer(staticdir=staticwww,
                                     database=dbip, logexport=logexport),
                            '/', conf)


