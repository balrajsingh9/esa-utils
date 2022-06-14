Portal.Portlet.Sequence_ViewerReport = Portal.Portlet.extend({

	init: function(path, name, notifier) {
		console.info("Created Sequence_ViewerReport");
		this.base(path, name, notifier);

		var notifier = Notifier.getInstance();
	    notifier.setListener(null, "CONTENT_LOADER_FINISHED", this.DownloaderFinished );   
	    notifier.setListener(null, "CONTENT_LOADER_CANCELED", this.DownloaderCancelled ); 
	    notifier.setListener(this, "SEARCH_EXECUTED", function(oListener, custom_data, sMessage, oNotifier) {
			// load sequence with markup, if not loaded
			if (!Portal.Portlet.Sequence_ViewerReport.LoadSequenceWithMarkup){
			    Portal.Portlet.Sequence_ViewerReport.LoadSequenceWithMarkup = true;
                Dispatcher.getInstance().notify(null, 'LoadSequenceWithMarkup');
			}
		});
	    
		var report = this.getValue('report');
		
		// no region data will be sent. Set to true so that 'Bitmask' does not wait for this message
		if (report == 'asn1'){
		    Portal.Portlet.Sequence_ViewerReport.regionAvailable = true;
		} 
		// for these reports, no messages will be sent
		else if (report != 'genbank' && report != 'genpept' && report != 'fasta' && report != 'gbwithparts' 
		&& report != 'gpwithparts' && report != 'ipg'){
		    this.CreateReport();
		}
		// no region data available for multiple record view, so don't wait for message
		else if (this.getInput('display_type') && this.getValue('display_type') == 'multi'){
		   Portal.Portlet.Sequence_ViewerReport.regionAvailable = true;
		}
	},
    
	listen: {
	        // events
	    /*    
	    "ShowSequenceLink<click>": function(e, target, name){
	        this.setValue('report', target.getAttribute('report'));
	        Portal.Portlet.Sequence_ViewerReport.displayLongRecord = true;
	        this.ReportPage();
	    },*/
	
        // messages
        'Sequence_ViewerReportFetchContent': function(sMessage, oData, sSrc) {
            this.FetchContent();
        },
        
        'Sequence_ViewerReportWaitOver': function(sMessage, oData, sSrc) {
            this.StartContentFetch();
        },
        
        'LoadSequenceWithMarkup': function(sMessage, oData, sSrc) {
            this.CreateReport();
        },
        
        'Sequence_ViewerReportRemainingNavMenu': function(sMessage, oData, sSrc) {
            this.RemainingNavBarMenu(oData.counter, 1);
        },
        
	    'SelectedRegion' : function(sMessage, oData, sSrc) {
	        //console.info("Region oData=" , oData)
	    //    console.info('message received. f:'+oData.from+' to:'+ oData.to + ' itemid:' + oData.itemid); //for debug
            Portal.Portlet.Sequence_ViewerReport.from = oData.from;  
            Portal.Portlet.Sequence_ViewerReport.to = oData.to; 
            Portal.Portlet.Sequence_ViewerReport.itemid = oData.itemid;
            if (oData.master){
                 Portal.Portlet.Sequence_ViewerReport.master = oData.master;
            }
             
	        Portal.Portlet.Sequence_ViewerReport.regionAvailable = true;	        
	        if (Portal.Portlet.Sequence_ViewerReport.bitmasksAvailable){
	            this.CreateReport(); 
	        }
	    },
	    
	    'Bitmask' : function(sMessage, oData, sSrc) { 
	        console.info("Customize oData=" , oData)
	        console.info('message received. extrafeat:', oData.extrafeat 
	        	//, ',fmt_mask:' , oData.fmt_mask 
	        		, "custom_view=", oData.custom_view
	            , ',strand:' , oData.strand); //for debug
	        Portal.Portlet.Sequence_ViewerReport.extrafeat = oData.extrafeat;
	        //Portal.Portlet.Sequence_ViewerReport.fmt_mask = oData.fmt_mask;
	        Portal.Portlet.Sequence_ViewerReport.custom_view = "&" + oData.custom_view.join("&");
	        
	        Portal.Portlet.Sequence_ViewerReport.strand = oData.strand;
	        Portal.Portlet.Sequence_ViewerReport.comp = oData.comp;
	        Portal.Portlet.Sequence_ViewerReport.show_sequence = oData.show_sequence;	        
	        if (oData.master){
                 Portal.Portlet.Sequence_ViewerReport.master = oData.master;
            }


	        Portal.Portlet.Sequence_ViewerReport.bitmasksAvailable = true;	        
	        if (Portal.Portlet.Sequence_ViewerReport.regionAvailable){
	            this.CreateReport(); 
	        }
	    }

	},
	
	CreateReport: function(){
	    var rPortlet = Portal.Portlet.Sequence_ViewerReport;
	    rPortlet.InDownloadCycle = false;
	
	    /* cancel all previous */
	    // if an instance of downloader was started and not finished or cancelled, cancel it before 
        // making another xml-http call to viewer or downloader
        if (rPortlet.downloader == 'on'){
            var notifier = Notifier.getInstance();
            notifier.Notify(null, "LOADER_CANCELED", {} );
        }
        ContentLoader.removeCancelMessages();
        /*
        if (rPortlet.viewer == 'on'){
            rPortlet.oRemoteDataProvider.Abort(); 
            console.info('oRemoteDataProvider.Abort');
        }
        */
        
        // while anything is executing, wait
        if(rPortlet.downloader == 'on' || rPortlet.viewer == 'on'){
            Portal.Portlet.Sequence_ViewerReport.waiting = true;
        }
        else {
            this.StartContentFetch();
        }        
    },
    
    StartContentFetch: function(){
    
        // clear the current contents
        jQuery( 'div.gbff' ).each( function() {
            this.innerHTML = "";
        });
        // remove any leftover navigation on those records which no not have contents (no .gbff)
        jQuery( 'div.hnav' ).each( function() {
            jQuery(this).remove();
        });
        
        var rPortlet = Portal.Portlet.Sequence_ViewerReport;
        rPortlet.counter = 0;
        if (!rPortlet.InDownloadCycle){
            rPortlet.InDownloadCycle = true;
            this.FetchContent();
        }     
    },
	
	FetchContent: function(){
	    var counter = ++Portal.Portlet.Sequence_ViewerReport.counter;
	    // two things to check. Execute only for the number of items on the page & stop processing 
	    // if a new round of processing has started because some setting was updated on the page
	    if (counter <= this.getValue("ItemCount") 
	        && Portal.Portlet.Sequence_ViewerReport.InDownloadCycle){
	        var FlatFileNode = document.getElementById("viewercontent" + counter);
	        if (FlatFileNode && jQuery(FlatFileNode).hasClass('gbff')){
	            
	            // decide what type of page to show
                var PageType = this.DecideToShowReport(FlatFileNode);
                
                if (PageType == 'report'){
                    this.ViewerPage(FlatFileNode);
                }
                else if (PageType == 'downloader'){
                    this.DownloaderPage(FlatFileNode);
                }
                
                // change the navigation bar 
                this.NavBar(FlatFileNode, counter, true, 1);
            
                // redraw the title in IE6
	            //this.reDrawTitle(counter, FlatFileNode.getAttribute('val'));
	            
	        }//if flatfilenode
	        else if (FlatFileNode){
	            // add the navigation bar if there are records before and after  
                this.NavBar(FlatFileNode, counter, false, 1);
	            this.FetchContent();
	        }
        }
        Notifier.getInstance().Notify(null, "SEQUENCE_PART_LOADED", parseInt(this.getValue("ItemCount")) - counter + 1);
	},
    
    ViewerPage: function(FlatFileNode){
        var oThis = this;   
    	
        var oPh = FlatFileNode;
        oPh.style.display = "block";
    	
    	var x = Portal.Portlet.Sequence_ViewerReport;
    	
	    // Overload remote data provider callbacks
	    x.oRemoteDataProvider.onSuccess = function(oObj) {
    	    if (oObj.responseText.indexOf("OUTPUT_TOO_BIG") != -1) {
    	        oPh.innerHTML = "";
    	        x.viewer = 'off';
    	        if (x.InDownloadCycle){
        	        oThis.DownloaderPage(FlatFileNode);
        	    }
        	    else if (Portal.Portlet.Sequence_ViewerReport.waiting){
        	        Portal.Portlet.Sequence_ViewerReport.waiting = false;
        	        oThis.StartContentFetch();
        	    }
    	    } else {
    	        // render the page
	            var report = oThis.getValue('report');
	            var elem = ( report == "genbank" || report == "genpept" || report ==  "gbwithparts" || 
	                        report ==  "gpwithparts" || report ==  "ipg") ? "div" : "pre";
     	        setTimeout(function() { oPh.innerHTML = "<" + elem + ">" 
     	                                                + oObj.responseText + "</" + elem +">" ; }, 100); 
     	        x.viewer = 'off';
     	        
     	        // call next iteration     	        
     	        if (x.InDownloadCycle){
     	            oThis.FetchContent();
     	        }
     	        else if (Portal.Portlet.Sequence_ViewerReport.waiting){
        	        Portal.Portlet.Sequence_ViewerReport.waiting = false;
        	        oThis.StartContentFetch();
        	    }
    	    }
    	    setTimeout(function() {Notifier.getInstance().Notify(null, "SEQUENCE_LOADED");}, 500);
	    }
	    
	    // on error, make a second attempt at download by using the downloader
	    x.oRemoteDataProvider.onError = function(oObj) {
	        oPh.innerHTML = "";
	        x.viewer = 'off';
	        if (x.InDownloadCycle){
                oThis.DownloaderPage(FlatFileNode);
            }
            else if (Portal.Portlet.Sequence_ViewerReport.waiting){
    	        Portal.Portlet.Sequence_ViewerReport.waiting = false;
    	        oThis.StartContentFetch();
    	    }
	    }
	    
	    x.oRemoteDataProvider.onStart = function(oObj) {
	        // show text when started loading the page
	        oPh.innerHTML = "<div class='loading'>Loading ... " +
	            "<img src='/core/extjs/ext-2.1/resources/images/default/grid/loading.gif'" 
	            + " alt='record loading animation'/></div>";
	    }

        // create url to viewer.fcgi and call asynchronous HTTP request to viewer.fcgi

	    var sRequest = oThis.CreateUrl(oPh)
	      + "&maxdownloadsize=" + oThis.getValue('maxdownloadsize');
	    
	    if (x.InDownloadCycle && x.viewer == 'off'){
	        x.viewer = 'on';
	        x.oRemoteDataProvider.Get(sRequest);
	    }	        
    },
    
    DownloaderPage: function(FlatFileNode){
        // call pload.cgi
        // see https://www.ncbi.nlm.nih.gov/core/ajax_loader/2.1/js/contentLoader.js
        //create an instance of the loading bar
        var sb = new LoadingBar();                
        //initialize the loading bar
        sb.init();
        
        //build the path to the file that we want to request .cgi, NOT .fcgi!
        // always use 'http' - see https://jira.ncbi.nlm.nih.gov/browse/ID-2940
        var lFile = "http://" + document.location.hostname + "/sviewer/viewer.cgi?" + this.CreateUrl(FlatFileNode);
        
        //alert("lFile=" + lFile);

        var report = this.getValue('report');
        var elem = ( report == "genbank" || report == "genpept" || report == "gbwithparts" 
                  || report ==  "gpwithparts" || report ==  "ipg") ? "div" : "pre";
        //create a new instance of the ContentLoader specifing the id of the output location and the file url
        var cl = new ContentLoader(FlatFileNode.getAttribute('id'), lFile);
        
        //Start the rendering of the file  
        if (Portal.Portlet.Sequence_ViewerReport.InDownloadCycle && Portal.Portlet.Sequence_ViewerReport.downloader == 'off'){
            Portal.Portlet.Sequence_ViewerReport.downloader = 'on'; 
            cl.startFetch(); 
        }
    }, 
    
    // create main part of URL to viewer (don't include report param)
    CreateUrl: function(FlatFileNode){
        // create URL to fetch report
        var x = Portal.Portlet.Sequence_ViewerReport;
        var report = this.getValue('report');
        //if (x.master == 'false' && report.toLowerCase() == 'genbank'){ report = 'gbwithparts';} // commented because of ID-1729
        
        if (x.from > 0 || x.to > 0) {
        	//x.custom_view = x.custom_view.replace("&conwithfeat=on", "");
        	x.custom_view = x.custom_view.replace("&withparts=on", "");
        }
        var URL =  "id=" + FlatFileNode.getAttribute('val')
          + "&db=" + this.getValue('db')
   	      + "&report=" + (report === "fasta_text" ? "fasta" : report)   
          + (x.extrafeat !== "" ? "&extrafeat=" + x.extrafeat : "")
          + (x.custom_view ? x.custom_view : "")
          + (x.itemid > 0 ? "&itemID=" + x.itemid : "")
          + (x.from > 0 ? "&from=" + x.from : "")
          + (x.to > 0 ? "&to=" + x.to : "")
          + (x.strand == "on" ? "&strand=" + x.strand : "")
          + (x.comp == 1 ? "&comp=1" : "")
   	      + (report === "fasta_text" ? "&retmode=text" : "&retmode=html")
   	      + "&withmarkup=on&tool=portal&log$=seqview";
	    
        if (this.getValue('ExpandGaps') === "on") {
        	URL += '&expand-gaps=on';
        }
        if (this.getValue('InUse')) {
        	URL += '&inuse=' + this.getValue('InUse');
        }
        if (this.getValue('Hup')) {
        	URL += '&hup=' + this.getValue('Hup');
        }
        if (this.getInput('protein_id')){
	        URL += '&protein_id=' + this.getValue('protein_id');
	    }
	    if (this.getInput('Sat')){
	        URL += '&sat=' + this.getValue('Sat');
	    }
	    if (this.getInput('SatKey')){
	        URL += '&satkey=' + this.getValue('SatKey');
	    }
	    if (this.getInput('Location')){
	        URL += '&location=' + this.getValue('Location');
	    }
	    
	    
	    //if (document.getElementById("SCDsnp") && document.getElementById("SCDsnp").checked) { // ID-5345, ID-5346
	    //    URL += '&show-vdb-snp=1'; 
	    //}

	    if ((report == "fasta_text") && this.getInput('fasta_text_params')){
	        URL += this.getValue('fasta_text_params');
	    }
	    if (x.LoadSequenceWithMarkup && (
	        report == 'gbwithparts' || report == 'gpwithparts' ||
	        report == 'genbank' || report == 'genpept' ||
	        report == 'fasta'
	        )) {
            URL += '&search=1';
        }
	    
        console.info("URL for pload:", URL);  
        return URL;      
    },
	
	DecideToShowReport: function(FlatFileNode){ 
	    var ShowReport = 'report'; //'report' | 'downloader';
	    var x = Portal.Portlet.Sequence_ViewerReport;
	    var Limit = 1 * this.getValue('maxdownloadsize');
	    var currentSize = 1 * FlatFileNode.getAttribute('sequencesize');
	    var virtualseq = FlatFileNode.getAttribute('virtualsequence');
	    
	    if (x.itemid || virtualseq == 'true'){
	        // do nothing, ShowReport is already set to 'report'
	    }
	    else if (x.from > 0 || x.to > 0){
	        //if either to or from or both have values, get the range size
	        if (x.from > 0 && x.to > 0){
	        	if (x.from > x.to ) {
		            currentSize = currentSize + x.to - x.from + 1;	        		
	        	}
	        	else {
		            currentSize = x.to - x.from;	        		
	        	}
	        }
	        else if (x.from > 0){
	            currentSize -= x.from;
	        } 
	        else if (x.to > 0){
	            currentSize = x.to; 
	        }
	        
	        if (currentSize >= Limit){
	            ShowReport = 'downloader';
	        } 
	    }
	    else if (currentSize >= Limit){
            ShowReport = 'downloader';
        } 
	    
	    console.info(currentSize, Limit);
	    return ShowReport;
	},
	
	DownloaderFinished: function(oThis){
	    var counter = Portal.Portlet.Sequence_ViewerReport.counter;
        Portal.Portlet.Sequence_ViewerReport.downloader = 'off'; 
        
        // call next iteration     	        
        if (Portal.Portlet.Sequence_ViewerReport.InDownloadCycle){
             Dispatcher.getInstance().notify(null, 'Sequence_ViewerReportFetchContent');
        }
        else if (Portal.Portlet.Sequence_ViewerReport.waiting){
	        Portal.Portlet.Sequence_ViewerReport.waiting = false;
            Dispatcher.getInstance().notify(null, 'Sequence_ViewerReportWaitOver');
	    }
	    
	    // if it was segmented set, look for more menus to transform 
        Dispatcher.getInstance().notify(null, 'Sequence_ViewerReportRemainingNavMenu', {'counter': counter});
	},
	
	DownloaderCancelled: function(){
	    var counter = Portal.Portlet.Sequence_ViewerReport.counter;
	    Portal.Portlet.Sequence_ViewerReport.downloader = 'off';
	    
	    if (Portal.Portlet.Sequence_ViewerReport.waiting){
	        Portal.Portlet.Sequence_ViewerReport.waiting = false;
            Dispatcher.getInstance().notify(null, 'Sequence_ViewerReportWaitOver');
	    }
	    
	    // if it was segmented set, look for more menus to transform 
        Dispatcher.getInstance().notify(null, 'Sequence_ViewerReportRemainingNavMenu', {'counter': counter});
	},
	
	SequenceSearchExecuted: function(){
	    // load sequence with markup, if not loaded
		if (!Portal.Portlet.Sequence_ViewerReport.LoadSequenceWithMarkup){
		    Portal.Portlet.Sequence_ViewerReport.LoadSequenceWithMarkup = true;
	        this.CreateReport();
		}
	},
	
	'NavBar': function(SeqNode, index, expectContent, iteration){
	    var othis = this;
	
	    // we don't want to add navigation for fasta_text format
        var report = this.getValue("report");       
        if (report != 'fasta_text' && report != 'ipg'){
            
            var seqid = jQuery(SeqNode).attr("val"); 
            
    	    // if this record has content
            if (jQuery(SeqNode).find('.localnav').html()){
                console.info('found localnav in iteration ' + iteration);
                jQuery(SeqNode).find('.localnav').each( function(lNavIndex){
                    var localNav = jQuery(this);
                    var prevnext = '';
                    var newNav = '';
                    
                    newNav = '<div class="hnav" id="hnav' + seqid + '_' + lNavIndex + '">' 
                        + '<div class="goto">' 
                        +    '<a href="#goto' + seqid + '_' + lNavIndex + '" class="tgt_dark jig-ncbipopper" config="' 
                               + "openMethod : 'click', closeMethod : 'click', destPosition: 'top left', adjustFit: 'none', triggerPosition: 'bottom left'"
                               + '"' + 'id="gotopopper' + seqid +  '_' + lNavIndex + '">Go to:</a>'
                        + '</div>' ;
                        
                    // add next previous
                    if (lNavIndex == 0){
                        prevnext = othis.NavBarPrevNext(index);
                    }
                    newNav += prevnext + '</div>';
                    var popper = '<div class="tabPopper nonstd_popper" style="display: none;" id="goto' + seqid +  '_' + lNavIndex + '"><ul class="locals">'
                     + othis.NavBarMenuContent(localNav)
                     + '</ul></div>'; 
                   
                    // replace content
                    localNav.replaceWith(newNav);
                    jQuery('#hnav' + seqid + '_' + lNavIndex).after(popper);
                    jQuery.ui.jig.scan(jQuery('#hnav' + seqid + '_' + lNavIndex));
                });                   
            }
            // if no existing navigation is present, but record is loaded, we add navigation
            else if (jQuery(SeqNode).find('pre').html()){
                console.info('found pre in iteration ' + iteration);
                var prevnext = '';
                var newNav = '';
                prevnext = this.NavBarPrevNext(index);
                if (prevnext != ''){
                    newNav = '<div class="hnav"><div class="goto"/>' + prevnext + '</div>';
                    // create nav before other content
                    jQuery(SeqNode).prepend(newNav); 
                }      	    
        	}
    	    // if we expect content in the record, but it is not available yet, we wait for the record to load
    	    else if (iteration <= 20 && expectContent){
    	        var oThis = this;
    	        setTimeout(function() { oThis.NavBar(SeqNode, index, expectContent, iteration + 1); }, 100);
    	    }
    	    // if we don't expect the record to have any content - just add prev/next. This is also the fall-back case
    	    else {
    	        console.info('default case prevnext only in iteration ' + iteration);
    	        var prevnext = '';
    	        var newNav = '';
    	        prevnext = this.NavBarPrevNext(index);
                if (prevnext != ''){
                    newNav = '<div class="hnav"><div class="goto"/>' + prevnext + '</div>';
                    // create nav before other content
                    jQuery(SeqNode).prepend(newNav); 
                }   	
    	    }
        } // report != fasta_text        
	},
	
	'NavBarPrevNext': function(index){
	    var prevNode = document.getElementById('viewercontent' + (index - 1));
	    var nextNode = document.getElementById('viewercontent' + (index + 1));
	    
	    if (prevNode || nextNode){
	        var prevnext = '<ul class="links inline_list_right">';
	        
	        if (prevNode){
	            var previd = jQuery(prevNode).attr("val");
	            var link = previd ? 'title' + previd : 'title_' + (index - 1);
	            prevnext += '<li><a href="#' + link + '">Previous record</a></li>';
	        }
	        if (nextNode){
	            var nextid = jQuery(nextNode).attr("val");
	            var link = nextid ? 'title' + nextid : 'title_' + (index + 1);
	            prevnext += '<li><a href="#' + link + '">Next record</a></li>';
	        }
	        prevnext += '</ul>';
	        return prevnext;
	    }
	    else return '';
	},
	
	'NavBarMenuContent': function(content){
	    var menucontent = ''; 
	    if (content.find('.nextprevlinks li.prev').html()){
	        content.find('.nextprevlinks li.prev a').text('Previous segment');
	        menucontent += '<li>' + content.find('.nextprevlinks li.prev').html() + '</li>';
	    }
	    if (content.find('.locals').html()){
	        menucontent += content.find('.locals').html();
	    }
	    if (content.find('.nextprevlinks li.next').html()){
	        content.find('.nextprevlinks li.next a').text('Next segment');
	        menucontent += '<li>' + content.find('.nextprevlinks li.next').html() + '</li>';
	    }
	    return menucontent;
	},
	
	'RemainingNavBarMenu': function(recordindex, iteration){
	    var othis = this;
	    var FlatFileNode = document.getElementById("viewercontent" + recordindex);
	    
	    if (jQuery(FlatFileNode).find('.localnav').html()){
	        var seqid = jQuery(FlatFileNode).attr("val"); 
	        
	        jQuery(FlatFileNode).find('.localnav').each( function(lNavIndex){
                var localNav = jQuery(this);
                var newNav = '';
                    
                newNav = '<div class="hnav" id="hnav' + seqid + '__' + lNavIndex + '">' 
                    + '<div class="goto">' 
                    +    '<a href="#goto' + seqid + '__' + lNavIndex + '" class="tgt_dark jig-ncbipopper" config="' 
                           + "openMethod : 'click', closeMethod : 'click', destPosition: 'bottom left', adjustFit: 'none', triggerPosition: 'bottom left'"
                           + '"' + 'id="gotopopper' + seqid +  '__' + lNavIndex + '">Go to:</a>'
                    + '</div></div>' ;
                        
                var popper = '<div class="tabPopper nonstd_popper" style="display: none;" id="goto' + seqid +  '_' + lNavIndex + '"><ul class="locals">'
                 + othis.NavBarMenuContent(localNav)
                 + '</ul></div>'; 
               
                // replace content
                localNav.replaceWith(newNav);
                jQuery('#hnav' + seqid + '__' + lNavIndex).after(popper);
                jQuery.ui.jig.scan(jQuery('#hnav' + seqid + '__' + lNavIndex));
            });    
	    }
	    else if (iteration <= 5){
            var oThis = this;
            setTimeout(function() { othis.RemainingNavBarMenu(recordindex, iteration + 1); }, 100);
    	}
	}
},

{
    InDownloadCycle: false,
    counter : 0,
    oRemoteDataProvider:new RemoteDataProvider("/sviewer/viewer.fcgi?"),
    displayLongRecord: false,
    master: '',
    regionAvailable: false,
    bitmasksAvailable: false,
    extrafeat: "",
    custom_view:"",
    itemid: '',
    protein_id: '',
    strand: '',
    comp: '',
    to: '',
    from: '',
    downloader: 'off',
    viewer: 'off',
    waiting: false,
    LoadSequenceWithMarkup: false
});



;
/*
*************************************************************************
$Id: seq_search_base.js 328365 2011-08-02 19:12:11Z sponomar $
Common code for the Portal and for the Sequence Viewer
*************************************************************************
*/
//oNotifier.bTraceOn = true;


// --------------------- Common code BEGIN ---------------------

/*
*************************************************************************
*************************************************************************
*/
function Seq_Search_Base() {
    this.NAME = "Seq_Search_Base";

    this.Ids = [];
    this.Totals = {};
    this.Acc = {};
    this.Offset = {};
    this.CurrentId = "";
    this.Current = 0;

    this.oNotifier = new Notifier();
    //    this.oNotifier.bTraceOn = true;

    // messages
    this.oNotifier.Search = 1;
    this.oNotifier.Clear = 2;
    this.oNotifier.DataIsReady = 3;
    this.oNotifier.Init = 4;
    this.oNotifier.SetCurrent = 5;
    this.oNotifier.Next = 6;
    this.oNotifier.First = 7;
    this.oNotifier.Previous = 8;
    this.oNotifier.Last = 9;
    this.oNotifier.ShowSearchBar = 10;
    this.oNotifier.ScrollTo = 12;
    this.oNotifier.NotFound = 13;
    this.oNotifier.Reset = 14;
    
    
    this.oNotifier.setListener(this, this.oNotifier.ScrollTo, function(x, sId) {
        var el = document.getElementById(sId);
        if (!el) {
            el = document.getElementsByName(sId);
            if (el[0]) el = el[0];
        }
        var y = utils.getXY(el).y;
        var iScrollY = utils.getScrolls().y;
        var iH = utils.getWindowDim().h;

        //        console.info(y, iScrollY, iH);

        if (y < iScrollY || y > iScrollY + iH) {
            window.scrollTo(0, y - 150);
        }
    });
}

/*
*************************************************************************
*************************************************************************
*/
Seq_Search_Base.prototype.CheckIfAllSequencesAreLoaded = function() {
    return true;
}

/*
*************************************************************************
*************************************************************************
*/
Seq_Search_Base.prototype.Init = function() {
    alert("You have to override that function");
}

/*
*************************************************************************
*************************************************************************
*/
Seq_Search_Base.prototype.Run = function(oGlobalNotifier) {
    var oThis = this;
    this.oGlobalNotifier = oGlobalNotifier;
    // ----------------------------------------------------------------------------------------
    this.oNotifier.setListener(this, this.oNotifier.Clear, function() {
        // clear previous search result
        x_Reset();
    });
    // ----------------------------------------------------------------------------------------
    this.oNotifier.setListener(this, this.oNotifier.Reset, function() {
        // clear previous search result
        x_Reset();
    });
    // ----------------------------------------------------------------------------------------
    function x_Reset() {
        oThis.Ids = [];
        oThis.Acc = {};
        oThis.Totals = {};
        oThis.Offset = {};
        oThis.CurrentId = "";
        oThis.Current = 0;
        oThis.Totals = {};
    }
}
/*
*************************************************************************
*************************************************************************
*/
Seq_Search_Base.prototype.Search = function() {
    if (this.CheckIfAllSequencesAreLoaded()) {
        this.oNotifier.Notify(this, this.oNotifier.Search);
    } else {
        setTimeout(function() { this.Search(); }, 1000);
    }
}


/*
*************************************************************************
*************************************************************************
*/
function Seq_SearchBar_Base(oSeqSearchData) {
}
/*
*************************************************************************
*************************************************************************
*/
Seq_SearchBar_Base.prototype.Run = function(SeqSearchData, elSearchBar) {
    this.SeqSearchData = SeqSearchData;
    this.elSearchBar = elSearchBar;
    this.oNotifier = this.SeqSearchData.oNotifier;
}

/*
*************************************************************************
*************************************************************************
*/
Seq_SearchBar_Base.prototype.SetListeners = function() {

    var oThis = this;

    //-----------------------------------------------------------------------------------------
    oThis.SeqSearchData.oGlobalNotifier.setListener(this, oThis.SeqSearchData.oGlobalNotifier.HideSearchBar, function() {
        utils.removeClass(document.body, "with-searchbar");
        oThis.elSearchBar.style.display = "none";
        oThis.oNotifier.Notify(this, oThis.oNotifier.Clear);
    });

    //-----------------------------------------------------------------------------------------
    this.oNotifier.setListener(this, this.oNotifier.First, function() {
        oThis.oNotifier.Notify(this, oThis.oNotifier.Previous);
    });

    //-----------------------------------------------------------------------------------------
    this.oNotifier.setListener(this, this.oNotifier.Last, function() {
        oThis.oNotifier.Notify(this, oThis.oNotifier.Next);
    });
}
/*
*************************************************************************
*************************************************************************
*/
Seq_SearchBar_Base.oTimeout = null;
Seq_SearchBar_Base.prototype.Transition = function(el) {
    var color = ["#985735", "#a86745", "#b87755", "#c88765", "#da8", "#ddc", "#eee"];
    len = color.length;
    var t = 1000 / len;
    var i = 0;
    function x_Transition() {
        el.style.backgroundColor = color[i++];
        if (i <= len) {
            if (Seq_SearchBar_Base.oTimeout) clearTimeout(Seq_SearchBar_Base.oTimeout);
            Seq_SearchBar_Base.oTimeout = setTimeout(x_Transition, t);
        }
        else el.style.backgroundColor = color[len -1];
    }
    x_Transition();
}

;
var oFeat_Highlight;
var oData;
Notifier.getInstance().setListener(this, "SEQUENCE_PART_LOADED", function(x, ItemsLeft) {
    if (ItemsLeft > 0) return;
//    console.info("SEQUENCE_PART_LOADED, ",ItemsLeft)
    // IE cannot run script which came with XHTTP request. FF does.
    setTimeout(function() {
        var a = document.querySelectorAll(".feature");
        if (a.length == 0) {
            a = document.querySelectorAll(".seq");
        }
        if (oFeat_Highlight) {
            delete oFeat_Highlight;
        }
        oData = [];
        
        var iGi, j = 0;
        for (var i = 0; i < a.length; ++i) {
        	var b = a[i].getElementsByTagName("script");
        	if (b && b[0]) {
        	    try {
        		    eval(b[0].innerHTML);
        		    var aa = b[0].parentNode.id.split("_");
        		    var iCurrentGi;
        		    if (aa.length == 5) { // feature_NM_131081.2_source_0
        		    	iCurrentGi = aa[1] + "_" + aa[2];
        		    } else {
            		    iCurrentGi = aa[1]; // feature_NM131081.2_source_0
        		    }
        		    if (iGi != iCurrentGi) {
        		        // because we removed Gi from script 'b[0]',
        		        // take Gis from node <span id="feature_<gi>_<number of feature>"
             	        iGi = iCurrentGi;
            	        oData[j++].gi = iGi;
            	    }
       		} catch (e) {
        		    ncbi.sg.ping({
                        jsevent:"sequenceFeature_loaderror", 
                        data: escape(b[0].innerHTML) 
                    });
        		}
        	}
        }
        console.info("oData=", oData);
        
        var x = Portal.Portlet.Sequence_ViewerReport;
        if (x.from > 1 || x.to > 1 || x.itemid > 0) return;

        if (document.getElementById("fh_bar")) {
            for (var i = 0; i < oData.length; ++i) {
                if (oData[i].features) {
                    // skip 'source' and 'gap'
                    for (var f in oData[i].features) {
                        if (f == "source" || f == "gap") continue;
                        // it looks we do have some features
                        oFeat_Highlight = new Feat_Search(oData);
                        return;
                    }
                }
            }
        }
    }, 200);
});

;
/*
*************************************************************************
URLs for test:
http://dev.ncbi.nlm.nih.gov/protein/6 - quick test
http://dev.ncbi.nlm.nih.gov/protein/146231940 - multisegment sites

http://dev.ncbi.nlm.nih.gov/protein/146231940?feature=Site:900 - highlight Site #42 
http://dev.ncbi.nlm.nih.gov/protein/6?feature=any - highlight first existing feature

http://dev.ncbi.nlm.nih.gov/nuccore/2 - sequence does not have any feature
http://dev.ncbi.nlm.nih.gov/nuccore/2,AC_000020?report=gbwithparts - first sequence does not have any feature

http://dev.ncbi.nlm.nih.gov/nuccore/1304378 - multiset sequence
http://dev.ncbi.nlm.nih.gov/nuccore/338770040 - pretty long sequence
http://dev.ncbi.nlm.nih.gov/nuccore/1304378 - very long sequence wich loaded part-by-part by ploader
http://dev.ncbi.nlm.nih.gov/nuccore/GL945016.1 - master record of contig

*************************************************************************
*/
function Feat_Search(oData) {
    this.constructor.call(this, oData);
    this.NAME = "Feat_Search";
	var aParams = utils.getParams(document.location.href.split("?")[1]);
    if (aParams["from"] || aParams["to"] || aParams["itemid"]) return;

    this.oNotifier.Highlight = 100;
    this.oNotifier.Update = 101;
    
    // [cds: [n, "acc", gi, [coords]], 
    this.oData = {};
    for (var i = 0; i < oData.length; ++i) {
        if (oData[i].features) {
            var d = oData[i];
            for (var f in d.features) {
                if ("gap" == f || "source" == f) continue;
                if (!this.oData[f]) this.oData[f] = [];
                for (var j = 0; j < d.features[f].length; ++j) {
                    var x = [];
                    x.push(j);
                    x.push(d.gi);
                    x.push(d.acc);
                    x.push(d.features[f][j]);
                    this.oData[f].push(x);
                }
            }
        }
    }
    
    this.sFeat = "";
    this.iFeat = 0;
    this.iTotal = 0;
    this.sCookieName = "feature_to_highlight";
    
    // &feature=<feature-name>:start[:stop]
    // http://dev.ncbi.nlm.nih.gov/protein/146231940?p$site=/projects/Sequences/SeqDbDev@1.3&report=genpept&feature=Site:46
    if (aParams["feature"] && oData.length == 1) {
	    this.sFeat = aParams["feature"].split("#")[0];
	    if (this.sFeat && this.sFeat != "any") {
	        var a = this.sFeat.split(":");
	        this.sFeat = a[0];
	        if (a[1] != undefined) {
	        	var aa = a[1].split("-");
	        	this.iStartFrom = aa[0];
	        	if (aa[1] != undefined)
	        		this.iStopTo = aa[1];
        		else 
        			this.iStopTo = 0;
	        } else
	        	this.iStartFrom = 0;
	    }
//	    console.info("sFeat=", this.sFeat, ", iStartFrom=", this.iStartFrom, ", iStopTo=", this.iStopTo);
	} else {
		var iGi, iFeat, sFeat;
		var s = utils.readCookie(this.sCookieName);		// feature_146231940_Site_27
		if (s > "") {
			var a = s.split("_");
			if (a.length >= 4) {
				iGi = parseInt(a[1]);
				iFeat = parseInt(a[a.length - 1]);
				var x = [];
				for (var i = 2; i < a.length - 1; ++i) x.push(a[i]);
				sFeat = x.join("_");
				
//				console.info("sFeat=", sFeat, " iGi=", iGi)
				if (this.oData[sFeat]) {
				    for (var i = 0; i < this.oData[sFeat].length; ++i) {
//				        console.info(i, this.oData[sFeat][i][0], iFeat, this.oData[sFeat][i][1], iGi)
				        if (this.oData[sFeat][i][0] == iFeat && this.oData[sFeat][i][1] == iGi) {
        					this.iFeat = i;
        					this.sFeat = sFeat;
        					break;
				        }
				    }
				}
			}
		}
//		console.info("cookie '", this.sCookieName, "'=", s, this.iFeat, this.sFeat);
	} 
	
	this.Run(Notifier.getInstance());
//	console.info('Feat_Search: this.sFeat=', this.sFeat, ', this.iFeat=', this.iFeat, oData)

}

/*
*************************************************************************
*************************************************************************
*/
Feat_Search.prototype.constructor = Seq_Search_Base;

/*
*************************************************************************
*************************************************************************
*/
Feat_Search.prototype.Run = function(oGlobalNotifier) {
//	console.info("Feat_Search.prototype.Run")
//console.info(this.oData)
    var oThis = this;
    this.constructor.prototype.Run.call(this, oGlobalNotifier);


    // ----------------------------------------------------------------------------------------
    if (this.oFeat_SearchHighligt) {
        for (var x in this.oFeat_SearchHighligt) delete this.oFeat_SearchHighligt[x];
        delete this.oFeat_SearchHighligt;
    }
    this.oFeat_SearchHighligt = new Feat_SearchHighligt(this);

    var elSearchBar = document.getElementById("fh_bar");
    if (elSearchBar) {
        if (this.oFeat_SearchBar) {
            for (var x in this.oFeat_SearchBar) delete this.oFeat_SearchBar[x];
            delete this.oFeat_SearchBar;
        }
        this.oFeat_SearchBar= new Feat_SearchBar();
        this.oFeat_SearchBar.Run(this, elSearchBar);
    }

    this.oNotifier.Notify(this, this.oNotifier.Clear);
    if (this.oData == {}) {
        this.oNotifier.Notify(this, this.oNotifier.NotFound);
    } else {
        this.oNotifier.Notify(this, this.oNotifier.DataIsReady);
        if (this.sFeat && this.iFeat >= 0) 
            this.oNotifier.Notify(this, this.oNotifier.Update);
    }
}

/*
*************************************************************************
*************************************************************************
*/
function Feat_SearchBar() {
    this.NAME = "Feat_SearchBar";
    var oThis = this;
}

Feat_SearchBar.prototype = new Seq_SearchBar_Base;
    
/*
*************************************************************************
*************************************************************************
*/
Feat_SearchBar.prototype.Run = function(SearchObj, elSearchBar) {
    var oThis = this;

    var elText = document.getElementById("fh_bar_text");
    var elNavCtrls = document.getElementById("feat_nav_control");
    var elSelect = document.getElementById("fh_bar_select");
    var elNext = document.getElementById("fh_bar_next");
    var elPrevious = document.getElementById("fh_bar_previous");
    var elFirst = document.getElementById("fh_bar_first");
    var elLast = document.getElementById("fh_bar_last");
    var elClear = document.getElementById("fh_bar_clear");
    var elHide = document.getElementById("fh_bar_hide");
    var elRange = document.getElementById("fh_bar_total");
    var elMessage = document.getElementById("fh_bar_message");
    var elWarning = document.getElementById("fh_bar_warning");
    var elHandler = document.getElementById("fh_handler");

    var elGenbank = document.getElementById("fh_bar_genbank");
    var elFasta = document.getElementById("fh_bar_fasta");

    var elDetailsBodyHandler = document.getElementById("fh_bar_details");
    var elDetailsBody = document.getElementById("fh_bar_details_body");
    
    var elGotoFeature = document.getElementById("fh_bar_to_feature");

    this.constructor.prototype.Run.call(this, SearchObj, elSearchBar);
    this.constructor.prototype.SetListeners.call(this);

    // ----------------------------------------------------------------------------------------
    function Update(iDir) {
//        console.info("SearchObj.iStartFrom=", SearchObj.iStartFrom);

        oThis.oNotifier.Notify(this, oThis.oNotifier.ShowSearchBar, iDir == 0);

        if (iDir == 1 || iDir == -1) {
            SearchObj.iFeat += iDir;
        } else if (SearchObj.iStartFrom > 0) {
            var b = true;
            // one sequence on the page and start position for given feature is set.
            var x = SearchObj.oData[SearchObj.sFeat];
            if (x) {
 //               console.info("SearchObj.iStartFrom=", SearchObj.iStartFrom,"SearchObj.iStopTo=", SearchObj.iStopTo, x);
            	if (SearchObj.iStopTo > 0 && SearchObj.iStartFrom > SearchObj.iStopTo) {
            		// reverse coordinates are set
            		var k = SearchObj.iStartFrom;
            		SearchObj.iStartFrom = SearchObj.iStopTo;
            		SearchObj.iStopTo = k;
            	}

				// try to find first feature which starts from or after iStartFrom 
                for (var i = 0; i < x.length; ++i) {
                    var a = x[i][3][0]; // first [start, stop]
                    var iFrom = a[0];
//                    console.info("i=", i, iFrom, SearchObj.iStartFrom)
                    if (iFrom >= SearchObj.iStartFrom) {
                    	// found it!
                        SearchObj.iFeat = i;
                        SearchObj.iStartFrom = iFrom;
                        b = false;
                        break;
                    }
                }
                if (b) {
                	// no any features started from or after iStartFrom found
                    SearchObj.iFeat = 0;
                    SearchObj.iStartFrom = 0;
                } else if (SearchObj.iStopTo > 0) {
                	// look at first feature which stops to or before iStopTo
                	for (var i = SearchObj.iFeat; i < x.length; ++i) {
                		var j = x[i][3].length - 1;
//                		console.info(x[i], x[i][3])
                		var iTo = x[i][3][j][1];
//                		console.info("j=", j, iTo)
                		if (iTo > SearchObj.iStopTo) {
                			// found next feature after one we looked for
                			if (SearchObj.iFeat < i - 1) SearchObj.iFeat = i - 1;
                			break;
                		}
                	}
                }
//                console.info("SearchObj.iStartFrom=", SearchObj.iStartFrom, "SearchObj.iStopTo=", SearchObj.iStopTo, ", SearchObj.iFeat=", SearchObj.iFeat);
            }
            SearchObj.iStartFrom = null; // we do not need it anymore - it has been used at first time.
        }


        if (SearchObj.sFeat == "any" || SearchObj.sFeat == "") {
            SearchObj.sFeat = elSelect.options[0].value;
        }

        var aFeat = SearchObj.oData[SearchObj.sFeat];

        if (!aFeat) {
            oThis.SeqSearchData.oGlobalNotifier.Notify(this, oThis.SeqSearchData.oGlobalNotifier.HideSearchBar);
            alert("Cannot find feature '" + SearchObj.sFeat + "'");
            SearchObj.sFeat = "";
            return;
        }

//    console.info("SearchObj.iFeat=", SearchObj.iFeat)

        if (SearchObj.iFeat <= 0) SearchObj.iFeat = 0;
        if (SearchObj.iFeat == 0) x_DisableFirst(); else x_EnableFirst();

        if (SearchObj.iFeat >= aFeat.length) SearchObj.iFeat = aFeat.length - 1;
        if (SearchObj.iFeat >= aFeat.length - 1 ) x_DisableLast(); else x_EnableLast();
        
        
        var aCurrFeat = aFeat[SearchObj.iFeat];
        var iSegments = aCurrFeat[3].length;
        var bIsComplement = aCurrFeat[3][0][0] > aCurrFeat[3][0][1];
        
        
        elRange.innerHTML = (1 + SearchObj.iFeat) + " of " + aFeat.length;
        elMessage.innerHTML = aCurrFeat[2]
            + " : " + iSegments + " segment" + utils.getPlural(iSegments)
            + (bIsComplement ? " (minus strand)" : "");
        var sFeatId = "feature_" + aCurrFeat[1] + "_" + SearchObj.sFeat + "_" + aCurrFeat[0];
        var elFeatSpan = document.getElementById(sFeatId);
        var elA = utils.getNextSibling(utils.getFirstChild(elFeatSpan));
        //        console.info(elA);
        var b = elA.href.indexOf("item") == -1; // no &itemID/itemid in the URL, see ID-4284
        elGenbank.href = elA.href + "&report=gbwithparts" + (b && bIsComplement ? "&strand=2" : "");
        elFasta.href = elA.href + "&report=fasta" + (b && bIsComplement ? "&strand=2" : "");
        elGotoFeature.href = "#" + sFeatId;
        
        utils.createCookie(SearchObj.sCookieName, sFeatId);
        x_RefreshDetails();

        oThis.oNotifier.Notify(this, oThis.oNotifier.Highlight, aCurrFeat[3]);
        return;


        // ----------------------------------------------------------------------------------------
        function x_DisableFirst() {
            utils.addClass(elFirst, "disabled");
            utils.addClass(elPrevious, "disabled");
            SearchObj.iFeat = 0;
        }

        // ----------------------------------------------------------------------------------------
        function x_EnableFirst() {
            if (utils.hasClass(elFirst, "disabled")) {
                utils.removeClass(elFirst, "disabled");
                utils.removeClass(elPrevious, "disabled");
            }
        }

        // ----------------------------------------------------------------------------------------
        function x_DisableLast() {
            utils.addClass(elLast, "disabled");
            utils.addClass(elNext, "disabled");
        }

        // ----------------------------------------------------------------------------------------
        function x_EnableLast() {
            utils.removeClass(elLast, "disabled");
            utils.removeClass(elNext, "disabled");
        }

    }
    // ----------------------------------------------------------------------------------------
    function x_UpdateDetails(el) {
        elDetailsBody.style.height = 0;
        elDetailsBody.innerHTML = "";
        var a = el.innerHTML.split("                    "); // 20 spaces
        var aa = a[0].split(" ");
        a[0] = aa[aa.length - 1];
        for (var i = 0; i < a.length; ++i) {
            var el = document.createElement("div");
            el.innerHTML = a[i];
            elDetailsBody.appendChild(el);
        }
        ncbi.sg.scanLinks();
 		x_RefreshDetails();
    }
    
        // ----------------------------------------------------------------------------------------
    function x_RefreshDetails() {
    	var el = utils.getParent(elDetailsBodyHandler);
        if (utils.hasClass(elDetailsBody, "is-hidden")) {
            utils.addClass(elDetailsBodyHandler, "tgt_dark_up");
            utils.removeClass(elDetailsBodyHandler, "tgt_dark");
            utils.addClass(el, "is-hidden");
            elDetailsBodyHandler.setAttribute("ref", "ref=discoid=featurehighlight&log$=featurehighlight&sectionAction=open");
            elDetailsBody.style.display = "none";
        } else {
            utils.removeClass(elDetailsBodyHandler, "tgt_dark_up");
            utils.addClass(elDetailsBodyHandler, "tgt_dark");
            utils.removeClass(el, "is-hidden");
            elDetailsBodyHandler.setAttribute("ref", "ref=discoid=featurehighlight&log$=featurehighlight&sectionAction=close");
			var w = 450;
	        var oPageDim = utils.getPageDim();
	        var x = oPageDim.w - w - 20;
	        elDetailsBody.style.left = x  + "px";
	        elDetailsBody.style.width = w + "px";
	        oDetailsBodyDim = utils.getPageDim(elDetailsBody);
	        var h = oDetailsBodyDim.h;
	        elDetailsBody.style.height = h + "px";
	        elDetailsBody.style.top = -(h + 15) + "px";
            elDetailsBody.style.display = "";
        }
    }
    

    // Listener started =======================================================================

    // ----------------------------------------------------------------------------------------
    this.oNotifier.setListener(this, this.oNotifier.Update, function() {
    	Update(0);
    	return true;
	});
    // ----------------------------------------------------------------------------------------
    this.oNotifier.setListener(this, this.oNotifier.ShowSearchBar, function(x, bWithTransitionEffect) {
    	var b = elSearchBar.style.display != "block";
        elSearchBar.style.display = "block";
        if (b && bWithTransitionEffect) oThis.Transition(elSearchBar);
        utils.addClass(document.body, "with-searchbar");
    });

    // ----------------------------------------------------------------------------------------
    this.oNotifier.setListener(this, this.oNotifier.Clear, function() {
    	elWarning.style.display = "none";
 		elWarning.innerHTML = "";
    });

    // ----------------------------------------------------------------------------------------
    this.oNotifier.setListener(this, this.oNotifier.NoSequence, function() {
 		elWarning.innerHTML = "Warning: Cannot highlight feature because no sequence is shown. "
 		+ "<a href='#' onclick=\"document.location.search += '&withparts=on&expand-gaps=on'\">Show the sequence</a>";
 		elWarning.style.display = "";
    });


    // ----------------------------------------------------------------------------------------
    this.oNotifier.setListener(this, this.oNotifier.DataIsReady, function() {
//        console.info("DataIsReady, ", SearchObj.oData.length);
        // get list of unique features for all sequences on the page
        // sort features case insensitive
        var a = [];
        for (var f in SearchObj.oData) a.push(f);
        
        a = a.sort(function(x,y){ 
	      var a = String(x).toUpperCase(); 
	      var b = String(y).toUpperCase(); 
	      if (a > b) return 1 
	      if (a < b) return -1 
	      return 0; 
	    });
        
        
        // create pop-up menu with features 
        utils.removeChildren(elSelect);
        for (var i = 0; i < a.length; ++i) {
        	if (a[i] == "source") continue;
            var el = document.createElement("option");
            el.innerHTML = a[i];
            el.setAttribute("value", a[i]);
            if (SearchObj.sFeat == a[i]) el.setAttribute("selected", "selected");
            elSelect.appendChild(el);
        }
        elMessage.innerHTML = "";
        utils.removeClass(elNavCtrls, "hide");

        if (SearchObj.iStartFrom > 0) Update(0);

        elDetailsBodyHandler.onclick = function(e) {
            e = e || event;
            utils.preventDefault(e);
            utils.toggleClass(elDetailsBody, "is-hidden");
            Update(0);
        };

        for (var sFeat in SearchObj.oData) {
//            console.info(sFeat);
            for (var i = 0; i < SearchObj.oData[sFeat].length; ++i) {
                var x = SearchObj.oData[sFeat][i];
                var iGi = x[1];
                var iFeatLocal = x[0];
                var s = "feature_" + iGi + "_" + sFeat + "_" + iFeatLocal;
                var el = document.getElementById(s);
                if (!el) continue;
                el = utils.getFirstChild(el);
                if (!el) continue;
                el = utils.getNextSibling(el, "a");
                if (!el) continue;
                el.setAttribute("igi", iGi);
                el.setAttribute("sfeat", sFeat);
                el.setAttribute("ifeat", i);
                el.setAttribute("ref", "discoid=featurehighlight&log$=featurehighlight");
                utils.addClass(el, "pseudolink");
                el.onclick = x_GotoFeature;
            }
        }

        // ----------------------------------------------------------------------------------------
        function x_GotoFeature(e) {
            e = e || event;
            utils.preventDefault(e);
            oThis.SeqSearchData.oGlobalNotifier.Notify(this, oThis.SeqSearchData.oGlobalNotifier.HideSearchBar);
            SearchObj.iFeat = parseInt(this.getAttribute("ifeat"));
            var sFeat = this.getAttribute("sfeat");
            if (SearchObj.sFeat != sFeat) {
                SearchObj.sFeat = sFeat;
                for (var i = 0; i < elSelect.options.length; ++i) {
                    var el = elSelect.options[i];
                    if (el.value == sFeat) {
                        el.setAttribute("selected", "selected");
                   } else 
                       el.removeAttribute("selected");
                }
            }

            var el = utils.getParent(this);
            x_UpdateDetails(el);
            SearchObj.iStartFrom = null;
//            console.info("Update x_GotoFeature")
            Update(0);
            return false;
        }

    });

    //-----------------------------------------------------------------------------------------
    this.oNotifier.setListener(this, this.oNotifier.Highlight, function(x, data) {
        var x = SearchObj.oData[SearchObj.sFeat][SearchObj.iFeat];
        var iGi = x[1];
        var iFeatLocal = x[0];
        var s = "feature_" + iGi + "_" + SearchObj.sFeat + "_" + iFeatLocal;
//        console.info(s);
        var el = document.getElementById(s);
        x_UpdateDetails(el);
    });


    // ----------------------------------------------------------------------------------------
    this.oNotifier.setListener(this, this.oNotifier.NotFound, function() {
        utils.removeChildren(elSelect);
        var el = utils.getParent(elSelect);
        utils.removeChildren(el);
        el.innerHTML = "No feature is found";
    });


    // ----------------------------------------------------------------------------------------
    this.oNotifier.setListener(this, this.oNotifier.Next, function() {
        Update(1);
    });

    // ----------------------------------------------------------------------------------------
    this.oNotifier.setListener(this, this.oNotifier.Previous, function() {
        Update(-1);
    });

    // Listeners ended =========================================================================

    // Events started ==========================================================================
	// all events have to be set only once!
    //-----------------------------------------------------------------------------------------
    if (elHandler) elHandler.onclick = function(e) {
        e = e || event;
        utils.preventDefault(e);
        oThis.oNotifier.Notify(this, oThis.oNotifier.Clear);
        SearchObj.oGlobalNotifier.Notify(this, SearchObj.oGlobalNotifier.HideSearchBar);
        oThis.oNotifier.Notify(this, oThis.oNotifier.ShowSearchBar, true); // show with transition effect
    };

    //-----------------------------------------------------------------------------------------
    elSelect.onchange = function(e) {
        e = e || event;
        utils.preventDefault(e);
        
        SearchObj.sFeat = this.options[this.selectedIndex].value;
        Update(0);
        var x = SearchObj.oData[SearchObj.sFeat][SearchObj.iFeat];
        
        var obj = {jsevent:"fh_bar_menuchange"
        	, ncbi_uid:x[1] 
        	, ncbi_accn:x[2] 
        	, feature_type:SearchObj.sFeat}; 
        ncbi.sg.ping(obj);
    };

    //-----------------------------------------------------------------------------------------
    elNext.onclick = function(e) {
        e = e || event;
        utils.preventDefault(e);
        if (!utils.hasClass(this, "disabled"))
            oThis.oNotifier.Notify(this, oThis.oNotifier.Next);
    };

    //-----------------------------------------------------------------------------------------
    elPrevious.onclick = function(e) {
        e = e || event;
        utils.preventDefault(e);
        if (!utils.hasClass(this, "disabled"))
            oThis.oNotifier.Notify(this, oThis.oNotifier.Previous);
    };

    //-----------------------------------------------------------------------------------------
    elFirst.onclick = function(e) {
        e = e || event;
        utils.preventDefault(e);
        if (utils.hasClass(this, "disabled")) return;
        SearchObj.iFeat = 0;
        oThis.oNotifier.Notify(this, oThis.oNotifier.First);
    };

    //-----------------------------------------------------------------------------------------
    elLast.onclick = function(e) {
        e = e || event;
        utils.preventDefault(e);
        if (utils.hasClass(this, "disabled")) return;
        SearchObj.iFeat = SearchObj.oData[SearchObj.sFeat].length - 1;
//        console.info("SearchObj.iFeat=", SearchObj.iFeat)
        oThis.oNotifier.Notify(this, oThis.oNotifier.Last);
    };

    //-----------------------------------------------------------------------------------------
   elHide.onclick = function(e) {
        e = e || event;
        utils.preventDefault(e);
        oThis.oNotifier.Notify(this, oThis.oNotifier.Clear);
        utils.eraseCookie(SearchObj.sCookieName, true);
        SearchObj.oGlobalNotifier.Notify(this, SearchObj.oGlobalNotifier.HideSearchBar);
    };
}


/*
*************************************************************************
*************************************************************************
*/
function Feat_SearchHighligt(SearchObj) {
    this.NAME = "Seq_SearchHighligt";
    var oThis = this;
    var oNotifier = SearchObj.oNotifier;

    var Cache = {};
    var iLineLength = 60;

    //-----------------------------------------------------------------------------------------
    oNotifier.setListener(this, oNotifier.Clear, function(x, a) {
//      restore original content from cahce
        var el;
        for (var id in Cache) {
            el = document.getElementById(id);
            if (el) el.innerHTML = Cache[id];
        }
        Cache = {};
    });
    

    //-----------------------------------------------------------------------------------------
    oNotifier.setListener(this, oNotifier.Highlight, function(x, a) {
        oNotifier.Notify(this, oNotifier.Clear);
//        console.info(SearchObj.oData)
        var el;        
        var sId = SearchObj.oData[SearchObj.sFeat][SearchObj.iFeat][1] + "_";
//        console.info("sId=", sId)
        var sText = "";
        var sLinId = "";
        var sBuff = "";
        var prev_stop = 0;
        for (var i = 0; i < a.length; ++i) {
            var start = a[i][0];
            var stop = a[i][1];
            if (start > stop) {
                var xx = start; start = stop; stop = xx;
            }
            var iStart = Math.floor((start - 1) / iLineLength) * iLineLength + 1;
            var iStop = Math.floor((stop - 1) / iLineLength) * iLineLength + 1;
            
            //console.info("iStart=", iStart, ", iStop=" , iStop);

            for (var j = iStart; j <= iStop; j += iLineLength) {
                var sNewLineId = sId + j;
                //console.info("sNewLineId=", sNewLineId)
                if(!document.getElementById(sNewLineId)) {
                	/* see ID-4512
                	// https://dev.ncbi.nlm.nih.gov/nuccore/AH003527.2?&feature=CDS
                	4441 cttgtacatg gaaatgtcct gtttac                                     
                    [gap 100 bp]    Expand Ns
                    4567       tcct cattcatcat tgtttctttt cacatagaac aagtgtttcc cttgtccaag               	
                	*/                	
                	var b = false;
                	for(var k = j; k < j + iLineLength && k <= iStop; k++) {
                		//console.info(sId+ k, document.getElementById(sId + k));
                		b = !!document.getElementById(sId + k);
                		if (b) break;
                	}
                	if (b) {
                		sNewLineId = sId + k;
                	} else {
	                	oNotifier.Notify(this, oNotifier.NoSequence);
	                	return;
                	}
                }
                if (sNewLineId != sLinId) {
                    // flush buffered data
                    if (el) el.innerHTML = sBuff + sText;

                    sLinId = sNewLineId;
                    el = document.getElementById(sLinId);
                    sText = el.innerHTML;
                    Cache[sLinId] = sText;
                    sBuff = "";
                    prev_stop = 0;
                }

//                console.info("segment=", i, ", line_id=", j, ", strat=", start, ", stop=", stop, ", prev_stop=", prev_stop);
//                console.info(sText);

                if (start <= j && stop >= j + iLineLength) {
                    // whole line should be highlighted
                    sBuff = "<span class='feat_h'>" + sText + "</span>";
                    sText = "";
                } else {
                    var s1, s2;
                    var k1 = start - j;
                    var k2 = stop - j + 1;
                    if (k2 > j + iLineLength) k2 = iLineLength;
                    k2 += Math.floor(k2 / 10) - prev_stop;

//                    console.info("k1=", k1, ", k2=", k2, ", prev_stop=", prev_stop);

                    if (k1 > 0) {
                        k1 += Math.floor(k1 / 10) - prev_stop;
                        s1 = sText.substr(0, k1);
                    } else {
                        k1 = 0;
                        s1 = "";
                    }

                    s2 = sText.substr(k1, k2 - k1);
                    sText = sText.substr(k2, sText.length);
                    prev_stop += k2;

//                    console.info("s1='" + s1 + "' s2='" + s2 + "', sText='" + sText + "'");
                    sBuff += s1
                        + (s2 != "" ? "<span class='feat_h'>"
                        + (s2[s2.length - 1] == " " ? s2.substr(0, s2.length - 1) + "</span>" + " " : s2 + "</span>")
                          : "");
//                    console.info("sBuff=", sBuff);

                }
            }
            if (sBuff) el.innerHTML = sBuff + sText;
            oNotifier.Notify(this, oNotifier.ScrollTo, sId + iStart);
        }
    });

}
   
// --------------------- Common code END ---------------------



