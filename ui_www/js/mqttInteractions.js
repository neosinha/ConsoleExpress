
var mqtt = null;
var mserver = '23.94.247.117:9083';
var mqttServer = mserver.split(':')[0];
var mqttPort = mserver.split(':')[1];
function mqttInit() {
	console.log("Initializing MQTT Server ("+mqttServer+", " +mqttPort);
	
	mqtt = new Paho.MQTT.Client(mqttServer, Number(mqttPort), '',
							'cl'+getEpoch() ); 
	
	mqtt.onMessageArrived = mqttOnMessage;
	mqtt.onConnectionLost = mqttConnectionLost;
	mqttConnect();
	
}

function mqttConnect() {
	var options = { timeout: 300,
	        userName: 'apiuser',
            password: 'millionchamps',
			onSuccess: onConnect, 
			onFailure: mqttFailure 
			};
	mqtt.connect(options); 
}

function mqttConnectionLost(response){
	console.log(getEpoch()+": Connection lost");
    console.log(response.errorMessage);
	setTimeout(mqttConnect, 10);
}

function getEpoch() {
	var ts = new Date();
	var tss = ts.getTime();
	return tss;
}


function onConnect() {
	var topics = ['bexp/cmd', 'console1/console' ];
	for (idx = 0; idx < topics.length; idx++) {
		mqtt.subscribe(topics[idx]);
		console.log("Subscribed: "+ topics[idx] );
	}
}



function subscribeChannel(channelid) {
    var chatterids = ['console', 'status', 'command'];

    if (mqtt != null) {
        for (i=0; i < chatterids.length; i++) {
            var tpx = channelid + '/'+chatterids[i];
            mqtt.subscribe(tpx);
            console.log('Subscribed to channel '+ tpx);
        }
    }
}

function mqttOnMessage(msg){
	var msgstr = msg.payloadString;

	console.log(msg.destinationName +' == ' + msgstr );
	var status = JSON.parse(msgstr);

	if (msg.destinationName === 'console1/console') {
		//updateSystemStats(status);
		console.log("BEX: "+ msg/str);
		updateConsole(msgstr);
	}
    console.log('Update Serial# '+ msgstr);
    //if (serial != null) {
    var serial = null;

	if (msg.destinationName.includes('console')) {
	        //updateSystemStats(status);
	        serial =msg.destinationName.split('/')[0] ;
	        //console.log('Console: '+ serial);
	        //console.log("Console, SN#: "+ serial + ' =='+ msgstr);
		    updateConsole(serial, msgstr);
	    }



    var end = false;

	if (msg.destinationName.includes('status')) {
		    //updateSystemStats(status);
		    serial =msg.destinationName.split('/')[0] ;
	        console.log('Console: '+ serial);
	        console.log("Console, SN#: "+ serial + ' =='+ msgstr);

		    console.log("SN Status#: "+ serial  + ' =='+ msgstr);
		    //updateConsole(msgstr);
		    if (status['status'] == 'RESET') {
		        views.resetView(serial);
		    }

		    if (status['status'] == 'PASSED') {
		        views.passView(serial);
		        end = true;
		    }


		    if (status['status'] == 'NOTFOUND') {
		        views.errorView(serial, status['msg']);
		        end = true;
		    }

		    if (status['status'] == 'FAILED') {
		        views.errorView(serial, status['msg']);
		        end = true;
		    }

            if (end) {
		        var ridx = serialList.indexOf(serial);
		        //console.log('UpdatedSNList: '+JSON.stringify(serialList) + '--' + ridx);
		        serialList.splice(ridx, 1);
		        //console.log('UpdatedSNList: '+JSON.stringify(serialList));
		        //websx.requestlogtable();
		    }
	    }

    //}

	
}


function sendCmd(cmd) {
	console.log("Publishing: "+ cmd);
	mqtt.send(topic="trex/cmd", payload=cmd, qos=0);
}


function mqttFailure() {
	console.log("MQTT Connection failed..("+mqttServer+','+ mqttPort+')');
	
}
