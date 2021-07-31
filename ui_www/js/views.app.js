// $Id$

// file holds the code which designs the UI views
// or bigger/composite UI view elements
var ui = new Bootstrap();

var serial = null;
var consoleClocks = {}

function triggerUnit() {
    var snum = $('#rserial').val();
    var cons = $('#rconsole').val();
    console.log('Kicking off: '+ snum + '/' + cons);

    serial = snum;
    if (appModel['serials'].includes(serial) ) {
    } else {
        appModel['serials'].push(serial);
    }
    subscribeChannel(snum);
    websx.requestbaudservice(snum, cons);
    var stat = document.getElementById('statusbtn');

    stat.innerHTML = 'Testing SN# '+ snum;
    var cls = stat.setAttribute('class', 'btn btn-block btn-warning');

}


var modalobj = null;
var productList = null ;


function triggerSerial (moveobjStr) {
    console.log("Trigger Serial: "+moveobjStr);
    var moveobj = JSON.parse(moveobjStr);
    //alert("Serial: "+ serial + "/Move: "+movenum + ' /Part: '+ partnum);
    modalobj = moveobj;
    serial = moveobj['SerialNumber'];

    var cons = '10.31.221.215:3010';
    subscribeChannel(serial);
    //websx.requestscanlist(partnum);
    views.scanPrompt();
    initScanBoxes();
}


function initScanBoxes() {

     var scanlist = modalobj['scanlist'];
     for (i=0; i < scanlist.length; i++) {
         var scanitem = scanlist[i];
         var key = Object.keys(scanitem);
         console.log("ScanItem: "+ key);
         var ibox = document.getElementById(scanitem[key]);
     }
}

function clearScanForm() {

     var scanlist = modalobj['scanlist'];
     for (i=0; i < scanlist.length; i++) {
         var scanitem = scanlist[i];
         var key = Object.keys(scanitem);
         var ibox = document.getElementById(scanitem[key]);
         ibox.value = '';
     }
}

function readScanForm(scanlistobj, sku) {
    //alert('Reading Scan Data');

    console.log('ReadScanForm: '+sku + '==='+ scanlistobj);

     //var scanlist = modalobj['scanlist'];
     var scanlist = JSON.parse(scanlistobj) ;

     //scanlist.push({'Console' : {'id' : 'iconsole'} });
     //scanlist.push({'SerialNumber' : {'id' : 'iserial'} });
     var incomp = new Array();

    var formdata = {};
    if (scanidobj != null) {
     var formdata = { 'SerialNumber' : modalobj['SerialNumber'],
                      'PartNumber' : modalobj['PartNumber'],
                      'SKU' : modalobj['SKU']} ;
    }

    var gserial = null;
     for (i=0; i < scanlist.length; i++) {
         var scanitem = scanlist[i];
         var scanidobj = Object.keys(scanitem);
         var scanid = scanitem[scanidobj]['id'];
         console.log("Reading ScanItem: "+ scanidobj+ '/Key: '+ scanid );

         var ibox = document.getElementById(scanid);
         ivalue = ibox.value ;
         if (ivalue === "") {
            incomp.push(scanid);
            ibox.value = 'INCOMPLETE';
         } else {
              formdata[scanid] = ivalue;
              scanitem[scanidobj]['value'] = ivalue;
              if (scanitem[scanidobj]['SerialNumber']) {
                if (serialList.includes(ivalue)) {
                    console.log('SN: '+ ivalue + ' is already in progress..');
                } else {
                   console.log('MQTT Channel: '+ ivalue);
                   subscribeChannel(ivalue);
                   serialList.push(ivalue);
                   gserial = ivalue;
                }
              }
         }

         console.log("Value, "+scanidobj + " ==" + scanitem['value']);
     }

     if (incomp.length > 0) {
        var ftr = document.getElementById('appmodalfooter');
        ftr.innerHTML = 'INCOMPLETE';
     } else {
        console.log('ScanData: '+ JSON.stringify(formdata) );
        closeScanModal();

        if (serial != null) {
            var stat = document.getElementById('statusbtn-'+serial);
            stat.innerHTML = 'Testing SN# '+ serial;
            stat.setAttribute('class', 'btn btn-block btn-warning');
        }


        console.log("Value ScanList: "+ JSON.stringify(scanlist) );
        console.log("Serials: "+ JSON.stringify(serialList) );
        views.consoleView(gserial);

        websx.requestbaudservice(scanlist, sku);

     }

}






function startTest() {
    var formdata = readScanForm();
    websx.requestbaudservice(serial, cons);
    var stat = document.getElementById('statusbtn-'+serial);
}


var Views = function() {

    this.showProg = function() {
        var prog = document.getElementById('progbody');
        //<img src="img/prog-linear.gif" class="img-rounded imcenter" >
        var img = document.createElement('img');
        img.setAttribute('src', 'img/prog-linear.gif');
        img.setAttribute('class', 'img-rounded imcenter');

        prog.innerHTML = '';
        prog.appendChild(img);

         $("#progress").modal("show");
    }

    this.hideProg = function() {
        var prog = document.getElementById('progress');
        $("#progress").modal("hide");
    }

    this.tabview = function() {

        var tabdefs = new Array();

        tabdefs.push({ 'name': '<span class="tabtitle">OOBA Test</span>',
                        'content' : this.testView() });

       tabdefs.push({ 'name': '<span class="tabtitle">OOBA Inspect</span>',
                    'content' : this.oobaInspect() });


        tabdefs.push({ 'name': '<span class="tabtitle">LogSearch</span>',
                        'content' : this.logTableView() });

         var tabsx = ui.navtabs('navtabs', 'justified', tabdefs);

         return tabsx;
    }

    this.oobaInspect = function() {
          var oo = ui.createElement('div', 'oobainspect');


          var plist = new Array();
          //createListGroupWithButtons = function(id, listFunction, listArr)
          var prodarr = appModel['products'];
          console.log("ProductList has "+ prodarr.length + ' elements.')
          for (ix=0; ix < prodarr.length; ix++) {

             var pname = prodarr[ix];
             console.log('Product'+ix+':'+ JSON.stringify(pname) );
             console.log("ProductName: "+ pname['product']);

             plist.push({'type' : 'basic', 'content' : pname['product'],
             'onclick' : 'views.inspectionStep(\''+ pname['product'] +'\', ' +ix+ ' );'} );

          }



          var prods = ui.createListGroupWithButtons('oobaprods', 'alert' , plist);
          var prodHead = ui.createElement('p', 'oobaviewlisthead');
          prodHead.setAttribute('class', 'prodhead');
          prodHead.innerHTML = 'Products';


          var rows = ui.addRowColContent('oobainspect', [ {'size' : 8, 'content' : '<h3>Inspection Steps</h3>' },
                                                          {'size' : 4, 'content' : [prodHead, prods]}
          ]);

          oo.appendChild(rows);


          return oo;
    }

    this.updateLogTable = function() {

            var ltbl = document.getElementById('logtablex-col0');
            //var lg = document.getElementById('logtabledata');
            //lg.remove();
            ltbl.innerHTML = '';

            ltbl.appendChild(this.logTableView());
    }

    this.logTableView = function() {
        var tbl = ui.createElement('div', 'logtabledata');

        //console.log("Updating LogTable");

        var hdr = ['Serial', 'Start Date' ,'Status'];
        var tbldata = [];
        var logs = appModel['logtable'];
        for (i=0; i < logs.length; i++) {
            var log = logs[i];
            //console.log("LogTable: "+JSON.stringify(log));
            var statx = 'success';
            if (log['status']['status'] == 'FAILED') {
                statx = 'fail-row';
            }
            var srnum = log['SerialNumber'];
            var sttime = log['startdatetime'];

            var dttime = log['startdatetime'].split('_');
            var dttimestr = dttime[0]+' '+dttime[1];

            var btn = ui.createElement('span', 'logclk'+srnum);
            btn.setAttribute('onclick', 'websx.gettestlog(\''+srnum+'\', \''+sttime+'\'); ');
            btn.innerHTML = log['SerialNumber'];

            tbldata.push([btn, dttimestr , log['status']['status'], statx]);
        }
        var stbl = ui.table ("logstatustable", 'table-bordered table-hover' ,hdr, tbldata);
        var inparr = [];

        inparr.push({'label' : 'SerialNumber:  ',
			    'type' : "text",
			    'name' : 'SerialNumber: ',
			    'id'   : 'searchserialnumber',
			    'value' : '',
			    'placeholder': '' } );

	    inparr.push({'label' : 'Submit: ',
			    'type' : "submit",
			    'name' : 'submit',
			    'id'   : 'submit-serialnumber',
			    'onclick' : 'alert("Submit: ");',
			    'placeholder': '' } );

        var inpbar = ui.buttonInputBar({'id': 'serialbox', 'type' : 'text', 'label' : 'SerialNumber: ',
                                         'value' : '1908Q-20179', 'placeholder' : '1908Q-20179',
                                         'button' : 'Search<span class="glyphicon glyphicon-search"></span>', 'onclick' : 'readSearchBox();'});
        var hform = ui.createInlineForm('logsrch', inparr);
        var hash = ui.hr();

        var rows = ui.addRowColContent('logtablex', [{'size' : 6, 'content' : [inpbar,hash, stbl] },
                                                    {'size' : 6, 'content' : '<p></p>' }
          ]);

        tbl.appendChild(rows);

        return tbl;

    }

    this.loadtestlog = function(resp) {
        var lgcol = document.getElementById('logtablex-col1');

        var cons = ui.createElement('div', 'logwell-100');
        cons.setAttribute('class', 'lgconsole');
        var conlines = JSON.parse(resp);
        var linex = '';
        lgcol.innerHTML = '';


        for (var h=0 ; h <conlines.length; h++) {
            var line = conlines[h];
            console.log('LogLine: '+line);
            linex = '<BR/>'+ line;
            cons.innerHTML += line + '<BR/>';
        }
        //cons.innerHTML = linex;
        lgcol.appendChild(cons);
    }


    this.moveTable = function() {
        var dvx = ui.createElement('div', 'movetable-div');
        var crow = ui.addRowCol('dashboard', 1);
        dvx.appendChild(crow);


        return dvx;
    }

    this.productlist = function() {
        var dvx = ui.createElement('div', 'prodtable-div');
        var crow = ui.addRowCol('productslist', 2);
        dvx.appendChild(crow);

        return dvx
    }


    this.consoleView = function(serialNum) {
            var con = document.getElementById('oobarow-col0');

            var dconv = document.getElementById('conswell-'+serialNum);
            if (dconv) {
                dconv.innerHTML = '';
                console.log('ConsoleExists: '+serialnum + ' exists, clearning up. ' );
            } else {
               var dconv = ui.createElement('div', 'conswell-'+serialNum);
               dconv.setAttribute('class', 'alert alert-info');

               //ac.setAttribute('data-dismiss', 'alert');
               //ac.setAttribute('aria-label', 'close');
               //ac.innerHTML = '&times;';

               //dconv.appendChild(ac);
               con.appendChild(dconv);
            }

            console.log('ConsoleView: '+ serialNum);
           // var drow = ui.addRowCols();

            var px = ui.createElement('p', 'serialhead-'+serialNum);
            px.setAttribute('class', 'serialhead');

            var spanx = ui.createElement('span', 'serialheadtxt-'+serialNum);
            spanx.setAttribute('class', 'pull-left');
            spanx.innerHTML = serialNum;
            px.appendChild(spanx);

            var spanx = ui.createElement('span', 'clock-'+serialNum);
            spanx.setAttribute('class', 'pull-right');
            spanx.innerHTML = 'ElaspsedTime';
            px.appendChild(spanx);

           /* var ac = ui.createElement('span', 'close-'+serialNum);
            ac.setAttribute('class', 'glyphicon glyphicon-remove');
            ac.setAttribute('onclick', 'views.closeConsole(\''+serialNum+'\'); ');
            spanx.appendChild(ac);
            */


            var conswell = ui.createElement('div', 'consolewell-'+serialNum);
            conswell.setAttribute('class', 'box effect1');

            var conx = ui.createElement('div', 'tconsolex-'+serialNum);
            conx.setAttribute('class', 'console tconsole');

            var consx = ui.createElement('div', 'conswell-'+serialNum);
            //var snpaneldefs = [ {'heading' : serialNum, 'content' : conx, 'type' : 'basic'} ];
            //var snpnx = ui.createPanels('panel-'+serialNum, snpaneldefs);
            dconv.appendChild(px);
            dconv.appendChild(conx);

            var dx = ui.createElement('div', 'status-'+serialNum);
            dx.setAttribute('class', 'console-status');
            dconv.appendChild(dx);

    }


    this.testView = function () {
         var wizdivx = ui.createElement('div', 'oobawizardx');
          wizdivx.setAttribute('class', 'wellx');

          //var rows = ui.addRowCols('oobarow', [8,4]);
          //var rows = ui.createElement('div', 'oobarow');
          //rows.setAttribute('class', 'row');

          var img = ui.createElement('img', 'bcodegif');
          img.setAttribute('src', 'img/qr-scan.gif');
          img.setAttribute('class', 'imcenter');
          wizdivx.appendChild(ui.br());
          //wizdivx.appendChild(rows);

          //wizdivx.appendChild(img);

          var scanitems = new Array();
          scanitems.push({'label' : 'SerialNumber',
			    'type' : "text",
			    'id'   : 'oobacode',
			    'value' : 'TH012040Q-40008',
			    'placeholder': 'TH012040Q-40008' } );

		  var snformx = ui.buttonInputBar({'id' : 'srnumbox', 'button' : 'StartTest', 'label' : 'SerialNumber',
		                                    'type' : 'text', 'placeholder' : 'TH012040Q-40008',
		                                    'value' : 'TH012040Q-40008',
		                                    'onclick' : 'alert(\"Inp Box\"); '});

          var plist = new Array();
          //createListGroupWithButtons = function(id, listFunction, listArr)
          var prodarr = appModel['products'];
          console.log("ProductList has "+ prodarr.length + ' elements.')

          for (ix=0; ix < prodarr.length; ix++) {

             var pname = prodarr[ix];
             console.log('Product'+ix+':'+ JSON.stringify(pname) );
             console.log("ProductName: "+ pname['product']);
             var btndiv = ui.createElement('div', 'proddriver'+ix);
             var btndefs = [
                                {'type' : 'default', 'onclick' : 'alert();', 'content' : 'Test' },
                                {'type' : 'default', 'onclick' : 'alert();', 'content' : 'OOBA' }
                            ];

             btndiv.appendChild(ui.buttonGroup('proddef'+ix, btndefs) );

             plist.push({'type' : 'basic', 'content' : pname['product'],
             'onclick' : 'views.scanPromptView(\''+ JSON.stringify(pname['scanlist']) + '\', \'' + pname['product']
             +'\');'} );

          }
          //var btnx = ui.dropdown('oobadropdown', 'danger', 'Product List', plist);
          console.log("PLIST: "+ plist.length);
          var rstDiv = ui.createElement('div', 'rstbtns');
          rstDiv.setAttribute('class','alert alert-danger');
          var rstBtn = ui.button('clearConsole', 'Clear Console', 'danger btn-lg btn-block', 'views.clearConsole(); ');
          var py = ui.createElement('p', 'hsep');
          rstDiv.appendChild(py);
          rstDiv.appendChild(rstBtn);

          var prods = ui.createListGroupWithButtons('oobaprods', 'alert' , plist);
          var prodHead = ui.createElement('p', 'prodlisthead');
          prodHead.setAttribute('class', 'prodhead');
          prodHead.innerHTML = 'Products';

          var rows = ui.addRowColContent('oobarow', [{'size' : 8, 'content' : '' },
                                                     {'size' : 4, 'content' : [prodHead, prods]}
          ]);

          wizdivx.appendChild(rows);

         return wizdivx;
    }


    this.getproductList = function() {
        var plist = new Array();
          //createListGroupWithButtons = function(id, listFunction, listArr)
          var prodarr = appModel['products'];
          console.log("ProductList has "+ prodarr.length + ' elements.')
          for (ix=0; ix < prodarr.length; ix++) {

             var pname = prodarr[ix];
             console.log('Product'+ix+':'+ JSON.stringify(pname) );
             console.log("ProductName: "+ pname['product']);

             plist.push({'type' : 'basic', 'content' : pname['product'],
             'onclick' : 'views.scanPromptView(\''+ JSON.stringify(pname['scanlist']) + '\', \'' + pname['product']
             +'\');'} );

          }

        return plist;
    }

    this.closeConsole = function(snum) {
        console.log("Clearing Consoles.. "+snum);
        var divx = document.getElementById('conswell-'+snum);
        if (divx){
            divx.remove();
        }

    }


    this.oobawizardView = function () {
        var wizdiv = ui.createElement('div', 'oobawizardx');
            var wizdivx = ui.createElement('div', 'oobawizard');
            var ulx = ui.createElement('ul', 'oobawizard-ul');
            ulx.setAttribute('class', 'nav');


            var tabc = ui.createElement('div', 'oobawizardtabs');
            tabc.setAttribute('class', 'tab-content');



            var steps = new Array();
            var tabs = new Array();

            steps.push({'header': 'STep1', 'content' : 'Step1 Content is described here'});
            steps.push({'header': 'STep2', 'content' : 'Step2 Content is described here'});
            steps.push({'header': 'STep3', 'content' : 'Step3 Content is described here'});

            for (i=0; i < steps.length; i++) {
                var step = steps[i];
                var dstep = ui.createElement('li', 'lstep'+i);
                var adstep = ui.createElement('a', 'tabstep'+i);
                adstep.setAttribute('class', 'nav-link');
                adstep.setAttribute('href', '#tabstep'+i);

                adstep.innerHTML = 'OOBA STEP'+i;
                dstep.appendChild(adstep);
                ulx.appendChild(dstep);

                var tabel = ui.createElement('div', 'tabstep'+i);
                tabel.setAttribute('class', 'tab-pane');
                tabel.setAttribute('role', 'tabpanel');
                tabel.innerHTML = 'OOBA STEP CONTENT' + i;
                tabc.appendChild(tabel);


            }
            wizdivx.appendChild(ulx);
            wizdivx.appendChild(tabc);

            wizdiv.appendChild(wizdivx);

        return wizdiv;
    }


    /*<h3>Keyboard</h3>
    <section>
        <p>Try the keyboard navigation by clicking arrow left or right!</p>
    </section>
    <h3>Effects</h3>
    <section>
        <p>Wonderful transition effects.</p>
    </section>
    <h3>Pager</h3>
    <section>
        <p>The next and previous buttons help you to navigate through your content.</p>
    </section>*/


    var ijobs = null;

    this.updateInspections = function(msg) {
        console.log('Update Inspections:' + msg);
        ijobs = JSON.parse(msg);

        //oobawizardx
        //oobarow-col0
        var prodlist = document.getElementById('oobarow-col0');
        var prodlist = document.getElementById('oobarow');
        //prodlist.innerHTML = '';



        var owiz = document.getElementById('oobarow');
        owiz.innerHTML = '';

        var plist = new Array();
        for (i=0; i < ijobs.length; i++) {
            var ijob  = ijobs[i];
            var pname = ijob['product'];
            if (ijob.hasOwnProperty('inspection')){
                var hx = ui.createElement('h3', 'hjob'+i);
                hx.innerHTML = '';
                var sec = ui.createElement('section', 'sect'+i);

                var btn = ui.createElement('button', 'oobaprod'+i);
                btn.innerHTML = pname;
                btn.setAttribute('class', 'btn btn-primary btn-block');
                btn.setAttribute('onclick', 'alert("'+pname+'"); ');

                //prodlist.appendChild(btn);
                plist.push({'title' : pname , 'onclick' : 'views.inspectionStep(\''+pname+'\','+i+' ); '});
                if (i==0) {
                    console.log("Log["+i+"]");
                }


            }
        }
        //dropdown = function(id, btntype, drarr)
        var btnx = ui.dropdown('oobadropdown', 'danger', 'Product List', plist);
        //prodlist.appendChild(btnx);


        owiz.appendChild(btnx);
        owiz.appendChild(ui.hr());

        var row2 = ui.createElement('div', 'oobarow-col1');
        //row2.setAttribute('class', 'row');
        owiz.appendChild(row2);

    }



    this.inspectionStep = function (prodname, idx) {
           var prodlist = document.getElementById('oobainspect-col0');
           prodlist.innerHTML = '';


           var dprod = ui.createElement('div', 'oobarowx1');
           dprod.setAttribute('class', 'panel panel-danger');

           var dprodc = ui.createElement('div', 'oobarowcon');
           dprodc.setAttribute('class', 'panel-body');

           //alert('Prod: '+ ijob + '/'+ idx);

           var ijobs = appModel['inspections'][idx];
           var ijob = ijobs[idx];



           if (ijob == null) {
                 var px = ui.createElement('p', 'missinstep');
                 px.innerHTML = 'No Inspections defined';
                 prodlist.appendChild(px);
                 return ;
           }

           if (ijob.hasOwnProperty('inspections')) {
            console.log('Inspection: '+ JSON.stringify(ijobs) );
            // var about = ijob['about'];
           //var prod = ijob['product'];

              var hdr = ui.createElement('div', 'spantext'+idx);
               hdr.setAttribute('class', 'panel-heading');
               hdr.innerHTML = prodname.toUpperCase();
               dprod.appendChild(hdr);

            //prodlist.innerHTML = JSON.stringify(ijob);
                var img = ui.createElement('img', 'prod-img-'+idx);
               // img.setAttribute('src', '/pimages/'+about['image']);
                img.setAttribute('class', 'img-thumbnail');
                dprodc.appendChild(img);
                var ptxt = ui.createElement('p', 'oobatext-'+i);
                ptxt.setAttribute('class', 'abouttext');
                //  ptxt.innerHTML = about['text'];
                dprodc.appendChild(ptxt);

                var nbtn = ui.createElement('button', 'oobanext-btn'+idx);
                nbtn.setAttribute('class', 'btn btn-block btn-success');
                nbtn.setAttribute('onclick', 'views.driveInspection("'+idx+'"); ');
                nbtn.innerHTML = "Start Inspection";
                dprodc.appendChild(nbtn);

                dprod.appendChild(dprodc);
                prodlist.appendChild(dprod);
            } else {
                 var px = ui.createElement('p', 'missinstep');
                 px.innerHTML = 'No Inspections defined';
                 prodlist.appendChild(px);
                 return ;
            }



    }

    this.driveInspection = function(idx, elmid) {
        console.log("Insp: "+ idx);
        var ijob = ijobs[idx];
        var inspx = ijob['inspection'][0];

        var idiv = document.getElementById(elmid);
        idiv.innerHTML = '';
        var isteps = inspx['steps'];

        for (i=0; i < isteps.length; i++) {
            var istep = isteps[i];
            var h3x = ui.createElement('h3', 'h3x'+i);
            h3x.innerHTML = istep['title'];
            idiv.appendChild(h3x);

            var sect = ui.createElement('section', 'sx'+i);
            var cntx = istep['content'] ;
            sect.innerHTML = cntx;
            idiv.appendChild(sect);


        }
        $("#oobarowcon").steps({
            headerTag: "h3",
            bodyTag: "section",
            transitionEffect: "slideLeft",
            enableCancelButton : true,
            autoFocus: true
        });
    }


    this.updateProductList = function(msg) {
        var prods = JSON.parse(msg);
        //console.log('Product List: '+ msg);

        var dvx = document.getElementById('productslist-col0');
        dvx.innerHTML = '';

        var panelarr = new Array();
        if (prods.length > 0) {
            for (i=0; i < prods.length; i++) {
                var prodx = prods[i];
                var prod = prodx['product'];
                var about = null;
                if (prodx['about']) {
                    about = prodx['about'];
                }

                var btn = ui.createElement('button', 'product-'+i);
                btn.setAttribute('onclick', "views.prodScanForm('"+ JSON.stringify(prodx) +"')");
                btn.setAttribute('class', 'btn btn-block btn-info');
                btn.innerHTML = prod;

                var img = ui.createElement('img', 'prod-img-'+i);
                img.setAttribute('src', '/pimages/'+about['image']);
                img.setAttribute('class', 'img-thumbnail');

                var ctn = ui.createElement('div', 'divx-prod-'+i);
                ctn.appendChild(img);
                ctn.appendChild(btn);
                //dvx.appendChild(btn);
                panelarr.push({'heading' : prod, 'content' : ctn , 'type' : 'danger'});
            }
        }

        var panela  = ui.createPanels('prodpanel', panelarr);
        dvx.appendChild(panela);

         //Request Inspections
         websx.requestinspections();

    }

    this.prodScanForm = function(formx) {
            console.log('ProductScan: '+ formx);

            var sku = JSON.parse(formx);

            var scanhdr = document.getElementById('appmodalheader');
            scanhdr.innerHTML = sku['product'] ;


            var scanmodalcontent = document.getElementById('appmodalbody');
            var scandiv = ui.createElement('div', 'scandiv');
            scandiv.setAttribute('class', 'well');

            var scanitems = new Array();
            /*
            scanitems.push( {'label' : 'SerialNumber',
			    'type' : "text",
			    'name' : 'iserial',
			    'id'   : 'iserial',
			    'value' : 'TH012040Q-40008',
			    'placeholder': 'TH012040Q-40008' } );

            scanitems.push( {'label' : 'Console',
			    'type' : "text",
			    'name' : 'iconsole',
			    'id'   : 'iconsole',
			    'value' : '10.31.221.215:3010',
			    'placeholder': key } );
             */
            var scanlist = sku['scanlist'];
            for (i=0; i < scanlist.length; i++) {
                var scanitem = scanlist[i];
                var key = Object.keys(scanitem);

                var scanidobj = scanitem[key];
                console.log("ScanItem: "+ key + '/'+ scanidobj);
                var dvalue = '';
                /*if (scanid.includes(':') ) {
                    console.log('Item '+ key + ' has default '+scanid );
                    var sarray = scanid.split(':');
                    scanid = sarray[0];
                    dvalue = sarray[1];
                }*/
	            scanitems.push({'label' : key,
			    'type' : "text",
			    'name' : scanidobj['id'],
			    'id'   : scanidobj['id'],
			    'value' : scanidobj['value'],
			    'placeholder': scanidobj['value'] } );
            }


	        var scanform = ui.createForm('scanform', scanitems);
	        scandiv.appendChild(scanform);

	        var btngrp = ui.createElement('div', 'scanbtngrp');
	        btngrp.setAttribute('class', 'btn-group btn-group-justified');

	        var sbmt = ui.createElement('a', 'scansubmit');
	        //sbmt.setAttribute('type', 'button');
	        sbmt.setAttribute('class', 'btn btn-danger');
	        sbmt.innerHTML = 'Start Test';
	        var sobj = JSON.stringify({'scanlist' : scanlist});
	        sbmt.setAttribute('onclick', "readScanForm('"+  sobj +"'); ");
	        btngrp.appendChild(sbmt);

	        var clr = ui.createElement('a', 'scanclear');
	        clr.setAttribute('class', 'btn btn-default');
	        clr.setAttribute('onclick', 'clearScanForm();');
	        clr.innerHTML = 'Clear Data';
	        btngrp.appendChild(clr);

	        var cmodal = ui.createElement('a', 'closemodal');
	        cmodal.setAttribute('class', 'btn btn-info');
	        cmodal.setAttribute('onclick', 'closeScanModal();');
	        cmodal.innerHTML = 'Close';
	        btngrp.appendChild(cmodal);



	        scandiv.appendChild(btngrp);

            scanmodalcontent.innerHTML = '';
            scanmodalcontent.appendChild(scandiv);


           showScanModal();


    }

    this.updateMoveTable = function() {
        var crow = document.getElementById('dashboard-col0');
        var clx = crow.getAttribute('class');
        crow.setAttribute('class', clx+' dashboardx');
        var tbldata = new Array();

        var lgroup = ui.createElement('div', 'movelist');
        var colclass = 'col-xs-4';

        for (i=0; i < movetable.length; i++) {
            var moveobj = movetable[i];
            tbldata.push([moveobj['SerialNumber'], moveobj['MoveNumber'], moveobj['Status'] ]);

            var ax = ui.createElement('a', 'lgroup'+i);
            ax.setAttribute('href', 'javascript:null');

            if (moveobj['Status'] == null) {
                ax.setAttribute('class', 'list-group-item list-group-item-info');
            } else if (moveobj['Status'] == 'FAILED') {
                ax.setAttribute('class', 'list-group-item list-group-item-danger');
            }

            var lrow = ui.createElement('div', 'div-'+moveobj['SerialNumber']);
            lrow.setAttribute('class','row');

            var col0 = ui.createElement('div', 'lstat-cell0'+i);
            col0.setAttribute('class', colclass+' mrow');
            var cspan = ui.createElement('span', 'span'+i);
            cspan.setAttribute('class', "mcell1");
            cspan.innerHTML = moveobj['SerialNumber']+
                              '<div class="mcell2">'+moveobj['SKU']+'</div>' ;
                //htm +='<span class="mcell2">'+moveobj['MoveNumber']+'</span>' ;
            col0.appendChild(cspan);

            var btn = ui.createElement('button', 'statusbtn-'+moveobj['SerialNumber']);
            btn.setAttribute('onclick',
                            'triggerSerial(\''+ JSON.stringify(moveobj) + '\'); ');
            btn.setAttribute('class', 'btn btn-block btn-basic mcell4');
            btn.innerHTML = 'Start/'+moveobj['MoveNumber'];
            col0.appendChild(btn);

            var res = ui.createElement('p', 'result-'+moveobj['SerialNumber']);
            res.setAttribute('class', 'results');
            col0.appendChild(res);


            lrow.appendChild(col0);



            var col2 = ui.createElement('div', 'lstat-cell2'+i);
            col2.setAttribute('class', colclass+' mrow');
            col2.innerHTML = moveobj['MoveNumber'];
            //lrow.appendChild(col2);

            var col1 = ui.createElement('div', 'lstat-cell1'+i);
            col1.setAttribute('class', colclass+' form-group mrow mcell3');

            var inpx = ui.createElement('input', 'consolex-'+moveobj['SerialNumber']);
            inpx.setAttribute('type', 'text');
            inpx.setAttribute('class', 'form-control mcell4');
            //col1.appendChild(inpx);
            //lrow.appendChild(col1);



            var col3 = ui.createElement('div', 'lstat-cell3'+i);
            col3.setAttribute('class', 'col-xs-8 mrow');
            var consx = this.consolearea(moveobj['SerialNumber']);
            col3.appendChild(consx);

            lrow.appendChild(col3);
            lgroup.appendChild(lrow);

            var px = ui.createElement('div', 'divider'+i);
            px.setAttribute('class', 'rowd');
            px.innerHTML = '  ';

            lgroup.appendChild(px);
        }

        var hdr = ['Serial', 'MoveNumber' ,'Status'];
        var stbl = ui.table ("movestatustable", 'table-stripe table-hover' ,hdr, tbldata);
        //crow.appendChild(stbl);
        crow.appendChild(lgroup);
    }


    this.updateMoveTable2 = function() {
        var crow = document.getElementById('dashboard-col0');
        var clx = crow.getAttribute('class');
        crow.setAttribute('class', clx+' dashboardx');
        var tbldata = new Array();
        /*<div class="list-group">
             <a href="#" class="list-group-item active">First item</a>
             <a href="#" class="list-group-item">Second item</a>
             <a href="#" class="list-group-item">Third item</a>
        </div>*/
        var lgroup = ui.createElement('div', 'movelist');
        var colclass = 'col-xs-4';
        for (i=0; i < movetable.length; i++) {
            var moveobj = movetable[i];
            tbldata.push([moveobj['SerialNumber'], moveobj['MoveNumber'], moveobj['Status'] ]);

            var ax = ui.createElement('a', 'lgroup'+i);
            ax.setAttribute('href', 'javascript:null');
            if (moveobj['Status'] == null) {
                ax.setAttribute('class', 'list-group-item list-group-item-info');
            } else if (moveobj['Status'] == 'FAILED') {
                ax.setAttribute('class', 'list-group-item list-group-item-danger');
            }

            var lrow = ui.createElement('div', 'lstat'+i);
            lrow.setAttribute('class','row');

            var col0 = ui.createElement('div', 'lstat-cell0'+i);
            col0.setAttribute('class', colclass+' mrow');
            var htm = '<span class="mcell1" >'+moveobj['SerialNumber'] +'</span>';
                htm +='<p class="mcell2">'+moveobj['SKU']+'</p>' ;
                //htm +='<span class="mcell2">'+moveobj['MoveNumber']+'</span>' ;
            col0.innerHTML = htm ;
            lrow.appendChild(col0);



            var col2 = ui.createElement('div', 'lstat-cell2'+i);
            col2.setAttribute('class', colclass+' mrow');
            col2.innerHTML = moveobj['MoveNumber'];
            //lrow.appendChild(col2);

            var col1 = ui.createElement('div', 'lstat-cell1'+i);
            col1.setAttribute('class', colclass+' form-group mrow mcell3');
            var inpx = ui.createElement('input', 'consolex'+i);
            inpx.setAttribute('type', 'text');
            inpx.setAttribute('class', 'form-control mcell4');

            //col1.appendChild(inpx);
            //lrow.appendChild(col1);


            var col3 = ui.createElement('div', 'lstat-cell3'+i);
            col3.setAttribute('class', colclass+' mrow');
            var btn = ui.createElement('button', 'btncell'+i);
            btn.setAttribute('onclick',
                            'triggerSerial(\''+JSON.stringify(moveobj)+'\'); ');

            btn.setAttribute('class', 'btn btn-block btn-info mcell4');
            btn.innerHTML = 'Start/'+moveobj['MoveNumber'];
            col3.appendChild(btn);

            var stat = ui.createElement('div', 'statusbar');
            stat.setAttribute('class', 'statusbar');
            var btn = ui.createElement('button', 'statusbtn');
            btn.setAttribute('class', 'btn btn-block btn-info');
            btn.innerHTML = 'No tests Running';
            stat.appendChild(btn);
            col3.appendChild(stat);

            lrow.appendChild(col3);

            lgroup.appendChild(lrow);
        }

        var hdr = ['Serial', 'MoveNumber' ,'Status'];
        var stbl = ui.table ("movestatustable", 'table-stripe table-hover' ,hdr, tbldata);
        //crow.appendChild(stbl);
        crow.appendChild(lgroup);
    }


    this.consoleArea = function() {
            var d = document.getElementById('dashboard-col1');
            var dx = ui.createElement('div', 'consolewell');
            dx.setAttribute('class', 'well well-lg');

            var crow = ui.addRowCol('inpbox', 3);
            dx.appendChild(crow);


            var px = ui.createElement('p', 'p1');
            //var inp = ui.createElement('textarea', 'consolex');

            var drow = ui.addRowCol('cbox', 1);
            var cons = ui.createElement('div', 'consolex');
            cons.setAttribute('class', 'console');

            var tcons = ui.createElement('div', 'tconsolex');
            tcons.setAttribute('class', 'tconsole');
            cons.appendChild(tcons);

            //drow.appendChild(ui.br());
            //drow.appendChild(px);
            drow.appendChild(cons);



            //drow.appendChild(ui.br());
            //crow.appendChild(stat);

            //dx.appendChild(drow);

            d.appendChild(dx);
            //d.appendChild(stat);

            var cx_col = document.getElementById('dashboard-col1');
            cx_col.appendChild(drow);



            //Phase2
            var inpx = new Array();
	        inpx.push({'label' : "Serial Number",
			'type' : "text",
			'name' : 'rserial',
			'id'   : 'rserial',
			'placeholder': "1951Q-30149"});

		    var form1 = ui.createForm('registerform1', inpx);
            var col0 = document.getElementById('inpbox-col0');
            col0.appendChild(form1);
             $('#rserial').val('1951Q-30149');

            //Phase2
            var inpx = new Array();
	        inpx.push({'label' : "Console",
			'type' : "text",
			'name' : 'rconsole',
			'id'   : 'rconsole',
			'placeholder': "10.31.221.215:3010"});

		    var form2 = ui.createForm('registerform2', inpx);
            var col0 = document.getElementById('inpbox-col1');
            col0.appendChild(form2);
            $('#rconsole').val('10.31.221.215:3010');


            //Phase3
            var inpx = new Array();
	        inpx.push({'label' : "Submit",
			'type' : "submit",
			'name' : 'rsubmit',
			'id'   : 'rsubmit',
			'onclick': 'triggerUnit();'}
			);

		    var form3 = ui.createForm('registerform3', inpx);
            var col0 = document.getElementById('inpbox-col2');
            col0.appendChild(form3);

            var sb = document.getElementById('rsubmit');
            var clx = sb.getAttribute('class');
            sb.setAttribute('class', clx+' btn btn-danger');

            return dx;

    }

     this.consolearea = function(serialnum) {

            var dx = ui.createElement('div', 'consolewell');
            dx.setAttribute('class', 'well well-lg');


            var drow = ui.addRowCol('cbox-'+serialnum, 1);
            var cons = ui.createElement('div', 'consolex-'+serialnum);
            cons.setAttribute('class', 'console');

            var tcons = ui.createElement('div', 'tconsolex-'+serialnum);
            tcons.setAttribute('class', 'tconsole');
            cons.appendChild(tcons);

            //drow.appendChild(ui.br());
            drow.appendChild(cons);

            var stat = ui.createElement('div', 'statusbar');
            stat.setAttribute('class', 'statusbar');
            var btn = ui.createElement('button', 'statusbtn');
            btn.setAttribute('class', 'btn btn-block btn-info');
            btn.innerHTML = 'No tests Running';
            stat.appendChild(btn);

            //drow.appendChild(ui.br());
            //drow.appendChild(stat);
            dx.appendChild(drow);

            return dx;
     }



    this.appNavBar = function() {
	    //navbar = ui.navbar("navarea", '<img align="middle" class="logo-img" src="img/logo-header-psi.png"></img>');
	    var navbar = ui.navbar("navarea", '<span class="brand">'+
								   '<img class="logo-img img-rounded pull-left" src="img/logo-64px.png"></img>'+
								   '<span class="brandtext">BAUD Express</span>'+
								   '</span>' +
								   '<span class="clock" id="clock">Clock</span>'
								   );
	    ui.addSubViewToMain([navbar]);
    }

    this.updateConsole = function(snum, msgStr) {
        console.log("Updating ID: tconsolex-"+snum);
        var cx = document.getElementById('tconsolex-'+snum);
        var consoleLinex = JSON.parse(msgStr);
        var lines = consoleLinex['console'];
        var line = null;
        if (lines.length > 1) {
            line = lines.join('<BR/>');
        } else {

            /*if (line === 'RESET') {
                cx.innerHTML = '';
                console.log('');
            } else if (line['status']) {
                    if (line['status'] == 'PASSED') {
                        console.log('PASSED');
                    }
            } else {*/
                line = lines+'<BR/>';

        }
        cx.innerHTML += line ;
        cx.scrollTop = cx.scrollHeight;

        //this.updateStatus(serial);
    }


    this.registerForm = function() {
	    var inpx = new Array();
	    inpx.push({'label' : "User Name",
			'type' : "text",
			'name' : 'rusername',
			'id'   : 'rusername',
			'placeholder': "User Name"});

		var form1 = ui.createForm('registerform1', inpx);

	    return form1
    }


     this.startupView = function() {
            alert('Starup Alert');
     }

     this.updateStatus = function(snum) {
             var stat = document.getElementById('statusbtn-'+snum);
            stat.innerHTML = 'Testing SN# '+ snum;
            var cls = stat.setAttribute('class', 'btn btn-block btn-warning');

     }

     this.passView = function(snum) {
            var stat = document.getElementById('status-'+snum);
            stat.innerHTML = '';
            var alrt = ui.createAlert('status-notification-'+snum, 'success',
                                       'Passed! ', snum+' has finished testing.');

            stat.appendChild(alrt);

            var wcol = document.getElementById('conswell-'+snum);
            wcol.setAttribute('class', 'alert alert-success');
        }

    this.resetView = function (snum) {
            //var stat = document.getElementById('statusbtn-'+snum);
            var stat = document.getElementById('tconsolex-'+snum);
            stat.innerHTML = '';
            var d = new Date();
            consoleClocks[snum] = {'start' : d.getTime() };

            var stat = document.getElementById('status-'+snum);
            stat.innerHTML = '';

            var prog = ui.createElement('div', 'prog-'+snum);

            var alrt = ui.createAlert('status-notification-'+snum, 'warning',
                                       'Testing! ', snum + ' is in progress.');

            stat.appendChild(alrt);
            ///var cls = stat.setAttribute('class', 'btn btn-block btn-info');

            //var cnsl = document.getElementById('statusbtn');
            //cnsl.innerHTML = '';
            //console.log('Clocks: '+ JSON.stringify(consoleClocks) );

        }

        /*<div class="alert alert-success">
            <strong>Success!</strong> You should <a href="#" class="alert-link">read this message</a>.
        </div>*/
        this.errorView = function (snum, msg) {
            var stat = document.getElementById('status-'+snum);
            stat.innerHTML = '';
            var alrt = ui.createAlert('status-notification-'+snum, 'danger',
                                       'Failure! ', msg);

            stat.appendChild(alrt);

            var wcol = document.getElementById('conswell-'+snum);
            wcol.setAttribute('class', 'alert alert-danger');

            //clock-TH012040Q-40008
            var spandx = document.getElementById('clock-'+snum);
            var ac = ui.createElement('span', 'close-'+snum);
            ac.setAttribute('class', 'glyphicon glyphicon-remove');
            ac.setAttribute('onclick', 'views.closeConsole(\''+snum+'\'); ');
            spandx.appendChild(ac);


        }

         this.scanPromptView = function(scanData, sku) {
            console.log('ScanDataView: '+ scanData);
            console.log('SKU: '+ sku);


            var scanhdr = document.getElementById('appmodalheader');
            scanhdr.innerHTML =  sku;


            var scanmodalcontent = document.getElementById('appmodalbody');
            var scandiv = ui.createElement('div', 'scandiv');
            scandiv.setAttribute('class', 'well');

            var scanitems = new Array();

            scanitems.push( {'label' : 'Console',
			    'type' : "text",
			    'name' : 'iconsole',
			    'id'   : 'iconsole',
			    'value' : '10.31.221.215:3010',
			    'placeholder': key } );

			scanitems.push( {'label' : 'SerialNumber',
			    'type' : "text",
			    'name' : 'iserial',
			    'id'   : 'iserial',
			    'value' : '1908Q-20179',
			    'placeholder': '1908Q-20179' } );


            var scanlist = JSON.parse(scanData);
            for (i=0; i < scanlist.length; i++) {
                var scanitem = scanlist[i];
                var key = Object.keys(scanitem);

                var scanidobj = scanitem[key];
                console.log("ScanItem: "+ key + '/'+ scanidobj);
                var dvalue = '';
                /*if (scanid.includes(':') ) {
                    console.log('Item '+ key + ' has default '+scanid );
                    var sarray = scanid.split(':');
                    scanid = sarray[0];
                    dvalue = sarray[1];
                }*/
	            scanitems.push({'label' : key,
			    'type' : "text",
			    'name' : scanidobj['id'],
			    'id'   : scanidobj['id'],
			    'value' : scanidobj['value'],
			    'placeholder': scanidobj['value'] } );
            }



            /*
	        scanitems.push({'label' : "Start Test",
			'type' : "submit",
			'name' : 'modalsubmit',
			'id'   : 'modalsubmit',
			'onclick': 'readScanForm();'}
			);*/




	        var scanform = ui.createForm('scanform', scanitems);
	        scandiv.appendChild(scanform);

	        var btngrp = ui.createElement('div', 'scanbtngrp');
	        btngrp.setAttribute('class', 'btn-group btn-group-justified');

	        var sbmt = ui.createElement('a', 'scansubmit');
	        //sbmt.setAttribute('type', 'button');
	        sbmt.setAttribute('class', 'btn btn-danger');
	        sbmt.innerHTML = 'Start Test';
	        sbmt.setAttribute('onclick', "readScanForm('"+ JSON.stringify(scanlist) +"', \""+sku+"\" ); ");
	        btngrp.appendChild(sbmt);

	        var clr = ui.createElement('a', 'scanclear');
	        clr.setAttribute('class', 'btn btn-default');
	        clr.setAttribute('onclick', 'clearScanForm();');
	        clr.innerHTML = 'Clear Data';
	        btngrp.appendChild(clr);

	        var cmodal = ui.createElement('a', 'closemodal');
	        cmodal.setAttribute('class', 'btn btn-info');
	        cmodal.setAttribute('onclick', 'closeScanModal();');
	        cmodal.innerHTML = 'Close';
	        btngrp.appendChild(cmodal);



	        scandiv.appendChild(btngrp);

            scanmodalcontent.innerHTML = '';
            scanmodalcontent.appendChild(scandiv);



           showScanModal();


        }



        this.scanPrompt = function() {
            console.log('ScanPrompt: '+JSON.stringify(modalobj));

            var scanhdr = document.getElementById('appmodalheader');
            scanhdr.innerHTML = modalobj['SKU'] ;


            var scanmodalcontent = document.getElementById('appmodalbody');
            var scandiv = ui.createElement('div', 'scandiv');
            scandiv.setAttribute('class', 'well');

            var scanitems = new Array();

            scanitems.push( {'label' : 'Console',
			    'type' : "text",
			    'name' : 'iconsole',
			    'id'   : 'iconsole',
			    'value' : '10.31.221.215:3010',
			    'placeholder': key } );

            var scanlist = modalobj['scanlist'];
            for (i=0; i < scanlist.length; i++) {
                var scanitem = scanlist[i];
                var key = Object.keys(scanitem);

                var scanidobj = scanitem[key];
                console.log("ScanItem: "+ key + '/'+ scanidobj);
                var dvalue = '';
                /*if (scanid.includes(':') ) {
                    console.log('Item '+ key + ' has default '+scanid );
                    var sarray = scanid.split(':');
                    scanid = sarray[0];
                    dvalue = sarray[1];
                }*/
	            scanitems.push({'label' : key,
			    'type' : "text",
			    'name' : scanidobj['id'],
			    'id'   : scanidobj['id'],
			    'value' : scanidobj['value'],
			    'placeholder': scanidobj['value'] } );
            }



            /*
	        scanitems.push({'label' : "Start Test",
			'type' : "submit",
			'name' : 'modalsubmit',
			'id'   : 'modalsubmit',
			'onclick': 'readScanForm();'}
			);*/




	        var scanform = ui.createForm('scanform', scanitems);
	        scandiv.appendChild(scanform);

	        var btngrp = ui.createElement('div', 'scanbtngrp');
	        btngrp.setAttribute('class', 'btn-group btn-group-justified');

	        var sbmt = ui.createElement('a', 'scansubmit');
	        //sbmt.setAttribute('type', 'button');
	        sbmt.setAttribute('class', 'btn btn-danger');
	        sbmt.innerHTML = 'Start Test';
	        sbmt.setAttribute('onclick', "readScanForm('"+ JSON.stringify(scanlist) +"'); ");
	        btngrp.appendChild(sbmt);

	        var clr = ui.createElement('a', 'scanclear');
	        clr.setAttribute('class', 'btn btn-default');
	        clr.setAttribute('onclick', 'clearScanForm();');
	        clr.innerHTML = 'Clear Data';
	        btngrp.appendChild(clr);

	        var cmodal = ui.createElement('a', 'closemodal');
	        cmodal.setAttribute('class', 'btn btn-info');
	        cmodal.setAttribute('onclick', 'closeScanModal();');
	        cmodal.innerHTML = 'Close';
	        btngrp.appendChild(cmodal);



	        scandiv.appendChild(btngrp);

            scanmodalcontent.innerHTML = '';
            scanmodalcontent.appendChild(scandiv);



           showScanModal();


        }



} ;



function loadPanels() {
	
}

function closeScanModal() {
    var scanmodal = document.getElementById('appmodal');
    $("#appmodal").modal('hide');
}

function showScanModal() {
    var scanmodal = document.getElementById('appmodal');
    $("#appmodal").modal('show');
}



function clicker() {
	alert('Clicked..');
}
