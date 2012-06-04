

$(document).ready(function(){
        player=$('#vid').get(0);
        $(document).on('change', '#subfselect', function(e){
        	e.preventDefault();
        	submitSubtitleForm(e);
        });
        
        $('#vselect').change(function(){
        	resetPlayerButtons();
        	setVideoSrc(player);
        	clearResults();
        	hideResults();
        	
        	});
        
        $('.video_play a').click(function(e){
        	playVideo(player);
        	//return false;
        	e.preventDefault();
        	});
        
        $('.video_pause a').click(function(e){
        	pauseVideo(player);
        	e.preventDefault();
        	});
        
        $('#kwsearch').click(function(e){
        	searchInSubtitles();
        	e.preventDefault();
        	});
        
        $(document).on('click', '.mylinkclass', function(e) {
            getLinkText(this,player);
            e.preventDefault();
        });
    });

function submitSubtitleForm(e){
	var form = $('#subfileform').get(0);
	var formData = new FormData(form);
	//console.log('submitSubtitleForm():formData');
	var file = $('#subfselect').get(0).files[0];
	//console.log('submitSubtitleForm():file=',file.name);
	var xhr = new XMLHttpRequest();
	formData.append('file', file);
	xhr.open('POST', 'upload/', true);//async
	xhr.send(formData);
	
	xhr.onreadystatechange=function(){
	   if (xhr.readyState==4 && xhr.status==200){
	      var data = $.parseJSON(xhr.responseText);
	      var uploadResult = data['store_message']
	      //console.log('uploadResult=',uploadResult);
	      
	      if (uploadResult=='failure'){
	         //console.log('failed to upload file');
	         displayErrorMessage('failed to upload');
	      }else if (uploadResult=='success'){
	         //console.log('successfully uploaded file');
	      }
	   }
	}
	
}

/*
var doneAjaxUpload = function(res, status) {
    if (status == "success"){
      //console.log("name sent");
    }else{
      //console.log("failed to send name");
      displayErrorMessage("failed to upload");
    }
};
*/
function resetPlayerButtons(){
	//set play,pause buttons to normal
	$('.video_play a').removeClass('active');
	$('.video_pause a').removeClass('active');
}

//set video current time to clicked links's timevalue
function getLinkText(that,player){
	var txt = $(that).text();
	//console.log('txt=',txt);
	var time = parseInt(txt);
	//console.log('time=',time);
	player.currentTime = time;
	//TODO:check why player goes to 42s when link to 102s clicked
	return;
}

//call django view to search
function searchInSubtitles(){
	var keywords = $('#kwords').val();
	if (keywords !=""){
		$('#errorfld').html('');
		var data = {kwords:keywords}
		var args = { type:"POST", url:"search/", data:data, complete:showSearchResults };
		$.ajax(args);
	}else{
		$('#results').html('');
		hideElement('results');
		$('#errorfld').html('enter keywords');
		
	}
}

function showElement(elementId){
    var elem_selector='#'+elementId;
    $(elem_selector).show();
    
}

function hideElement(elementId){
    var elem_selector='#'+elementId;
    $(elem_selector).hide();
   
}

function clearResults(){
	$('#results').html('');
}

function hideResults(){
	hideElement('results');
}

function showSearchDiv(){
	showElement('searchdiv');
}

function hideSearchDiv(){
	hideElement('searchdiv');
}

//list the search results 
var showSearchResults = function(res,status){
	if (status == "success"){
		var data = $.parseJSON(res.responseText);
		var results = data['results']
		
		var formatedResult = "";
		for(var item in results) {
			var time = results[item][1];
			//console.log('time='+time);
			var resStr =results[item][0];
			//console.log('resStr='+resStr);
			formatedResult +='<a href="#" class="mylinkclass">'+ time +'</a>' + " : " + resStr +'<br>';
		}
		//console.log('formatedResult='+formatedResult);
		displayResults(formatedResult);
		
	    }else{
	    	var data = $.parseJSON(res.responseText);
	    	var msg = data['msg']
	    	displayErrorMessage(msg);
	    }
};

function displayResults(result){
	$('#results').html(result);
	showElement('results');
	$('#errorfld').html('');
	return;
}

function displayErrorMessage(msg){
	$('#results').html('');
	hideElement('results');
	$('#errorfld').html(msg);
}

//tell django about video file's name
function sendFileName(){
	var file = $('#vselect').get(0).files[0];
    //console.log('filename='+file.name)
    var data = { name:file.name };
    var args = { type:"POST", url:"sendname/", data:data, complete:done };
    $.ajax(args);
}
var done = function(res, status) {
    if (status == "success"){
      //console.log("name sent");
    }else{
      //console.log("failed to send name");
      displayErrorMessage("failed to send name");
    }
};




function checkCanPlay(player,file){
	var type = file.type;
	//console.log('type=',type);
	var canPlay = player.canPlayType(type);
	//console.log('canPlay=',canPlay);
	if (canPlay==''){
		return false;
	}else{
		return true;
	}
		
}

function setVideoSrc(player){
	var file = $('#vselect').get(0).files[0];
	
	var canPlay = checkCanPlay(player,file);
    //console.log('you chose:'+file);
    if ((!canPlay)||(file == undefined) ){
        //console.log('no file chosen');
    	displayErrorMessage('select a supported video');
    	hideSearchDiv();
    	player.src = '';
     }else{
    	 var myURL = window.URL || window.webkitURL;
    	 //console.log('winurl='+myURL);
    	 var fileURL = myURL.createObjectURL(file);
    	 //console.log('fileURL='+fileURL);
    	 if(fileURL){
    		 player.src=fileURL;
    		 player.load();
    		 showSearchDiv();
    		 $('#errorfld').html('');
    		 sendFileName();
    	 }
     }
    return;
}
    
function playVideo(player) {
     if(player.paused){
        player.play();
        $('.video_play a').addClass('active');
        $('.video_pause a').removeClass('active');
     }
}

//if vid is playing,pause it
function pauseVideo(player) {
     if (!(player.paused)){
        player.pause();
        $('.video_pause a').addClass('active');
        $('.video_play a').removeClass('active');
     }
}

//video currenttime to 20 secs
function jumpToTime20(player){
    //$("#vid").get(0).currentTime=20;
	player.currentTime=20;
}

//needed for csrf 
$(document).ajaxSend(function(event, xhr, settings) {
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    function sameOrigin(url) {
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }
    function safeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    }
});

