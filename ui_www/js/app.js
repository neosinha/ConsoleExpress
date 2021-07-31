
var serverLocation = location.host; 
var server = "http://" + serverLocation ;
console.log("Location: "+ server);

var views = new Views();
var websx = new WebServices();

var appModel = {};
appModel['products']    = null;
appModel['movetable']   = null;
appModel['inspections'] = null;
var serialList = new Array();


/*Fireoff Backend Requests*/
/*websx.getmovetable();
websx.requestproducts();
websx.requestinspections();
*/

function appInit() {
    console.log("BackEndModel: "+ JSON.stringify(appModel['movetable']) );
    console.log("BackEndModel: "+ JSON.stringify(appModel['products']) );
    console.log("BackEndModel: "+ JSON.stringify(appModel['inspections']) );
    appModel['serials'] = new Array();
    viewsInit();
}

function appLoad() {
    console.log("===App Load ==");
    views.showProg();
    websx.requestbackenddata();
}

function viewsInit() {
    mqttInit();

	views.appNavBar();
	loadLandingView();
	updatePerSecond();

	 //views.startupView();
	//views.consolearea();
    //views.updateMoveTable();

     // SmartWizard initialize
    /*$('#oobawizard').smartWizard(
            {   justified: true, // Nav menu justification. true/false
                 darkMode:false
            }
    );*/


}


var serialnum = null; 
var clock;


function scanView() {
}

function updateClock() {
	var dt = new Date();
	$('#clock').html( dt.toLocaleString()); 
}

function updatePerSecond() {
	updateClock();
	updateConsoleClocks();
	setTimeout(updatePerSecond, 1000);
}

function updateConsoleClocks() {
    console.log('ConsoleClocks: '+ JSON.stringify(serialList) );
    for (idx=0; idx < serialList.length; idx++) {
        var sr = serialList[idx];
        var clkel = document.getElementById('clock-'+sr);
        if (consoleClocks[sr]) {
            var dtnow = new Date();
            var st = consoleClocks[sr]['start'];
            var elapsedTime = dtnow.getTime() - consoleClocks[sr]['start'] ;
            var elapsedTime = Math.floor(elapsedTime/1000);

            var hh = Math.floor(elapsedTime / 3600);
            elapsedTime %= 3600;
            var mm = Math.floor(elapsedTime / 60);
            var ss = elapsedTime % 60;

            mm = String(mm).padStart(2, "0");
            hh = String(hh).padStart(2, "0");
            ss = String(ss).padStart(2, "0");

            clkel.innerHTML = hh + ':'+ mm + ':' + ss;
            //clkel.innerHTML = new Date(elapsedTime).toISOString().substr(11, 8);
        }

    }
}


function loadLandingView() {
		
		var h1x = ui.h3(null, '', [{'name' : 'class', 'value' : 'mainlogo text-center' }]);
		var jum = ui.jumbotron('view1', h1x,' bg-basic'); 
		

        var crow = ui.createElement('div', 'dashbrd');
        //var brow = ui.addRowCol('buttonrow', 1);
        var tabs = views.tabview();


		var resultarea = ui.createElement('div', 'results');
		var notifyarea = ui.createElement('div', 'notify');
		

        //jum.appendChild(crow);
        //jum.appendChild(brow);
		//jum.appendChild(resultarea);
		
		//jum.appendChild(xmlarea);
		//jum.appendChild(notifyarea);

		var wz = views.testView();
		
		//ui.addSubViewToMain([wz, tabs, resultarea, notifyarea]);
		//jum.appendChild(tabs);
		var pr = ui.createElement('br', 'firstrow');
		//ui.addSubViewToMain([jum, resultarea, notifyarea]);
		ui.addSubViewToMain([pr, tabs, resultarea, notifyarea]);

		$('#modalheader').html(''); 
		$('#modalbody').html('uuuu'); 
		$('#modalfooter').html(''); 
		
}


function updateConsole(snum, msgStr) {
    views.updateConsole(snum, msgStr);
}




function progressModal() {

 var mcnt = document.getElementById('modalcontent');
    mcnt.innerHTML = '';
    var img = ui.createElement('img', 'pcontent');
    img.setAttribute('src', 'img/file_uploading.gif');
    img.setAttribute('class', 'imcenter');

    //mcnt.appendChild(img);
}

function addNotification(alertType, msg) {
    removeNotification();
    var msg = ui.createNotification(alertType, msg);
    var notify = document.getElementById('notify');
    notify.appendChild(msg);
}

function removeNotification() {
    var notify = document.getElementById('notify');
    notify.innerHTML = '';
}






var systemModel = null; 
var networkObj = null; 

function getsystem_callback(respx) {
	console.log(respx);
	systemModel = JSON.parse(respx); 
	networkObj = systemModel['network'];
	
	drawView();
	
}


