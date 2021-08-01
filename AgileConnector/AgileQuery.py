'''
Created on Oct 8, 2018

@author: nasinha
'''

import json
import os
import time

import cherrypy as AgileServer
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


class AgileQuery(object):
    '''
    Agile driver for programmatic extraction of information
    '''

    browser = None

    def __init__(self):
        '''
        Constructor
        '''
        options = Options()
        options.set_headless(headless=False)
        geckopath = os.path.join(os.getcwd(),'..', 'bin', 'geckodriver')
        profile = webdriver.FirefoxProfile()
        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.download.manager.showWhenStarting", False)
        options.set_preference("browser.download.dir", "/data")
        options.set_preference("browser.helperApps.neverAsk.saveToDisk",
                               "application/octet-stream,application/vnd.ms-excel")
        #driver = webdriver.Firefox(firefox_options=self.options)
        profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/vnd.ms-excel");
        self.browser = webdriver.Firefox(firefox_options=options, executable_path=geckopath, firefox_profile=profile)

        # self.browser = webdriver.Safari()
        time.sleep(2)
        self.browser.get("https://agileplm..jsp")
        self.login_handler()
        print("Windows: %s" % (len(self.browser.window_handles)))
        maxidx = len(self.browser.window_handles) -1
        self.browser.switch_to_window(self.browser.window_handles[maxidx])

        time.sleep(5)
        # self.quicksearch(query="BR-MLX-10GX20-M")
        
    
    
    def login_handler(self):
        """
        """
        username = self.browser.find_element_by_id("j_username")
        username.clear()
        username.send_keys("nasinha")

        passwd = self.browser.find_element_by_id("j_password")
        passwd.clear()
        passwd.send_keys("Funding2021")

        print("Windows: %s" % (len(self.browser.window_handles)))
        login = self.browser.find_element_by_id("login")
        window1 = self.browser.window_handles[0]
        login.click()
         
        print(self.browser.title)
        time.sleep(10)
        print("Windows: %s" % (len(self.browser.window_handles)))
        
        time.sleep(2)
        self.browser.refresh()
        self.browser.close()
        time.sleep(2)
    
    
    @AgileServer.expose
    def index(self):
        """
        Server Index Page
        """
        status = {'epoch' : self.epoch()}
        return json.dumps(status)
        
 
    def epoch(self):
        """
        Returns the current EPOCH time
        """
        millis = int(round(time.time() * 1000))
        
        return millis
    
    
    @AgileServer.expose
    def quicksearch(self, query='BR-MLX-10GX20-M'):
        # print(self.browser.page_source)
        
               
        qsearch = self.browser.find_element_by_id("QUICKSEARCH_STRING")
        if query: 
            qsearch.clear()
            qsearch.send_keys(query)
            srchbutton = self.browser.find_element_by_id("top_simpleSearch")
            srchbutton.click()
            time.sleep(5)
        
        qsrch_table = self.browser.find_element_by_id("QUICKSEARCH_TABLE")
        partnumber = {}
        rows = []
        print("=============================================")
        for row in qsrch_table.find_elements_by_xpath(".//tr"):
            # rowlist = ([ td.text for td in row.find_elements_by_xpath(".//td[text()]")  if len(td.text) > 1  & ('Product' in td.text)])
            rowlist = ([ td.text for td in row.find_elements_by_xpath(".//td[text()]")  if len(td.text) > 1 ])
            # print('================== %s' % (len(rowlist)))
            if len(rowlist) > 1:
                # print(rowlist)
                rowliststr = '%r' % (rowlist)
                if len(rowlist) == 4: 
                    if 'Product SKU' in rowliststr: 
                        print('Query: %s, %s' % (query, rowliststr))
                        partnumber['partnumber'] = rowlist[1]
                        partnumber['description'] = rowlist[2]
                        partnumber['lifecycle'] = rowlist[3] 
                
                rows.append(rowlist)
                
       
        
        return json.dumps(partnumber)
        # self.browser.close()
    
    @AgileServer.expose
    def getbom(self, partnum='BR-MLX-10GX20-M'):
        # print(self.browser.page_source)
        qsearch = self.browser.find_element_by_id("QUICKSEARCH_STRING")
        if partnum: 
            qsearch.clear()
            qsearch.send_keys(partnum)
            srchbutton = self.browser.find_element_by_id("top_simpleSearch")
            srchbutton.click()
            time.sleep(2)
        
        qsrch_table = self.browser.find_element_by_id("QUICKSEARCH_TABLE")
        partnumber = {}
        rows = []
        #driver.find_element_by_id("QUICKSEARCH_STRING").click()
        #driver.find_element_by_xpath("//span[@id='top_simpleSearchspan']/em").click()
        qsrch_table = self.browser.find_element_by_xpath(
            "//table[@id='QUICKSEARCH_TABLE']/tbody/tr[2]/td[2]/div/div/table/tbody/tr[23]/td[7]").click()

        self.browser.find_element_by_link_text(partnum).click()
        time.sleep(1)
        self.browser.find_element_by_link_text("BOM").click()
        time.sleep(1)

        #self.browser.find_element_by_id("table_actions_3").click()
        #time.sleep(0.5)
        #self.browser.find_element_by_id("MSG_More_3span").click()
        #time.sleep(0.5)
        #self.browser.find_element_by_id("view_controls_3").click()
        #time.sleep(0.5)
        self.browser.find_element_by_id("Actions").click()
        #self.browser.find_element_by_xpath("(//a[contains(text(),'Actions')])[3]").click()
        #self.browser.find_element_by_id("Actionsem_29").click()
        time.sleep(0.5)
        self.browser.find_element_by_xpath("(//a[contains(text(),'Export')])[3]").click()
        time.sleep(0.5)
        print("Windows: %s" % (len(self.browser.window_handles)))

        maxidx = len(self.browser.window_handles) - 1
        self.browser.switch_to_window(self.browser.window_handles[1])
        time.sleep(0.85)
        print("Window Title: {}".format(self.browser.title))
        # ERROR: Caught exception [ERROR: Unsupported command [selectWindow | win_ser_1 | ]]
        self.browser.find_element_by_id("cmdNext").click()
        time.sleep(0.5)
        self.browser.find_element_by_id("cmdNext").click()
        time.sleep(0.5)
        self.browser.find_element_by_id("cmdNext").click()
        time.sleep(0.5)
        self.browser.find_element_by_id("cmdFinish").click()
        time.sleep(10)
        alert_obj = self.browser.switch_to_alert()
        print('AlertText: {}'.format(alert_obj.text))

        #self.browser.find_element_by_xpath("//span[@id='cmdNextspan']/em").click()
        #self.browser.find_element_by_xpath("//span[@id='cmdNextspan']/em").click()
        #self.browser.find_element_by_xpath("//span[@id='cmdFinishspan']/em").click()
        # ERROR: Caught exception [ERROR: Unsupported command [selectWindow | win_ser_2 | ]]
        #self.browser.find_element_by_id("cmdClosespan").click()
        self.browser.driver.close()

        return json.dumps(partnumber)
        # self.browser.close()
        





if __name__ == "__main__":
    portnum = 9101
    wwwPath = os.path.join(os.getcwd(), "ui_www")
    dbaddress = ""
    AgileServer.config.update(
                        {'server.socket_host' : '127.0.0.1',
                            'server.socket_port': portnum,
                            'server.socket_timeout': 600,
                            'server.thread_pool' : 8,
                            'server.max_request_body_size': 0
                            }
                        )
    
    conf = {
            '/': {
                'tools.sessions.on': True,
                'tools.staticdir.on': True,
                'tools.staticdir.dir': wwwPath
            }
        }
    
    
    #AgileServer.quickstart(AgileQuery(), '/', conf)
    aq = AgileQuery()
    #aq.quicksearch(query="NI-MLX-10GX8-M")
    aq.getbom(partnum="SLX9150-48XT-6C-AC-F")
            
        
    
 

        
        