import json
import logging
import os
import sys

from pymongo import MongoClient


class SequenceUpdater(object):
    """
    BuadExpress: Baudexpress takes in SN# and looks up actions
    """

    def __init__(self, mqttclient=None, mongodb=None, logexport=None):
        '''
        Constructor for BExpress Core
        '''
        logging.info("BExpress Sequence Updater")
        dbase = '127.0.0.1'
        if mongodb:
            # Connect to database
            dbase = mongodb
            logging.info("Connecting to Mongo Instance at %s" % (dbase))
            ## there is a port notation embedded
            if ':' in mongodb:
                self.database, port = mongodb.split(':')
                port = int(port)

            self.client = MongoClient(self.database, port)
            self.client = MongoClient(dbase, 27017)
            database = self.client['baudexpress']
            self.dbcol = database['sequences']


    def uploader(self, jsonfile=None, rev=None):
        """
        Uploads Sequences into DB
        :return:
        """
        print("JSON File: {}".format(jsonfile) )
        with open(jsonfile, 'r') as jsonf:
            jsonstrx = jsonf.read()
            seqobj = json.loads(jsonstrx)
            #seqobj['version'] = '1.0.0'
            query = {'sku': seqobj['sku']}
            upseq = seqobj.copy()
            logging.info("JSON SKU {}, {}".format(seqobj['sku'], json.dumps(seqobj, indent=2)))

            res = self.dbcol.update(query, upseq, upsert=True)
            if res['updatedExisting']:
                logging.info("SKU: {} was already loaded".format(seqobj['sku']))


#main code section
if __name__ == '__main__':

    logpath = os.path.join(os.getcwd(), 'log', 'baudexpress-updater.log')
    logdir = os.path.dirname(logpath)
    if not os.path.exists(logdir):
        print("Log directory does not exist, creating %s" % (logdir))
        os.makedirs(logdir)

    logging.basicConfig(filename=logpath, level=logging.DEBUG, format='%(asctime)s %(message)s')
    handler = logging.StreamHandler(sys.stdout)
    logging.getLogger().addHandler(handler)

    basedir = os.path.join(os.getcwd(), 'sequences')

    updtr = SequenceUpdater(mongodb='data.sinhamobility.com:28018')
    for jsonfilex in os.listdir(basedir):
        if jsonfilex.endswith('json'):
            logging.info("JSON file {}:".format(jsonfilex))
            #updtr.uploader(jsonfile=os.path.join(basedir,jsonfilex))

    jsonfile = os.path.join(os.getcwd(), 'sequences', 'NI-CER-2024C.json')
    updtr.uploader(jsonfile=jsonfile)



