
from BExpress.AutomationSequence import ParseEngine


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

