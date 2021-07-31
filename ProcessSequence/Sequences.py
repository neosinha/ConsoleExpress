svnrevision="$Id: Sequences.py 525 2021-06-18 16:34:25Z nasinha $"


from BExpress.AutomationSequence import ParseEngine

CommandSequence = {}
StructureDef = {}

#
#     parse.addparser('james', 'hi.this.*(ja.es)')
#     parse.addparser('version', 'version.=.(.*)')
#     parse.addparser('module', 'module')
#
#     print parse.extract(buffer, 'james', 'version', 'module')
#
def failmsg():
    """

    :return:
    """
    print("Fail Message")

#slxparseobj = ParseEngine(key='swversion', regex='Firmware.name:(.*)', expect='20.2.3a')
slxparseobj = ParseEngine(key='osversion', regex='Firmware.name:(.*)')
slxparseobj.addparser(key='swversion', regex='Firmware.name:(.*)', expect='20.2.3a', notmatchcallback=failmsg())
slxparseobj.addparser(key='chassis_pn', regex='Factory.Part.Num:(.*)')
slxparseobj.addparser(key='chassis_sn', regex='Factory.Serial.Num:(.*)', expect="scanned.chassis_sn")
#slxparseobj.addparser(key='chassis_sn', regex='Factory.Serial.Num:(.*)')
slxparseobj.addparser(key='chassis_type', regex='Chassis.Name:(.*)')
slxparseobj.addparser(key='psu_id', regex='ID:(.*)')
slxparseobj.addparser(key='psu_pn', regex='Part.Num:(.*)')
slxparseobj.addparser(key='psu_sn', regex='Serial.Num:(.*)')
#slxparseobj.addparser(key='psu_type', regex='AirFlow:(.*)', expect='Intake')
slxparseobj.addparser(key='psu_type', regex='AirFlow:(.*)')
slxparseobj.addparser(key='mac', regex='Burned.In.MAC.*:.(..:..:..:..:..:..)')
slxparseobj.addparser(key='fan1speed', regex='Fan.1.*is.(.*).RPM')
slxparseobj.addparser(key='fan2speed', regex='Fan.2.*is.(.*).RPM')
slxparseobj.addparser(key='fan3speed', regex='Fan.3.*is.(.*).RPM')
slxparseobj.addparser(key='fan4speed', regex='Fan.4.*is.(.*).RPM')
slxparseobj.addparser(key='fan5speed', regex='Fan.5.*is.(.*).RPM')
slxparseobj.addparser(key='fan6speed', regex='Fan.6.*is.(.*).RPM')
slxparseobj.addparser(key='PSU1GOOD', regex='Power.Supply.#1.is(.*)', expect="OK")
#slxparseobj.addparser(key='PSU2GOOD', regex='Power.Supply.#2.is(.*)', expect="OK")


CommandSequence['SLX9150-48XT-6C-AC-F'] = \
    {
            'about' : {'image' : 'SLX9150-48XT-8C.png', 'text' : 'SLX9150-48XT-8C has 48x10G Copper ports and '
                                                                 '8xQSFP28'},
            'commandset': [
                    {'cmd': "\n", 'prompt': ["SLX.*login"], 'timeout': 10,
                        'usermsg' : {'text' : 'Please ensure that unit is powered on', 'image' : None}},
                    {'cmd': "\n", 'prompt': ["SLX.*login"], 'timeout': 10,
                     'usermsg' : {'text' : 'Please ensure that unit is powered on', 'image' : None}},
                    {'cmd': "admin\n", 'prompt': ["Password:"], 'timeout': 10},
                    {'cmd': "password\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "term len 0\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "dhcp ztp cancel\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show version\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show env power\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show env fan\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show chassis\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show system\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "exit\n", 'prompt': ["SLX.*login"], 'timeout': 10}
                    #{'cmd': "reload\n", 'prompt': ["reload.*switch.*y.n:"], 'timeout': 10},
                    #   {'cmd': "y\n", 'prompt': ["System.*initialization.*complete"], 'timeout': 180},

                    #{'cmd': "\n", 'prompt': ["SLX.*login"], 'timeout': 10},
                    #{'cmd': "admin\n", 'prompt': ["Password:"], 'timeout': 10},
                    #{'cmd': "password\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    #{'cmd': "term len 0\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    #{'cmd': "show system\n", 'prompt': ["SLX.*#"], 'timeout': 10}
                    ] ,
            'parseobj' : slxparseobj,
            'scanlist' : [
                           #{'SerialNumnber' : 'serialnum'},
                           {'Console' : { 'id' : 'iconsole', 'value' : '10.31.221.215:3010', 'telnet' : True }},
                           {'CHASSIS SN' : { 'id' : 'chassis_sn', 'value' : 'TH012040Q-40008', 'SerialNumber' : True}},
                           {'FAN1 SN' : { 'id' : 'fan1sn', 'value' : 'L214WJ000C06P' }},
                           {'FAN1 PN' : { 'id' : 'fan1pn', 'value' : '700-013684-0100'}},
                           {'FAN3 SN' : { 'id' : 'fan3sn', 'value' : 'L214WJ000C06Q' }},
                           {'FAN3 PN' : { 'id' : 'fan3pn', 'value' : '700-013684-0100'}},
                           {'FAN2 SN' : { 'id' : 'fan2sn', 'value' : 'L214WJ000C07P'}},
                           {'FAN2 PN' : { 'id' : 'fan2pn', 'value' : '700-013684-0100'}},
                           {'PSU1 SN': {'id': 'psu1sn', 'value': 'L214WJ000D07P'}},
                           {'PSU1 PN': {'id': 'psu1pn', 'value': '700-013684-0200'}}
                    ],
            #Map Reporting to ASBF tags
            'AsBuiltFeedMap' : {
                            'top_pn' : 'chassis_pn',
                            'top_sn' : 'chassis_sn',
                            'swversion' : 'swversion',
                            'components': [ { 'item': 'fan', 'component_sn' : "scanlist['fan1sn']",
                                                             'component_pn' : "scanlist['fan1pn']"
                                              },
                                              { 'item': 'fan', 'component_sn' : "scanlist['fan2sn']",
                                                             'component_pn' : "scanlist['fan2pn']"
                                              }
                                          ]
                    }

    }


CommandSequence['SLX9150-48XT-6C-AC-R'] = \
    {
            'about' : {'image' : 'SLX9150-48XT-8C.png',
                       'text' : 'SLX9150-48XT-8C has 48x10G Copper ports and '
                                                                 '8xQSFP28'},
            'inspection' : [ {'testname' : 'Box Inspection Steps',
                              'steps' : [ {'title' : "Step 1",
                                           'content' : 'Please check side of the box for holes',
                                           'upload' : True,
                                           'continueonfail' : True },

                                          {'title' : "Step 2",
                                           'content' : 'Please check side of the box for holes',
                                           'upload' : True,
                                           'continueonfail' : True },
                                          ] },
                            ],
            'commandset': [
                    {'cmd': "\n", 'prompt': ["SLX.*login"], 'timeout': 10,
                     'uiprompt' : {'text' : "Please ensure that unit is Powered ON. ", 'type' : 'confirm'} },

                    {'cmd': "admin\n", 'prompt': ["Password:"], 'timeout': 10},
                    {'cmd': "password\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "term len 0\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "dhcp ztp cancel\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show version\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show env power\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show env fan\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show chassis\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show system\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "exit\n", 'prompt': ["SLX.*login"], 'timeout': 10}
                    #{'cmd': "reload\n", 'prompt': ["reload.*switch.*y.n:"], 'timeout': 10},
                    #{'cmd': "y\n", 'prompt': ["System.*initialization.*complete"], 'timeout': 180},

                    #{'cmd': "\n", 'prompt': ["SLX.*login"], 'timeout': 10},
                    #{'cmd': "admin\n", 'prompt': ["Password:"], 'timeout': 10},
                    #{'cmd': "password\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    #{'cmd': "term len 0\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    #{'cmd': "show system\n", 'prompt': ["SLX.*#"], 'timeout': 10}
                    ] ,
            'parseobj' : slxparseobj,
            'instructions' : [ {'img' : '', 'text' : 'This is a cool instruction'}  ] ,
            'scanlist' : [
                           #{'SerialNumnber' : 'serialnum'},
                           {'CHASSIS SN' : { 'id' : 'chassis_sn', 'value' : 'TH012040Q-40008' }},
                           { 'FAN1 SN' : { 'id' : 'fan1sn', 'value' : 'L214WJ000C06P' }},
                           {'FAN1 PN' : { 'id' : 'fan1pn', 'value' : '700-013684-0100'}},
                           {'FAN3 SN' : { 'id' : 'fan3sn', 'value' : 'L214WJ000C06Q' }},
                           {'FAN3 PN' : { 'id' : 'fan3pn', 'value' : '700-013684-0100'}},
                           {'FAN2 SN' : { 'id' : 'fan2sn', 'value' : 'L214WJ000C07P'}},
                           {'FAN2 PN' : { 'id' : 'fan2pn', 'value' : '700-013684-0100'}},
                           {'PSU1 SN': {'id': 'psu1sn', 'value': 'L214WJ000D07P'}},
                           {'PSU1 PN': {'id': 'psu1pn', 'value': '700-013684-0200'}}
                    ],
            #Map Reporting to ASBF tags
            'AsBuiltFeedMap' : {
                            'top_pn' : 'chassis_pn',
                            'top_sn' : 'chassis_sn',
                            'swversion' : 'swversion',
                            'components': [ { 'item': 'fan', 'component_sn' : "scanlist['fan1sn']",
                                                             'component_pn' : "scanlist['fan1pn']"
                                              },
                                              { 'item': 'fan', 'component_sn' : "scanlist['fan2sn']",
                                                             'component_pn' : "scanlist['fan2pn']"
                                              },
                                           ]
                    }
    }

# slx8720 ----------------------------------------------------------------------
slx8720parseobj = ParseEngine(key='swversion', regex='Firmware.name:(.*)')
slx8720parseobj.addparser(key='chassis_pn', regex='Factory.Part.Num:(.*)')
slx8720parseobj.addparser(key='chassis_sn', regex='Factory.Serial.Num:(.*)', expect="scanned.chassis_sn")
#slx8720parseobj.addparser(key='chassis_sn', regex='Factory.Serial.Num:(.*)')
slx8720parseobj.addparser(key='chassis_type', regex='Chassis.Name:(.*)')
slx8720parseobj.addparser(key='psu_id', regex='ID:(.*)')
slx8720parseobj.addparser(key='psu_pn', regex='Part.Num:(.*)')
slx8720parseobj.addparser(key='psu_sn', regex='Serial.Num:(.*)')
#slx8720parseobj.addparser(key='psu_type', regex='AirFlow:(.*)', expect='Intake')
#slx8720parseobj.addparser(key='psu_type', regex='AirFlow:(.*)', expect='Port Side Intake')
slx8720parseobj.addparser(key='mac', regex='Burned.In.MAC.*:.(..:..:..:..:..:..)')
slx8720parseobj.addparser(key='fan1speed', regex='Fan.1.*is.(.*).RPM')
slx8720parseobj.addparser(key='fan2speed', regex='Fan.2.*is.(.*).RPM')
slx8720parseobj.addparser(key='fan3speed', regex='Fan.3.*is.(.*).RPM')
slx8720parseobj.addparser(key='fan4speed', regex='Fan.4.*is.(.*).RPM')
slx8720parseobj.addparser(key='fan5speed', regex='Fan.5.*is.(.*).RPM')
slx8720parseobj.addparser(key='fan6speed', regex='Fan.6.*is.(.*).RPM')
slx8720parseobj.addparser(key='PSU1GOOD', regex='Power.Supply.#1.is(.*)', expect="OK")
slx8720parseobj.addparser(key='PSU2GOOD', regex='Power.Supply.#2.is(.*)', expect="OK")
slx8720parseobj.addparser(key='tpmstatus', regex='TPM.Provision.status.:(.*)', expect="Provisioned")

#slxpa

CommandSequence['8720-32C-AC-R']  = \
    {
            'about' : {'image' : 'SLX9150-48XT-8C.png', 'text' : 'SLX 8720-32C-AC-R has 32x100G Copper ports and '
                                                                 '8xQSFP28'},
            'commandset': [
                    {'cmd': "\n\n", 'prompt': ["SLX.*login"], 'timeout': 10,
                        'usermsg' : {'text' : 'Please ensure that unit is powered on', 'image' : None}},
                    {'cmd': "\n", 'prompt': ["SLX.*login"], 'timeout': 10,
                     'usermsg' : {'text' : 'Please ensure that unit is powered on', 'image' : None}},
                    {'cmd': "admin\n", 'prompt': ["Password:"], 'timeout': 10},
                    {'cmd': "password\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "term len 0\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "dhcp ztp cancel\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show version\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show env power\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show env fan\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show chassis\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show system\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show tpm ekcert\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show tpm iakcert\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show tpm idevidcert\n", 'prompt': ["SLX.*#"], 'timeout': 10},

                    {'cmd': "start-shell\n", 'prompt': ["admin.*SLX.*#"], 'timeout': 10},
                    {'cmd': "\n", 'prompt': ["admin.*SLX.*#"], 'timeout': 10},
                    {'cmd': "dmesg\n", 'prompt': ["admin.*SLX.*#"], 'timeout': 60},
                    {'cmd': "exit\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show system\n", 'prompt': ["SLX.*#"], 'timeout': 10},

                    {'cmd': "write erase\n", 'prompt': ["SLX.*login"], 'timeout': 10},
                    {'cmd': "reload\n", 'prompt': ["n.*yes"], 'timeout': 2},
                    {'cmd': "y\n", 'prompt': ["System.*initialization.*complete"], 'timeout': 180}

                    #{'cmd': "\n", 'prompt': ["SLX.*login"], 'timeout': 10},
                    #{'cmd': "admin\n", 'prompt': ["Password:"], 'timeout': 10},
                    #{'cmd': "password\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    #{'cmd': "term len 0\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    #{'cmd': "show system\n", 'prompt': ["SLX.*#"], 'timeout': 10}
                    ] ,
            'parseobj' : slx8720parseobj,
            'scanlist' : [
                {'Console' : { 'id' : 'iconsole', 'value' : '127.0.0.1:5008', 'telnet' : True }},
                           {'CHASSIS SN' : { 'id' : 'chassis_sn', 'value' : 'TH01205Q-40040', 'SerialNumber' : True}},

                           {'FAN1 SN' : { 'id' : 'fan1sn', 'value' : '2052Q-41271' }},
                           {'FAN1 PN' : { 'id' : 'fan1pn', 'value' : 'XN-FAN-001-R'}},

                           {'FAN2 SN' : { 'id' : 'fan2sn', 'value' : '2052Q-41272' }},
                           {'FAN2 PN' : { 'id' : 'fan2pn', 'value' : 'XN-FAN-001-R'}},

                           {'FAN3 SN' : { 'id' : 'fan3sn', 'value' : '2052Q-41273' }},
                           {'FAN3 PN' : { 'id' : 'fan3pn', 'value' : 'XN-FAN-001-R'}},

                           {'FAN4 SN': {'id': 'fan4sn', 'value': '2052Q-41274'}},
                           {'FAN4 PN': {'id': 'fan4pn', 'value': 'XN-FAN-001-R'}},

                           {'FAN5 SN': {'id': 'fan5sn', 'value': '2052Q-41275'}},
                           {'FAN5 PN': {'id': 'fan5pn', 'value': 'XN-FAN-001-R'}},

                           {'FAN6 SN': {'id': 'fan6sn', 'value': '2052Q-41276'}},
                           {'FAN6 PN': {'id': 'fan6pn', 'value': 'XN-FAN-001-R'}},

                           {'PSU1 SN': {'id': 'psu1sn', 'value': 'L2571500JF06P'}},
                           {'PSU1 PN': {'id': 'psu1pn', 'value': 'XN-ACPWR-750W-R'}},

                           {'PSU2 SN': {'id': 'psu2sn', 'value': 'L2571500K306P'}},
                           {'PSU2 PN': {'id': 'psu2pn', 'value': 'XN-ACPWR-750W-R'}}
                    ],

            #Map Reporting to ASBF tags
            'AsBuiltFeedMap' : {
                            'top_pn' : 'chassis_pn',
                            'top_sn' : 'chassis_sn',
                            'swversion' : 'swversion',
                            'components': [ { 'item': 'fan', 'component_sn' : "scanlist['fan1sn']",
                                                             'component_pn' : "scanlist['fan1pn']"
                                              },
                                              { 'item': 'fan', 'component_sn' : "scanlist['fan2sn']",
                                                             'component_pn' : "scanlist['fan2pn']"
                                              },

                                             { 'item': 'fan', 'component_sn' : "scanlist['fan3sn']",
                                                             'component_pn' : "scanlist['fan3pn']"
                                              },

                                            {'item'        : 'fan', 'component_sn': "scanlist['fan4sn']",
                                             'component_pn': "scanlist['fan4pn']"
                                             },

                                            {'item'        : 'fan', 'component_sn': "scanlist['fan5sn']",
                                             'component_pn': "scanlist['fan5pn']"
                                             },

                                            {'item'        : 'fan', 'component_sn': "scanlist['fan6sn']",
                                             'component_pn': "scanlist['fan6pn']"
                                             },

                                            {'item'        : 'psu', 'component_sn': "scanlist['psu1sn']",
                                             'component_pn': "scanlist['psu1pn']"
                                             },

                                            {'item'        : 'psu', 'component_sn': "scanlist['psu2sn']",
                                             'component_pn': "scanlist['psu2pn']"
                                             }
                                            ]
                    }
    }

slx8720fparseobj = ParseEngine(key='swversion', regex='Firmware.name:(.*)')
slx8720fparseobj.addparser(key='chassis_pn', regex='Factory.Part.Num:(.*)')
slx8720fparseobj.addparser(key='chassis_sn', regex='Factory.Serial.Num:(.*)', expect="scanned.chassis_sn")
#slx8720fparseobj.addparser(key='chassis_sn', regex='Factory.Serial.Num:(.*)')
slx8720fparseobj.addparser(key='chassis_type', regex='Chassis.Name:(.*)')
slx8720fparseobj.addparser(key='psu_id', regex='ID:(.*)')
slx8720fparseobj.addparser(key='psu_pn', regex='Part.Num:(.*)')
slx8720fparseobj.addparser(key='psu_sn', regex='Serial.Num:(.*)')
#slx8720fparseobj.addparser(key='psu_type', regex='AirFlow:(.*)', expect='Intake')
slx8720fparseobj.addparser(key='psu_type', regex='AirFlow:(.*)', expect='Port Side Exhaust')
slx8720fparseobj.addparser(key='mac', regex='Burned.In.MAC.*:.(..:..:..:..:..:..)')
slx8720fparseobj.addparser(key='fan1speed', regex='Fan.1.*is.(.*).RPM')
slx8720fparseobj.addparser(key='fan2speed', regex='Fan.2.*is.(.*).RPM')
slx8720fparseobj.addparser(key='fan3speed', regex='Fan.3.*is.(.*).RPM')
slx8720fparseobj.addparser(key='fan4speed', regex='Fan.4.*is.(.*).RPM')
slx8720fparseobj.addparser(key='fan5speed', regex='Fan.5.*is.(.*).RPM')
slx8720fparseobj.addparser(key='fan6speed', regex='Fan.6.*is.(.*).RPM')
slx8720fparseobj.addparser(key='PSU1GOOD', regex='Power.Supply.#1.is(.*)', expect="OK")
slx8720fparseobj.addparser(key='PSU2GOOD', regex='Power.Supply.#2.is(.*)', expect="OK")
slx8720fparseobj.addparser(key='tpmstatus', regex='TPM.Provision.status.:(.*)', expect="Provisioned")


CommandSequence['8720-32C-AC-F']  = \
    {
            'about' : {'image' : 'SLX9150-48XT-8C.png', 'text' : 'SLX 8720-32C-AC-F has 32x100G Copper ports and '
                                                                 '8xQSFP28'},
            'commandset': [
                    {'cmd': "\n\n", 'prompt': ["SLX.*login"], 'timeout': 10,
                        'usermsg' : {'text' : 'Please ensure that unit is powered on', 'image' : None}},
                    {'cmd': "\n", 'prompt': ["SLX.*login"], 'timeout': 10,
                     'usermsg' : {'text' : 'Please ensure that unit is powered on', 'image' : None}},
                    {'cmd': "admin\n", 'prompt': ["Password:"], 'timeout': 10},
                    {'cmd': "password\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "term len 0\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "dhcp ztp cancel\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show version\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show env power\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show env fan\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show chassis\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show system\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show tpm ekcert\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show tpm iakcert\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show tpm idevidcert\n", 'prompt': ["SLX.*#"], 'timeout': 10},

                    {'cmd': "start-shell\n", 'prompt': ["admin.*SLX.*#"], 'timeout': 10},
                    {'cmd': "\n", 'prompt': ["admin.*SLX.*#"], 'timeout': 10},
                    {'cmd': "dmesg\n", 'prompt': ["admin.*SLX.*#"], 'timeout': 60},
                    {'cmd': "exit\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show system\n", 'prompt': ["SLX.*#"], 'timeout': 10},

                    {'cmd': "write erase\n", 'prompt': ["SLX.*login"], 'timeout': 10},
                    {'cmd': "reload\n", 'prompt': ["n.*yes"], 'timeout': 2},
                    {'cmd': "y\n", 'prompt': ["System.*initialization.*complete"], 'timeout': 180}

                    #{'cmd': "\n", 'prompt': ["SLX.*login"], 'timeout': 10},
                    #{'cmd': "admin\n", 'prompt': ["Password:"], 'timeout': 10},
                    #{'cmd': "password\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    #{'cmd': "term len 0\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    #{'cmd': "show system\n", 'prompt': ["SLX.*#"], 'timeout': 10}
                    ] ,
            'parseobj' : slx8720fparseobj,
            'scanlist' : [
                {'Console' : { 'id' : 'iconsole', 'value' : '127.0.0.1:5008', 'telnet' : True }},
                           {'CHASSIS SN' : { 'id' : 'chassis_sn', 'value' : 'TH01205Q-40040', 'SerialNumber' : True}},

                           {'FAN1 SN' : { 'id' : 'fan1sn', 'value' : '2052Q-41271' }},
                           {'FAN1 PN' : { 'id' : 'fan1pn', 'value' : 'XN-FAN-001-R'}},

                           {'FAN2 SN' : { 'id' : 'fan2sn', 'value' : '2052Q-41272' }},
                           {'FAN2 PN' : { 'id' : 'fan2pn', 'value' : 'XN-FAN-001-R'}},

                           {'FAN3 SN' : { 'id' : 'fan3sn', 'value' : '2052Q-41273' }},
                           {'FAN3 PN' : { 'id' : 'fan3pn', 'value' : 'XN-FAN-001-R'}},

                           {'FAN4 SN': {'id': 'fan4sn', 'value': '2052Q-41274'}},
                           {'FAN4 PN': {'id': 'fan4pn', 'value': 'XN-FAN-001-R'}},

                           {'FAN5 SN': {'id': 'fan5sn', 'value': '2052Q-41275'}},
                           {'FAN5 PN': {'id': 'fan5pn', 'value': 'XN-FAN-001-R'}},

                           {'FAN6 SN': {'id': 'fan6sn', 'value': '2052Q-41276'}},
                           {'FAN6 PN': {'id': 'fan6pn', 'value': 'XN-FAN-001-R'}},

                           {'PSU1 SN': {'id': 'psu1sn', 'value': 'L2571500JF06P'}},
                           {'PSU1 PN': {'id': 'psu1pn', 'value': 'XN-ACPWR-750W-R'}},

                           {'PSU2 SN': {'id': 'psu2sn', 'value': 'L2571500K306P'}},
                           {'PSU2 PN': {'id': 'psu2pn', 'value': 'XN-ACPWR-750W-R'}}
                    ],

            #Map Reporting to ASBF tags
            'AsBuiltFeedMap' : {
                            'top_pn' : 'chassis_pn',
                            'top_sn' : 'chassis_sn',
                            'swversion' : 'swversion',
                            'components': [ { 'item': 'fan', 'component_sn' : "scanlist['fan1sn']",
                                                             'component_pn' : "scanlist['fan1pn']"
                                              },
                                              { 'item': 'fan', 'component_sn' : "scanlist['fan2sn']",
                                                             'component_pn' : "scanlist['fan2pn']"
                                              },

                                             { 'item': 'fan', 'component_sn' : "scanlist['fan3sn']",
                                                             'component_pn' : "scanlist['fan3pn']"
                                              },

                                            {'item'        : 'fan', 'component_sn': "scanlist['fan4sn']",
                                             'component_pn': "scanlist['fan4pn']"
                                             },

                                            {'item'        : 'fan', 'component_sn': "scanlist['fan5sn']",
                                             'component_pn': "scanlist['fan5pn']"
                                             },

                                            {'item'        : 'fan', 'component_sn': "scanlist['fan6sn']",
                                             'component_pn': "scanlist['fan6pn']"
                                             },

                                            {'item'        : 'psu', 'component_sn': "scanlist['psu1sn']",
                                             'component_pn': "scanlist['psu1pn']"
                                             },

                                            {'item'        : 'psu', 'component_sn': "scanlist['psu2sn']",
                                             'component_pn': "scanlist['psu2pn']"
                                             }
                                            ]
                    }
    }




slx8720dcrparseobj = ParseEngine(key='swversion', regex='Firmware.name:(.*)', expect=['20.2.3a', '20.2.1'])
slx8720dcrparseobj.addparser(key='chassis_pn', regex='Factory.Part.Num:(.*)')
slx8720dcrparseobj.addparser(key='chassis_sn', regex='Factory.Serial.Num:(.*)', expect="scanned.chassis_sn")
#slx8720fparseobj.addparser(key='chassis_sn', regex='Factory.Serial.Num:(.*)')
slx8720dcrparseobj.addparser(key='chassis_type', regex='Chassis.Name:(.*)')
slx8720dcrparseobj.addparser(key='psu_id', regex='ID:(.*)')
slx8720dcrparseobj.addparser(key='psu_pn', regex='Part.Num:(.*)')
slx8720dcrparseobj.addparser(key='psu_sn', regex='Serial.Num:(.*)')
slx8720dcrparseobj.addparser(key='psu_type', regex='AirFlow:(.*)', expect='Port Side Intake,Type:DC')
#slx8720fparseobj.addparser(key='psu_type', regex='AirFlow:(.*)', expect='Port Side Exhaust')
slx8720dcrparseobj.addparser(key='mac', regex='Burned.In.MAC.*:.(..:..:..:..:..:..)')

slx8720dcrparseobj.addparser(key='fan1status', regex='Fan.1.is.(.*), speed', expect="Ok")
slx8720dcrparseobj.addparser(key='fan2status', regex='Fan.2.is.(.*), speed', expect="Ok")
slx8720dcrparseobj.addparser(key='fan3status', regex='Fan.3.is.(.*), speed', expect="Ok")
slx8720dcrparseobj.addparser(key='fan4status', regex='Fan.4.is.(.*), speed', expect="Ok")
slx8720dcrparseobj.addparser(key='fan5status', regex='Fan.5.is.(.*), speed', expect="Ok")
slx8720dcrparseobj.addparser(key='fan6status', regex='Fan.6.is.(.*), speed', expect="Ok")

slx8720dcrparseobj.addparser(key='PSU1GOOD', regex='Power.Supply.#1.is(.*)', expect="OK")
slx8720dcrparseobj.addparser(key='PSU2GOOD', regex='Power.Supply.#2.is(.*)', expect="OK")
slx8720dcrparseobj.addparser(key='tpmstatus', regex='TPM.Provision.status.:(.*)', expect="Provisioned")


CommandSequence['8720-32C-DC-R']  = \
    {
            'about' : {'image' : 'SLX9150-48XT-8C.png', 'text' : 'SLX 8720-32C-AC-F has 32x100G Copper ports and '
                                                                 '8xQSFP28'},
            'commandset': [
                    {'cmd': "\n\n", 'prompt': ["SLX.*login"], 'timeout': 10,
                        'usermsg' : {'text' : 'Please ensure that unit is powered on', 'image' : None}},
                    {'cmd': "\n", 'prompt': ["SLX.*login"], 'timeout': 10,
                     'usermsg' : {'text' : 'Please ensure that unit is powered on', 'image' : None}},
                    {'cmd': "admin\n", 'prompt': ["Password:"], 'timeout': 10},
                    {'cmd': "password\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "term len 0\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "dhcp ztp cancel\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show version\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show env power\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show env fan\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show chassis\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show system\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show tpm ekcert\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show tpm iakcert\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show tpm idevidcert\n", 'prompt': ["SLX.*#"], 'timeout': 10},

                    {'cmd': "start-shell\n", 'prompt': ["admin.*SLX.*#"], 'timeout': 10},
                    {'cmd': "\n", 'prompt': ["admin.*SLX.*#"], 'timeout': 10},
                    {'cmd': "dmesg\n", 'prompt': ["admin.*SLX.*#"], 'timeout': 60},
                    {'cmd': "exit\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show system\n", 'prompt': ["SLX.*#"], 'timeout': 10},

                    {'cmd': "write erase\n", 'prompt': ["SLX.*login"], 'timeout': 10},
                    #{'cmd': "reload\n", 'prompt': ["n.*yes"], 'timeout': 2},
                    {'cmd': "y\n", 'prompt': ["System.*initialization.*complete"], 'timeout': 120}

                    #{'cmd': "\n", 'prompt': ["SLX.*login"], 'timeout': 10},
                    #{'cmd': "admin\n", 'prompt': ["Password:"], 'timeout': 10},
                    #{'cmd': "password\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    #{'cmd': "term len 0\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    #{'cmd': "show system\n", 'prompt': ["SLX.*#"], 'timeout': 10}
                    ] ,
            'parseobj' : slx8720dcrparseobj,
            'scanlist' : [
                {'Console' : { 'id' : 'iconsole', 'value' : '127.0.0.1:5008', 'telnet' : True }},
                           {'CHASSIS SN' : { 'id' : 'chassis_sn', 'value' : 'TH01205Q-40040', 'SerialNumber' : True}},

                           {'FAN1 SN' : { 'id' : 'fan1sn', 'value' : '2052Q-41271' }},
                           {'FAN1 PN' : { 'id' : 'fan1pn', 'value' : 'XN-FAN-001-R'}},

                           {'FAN2 SN' : { 'id' : 'fan2sn', 'value' : '2052Q-41272' }},
                           {'FAN2 PN' : { 'id' : 'fan2pn', 'value' : 'XN-FAN-001-R'}},

                           {'FAN3 SN' : { 'id' : 'fan3sn', 'value' : '2052Q-41273' }},
                           {'FAN3 PN' : { 'id' : 'fan3pn', 'value' : 'XN-FAN-001-R'}},

                           {'FAN4 SN': {'id': 'fan4sn', 'value': '2052Q-41274'}},
                           {'FAN4 PN': {'id': 'fan4pn', 'value': 'XN-FAN-001-R'}},

                           {'FAN5 SN': {'id': 'fan5sn', 'value': '2052Q-41275'}},
                           {'FAN5 PN': {'id': 'fan5pn', 'value': 'XN-FAN-001-R'}},

                           {'FAN6 SN': {'id': 'fan6sn', 'value': '2052Q-41276'}},
                           {'FAN6 PN': {'id': 'fan6pn', 'value': 'XN-FAN-001-R'}},

                           {'PSU1 SN': {'id': 'psu1sn', 'value': 'L2571500JF06P'}},
                           {'PSU1 PN': {'id': 'psu1pn', 'value': 'XN-DCPWR-750W-R'}},

                           {'PSU2 SN': {'id': 'psu2sn', 'value': 'L2571500K306P'}},
                           {'PSU2 PN': {'id': 'psu2pn', 'value': 'XN-DCPWR-750W-R'}}
                    ],

            #Map Reporting to ASBF tags
            'AsBuiltFeedMap' : {
                            'top_pn' : 'chassis_pn',
                            'top_sn' : 'chassis_sn',
                            'swversion' : 'swversion',
                            'components': [ { 'item': 'fan', 'component_sn' : "scanlist['fan1sn']",
                                                             'component_pn' : "scanlist['fan1pn']"
                                              },
                                              { 'item': 'fan', 'component_sn' : "scanlist['fan2sn']",
                                                             'component_pn' : "scanlist['fan2pn']"
                                              },

                                             { 'item': 'fan', 'component_sn' : "scanlist['fan3sn']",
                                                             'component_pn' : "scanlist['fan3pn']"
                                              },

                                            {'item'        : 'fan', 'component_sn': "scanlist['fan4sn']",
                                             'component_pn': "scanlist['fan4pn']"
                                             },

                                            {'item'        : 'fan', 'component_sn': "scanlist['fan5sn']",
                                             'component_pn': "scanlist['fan5pn']"
                                             },

                                            {'item'        : 'fan', 'component_sn': "scanlist['fan6sn']",
                                             'component_pn': "scanlist['fan6pn']"
                                             },

                                            {'item'        : 'psu', 'component_sn': "scanlist['psu1sn']",
                                             'component_pn': "scanlist['psu1pn']"
                                             },

                                            {'item'        : 'psu', 'component_sn': "scanlist['psu2sn']",
                                             'component_pn': "scanlist['psu2pn']"
                                             }
                                            ]
                    }
    }



slx8720dcfrparseobj = ParseEngine(key='swversion', regex='Firmware.name:(.*)',
                                  expect=['20.2.3a', 'slxos20.2.3d_210424_1800'])
slx8720dcfrparseobj.addparser(key='chassis_pn', regex='Factory.Part.Num:(.*)')
slx8720dcfrparseobj.addparser(key='chassis_sn', regex='Factory.Serial.Num:(.*)', expect="scanned.chassis_sn")
#slx8720fparseobj.addparser(key='chassis_sn', regex='Factory.Serial.Num:(.*)')
slx8720dcfrparseobj.addparser(key='chassis_type', regex='Chassis.Name:(.*)')
slx8720dcfrparseobj.addparser(key='psu_id', regex='ID:(.*)')
slx8720dcfrparseobj.addparser(key='psu_pn', regex='Part.Num:(.*)')
slx8720dcfrparseobj.addparser(key='psu_sn', regex='Serial.Num:(.*)')
slx8720dcfrparseobj.addparser(key='psu_type', regex='AirFlow:(.*)', expect='Port Side Exhaust,Type:DC')
#slx8720fparseobj.addparser(key='psu_type', regex='AirFlow:(.*)', expect='Port Side Exhaust')
slx8720dcfrparseobj.addparser(key='mac', regex='Burned.In.MAC.*:.(..:..:..:..:..:..)')

slx8720dcfrparseobj.addparser(key='fan1status', regex='Fan.1.is.(.*), speed', expect="Ok")
slx8720dcfrparseobj.addparser(key='fan2status', regex='Fan.2.is.(.*), speed', expect="Ok")
slx8720dcfrparseobj.addparser(key='fan3status', regex='Fan.3.is.(.*), speed', expect="Ok")
slx8720dcfrparseobj.addparser(key='fan4status', regex='Fan.4.is.(.*), speed', expect="Ok")
slx8720dcfrparseobj.addparser(key='fan5status', regex='Fan.5.is.(.*), speed', expect="Ok")
slx8720dcfrparseobj.addparser(key='fan6status', regex='Fan.6.is.(.*), speed', expect="Ok")

slx8720dcfrparseobj.addparser(key='PSU1GOOD', regex='Power.Supply.#1.is(.*)', expect="OK")
slx8720dcfrparseobj.addparser(key='PSU2GOOD', regex='Power.Supply.#2.is(.*)', expect="OK")
slx8720dcfrparseobj.addparser(key='tpmstatus', regex='TPM.Provision.status.:(.*)', expect="Provisioned")


CommandSequence['8720-32C-DC-F']  = \
    {
            'about' : {'image' : 'SLX9150-48XT-8C.png', 'text' : 'SLX 8720-32C-AC-F has 32x100G Copper ports and '
                                                                 '8xQSFP28'},
            'commandset': [
                    {'cmd': "\n\n", 'prompt': ["SLX.*login"], 'timeout': 10,
                        'usermsg' : {'text' : 'Please ensure that unit is powered on', 'image' : None}},
                    {'cmd': "\n", 'prompt': ["SLX.*login"], 'timeout': 10,
                     'usermsg' : {'text' : 'Please ensure that unit is powered on', 'image' : None}},
                    {'cmd': "admin\n", 'prompt': ["Password:"], 'timeout': 10},
                    {'cmd': "password\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "term len 0\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "dhcp ztp cancel\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show version\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show env power\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show env fan\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show chassis\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show system\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show tpm ekcert\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show tpm iakcert\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show tpm idevidcert\n", 'prompt': ["SLX.*#"], 'timeout': 10},

                    {'cmd': "start-shell\n", 'prompt': ["admin.*SLX.*#"], 'timeout': 10},
                    {'cmd': "\n", 'prompt': ["admin.*SLX.*#"], 'timeout': 10},
                    {'cmd': "dmesg\n", 'prompt': ["admin.*SLX.*#"], 'timeout': 60},
                    {'cmd': "exit\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show system\n", 'prompt': ["SLX.*#"], 'timeout': 10},

                    {'cmd': "write erase\n", 'prompt': ["SLX.*login"], 'timeout': 10},
                    #{'cmd': "reload\n", 'prompt': ["n.*yes"], 'timeout': 2},
                    {'cmd': "y\n", 'prompt': ["System.*initialization.*complete"], 'timeout': 120}

                    #{'cmd': "\n", 'prompt': ["SLX.*login"], 'timeout': 10},
                    #{'cmd': "admin\n", 'prompt': ["Password:"], 'timeout': 10},
                    #{'cmd': "password\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    #{'cmd': "term len 0\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    #{'cmd': "show system\n", 'prompt': ["SLX.*#"], 'timeout': 10}
                    ] ,
            'parseobj' : slx8720dcfrparseobj,
            'scanlist' : [
                {'Console' : { 'id' : 'iconsole', 'value' : '127.0.0.1:5008', 'telnet' : True }},
                           {'CHASSIS SN' : { 'id' : 'chassis_sn', 'value' : 'TH01205Q-40040', 'SerialNumber' : True}},

                           {'FAN1 SN' : { 'id' : 'fan1sn', 'value' : '2052Q-41271' }},
                           {'FAN1 PN' : { 'id' : 'fan1pn', 'value' : 'XN-FAN-001-R'}},

                           {'FAN2 SN' : { 'id' : 'fan2sn', 'value' : '2052Q-41272' }},
                           {'FAN2 PN' : { 'id' : 'fan2pn', 'value' : 'XN-FAN-001-R'}},

                           {'FAN3 SN' : { 'id' : 'fan3sn', 'value' : '2052Q-41273' }},
                           {'FAN3 PN' : { 'id' : 'fan3pn', 'value' : 'XN-FAN-001-R'}},

                           {'FAN4 SN': {'id': 'fan4sn', 'value': '2052Q-41274'}},
                           {'FAN4 PN': {'id': 'fan4pn', 'value': 'XN-FAN-001-R'}},

                           {'FAN5 SN': {'id': 'fan5sn', 'value': '2052Q-41275'}},
                           {'FAN5 PN': {'id': 'fan5pn', 'value': 'XN-FAN-001-R'}},

                           {'FAN6 SN': {'id': 'fan6sn', 'value': '2052Q-41276'}},
                           {'FAN6 PN': {'id': 'fan6pn', 'value': 'XN-FAN-001-R'}},

                           {'PSU1 SN': {'id': 'psu1sn', 'value': 'L2571500JF06P'}},
                           {'PSU1 PN': {'id': 'psu1pn', 'value': 'XN-DCPWR-750W-R'}},

                           {'PSU2 SN': {'id': 'psu2sn', 'value': 'L2571500K306P'}},
                           {'PSU2 PN': {'id': 'psu2pn', 'value': 'XN-DCPWR-750W-R'}}
                    ],

            #Map Reporting to ASBF tags
            'AsBuiltFeedMap' : {
                            'top_pn' : 'chassis_pn',
                            'top_sn' : 'chassis_sn',
                            'swversion' : 'swversion',
                            'components': [ { 'item': 'fan', 'component_sn' : "scanlist['fan1sn']",
                                                             'component_pn' : "scanlist['fan1pn']"
                                              },
                                              { 'item': 'fan', 'component_sn' : "scanlist['fan2sn']",
                                                             'component_pn' : "scanlist['fan2pn']"
                                              },

                                             { 'item': 'fan', 'component_sn' : "scanlist['fan3sn']",
                                                             'component_pn' : "scanlist['fan3pn']"
                                              },

                                            {'item'        : 'fan', 'component_sn': "scanlist['fan4sn']",
                                             'component_pn': "scanlist['fan4pn']"
                                             },

                                            {'item'        : 'fan', 'component_sn': "scanlist['fan5sn']",
                                             'component_pn': "scanlist['fan5pn']"
                                             },

                                            {'item'        : 'fan', 'component_sn': "scanlist['fan6sn']",
                                             'component_pn': "scanlist['fan6pn']"
                                             },

                                            {'item'        : 'psu', 'component_sn': "scanlist['psu1sn']",
                                             'component_pn': "scanlist['psu1pn']"
                                             },

                                            {'item'        : 'psu', 'component_sn': "scanlist['psu2sn']",
                                             'component_pn': "scanlist['psu2pn']"
                                             }
                                            ]
                    }
    }



slx8720xparseobj = ParseEngine(key='osversion', regex='Firmware.name:(.*)')
slx8720xparseobj.addparser(key='chassis_pn', regex='Factory.Part.Num:(.*)')
slx8720xparseobj.addparser(key='chassis_sn', regex='Factory.Serial.Num:(.*)', expect="scanned.chassis_sn")
#slx8720xparseobj.addparser(key='chassis_sn', regex='Factory.Serial.Num:(.*)')
slx8720xparseobj.addparser(key='chassis_type', regex='Chassis.Name:(.*)')
slx8720xparseobj.addparser(key='psu_id', regex='ID:(.*)')
slx8720xparseobj.addparser(key='psu_pn', regex='Part.Num:(.*)')
slx8720xparseobj.addparser(key='psu_sn', regex='Serial.Num:(.*)')
#slx8720xparseobj.addparser(key='psu_type', regex='AirFlow:(.*)', expect='Intake')
slx8720xparseobj.addparser(key='psu_type', regex='AirFlow:(.*)')
slx8720xparseobj.addparser(key='mac', regex='Burned.In.MAC.*:.(..:..:..:..:..:..)')
slx8720xparseobj.addparser(key='fan1speed', regex='Fan.1.*is.(.*).RPM')
slx8720xparseobj.addparser(key='fan2speed', regex='Fan.2.*is.(.*).RPM')
slx8720xparseobj.addparser(key='fan3speed', regex='Fan.3.*is.(.*).RPM')
slx8720xparseobj.addparser(key='fan4speed', regex='Fan.4.*is.(.*).RPM')
slx8720xparseobj.addparser(key='fan5speed', regex='Fan.5.*is.(.*).RPM')
slx8720xparseobj.addparser(key='fan6speed', regex='Fan.6.*is.(.*).RPM')
slx8720xparseobj.addparser(key='PSU1GOOD', regex='Power.Supply.#1.is(.*)', expect="OK")
slx8720xparseobj.addparser(key='PSU2GOOD', regex='Power.Supply.#2.is(.*)', expect="OK")
slx8720xparseobj.addparser(key='tpmstatus', regex='TPM.Provision.status.:(.*)', expect="Provisioned")


CommandSequence['8720-32C']  = \
    {
            'about' : {'image' : 'SLX9150-48XT-8C.png', 'text' : 'SLX 8720-32C has 32x100G Copper ports and '
                                                                 '8xQSFP28'},
            'commandset': [
                    {'cmd': "\n\n", 'prompt': ["SLX.*login"], 'timeout': 10,
                        'usermsg' : {'text' : 'Please ensure that unit is powered on', 'image' : None}},
                    {'cmd': "\n", 'prompt': ["SLX.*login"], 'timeout': 10,
                     'usermsg' : {'text' : 'Please ensure that unit is powered on', 'image' : None}},
                    {'cmd': "admin\n", 'prompt': ["Password:"], 'timeout': 10},
                    {'cmd': "password\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "term len 0\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "dhcp ztp cancel\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show version\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show env power\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show env fan\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show chassis\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show system\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show tpm ekcert\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show tpm iakcert\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "show tpm idevidcert\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "start-shell\n", 'prompt': ["admin.*SLX.*#"], 'timeout': 10},
                    {'cmd': "\n", 'prompt': ["admin.*SLX.*#"], 'timeout': 10},
                    {'cmd': "dmesg | grep -i eth \n", 'prompt': ["admin.*SLX.*#"], 'timeout': 60},
                    {'cmd': "exit\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    {'cmd': "term len 0\n", 'prompt': ["SLX.*#"], 'timeout': 10},

                    {'cmd': "show system\n", 'prompt': ["SLX.*#"], 'timeout': 5},
                    {'cmd': "write erase\n", 'prompt': ["SLX.*#"], 'timeout': 5},
                    {'cmd': "y\n", 'prompt': ["Finished.*"], 'timeout': 60}
                    #{'cmd': "\n", 'prompt': ["SLX.*login"], 'timeout': 10},
                    #{'cmd': "admin\n", 'prompt': ["Password:"], 'timeout': 10},
                    #{'cmd': "password\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    #{'cmd': "term len 0\n", 'prompt': ["SLX.*#"], 'timeout': 10},
                    #{'cmd': "show system\n", 'prompt': ["SLX.*#"], 'timeout': 10}
                    ] ,
            'parseobj' : slx8720xparseobj,
            'scanlist' : [
                {'Console' : { 'id' : 'iconsole', 'value' : '127.0.0.1:5008', 'telnet' : True }},
                           {'CHASSIS SN' : { 'id' : 'chassis_sn', 'value' : 'TH01205Q-40040', 'SerialNumber' : True}}

                    ],

            #Map Reporting to ASBF tags
            'AsBuiltFeedMap' : {
                            'top_pn' : 'chassis_pn',
                            'top_sn' : 'chassis_sn',
                            'swversion' : 'osversion',
                            'components': [ ]
                    }
    }



