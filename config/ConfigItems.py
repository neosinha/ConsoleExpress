#MQTT server definitions
svnrevid= "$Id: ConfigItems.py 481 2021-02-10 12:41:24Z nasinha $"

mqtt = {
        'mqttserver' : { 'server' : '10.24.114.242', 'port' : 1883},
        'websocket': { 'server': '10.24.114.242' , 'port' : 8003 }
       }

#MongoDB Defintions
mongo = {
        'server': '10.24.114.242:',
        'port': 27017,
        'database' : 'baudexp'
        }


smartsheetDefs = { 'sheetid' : '5354789082032004',
                    # 'sheetid' : '1121086709491588',
                   'apitoken' : "zz4c0jv2ll1iacia3rh4fxrts0",
                   'columnkey': ['MoveNumber' , 'SerialNumber', 'SKU', 'Status']
                  }

