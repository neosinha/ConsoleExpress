
var serverLocation = location.host;
var server = "http://" + serverLocation ;
console.log("Location: "+ server);

var movetable = null;


var WebServices = function () {

    this.requestbaudservice = function(scanformdata, sku) {
          var snum = scanformdata['SerialNumber'];
          var console = scanformdata['iconsole'];
          //
          //alert('BaudExp SUbmit: '+ JSON.stringify(scanformdata)+'\n'+snum );
          $.ajax( {url : server+'/baudoperation',
                  sync: false,
                  method: "POST",
                  data : {'serialnumber': snum ,
                          'partnumber' : sku,
                          'console' : console,
                          'scandata' : JSON.stringify(scanformdata),
                          },
                  success: this.baudoperation
                  } );
    }

    this.requestbackenddata = function() {
          $.ajax( {url : server+'/getbackenddata',
                  sync: false,
                  method: "POST",
                  success: (function(msg) {
                            console.log('BackendData: '+ msg);
                            appModel = JSON.parse(msg);
                            views.hideProg();
                            viewsInit();
                           })
                  } );
    };

    this.requestlogtable = function() {
          $.ajax( {url : server+'/getbackenddata',
                  sync: false,
                  method: "POST",
                  success: (function(msg) {
                            console.log('BackendData: '+ msg);
                            appModel = JSON.parse(msg);
                            views.updateLogTable();
                           })
                  } );
    };


    this.requestproducts = function() {

        $.ajax( {url : server+'/getproducts',
                  sync: false,
                  method: "POST",
                  success: (function(msg) {
                            console.log('ProductX: '+ msg);
                            appModel['products'] = JSON.parse(msg);
                           })
                  } );

    }


    this.requestinspections = function() {
        $.ajax( {url : server+'/getinspections',
                  sync: false,
                  method: "POST",
                  success: (function(msg) {
                            console.log('InspectionsX: '+ msg);
                            appModel['inspections'] = JSON.parse(msg);
                            views.hideProg();
                            appInit();
                           })
                  }
               );
    }

     this.requestscanlist = function(pnum, snum, movenum) {
          $.ajax( {url : server+'/getscanlist',
                  sync: true,
                  method: "POST",
                  data : {'partnumber': pnum},
                  success: this.scanlistcallback
                  } );
    }

    this.getmovetable = function() {
          $.ajax( {url : server+'/getmovetable',
                  sync: true,
                  method: "POST",
                  success: this.getmovetablecallback
                  });
    }

    this.getmovetablecallback = function(resp){
        //console.log("Movetable: "+ resp);
        movetable = JSON.parse(resp);
        appModel['movetable'] = JSON.parse(resp);

    }

    this.gettestlog = function (snum, starttime) {
         $.ajax( {url : server+'/gettestlog',
                  sync: true,
                  data : {'serialnum': snum, 'startdatetime' : starttime},
                  method: "POST",
                  success: views.loadtestlog
                  });
    }


    this.getsntable = function (snum) {
         $.ajax( {url : server+'/getlogsforserial',
                  sync: true,
                  data : {'serialnum': snum},
                  method: "POST",
                  success: views.loadtestlog
                  });
    }

    this.baudoperation = function(resp) {
        console.log('BaudOperReturn: '+ resp);
        var baudOper = JSON.parse(resp);

    }


    this.scanlistcallback = function(resp) {
        console.log('ScanList: '+ resp);
        var scanlist = JSON.parse(resp);
        views.scanPrompt(resp);

    }

    this.updateProductList = function() {
    }


} ;



