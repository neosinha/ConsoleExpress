import cv2
import os, logging, sys, time
from pyzbar.pyzbar import decode as barcodedecode
from pylibdmtx.pylibdmtx import decode as dmatrixdecode
import numpy as np
import easyocr


logpath = os.path.join(os.getcwd(), 'log', 'labelexpress.log')
logdir = os.path.dirname(logpath)
if not os.path.exists(logdir):
    print("Log directory does not exist, creating %s" % (logdir))
    os.makedirs(logdir)

logging.basicConfig(filename=logpath, level=logging.DEBUG, format='%(asctime)s %(message)s')
handler = logging.StreamHandler(sys.stdout)
logging.getLogger().addHandler(handler)


class BarcodeCore(object):
    '''
    BarcodeCore Class
    '''

    def __init__(self, cascadePath=None):
        '''
        Constructor for PixelCore
        '''
        logging.info("Starting LabelExpress Core")

    def img_ocr(self, imagex=None):
        """
        Performs OCR on
        :param imagex:
        :return:
        """
        reader = easyocr.Reader(['en'])
        oclist = None
        if imagex:
            oclist = reader.readtext(imagex)
            for oc in oclist:
                print(oc)

    def barcode_decode(self, imagex=None):
        """
        Detects BarCode(s) in a iImage
        :param imagex:
        :return:
        """
        bcount = 0
        if imagex:
            imgx = cv2.imread(imagex)
            barcodes = barcodedecode(imgx)
            for bcode in barcodes:
                print(bcount, bcode)
                #print(bcount, bcode.data, bcode.type, bcode.re)
                data, ctype, rect, points = bcode
                bcount += 1


    def datamatix_decode(self, imagex=None):
        """

        :param imagex:
        :return:
        """
        if imagex:
            imgx = cv2.imread(imagex)
            dmatrixcodes = dmatrixdecode(imgx)
            for dmtrix in dmatrixcodes:
                data, rect = dmtrix
                datax = data.decode('utf-8')
                print(rect, datax)



    def epoch(self):
        """
        Returns Unix Epoch
        """
        epc = int(time.time() * 1000)

        return epc





# main code section
if __name__ == '__main__':
    pxc = BarcodeCore()

    #bcodes = pxc.find_barcode(imgpath='/Users/nasinha/Development/workspace/BarcodeDetector/examples/testimges/ap'
    #                                   '-7602-2.png')
    #for bcode in bcodes:
    #    print(bcode)
    imagex = '/Users/nasinha/Development/workspace/BarcodeDetector/examples/testimges/ap-7602-2.png'
    imagex = '/Users/nasinha/Downloads/DSC_0860.JPG'
    #imagex = '/Users/nasinha/Downloads/psu.PNG'

    oclist = pxc.img_ocr(imagex= imagex)
    print("=====")
    oclist = pxc.barcode_decode(imagex= imagex)
    print("=====")
    oclist = pxc.datamatix_decode(imagex= imagex)
