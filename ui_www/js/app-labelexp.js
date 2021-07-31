
var serverLocation = location.host; 
var server = "http://" + serverLocation ;
console.log("Location: "+ server); 


function appInit() {
	appNavBar();
	loadLandingView(); 
	updatePerSecond();
	//fileUploadRow();
	addImageCol();
	addButtonCol();
	//initUpload();
}

var serialnum = null; 
var clock;


function updateClock() {
	var dt = new Date();
	$('#clock').html( dt.toLocaleString()); 
}

function updatePerSecond() {
	updateClock();
	setTimeout(updatePerSecond, 1000);
}


function loadLandingView() {
		
		var h1x = ui.h3(null, '', [{'name' : 'class', 'value' : 'mainlogo text-center' }]);
		var jum = ui.jumbotron('view1', h1x,' bg-basic'); 
		
        var crow = ui.addRowCol('control', 1);
        var brow = ui.addRowCol('onrow', 1);


		var resultarea = ui.createElement('div', 'results');
		var notifyarea = ui.createElement('div', 'notify');
		

        jum.appendChild(crow);
        jum.appendChild(brow);
		jum.appendChild(resultarea);
		
		//jum.appendChild(xmlarea);
		jum.appendChild(notifyarea);
		
		ui.addSubViewToMain([jum]);
		
		$('#modalheader').html(''); 
		$('#modalbody').html('uuuu'); 
		$('#modalfooter').html(''); 
		
}



