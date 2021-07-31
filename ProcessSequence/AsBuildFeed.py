
import xml.etree.ElementTree as ET
import csv, base64, socket
import os,sys,  re, time, datetime
from dateutil import parser
import gc

import xml.etree.ElementTree as ET
from cgi import log
import base64, zlib, gzip
import logging, json
from pymongo import MongoClient
from datetime import date


class AsBuiltFeed(object):
    '''
    classdocs
    '''

    def __init__(self, outputloc=None):
        """

        :param outputloc:
        """
        self.outputloc = os.path.join(os.getcwd(), 'asbf')
        if outputloc:
            self.outputloc = outputloc

        if not (os.path.exists(self.outputloc)):
            os.makedirs(self.outputloc)




    def epoch(self):
        """
        Returns the current EPOCH time
        """
        millis = int(round(time.time() * 1000))
        return millis


    def getDateTime(self):
        """
        Get TimeStamp
        """
        now = datetime.datetime.now()

        dt = {"date": "%s-%02d-%02d" % (now.year, now.month, now.day),
              "time": "%02d-%02d-%02d" % (now.hour, now.minute, now.second)}

        return dt


    def generateTag(self, skupn=None, systemModel=None, scandata=None, asbfdefs=None):
        """

        :return:
        """
        logging.info("Generating XBTL tag")
        logging.info("ASBF JSON: {}".format(json.dumps(asbfdefs, indent=2)))
        self.asbf = ET.Element("as_built_feed")
        #20200626120622_1948B-90419_LM_brcd-admin_sra-mfglogs-test
        self.tstamp = '{}-{}'.format(self.getDateTime()['date'],
                                                        self.getDateTime()['time'])

        sysn =  systemModel[asbfdefs['top_sn']]

        self.fname = '{}-{}.xml'.format(systemModel[asbfdefs['top_sn']], self.tstamp)

        self.asbf.set('version', '1.1')


        uut = ET.SubElement(self.asbf, 'uut')
        uut.set('idx', '1')
        uut.set('source', 'bexp-asbfexporter')

        scanlist = scandata
        print("ScanList: {}".format(scanlist))

        for key, val in asbfdefs.items():
            print("Key: {} , Value: {}".format(key, val))

        uutsn = systemModel[asbfdefs['top_sn']]
        topsn = ET.SubElement(uut, 'top_sn')
        topsn.text = systemModel[asbfdefs['top_sn']]
        basepnarry  = systemModel[asbfdefs['top_pn']].split('-')
        basepn = "{}-{}".format(basepnarry[0], basepnarry[1])
        revid = basepnarry[2]
        logging.info("Top PN: {}, {}".format(basepn, revid))

        toppn = ET.SubElement(uut, 'top_pn')
        toppn.text = skupn
        toppn.set('rev', revid)

        msgid = '{}_{}_{}-bexp-asbexporter'.format(self.tstamp.replace('-', ''),
                                                   systemModel[asbfdefs['top_sn']], socket.gethostname() )
        self.asbf.set("msgid", msgid)

        dt = ET.SubElement(uut, 'date_time')
        dt.set('time_zone', 'UTC+7')
        dt.text = '{}-{}'.format(self.getDateTime()['date'].replace("-", ''),
                                 self.getDateTime()['time'].replace('-', ''))
        env = ET.SubElement(uut, 'environment')
        env.text = 'prod'

        ver = ET.SubElement(uut, 'swversion')
        ver.text = systemModel[asbfdefs['swversion']]

        sregex = re.compile('(.-.)')
        sregexpmatch = sregex.search(uutsn)
        if sregexpmatch:
            scode = ET.SubElement(uut, 'site_code')
            scode.text = sregexpmatch.group(0)

        comps = ET.SubElement(uut, 'components')

        #Create the Base Unit
        compx = ET.SubElement(comps, 'component')
        compx.set('idx', "1")
        compsn = ET.SubElement(compx, 'component_sn')
        compsn.text = uutsn
        comppn = ET.SubElement(compx, 'component_pn')
        comppn.text = basepn

        parentpn = ET.SubElement(compx, 'parent_pn')
        parentpn.text = skupn

        parentsn = ET.SubElement(compx, 'parent_sn')
        parentsn.text = systemModel[asbfdefs['top_sn']]



        idx = 1
        print("ScanData: {}".format(scanlist))
        for comp in asbfdefs['components']:
            idx += 1
            print('Comp[{}]: {}'.format(idx, comp))
            compx = ET.SubElement(comps,'component')
            compx.set('idx', "{}".format(idx))
            compsn = ET.SubElement(compx, 'component_sn')
            print("CompSN: {}".format(comp['component_sn']) )
            compsn.text = eval(comp['component_sn'])

            comppn = ET.SubElement(compx, 'component_pn')
            comppn.text = eval(comp['component_pn'])


            parentpn = ET.SubElement(compx, 'parent_pn')
            #parentpn.text = systemModel[asbfdefs['top_pn']]
            parentpn.text = skupn

            parentsn = ET.SubElement(compx, 'parent_sn')
            parentsn.text = systemModel[asbfdefs['top_sn']]

        #Write into file





    def writeXML(self):
        xmlstr = ET.tostring(self.asbf, encoding='utf-8', method='xml', xml_declaration=True)
        print(xmlstr)
        fname = os.path.join(self.outputloc, self.fname)
        f = open(fname, "wb")
        f.write(xmlstr)
        f.close()



if __name__ == "__main__":
    asbf = AsBuiltFeed()
    sysModel = {
                'chassis_pn' : '800950-00',
                'chassis_sn' : '1908Q-20179',
                'version' : '20.1.1',
                'psu_pn' : '700-013917-0000',
                'psu_sn' : 'L257VQ001505P'
                }
    asbf.generateTag(systemModel=sysModel)
    asbf.writeXML()

