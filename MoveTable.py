
import os
import argparse
import base64, json
import logging, ast, threading
import datetime, time, os, sys, shutil
import smartsheet
from numpy import unicode
from smartsheet.exceptions import UnexpectedRequestError

from config.ConfigItems import smartsheetDefs as ssdefs


class MoveTable(object):
    '''
    classdocs
    '''

    staticdir = None

    def __init__(self, staticdir=None, cascPath=None):
        '''
        Constructor
        '''
        print("====")
        self.ssid = ssdefs['sheetid']
        self.apitoken = ssdefs['apitoken']
        self.loadSmartSheet()

    def loadSmartSheet(self):
        """

        :return:
        """
        """
            Load SmartSheet Object
            """
        logging.info("Connecting to SmartSheet using id %s" % (self.ssid))
        self.ssclient = smartsheet.Smartsheet(self.apitoken)
        try:
            self.sheet = self.ssclient.Sheets.get_sheet(self.ssid)
        except UnexpectedRequestError as e:
            logging.error("Failed to access SmartSheet %s" % (self.ssid))
            logging.error(e.message)

        logging.info("Extracting SmartSheet Column Map")
        self.column_map = {}

        for column in self.sheet.columns:
            self.column_map[column.title] = column.id
            #logging.info("Column Title: %s" % (column.title))
            #logging.debug("Displaying column map,\n%s\n=========" % (self.column_map))
        logging.info("ColumnName: {}".format(self.column_map))
        self.ssrows = {}

        for row in self.sheet.rows:
            str = ''
            rowln = 0
            for colname, colid in self.column_map.items():
                cellx = row.get_column(colid).display_value

                str += "{} : {}, ".format(colname, cellx)

            print("==> {}".format(str))

    def getMoveEnteries(self, serialNum=None):
        """
        Get move entries for a serialnumber
        :param serialNum:
        :return:
        """
        moverows = []
        logging.info("Checking move details for {}".format(serialNum))
        if serialNum:
            serialid = self.column_map['SerialNumber']
            for row in self.sheet.rows:
                rowobj = {}
                for colname, colid in self.column_map.items():
                    cellx = row.get_column(colid).display_value
                    rowobj[colname] =  cellx
                    if cellx == serialNum:
                        logging.info("Found SN# : {}, {}".format(serialNum, rowobj))
                        moverows.append(rowobj)



        return moverows


    def getMoveTable(self):
        """
        Get move entries all
        :return:
        """
        moverows = []
        serialid = self.column_map['Status']
        for row in self.sheet.rows:
            rowobj = {}
            for colname, colid in self.column_map.items():
                cellx = row.get_column(colid).display_value
                rowobj[colname] = cellx

            print("MoveRow: {}".format(rowobj))
            if not rowobj['Status'] or  rowobj['Status'] == 'FAILED':
                    moverows.append(rowobj)



        return moverows


    def getOpenMoves(self, serialNum):
        """
        Get Open Moves
        :param serialNum:
        :return:
        """
        move = None
        for mv in self.getMoveEnteries(serialNum=serialNum):
            if not mv['Status']:
                move = mv
                break

        return move



    def getmovePartNumbers(self):
        """
        Get PartNumber List
        :return:
        """
        partnums = []
        self.loadSmartSheet()
        pnid = self.column_map['SKU']

        for row in self.sheet.rows:
            cellx = row.get_column(pnid).display_value
            if not cellx in partnums:
                partnums.append(cellx)

        return partnums


    def updateStatus(self, serialNum, moveNumber, status, updateTime):
        """
        Get move entries for a serialnumber
        :param serialNum:
        :return:
        """
        moverows = []
        if serialNum:
            serialid = self.column_map['SerialNumber']
            moveid = self.column_map['MoveNumber']

            rows = []
            new_row = None
            for row in self.sheet.rows:
                rowobj = {}
                serial_cell = row.get_column(serialid).display_value
                move_cell = row.get_column(moveid).display_value
                if serial_cell == serialNum and move_cell == moveNumber:
                    # Add new row
                    new_row = self.ssclient.models.Row()
                    new_row.id = row.id

                    for colname, colid in self.column_map.items():
                        cellx = row.get_column(colid).display_value
                        newCell = self.ssclient.models.Cell()
                        newCell.column_id = colid
                        if colname == 'Status':
                            newCell.value = status
                        elif colname == 'CompletionDate':
                            newCell.value = updateTime
                        else:
                            newCell.value = cellx

                        newCell.strict = False
                        new_row.cells.append(newCell)

                    rows.append(new_row)
                    break
            # Going to update Row
            if len(rows):
                logging.info("Updaring Row for {}/{}".format(serialNum, moveNumber))
                res = self.ssclient.Sheets.update_rows(self.ssid, rows)
                # logging.info("\nSSUpdate Res: %s" % (res))
                status = ("%s" % (res))
                if 'SUCCESS' in status:
                    logging.info("Update successful")
                else:
                    logging.error("Row update failed")

        return moverows


# main code section
if __name__ == '__main__':

    dbip = '127.0.0.1'
    logpath = os.path.join(os.getcwd(), 'log', 'movetable-syncr.log')
    logdir = os.path.dirname(logpath)

    cascPath = os.path.abspath(os.getcwd())

    logging.basicConfig(filename=logpath, level=logging.DEBUG, format='%(asctime)s %(message)s')
    handler = logging.StreamHandler(sys.stdout)
    logging.getLogger().addHandler(handler)

    ap = argparse.ArgumentParser()

    movetable = MoveTable()
    movetable.getMoveEnteries(serialNum='1908Q-20179')
    datetimestr = str(datetime.datetime.now()).split('.')[0]
    print("Updatetime: {}".format(datetimestr))
    movetable.updateStatus(serialNum='1908Q-20179', moveNumber='M23412', status='FAILED', updateTime=datetimestr)
    for pn in movetable.getmovePartNumbers():
        print("PN: {}".format(pn))

    for row in movetable.getMoveTable():
        print("ROw: {}".format(row))
