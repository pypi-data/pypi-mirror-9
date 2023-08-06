/*!
 * sws_utils 
 * Version 0.1 
 * Pedro Ten
 * @requires jQuery v1.2.3 or later
 */


// Gets or sets the outer html of a jQuery element
jQuery.fn.outerHTML = function(s) {
return (s)
? this.before(s).remove()
: jQuery("&lt;p&gt;").append(this.eq(0).clone()).html();
}

// Returns an array of start date and end date based on a given period 
function getDatePeriods(period){
	/**
	 * My comment starts here.asdf
	 * This is the second line prefixed with a `*`.
	 * ...
	 * ...
	 * All the follwing line will be prefixed with a `*` followed by a space.sadfASDFASDF
	 * ...
	 * ...
	 */
	var d = new Date(curtime);
	var now = new Date();

	var gmtHours = -d.getTimezoneOffset()/60;
	var from_day, from_month, from_year, from_time;
	var to_day, to_month, to_year, to_time;

	switch(period){
		case "1h":
			from_day = now.getDate(); 
			from_month =  parseInt(now.getMonth()+1) ; 
			from_year =  now.getFullYear(); 
			from_time = ('0'+now.getHours()).slice(-2) -1 + ':' + ('0'+now.getMinutes()).slice(-2) + ':' + ('0'+now.getSeconds()).slice(-2);
			to_day = now.getDate(); 
			to_month =  parseInt(now.getMonth()+1) ; 
			to_year =  now.getFullYear(); 
			to_time =  ('0'+now.getHours()).slice(-2) + ':' + ('0'+now.getMinutes()).slice(-2) + ':' + ('0'+now.getSeconds()).slice(-2);
			break;

		case "2h":
			from_day = now.getDate(); 
			from_month =  parseInt(now.getMonth()+1) ; 
			from_year =  now.getFullYear(); 
			from_time = ('0'+now.getHours()).slice(-2) -2 + ':' + ('0'+now.getMinutes()).slice(-2) + ':' + ('0'+now.getSeconds()).slice(-2);
			to_day = now.getDate(); 
			to_month =  parseInt(now.getMonth()+1) ; 
			to_year =  now.getFullYear(); 
			to_time =  ('0'+now.getHours()).slice(-2) + ':' + ('0'+now.getMinutes()).slice(-2) + ':' + ('0'+now.getSeconds()).slice(-2);
			break;

		case "3h":
			from_day = now.getDate(); 
			from_month =  parseInt(d.getMonth()+1) ; 
			from_year =  now.getFullYear(); 
			from_time = ('0'+now.getHours()).slice(-2) -3 + ':' + ('0'+now.getMinutes()).slice(-2) + ':' + ('0'+now.getSeconds()).slice(-2);
			to_day = now.getDate(); 
			to_month =  parseInt(now.getMonth()+1) ; 
			to_year =  now.getFullYear(); 
			to_time =  ('0'+now.getHours()).slice(-2) + ':' + ('0'+now.getMinutes()).slice(-2) + ':' + ('0'+now.getSeconds()).slice(-2);
			break;

		case "24h":
			from_day = now.getDate() -1; 
			from_month =  parseInt(d.getMonth()+1) ; 
			from_year =  now.getFullYear(); 
			from_time = ('0'+now.getHours()).slice(-2) + ':' + ('0'+now.getMinutes()).slice(-2) + ':' + ('0'+now.getSeconds()).slice(-2);
			to_day = now.getDate(); 
			to_month =  parseInt(now.getMonth()+1) ; 
			to_year =  now.getFullYear(); 
			to_time =  ('0'+now.getHours()).slice(-2) + ':' + ('0'+now.getMinutes()).slice(-2) + ':' + ('0'+now.getSeconds()).slice(-2);
			break;

		case "today":
			from_day = d.getDate(); from_month =  parseInt(d.getMonth()+1) ; from_year =  d.getFullYear(); from_time = "00:00:00";
			to_day = d.getDate(); to_month =  parseInt(d.getMonth()+1) ; to_year =  d.getFullYear(); to_time =  "23:59:59";
			break;
		case "yesterday": 
			d.setDate(d.getDate() - 1);
			from_day = d.getDate(); from_month =  parseInt(d.getMonth()+1) ; from_year =  d.getFullYear(); from_time = "00:00:00";
			to_day = d.getDate(); to_month =  parseInt(d.getMonth()+1) ; to_year =  d.getFullYear(); to_time = "23:59:59";
			break;
		case "week":
			to_day = d.getDate(); to_month =  parseInt(d.getMonth()+1) ; to_year =  d.getFullYear(); to_time =  "23:59:59";
			// Find last monday!
			if(d.getDay() != 1) while(d.getDay() != 1) d.setDate(d.getDate() - 1);  
			from_day = d.getDate(); from_month =  parseInt(d.getMonth()+1) ; from_year =  d.getFullYear(); from_time = "00:00:00";             
			break;
		case "month":
			to_day = d.getDate(); to_month =  parseInt(d.getMonth()+1) ; to_year =  d.getFullYear(); to_time =  "23:59:59";
			from_day = "01"; from_month =  parseInt(d.getMonth()+1) ; from_year =  d.getFullYear(); from_time = "00:00:00";
			break
		case "pweek":
			// Find last last monday
			while(d.getDay() != 1) d.setDate(d.getDate() - 1);
			d.setDate(d.getDate() - 1)
			while(d.getDay() != 1) d.setDate(d.getDate() - 1);
			from_day = d.getDate(); from_month =  parseInt(d.getMonth()+1) ; from_year =  d.getFullYear(); from_time = "00:00:00";             
			d.setDate(d.getDate() + 6);
			to_day = d.getDate(); to_month =  parseInt(d.getMonth()+1) ; to_year =  d.getFullYear(); to_time = "23:59:59";
			break;      
		case "pmonth":
			// Last day of the previous month 
			d.setDate(d.getDate() - (d.getDate()+1))
			var tempdate = new Date(d.getFullYear(),d.getMonth()+1,0)
			to_day = tempdate.getDate(); to_month =  parseInt(d.getMonth()+1) ; to_year =  d.getFullYear(); to_time = "23:59:59";
			from_day = "01"; from_month =  parseInt(d.getMonth()+1) ; from_year =  d.getFullYear(); from_time = "00:00:00";
			break;
		case "lastseven":
			d.setDate(d.getDate() - 1)
			to_day = d.getDate(); to_month =  parseInt(d.getMonth()+1) ; to_year =  d.getFullYear(); to_time = "23:59:59";
			d.setDate(d.getDate() - 7)
			from_day = d.getDate(); from_month =  parseInt(d.getMonth()+1) ; from_year =  d.getFullYear(); from_time = "00:00:00";             
			break;
		case "lastthirty":
			d.setDate(d.getDate() - 1)
			to_day = d.getDate(); to_month =  parseInt(d.getMonth()+1) ; to_year =  d.getFullYear(); to_time = "23:59:59";
			d.setDate(d.getDate() - 30)
			from_day = d.getDate(); from_month =  parseInt(d.getMonth()+1) ; from_year =  d.getFullYear(); from_time = "00:00:00";             
			break;
		case "p3month":
			d.setDate(d.getDate() - (d.getDate()+1))
			var tempdate = new Date(d.getFullYear(),d.getMonth()+1,0)
			to_day = tempdate.getDate(); to_month =  parseInt(d.getMonth()+1) ; to_year =  d.getFullYear(); to_time = "23:59:59";
			
			if((d.getMonth()+1) > 3){
				tempdate = new Date (tempdate.getFullYear,tempdate.getMonth()-2,0)
				from_day = "01"; from_month = d.getMonth() - 2; from_year = d.getYear(); from_time = "00:00:00";
			}
			else{
				from_month = parseInt(tempdate.getMonth() + 1) + 10
				from_year = parseInt(tempdate.getFullYear()) - 1                
				var tempdate = new Date(to_year,to_month,0)
				from_day = "01"
				from_time = "00:00:00"
				to_time = "23:59:59"
			}
			break;
			
		case "p6month":
			d.setDate(d.getDate() - (d.getDate()+1))
			var tempdate = new Date(d.getFullYear(),d.getMonth()+1,0)
			to_day = tempdate.getDate(); to_month =  parseInt(d.getMonth()+1) ; to_year =  d.getFullYear(); to_time = "23:59:59";
		
			if((d.getMonth()+1) > 6){
				tempdate = new Date (tempdate.getFullYear,tempdate.getMonth()-5,0)
				from_day = "01"; from_month = d.getMonth() - 2; from_year = d.getYear(); from_time = "00:00:00";
			}
			else{
				from_month = parseInt(tempdate.getMonth() + 1) + 7
				from_year = parseInt(tempdate.getFullYear()) - 1                
				from_day = "01"
				from_time = "00:00:00"
			}
			break;
		case "monthplustwo":
			from_day = "01"; from_month =  parseInt(d.getMonth()+1) ; from_year =  d.getFullYear(); from_time = "00:00:00";
			d = d.setDate(d.getDate()+60)
			to_day = d.getDate(); to_month =  parseInt(d.getMonth()+1) ; to_year =  d.getFullYear(); to_time =  "23:59:59";
			break;

		}
	if(from_month == 13 ){
		from_month = 1
		from_year = from_year + 1
	}
	return [from_year, from_month, from_day, from_time, to_year, to_month, to_day, to_time]
}

// Checks if a password is valid, numbers and letters and length
function isValidPassword(pass,length){
	if(pass.length >= length && pass.search(/\d/g) != -1 && pass.search(/\D/g) != -1) return true;
	else return false;
}

function createMessagesContainer(){

	// // Messages code
	html_messages = "<div id='main_result_messages' class='result_messages'></div>";
	$('#main_tabs_ul').append("<li id='show_messages_tab'><input id='main_show_messages_btn' type='button' value='Show Messages' role='button'/></li>");
	$('#main_tabs_ul').after(html_messages);
	$('#main_show_messages_btn').button();
	
	$('#main_tabs_ul').append("<p class='clear-fix'></p>");
}

function createProgressBarsContainer(){
	html_progressbar = "<div id='progressbar'></div>";
	$('#main_tabs_ul').after(html_progressbar);
	
}

function createLocalStorage(user_session_id){
	// // Clears and creates localStorage
	if(!localStorage.userSession){
		localStorage.clear();
		localStorage.userSession = JSON.stringify([{'id':user_session_id}]);
		localStorage.messages = JSON.stringify([]);
	} else {
		var stored_session = JSON.parse(localStorage["userSession"]);
		if(user_session_id != stored_session[0]['id']){
			localStorage.clear();
			localStorage.userSession = JSON.stringify([{'id':user_session_id}]);
			localStorage.messages = JSON.stringify([]);
		}
	}	
}

function setDeleteButtons(){
	//  Here we link delete buttons to the delete function (from local storage and vissualy we delete that node)
	$('.delete_msg_link').click(function(){
		id=$(this).parent().parent().attr('id');
		$(this).parent().parent().hide();

		// Delete messages from local storage
		var changes = JSON.parse(localStorage["messages"]);
		var to_delete = Array();
		changes.forEach(function(change){
			if (id == change.id){
				to_delete.push(change);
			}
		});
		for (i=0;i<to_delete.length;i++){
			changes.splice($.inArray(to_delete[i], changes),1);
		}

		if(changes.length == 0){
			$('#main_result_messages').html("<div id='msg_local_info_' class='messages_return info'><p>No Messages</p></div>");
		}
		localStorage['messages'] = JSON.stringify(changes);
	});

	addDeleteAllMessagesButton();
}

// Function to add a button that removes all messages with one click
function addDeleteAllMessagesButton(){
	$('#main_result_messages').prepend('<input type="button" name="deleteAllMessagesButton" value="X" id="deleteAllMessagesButton">');
	$('#deleteAllMessagesButton').click(function(){
		var msgs = JSON.parse(localStorage["messages"]);
		msgs.splice(0,msgs.length);
		localStorage['messages'] = JSON.stringify(msgs);
		$('#main_result_messages').html("<div id='msg_local_info_' class='messages_return info'><p>No Messages</p></div>");
		addDeleteAllMessagesButton();
	});
}

// NEW, with different parameters (close is for auto-folding the messages container )
function setClickToMessages(){
	$('#main_show_messages_btn').click(function(){
		$('#main_result_messages').html(' ');

		if($(this).attr('value') == "Show Messages"){
			$(this).attr('value', "Hide Messages");
			var stored_messages = JSON.parse(localStorage["messages"]);

			if(stored_messages.length == 0){
				$('#main_result_messages').html("<div id='msg_local_info_' class='messages_return info'><p>No Messages</p></div>");
			}
			else{
				for (j=0; j<stored_messages.length;j++) {
					$('#main_result_messages').prepend('<div id="'+stored_messages[j]['id']+'" class="messages_return '+stored_messages[j]['type']+'"><p>' + stored_messages[j]['text']+'</p></div>');
				}
			}
			$('#main_result_messages').slideDown();

			setDeleteButtons();
			
		} 
		else if($(this).attr('value') == "Hide Messages"){
			$(this).attr('value', "Show Messages");
			$('#main_result_messages').slideUp();	
			$('#main_result_messages').html('');
		}
	});
}

function openCloseMessagesDiv(time){
	// addDeleteAllMessagesButton();

	if($('#main_show_messages_btn').val() == 'Show Messages'){
		$('#main_result_messages').fadeIn();
		$('#main_show_messages_btn').val('Hide Messages');
		// alert('changed btn val...');
		// alert('in 5 secs slideUp...');
	}
	setTimeout(function() {
			$('#main_result_messages').slideUp(function(){
				$('#main_show_messages_btn').val('Show Messages');
			});
		}, time);
}

// Shows and hides messages return in ajax  
// (OLD, now we don't use ID parameter... we still leave it for now, since many calls to this function are still around the code) 
function showMessages(id, messages, time) {

	if(time == null){
		time = 5000;
	}

	if (messages.length > 0){
		// Messages of localStorage
		var stored_messages = JSON.parse(localStorage["messages"]);

		$('#main_result_messages').html(' ');

		for (j=0; j<messages.length;j++) {
			for (key in messages[j]) {
				// Adds message to stored_messages
				now = new Date();
				stored_messages.push({'id':'msg_item_'+(stored_messages.length), 'text':' '+now.getFullYear()+'/'+('0'+(now.getMonth()+1)).slice(-2)+'/'+('0'+now.getDate()).slice(-2)+' '+('0'+now.getHours()).slice(-2)+':'+('0'+now.getMinutes()).slice(-2)+':'+('0'+now.getSeconds()).slice(-2)+'  '+messages[j][key][0]+'<span class="delete_msg_link">delete</span>', 'view':'test_view', 'type':key});
			}
		}

		for(i=0; i<stored_messages.length;i++){
			$('#main_result_messages').prepend('<div id="'+stored_messages[i]['id']+'" class="messages_return '+stored_messages[i]['type']+'"><p>'
					+ stored_messages[i]['text'] +'</p></div>');
		}

		// openCloseMessagesDiv();
		displayMiniNotification(messages, time);

		// Stores messages in localStorage 
		localStorage["messages"] = JSON.stringify(stored_messages);

		setDeleteButtons();
	}
}

var mini_notification_timer;

function displayMiniNotification(messages, time){

	clearTimeout(mini_notification_timer);
	
	// $('#mini_notification').html('');
	for (j=0; j<messages.length;j++) {
		for (key in messages[j]){
			$('#mini_notification').prepend('<p class="'+key+'">'+messages[j][key][0]+'</p>');
			// $('#boxclose').after('<p class="'+key+'">'+messages[j][key][0]+'</p>');
		}
	}

	deleteOldNotifications();

	if(!checkNotificationStatus()){
		$('#mini_notification').toggleClass('not_showed_notification').toggleClass('showed_notification');
	}
	mini_notification_timer = setTimeout(function() {
		// $('#mini_notification').slideUp('slow');
		$('#mini_notification').toggleClass('not_showed_notification').toggleClass('showed_notification');
	}, time);
	// else{
	// 	$('#mini_notification').toggleClass('not_showed_notification').toggleClass('showed_notification');	
	// }
	
	// $('#mini_notification').slideDown('slow');
	// $('#mini_notification').toggleClass('not_showed_notification').toggleClass('showed_notification');
}

function displayLocalMiniNotification(message, type, time){

	clearTimeout(mini_notification_timer);
	
	// $('#mini_notification').html('');
	$('#mini_notification').prepend('<p class="'+type+'">'+message+'</p>');

	deleteOldNotifications();

	if(!checkNotificationStatus()){
		$('#mini_notification').toggleClass('not_showed_notification').toggleClass('showed_notification');			
	}
	mini_notification_timer = setTimeout(function() {
		// $('#mini_notification').slideUp('slow');
		$('#mini_notification').toggleClass('not_showed_notification').toggleClass('showed_notification');			
	}, time);
	// else{
	// 	$('#mini_notification').toggleClass('not_showed_notification').toggleClass('showed_notification');				
	// }

	// $('#mini_notification').slideDown('slow');
}

function deleteOldNotifications(){
	while($('#mini_notification').children().length > 3){
		($('#mini_notification').children()[$('#mini_notification').children().length - 1]).remove()
	}
}

// function deleteOldNotifications(){
// 	while($('#mini_notification').children().length > 5){
// 		c = $($('#mini_notification').children()[$('#mini_notification').children().length - 1])
// 		if(c.attr('class') != 'boxclose'){
// 			c.remove();
// 		} 
// 	}
// }

function checkNotificationStatus(){

	// if($('#mini_notification').css('display') != 'none'){
	// 	return true;
	// }

	if($('#mini_notification').attr('class') == 'showed_notification'){
		return true;
	}

	return false;
}



// Shows and hides messages return in ajax  
// NOT USED EVER ---> ERASED
// function showMessagesLimit(id, messages, limit) {


// Shows and hides messages
function createMessagesLocal(id, message, type, time) {

	if(time == null){
		time = 5000;
	}
	// Messages of localStorage
	var stored_messages = JSON.parse(localStorage["messages"]);

	// $('#'+id).html(' ');
	$('#main_result_messages').html('');


	for(i=0; i<stored_messages.length;i++){
		$('#main_result_messages').prepend('<div class="messages_return '+stored_messages[i]['type']+'"><p>'
				+ stored_messages[i]['text'] +'</p></div>');
	}
	now = new Date();
	stored_messages.push({'id':'msg_item_'+(stored_messages.length),'text':' '+now.getFullYear()+'/'+('0'+(now.getMonth()+1)).slice(-2)+'/'+('0'+now.getDate()).slice(-2)+' '+('0'+now.getHours()).slice(-2)+':'+('0'+now.getMinutes()).slice(-2)+':'+('0'+now.getSeconds()).slice(-2)+'  '+message+'<span class="delete_msg_link">delete</span>', 'view':'test_view', 'type':type});

	$('#main_result_messages').prepend('<div id="msg_item_'+(stored_messages.length+1)+'" class="messages_return '+type+'"><p>'
		+now.getFullYear()+'/'+('0'+(now.getMonth()+1)).slice(-2)+'/'+('0'+now.getDate()).slice(-2)+' '+('0'+now.getHours()).slice(-2)+':'+('0'+now.getMinutes()).slice(-2)+':'+('0'+now.getSeconds()).slice(-2)+'  '
		+ message + '<span class="delete_msg_link">delete</span></p></div>');
	// $('#'+id).append('<div id="msg_'+type+'_'+message+'" class="messages_return msg_'+type+'"><p>' 

	// 	+ message + '</p></div>');
	// hideMessages(id, time);
	// Adds message to stored_messages
	// console.log('Segundopush!!',stored_messages.length);
	// stored_messages.unshift({'text':message, 'view':'test_view', 'type':type});

	// $('#'+id).fadeIn();
	// $('#main_result_messages').fadeIn();
	// $('#main_show_messages_btn').val('Hide Messages');
	// $('#main_show_messages_btn').delay(5000).val('Show Messages');
	// $('#main_result_messages').delay(5000).slideUp();
	
	// openCloseMessagesDiv();
	displayLocalMiniNotification(message, type, time);

	// Stores messages in localStorage
	localStorage["messages"] = JSON.stringify(stored_messages);
}

function processFilters(id_id, filters){

	view_name = id_id.replace('_div_select_filters','')

	$('#'+id_id+' select').each(function(){
		// Store the current value
		var current_value = $(this).val();
		
		if (current_value != 'None'){
			var options = "<option value='None'>-----</option>";
			// options += '<option value="' + current_value + '" selected="selected">' +  $(this).children("[value="+current_value+"]").html() + '</option>';

			try
			{
				options += '<option value="' + current_value + '" selected="selected">' +  $(this).children("[value="+current_value+"]").html() + '</option>';
			}
			catch(e)
			{
				// console.log(e)
				options += '<option value="' + current_value + '" selected="selected">' +  current_value + '</option>';
			}
		}
		else{
			var options = "<option value='None' selected='selected'>-----</option>";
			$('#'+ view_name+'_filter_'+$(this)[0].name).select2({placeholder: '-----',})
		}


		for(i=0;i<filters[$(this).attr('name')].length;i++){
			if(filters[$(this).attr('name')][i][0] != current_value){
				// console.log(filters[$(this).attr('id')][i][0]);
				options += '<option value="' + filters[$(this).attr('name')][i][0] + '">' +  filters[$(this).attr('name')][i][1] + '</option>';    
			}

		}
		$(this).find('option').remove();

		$(this).append(options);
	});
}


function controlBlock(form_id,action)
{
	// console.log('typeof--->',typeof window[form_id]);
	if (typeof window[form_id] == "object" || typeof window[form_id] =="undefined")
		window[form_id] = 0

	if (action == 'block')
	{	
		window[form_id] = window[form_id] +1
	}
	else
	{	
		window[form_id] = window[form_id] -1
		if (window[form_id] < 0)
			window[form_id] = 0
	}
	
	if (window[form_id] <= 0)
	{
		$('#'+form_id).unblock();
	}
	else
	{
		$('#'+form_id).block();
	}
	// console.log('controlBlock-->',form_id,'--->',window[form_id]);
}

function controlBlockClass(form_id,action)
{
	// console.log('typeof--->',typeof window[form_id]);
	if (typeof window[form_id] == "object" || typeof window[form_id] =="undefined")
		window[form_id] = 0

	if (action == 'block')
	{	
		window[form_id] = window[form_id] +1
	}
	else
	{	
		window[form_id] = window[form_id] -1
		if (window[form_id] < 0)
			window[form_id] = 0
	}
	
	if (window[form_id] <= 0)
	{
		$(form_id).unblock();
	}
	else
	{
		$(form_id).block();
	}
	// console.log('controlBlock-->',form_id,'--->',window[form_id]);
}



function updateFilters(form_id, div_filters_id, url){
	filters_data = $('#'+form_id).serialize();
	// $('#'+form_id).block();
	controlBlock(form_id,'block')

	$.ajax({
		 url: url,
		 method: 'GET',
		 dataType: 'json',
		 data:filters_data,
		success: function(response) {
			filters = response;
			processFilters(div_filters_id,filters);
			// $('#'+form_id).unblock();

			$("#"+form_id).trigger('endUpdateFilters',[$(this).attr('id')]);
			controlBlock(form_id,'unblock')

		},
		error: function(jqXHR, textStatus, errorThrown){
			console.log('ERROR :'+errorThrown);
			console.log('textStatus :'+textStatus);
			console.log('jqXHR :'+jqXHR);
			$('#'+form_id).unblock();
			
		}
	});
}

function updateFiltersParam(form_id, div_filters_id, url,param){
	filters_data = $('#'+form_id).serialize()+'&'+param;
	$('#'+form_id).block();

	$.ajax({
		 url: url,
		 method: 'GET',
		 dataType: 'json',
		 data:filters_data,
		success: function(response) {
			filters = response;
			processFilters(div_filters_id,filters);
			$('#'+form_id).unblock();

		},
		error: function(jqXHR, textStatus, errorThrown){
			console.log('ERROR :'+errorThrown);
			console.log('textStatus :'+textStatus);
			console.log('jqXHR :'+jqXHR);
			$('#'+form_id).unblock();
		}
	});
}

function filtersClear(view, url) {
		$('#'+view+'_filters_form'+' select').each(function(){
			$(this).val('None');
		});
		updateFilters(view+'_filters_form', view+'_div_select_filters', url);
}

function filtersClearParam(view, url, param) {
	$('#'+view+'_filters_form'+' select').each(function(){
		$(this).val('None');
	});
	updateFiltersParam(view+'_filters_form', view+'_div_select_filters', url, param);
}


// In order to add a new value need to add the value/translation to filters tag (templates/sws_utils/sws_tags.py)

function transDayWeek(num_day)
{

	first_day_week = 'Monday'

	if (first_day_week == 'Monday')
	{
		if (num_day == 0)
			return 6
		else
			return num_day -1 
	}	
	else
		return num_day
}




function shortcutsDateFilter(view){

	period = window[view+'_selection_shortcuts']

	var now = now_user
	var from_date, to_date;

	start_hour = 00 
	start_minutes = 00 
	start_seconds = 00 
	finish_hour = 23 
	finish_minutes = 59 
	finish_seconds = 59 

		switch(period){
			case '1m':
				from_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),now.getHours(),now.getMinutes()-1,now.getSeconds());
				to_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),now.getHours(),now.getMinutes(),now.getSeconds());
				break;
			case '5m':
				from_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),now.getHours(),now.getMinutes()-5,now.getSeconds());
				to_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),now.getHours(),now.getMinutes(),now.getSeconds());
				break;
			case '10m':
				from_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),now.getHours(),now.getMinutes()-10,now.getSeconds());
				to_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),now.getHours(),now.getMinutes(),now.getSeconds());
				break;
			case '20m':
				from_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),now.getHours(),now.getMinutes()-20,now.getSeconds());
				to_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),now.getHours(),now.getMinutes(),now.getSeconds());
				break;
			case '30m':
				from_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),now.getHours(),now.getMinutes()-30,now.getSeconds());
				to_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),now.getHours(),now.getMinutes(),now.getSeconds());
				break;
			case '1h':
				from_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),now.getHours()-1,now.getMinutes(),now.getSeconds());
				to_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),now.getHours(),now.getMinutes(),now.getSeconds());
				break;
			case '2h':
				from_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),now.getHours()-2,now.getMinutes(),now.getSeconds());
				to_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),now.getHours(),now.getMinutes(),now.getSeconds());
				break;
			case '3h':
				from_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),now.getHours()-3,now.getMinutes(),now.getSeconds());
				to_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),now.getHours(),now.getMinutes(),now.getSeconds());
				break;
			case '6h':
				from_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),now.getHours()-6,now.getMinutes(),now.getSeconds());
				to_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),now.getHours(),now.getMinutes(),now.getSeconds());
				break;
			case '12h':
				from_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),now.getHours()-12,now.getMinutes(),now.getSeconds());
				to_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),now.getHours(),now.getMinutes(),now.getSeconds());
				break;
			case '24h':
				from_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),now.getHours()-24,now.getMinutes(),now.getSeconds());
				to_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),now.getHours(),now.getMinutes(),now.getSeconds());
				break;
			case 'today':
				from_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),start_hour,start_minutes,start_seconds);
				to_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),finish_hour,finish_minutes,finish_seconds);
				break;
			case 'yesterday':
				from_date = new Date(now.getFullYear(),now.getMonth(),(now.getDate()-1), start_hour,start_minutes,start_seconds);
				to_date = new Date(now.getFullYear(),now.getMonth(),(now.getDate()-1),finish_hour,finish_minutes,finish_seconds);
				break;
			case 'week':
				from_date = new Date(now.getFullYear(),now.getMonth(),(now.getDate()-(transDayWeek(now.getDay()))), start_hour,start_minutes,start_seconds);
				to_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),finish_hour,finish_minutes,finish_seconds);
				break;
			case 'month':
				from_date = new Date(now.getFullYear(),now.getMonth(),1,start_hour,start_minutes,start_seconds);
				to_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),finish_hour,finish_minutes,finish_seconds);
				break;
			case 'pweek':
				from_date = new Date(now.getFullYear(),now.getMonth(),(now.getDate()-now.getDay())-6, start_hour,start_minutes,start_seconds);
				to_date = new Date(now.getFullYear(),now.getMonth(),(now.getDate()-(transDayWeek(now.getDay())))-1,finish_hour,finish_minutes,finish_seconds);
				break;
			case 'pmonth':
				from_date = new Date(now.getFullYear(),now.getMonth()-1,1,start_hour,start_minutes,start_seconds);
				to_date = new Date(now.getFullYear(),now.getMonth(),(now.getDate()-now.getDate()),finish_hour,finish_minutes,finish_seconds);
				break;
			case 'lastseven':
				from_date = new Date(now.getFullYear(),now.getMonth(),now.getDate()-7,now.getHours(),now.getMinutes(),now.getSeconds());
				to_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),finish_hour,finish_minutes,finish_seconds);
				break;
			case 'lastthirty':
				from_date = new Date(now.getFullYear(),now.getMonth(),now.getDate()-30,now.getHours(),now.getMinutes(),now.getSeconds());
				to_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),finish_hour,finish_minutes,finish_seconds);
				break;
			case 'year':
				from_date = new Date(now.getFullYear(),0,1,start_hour,start_minutes,start_seconds);
				to_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),finish_hour,finish_minutes,finish_seconds);
				break;
			case "all":
				from_date = new Date(2014,0,01,00,00,00);
				to_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),finish_hour,finish_minutes,finish_seconds);
				break;
			// case 'year':
			// 	from_date = new Date(now.getFullYear(),0,1,start_hour,start_minutes,start_seconds);
			// 	to_date = new Date(now.getFullYear(),now.getMonth(),(now.getDate()-now.getDate()),finish_hour,finish_minutes,finish_seconds);
			// 	break;
			// case "all":
			// 	from_date = new Date(now.getFullYear()-1,9,01,00,00,00);
			// 	to_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),finish_hour,finish_minutes,finish_seconds);
			// 	break;

			case "all+forecast":
				from_date = new Date(now.getFullYear()-1,9,01,00,00,00);
				to_date = new Date(now.getFullYear()+1,now.getMonth(),now.getDate(),finish_hour,finish_minutes,finish_seconds);
				break;

			case "forecast":
				from_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),finish_hour,finish_minutes,finish_seconds)
				to_date = new Date(now.getFullYear()+1,now.getMonth(),now.getDate(),finish_hour,finish_minutes,finish_seconds);
				break;
		}

		val_from_date=from_date.getFullYear()+'-'+('0'+(from_date.getMonth()+1)).slice(-2)+'-'+('0'+from_date.getDate()).slice(-2)+' '+('0'+from_date.getHours()).slice(-2)+':'+('0'+from_date.getMinutes()).slice(-2)+':'+('0'+from_date.getSeconds()).slice(-2)
		val_to_date=to_date.getFullYear()+'-'+('0'+(to_date.getMonth()+1)).slice(-2)+'-'+('0'+to_date.getDate()).slice(-2)+' '+('0'+to_date.getHours()).slice(-2)+':'+('0'+to_date.getMinutes()).slice(-2)+':'+('0'+to_date.getSeconds()).slice(-2)

		if( $('input[id^="'+view+'_datepicker_from_"]').val().length>12)
		{
			val_from_date=from_date.getFullYear()+'-'+('0'+(from_date.getMonth()+1)).slice(-2)+'-'+('0'+from_date.getDate()).slice(-2)+' '+('0'+from_date.getHours()).slice(-2)+':'+('0'+from_date.getMinutes()).slice(-2)+':'+('0'+from_date.getSeconds()).slice(-2)
			val_to_date=to_date.getFullYear()+'-'+('0'+(to_date.getMonth()+1)).slice(-2)+'-'+('0'+to_date.getDate()).slice(-2)+' '+('0'+to_date.getHours()).slice(-2)+':'+('0'+to_date.getMinutes()).slice(-2)+':'+('0'+to_date.getSeconds()).slice(-2)
		}
		else
		{
			val_from_date=from_date.getFullYear()+'-'+('0'+(from_date.getMonth()+1)).slice(-2)+'-'+('0'+from_date.getDate()).slice(-2)
			val_to_date=to_date.getFullYear()+'-'+('0'+(to_date.getMonth()+1)).slice(-2)+'-'+('0'+to_date.getDate()).slice(-2)
		}   

		$('input[id^="'+view+'_datepicker_from_"]').val(val_from_date);
		$('input[id^="'+view+'_datepicker_to_"]').val(val_to_date);
}


function shortcutsDateFilterFromTo(view, period){
	var now = now_user
	var from_date, to_date;

	start_hour = 00 
	start_minutes = 00 
	start_seconds = 00 
	finish_hour = 23 
	finish_minutes = 59 
	finish_seconds = 59 
		switch(period){
			case '1m':
				from_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),now.getHours(),now.getMinutes()-1,now.getSeconds());
				to_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),now.getHours(),now.getMinutes(),now.getSeconds());
				break;
			case '5m':
				from_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),now.getHours(),now.getMinutes()-5,now.getSeconds());
				to_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),now.getHours(),now.getMinutes(),now.getSeconds());
				break;
			case '10m':
				from_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),now.getHours(),now.getMinutes()-10,now.getSeconds());
				to_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),now.getHours(),now.getMinutes(),now.getSeconds());
				break;
			case '20m':
				from_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),now.getHours(),now.getMinutes()-20,now.getSeconds());
				to_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),now.getHours(),now.getMinutes(),now.getSeconds());
				break;
			case '30m':
				from_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),now.getHours(),now.getMinutes()-30,now.getSeconds());
				to_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),now.getHours(),now.getMinutes(),now.getSeconds());
				break;
			case '1h':
				from_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),now.getHours()-1,now.getMinutes(),now.getSeconds());
				to_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),now.getHours(),now.getMinutes(),now.getSeconds());
				break;
			case '2h':
				from_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),now.getHours()-2,now.getMinutes(),now.getSeconds());
				to_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),now.getHours(),now.getMinutes(),now.getSeconds());
				break;
			case '3h':
				from_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),now.getHours()-3,now.getMinutes(),now.getSeconds());
				to_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),now.getHours(),now.getMinutes(),now.getSeconds());
				break;
			case '6h':
				from_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),now.getHours()-6,now.getMinutes(),now.getSeconds());
				to_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),now.getHours(),now.getMinutes(),now.getSeconds());
				break;
			case '12h':
				from_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),now.getHours()-12,now.getMinutes(),now.getSeconds());
				to_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),now.getHours(),now.getMinutes(),now.getSeconds());
				break;
			case '24h':
				from_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),now.getHours()-24,now.getMinutes(),now.getSeconds());
				to_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),now.getHours(),now.getMinutes(),now.getSeconds());
				break;
			case 'today':
				from_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),start_hour,start_minutes,start_seconds);
				to_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),finish_hour,finish_minutes,finish_seconds);
				break;
			case 'yesterday':
				from_date = new Date(now.getFullYear(),now.getMonth(),(now.getDate()-1), start_hour,start_minutes,start_seconds);
				to_date = new Date(now.getFullYear(),now.getMonth(),(now.getDate()-1),finish_hour,finish_minutes,finish_seconds);
				break;
			case 'week':
				from_date = new Date(now.getFullYear(),now.getMonth(),(now.getDate()-(transDayWeek(now.getDay()))), start_hour,start_minutes,start_seconds);
				to_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),finish_hour,finish_minutes,finish_seconds);
				break;
			case 'month':
				from_date = new Date(now.getFullYear(),now.getMonth(),1,start_hour,start_minutes,start_seconds);
				to_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),finish_hour,finish_minutes,finish_seconds);
				break;
			case 'pweek':
				from_date = new Date(now.getFullYear(),now.getMonth(),(now.getDate()-now.getDay())-6, start_hour,start_minutes,start_seconds);
				to_date = new Date(now.getFullYear(),now.getMonth(),(now.getDate()-(transDayWeek(now.getDay())))-1,finish_hour,finish_minutes,finish_seconds);
				break;
			case 'pmonth':
				from_date = new Date(now.getFullYear(),now.getMonth()-1,1,start_hour,start_minutes,start_seconds);
				to_date = new Date(now.getFullYear(),now.getMonth(),(now.getDate()-now.getDate()),finish_hour,finish_minutes,finish_seconds);
				break;
			case 'lastseven':
				from_date = new Date(now.getFullYear(),now.getMonth(),now.getDate()-7,now.getHours(),now.getMinutes(),now.getSeconds());
				to_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),finish_hour,finish_minutes,finish_seconds);
				break;
			case 'lastthirty':
				from_date = new Date(now.getFullYear(),now.getMonth(),now.getDate()-30,now.getHours(),now.getMinutes(),now.getSeconds());
				to_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),finish_hour,finish_minutes,finish_seconds);
				break;
			case 'year':
				from_date = new Date(now.getFullYear(),0,1,start_hour,start_minutes,start_seconds);
				to_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),finish_hour,finish_minutes,finish_seconds);
				break;
			case "all":
				from_date = new Date(2014,0,01,00,00,00);
				to_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),finish_hour,finish_minutes,finish_seconds);
				break;
			// case 'year':
			// 	from_date = new Date(now.getFullYear(),1,1,start_hour,start_minutes,start_seconds);
			// 	to_date = new Date(now.getFullYear(),now.getMonth(),(now.getDate()-now.getDate()),finish_hour,finish_minutes,finish_seconds);
			// 	break;
			// case "all":
			// 	from_date = new Date(2012,10,01,00,00,00);
			// 	to_date = new Date(now.getFullYear(),now.getMonth(),now.getDate(),finish_hour,finish_minutes,finish_seconds);
			// 	break;
		}

		// T = new Date();

		// if (T.getFullYear() != to_date.getFullYear())
		// {
		// 	to_date.setFullYear(T.getFullYear())
		// 	to_date.setMonth(T.getMonth())
		// 	to_date.setDate(T.getDate())
		// 	to_date.setHours(23)
		// 	to_date.setMinutes(59)
		// 	to_date.setSeconds(59)
		// }	

		// if (T.getFullYear() != from_date.getFullYear())
		// {
		// 	from_date.setFullYear(T.getFullYear())
		// 	from_date.setMonth(T.getMonth())
		// 	from_date.setDate(T.getDate())
		// 	from_date.setHours(00)
		// 	from_date.setMinutes(00)
		// 	from_date.setSeconds(00)
		// }	

		return {from_date:from_date,to_date:to_date}
	}

// Checks if a password is valid, numbers and letters and length
function isValidPassword(pass,length){
	if(pass.length >= length && pass.search(/\d/g) != -1 && pass.search(/\D/g) != -1) return true;
	else return false;
}

function comparePasswords(id_pass1, id_pass2, id_icon, URL) 
{
	$("#"+id_pass2).keyup(function(){
		var pass = $("#"+id_pass2).val();
			if(isValidPassword(pass,8) == true && pass == $("#"+id_pass1).val()){
				$("#"+ id_icon).html('<img src="'+URL+'img/success_small.png"/>');
			} 
			else {
				$("#"+ id_icon).html('<img src="'+URL+'img/error_small.png"/>');
			}
	});         
}


var dateFormat = function () {
	var token = /d{1,4}|m{1,4}|yy(?:yy)?|([HhMsTt])\1?|[LloSZ]|"[^"]*"|'[^']*'/g,
		timezone = /\b(?:[PMCEA][SDP]T|(?:Pacific|Mountain|Central|Eastern|Atlantic) (?:Standard|Daylight|Prevailing) Time|(?:GMT|UTC)(?:[-+]\d{4})?)\b/g,
		timezoneClip = /[^-+\dA-Z]/g,
		pad = function (val, len) {
			val = String(val);
			len = len || 2;
			while (val.length < len) val = "0" + val;
			return val;
		};

	// Regexes and supporting functions are cached through closure
	return function (date, mask, utc) {
		var dF = dateFormat;

		// You can't provide utc if you skip other args (use the "UTC:" mask prefix)
		if (arguments.length == 1 && Object.prototype.toString.call(date) == "[object String]" && !/\d/.test(date)) {
			mask = date;
			date = undefined;
		}

		// Passing date through Date applies Date.parse, if necessary
		date = date ? new Date(date) : new Date;
		if (isNaN(date)) throw SyntaxError("invalid date");

		mask = String(dF.masks[mask] || mask || dF.masks["default"]);

		// Allow setting the utc argument via the mask
		if (mask.slice(0, 4) == "UTC:") {
			mask = mask.slice(4);
			utc = true;
		}

		var _ = utc ? "getUTC" : "get",
			d = date[_ + "Date"](),
			D = date[_ + "Day"](),
			m = date[_ + "Month"](),
			y = date[_ + "FullYear"](),
			H = date[_ + "Hours"](),
			M = date[_ + "Minutes"](),
			s = date[_ + "Seconds"](),
			L = date[_ + "Milliseconds"](),
			o = utc ? 0 : date.getTimezoneOffset(),
			flags = {
				d:    d,
				dd:   pad(d),
				ddd:  dF.i18n.dayNames[D],
				dddd: dF.i18n.dayNames[D + 7],
				m:    m + 1,
				mm:   pad(m + 1),
				mmm:  dF.i18n.monthNames[m],
				mmmm: dF.i18n.monthNames[m + 12],
				yy:   String(y).slice(2),
				yyyy: y,
				h:    H % 12 || 12,
				hh:   pad(H % 12 || 12),
				H:    H,
				HH:   pad(H),
				M:    M,
				MM:   pad(M),
				s:    s,
				ss:   pad(s),
				l:    pad(L, 3),
				L:    pad(L > 99 ? Math.round(L / 10) : L),
				t:    H < 12 ? "a"  : "p",
				tt:   H < 12 ? "am" : "pm",
				T:    H < 12 ? "A"  : "P",
				TT:   H < 12 ? "AM" : "PM",
				Z:    utc ? "UTC" : (String(date).match(timezone) || [""]).pop().replace(timezoneClip, ""),
				o:    (o > 0 ? "-" : "+") + pad(Math.floor(Math.abs(o) / 60) * 100 + Math.abs(o) % 60, 4),
				S:    ["th", "st", "nd", "rd"][d % 10 > 3 ? 0 : (d % 100 - d % 10 != 10) * d % 10]
			};

		return mask.replace(token, function ($0) {
			return $0 in flags ? flags[$0] : $0.slice(1, $0.length - 1);
		});
	};
}();
			
// Some common format strings
dateFormat.masks = {
	"default":      "ddd mmm dd yyyy HH:MM:ss",
	shortDate:      "m/d/yy",
	mediumDate:     "mmm d, yyyy",
	longDate:       "mmmm d, yyyy",
	fullDate:       "dddd, mmmm d, yyyy",
	shortTime:      "h:MM TT",
	mediumTime:     "h:MM:ss TT",
	longTime:       "h:MM:ss TT Z",
	isoDate:        "yyyy-mm-dd",
	isoTime:        "HH:MM:ss",
	isoDateTime:    "yyyy-mm-dd'T'HH:MM:ss",
	isoUtcDateTime: "UTC:yyyy-mm-dd'T'HH:MM:ss'Z'"
};

// Internationalization strings
dateFormat.i18n = {
	dayNames: [
		"Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat",
		"Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"
	],
	monthNames: [
		"Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
		"January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"
	]
};

// For convenience...   
Date.prototype.format = function (mask, utc) {
	return dateFormat(this, mask, utc);
};

//tag_filters.html and tag_filter_select2.html
function datePickerFromTo(view) {
	var view = view;
	$("input[id*='"+view+"_datepicker_from_']").datepicker({
		defaultDate: "",
		dateFormat:"yy-mm-dd",
		changeMonth: true,
		numberOfMonths: 1,
		onClose: function(dateText, inst) {
			dateCallback(view);
			refreshDateTo(view)
		}
	});

	$("input[id*='"+view+"_datepicker_to_']").datepicker({
		defaultDate: "",
		dateFormat:"yy-mm-dd",
		changeMonth: true,
		numberOfMonths: 1,
		onClose: function(dateText, inst) {
			dateCallback(view);
			refreshDateFrom(view)
		}
	});
}

//tag_filters.html and tag_filter_select2.html
function datetimePickerFromTo(view) {
	var view = view;
	try{
		fd_str = $('#'+view+'_datepicker_from_calldate').val();
	}catch(e){
		fd_str = undefined
	}

	if (fd_str != undefined)
		from_date = new Date(fd_str.substring(0,4),parseInt(fd_str.substring(5,7))-1,fd_str.substring(8,10),fd_str.substring(11,13),fd_str.substring(14,16),fd_str.substring(17,19))
	else
		from_date = ''


	try{
		td_str = $('#'+view+'_datepicker_to_calldate').val();
	}catch(e){
		td_str = undefined;
	}

	if (td_str != undefined)
		to_date = new Date(td_str.substring(0,4),parseInt(td_str.substring(5,7))-1,td_str.substring(8,10),td_str.substring(11,13),td_str.substring(14,16),td_str.substring(17,19))
	else
		to_date = ''

	T = new Date();


	$("input[id*='"+view+"_datepicker_from_']").datetimepicker({
		// maxDate:to_date, 
		altFormat:'YYYY-MM-DD', 
		dateFormat:'yy-mm-dd', 
		timeFormat:'HH:mm:ss', 
		showAnim: 'blind', 
		hourGrid: 4, 
		minuteGrid: 10, 
		onClose: function(dateText, inst) {
			// console.log('ONCLOSE- FROM -->',view);
			dateCallback(view);
			refreshDatetimeTo(view)
		}
	});

	$("input[id*='"+view+"_datepicker_to_']").datetimepicker({ 
		// minDate:from_date,
		altFormat:'YYYY-MM-DD', 
		dateFormat:'yy-mm-dd', 
		timeFormat:'HH:mm:ss', 
		showAnim: 'blind', 
		hourGrid: 4, 
		minuteGrid: 10, 
		onClose: function(dateText, inst) {
			dateCallback(view);
			refreshDatetimeFrom(view)
		},
	});
}

function refreshDatetimeTo(view)
{
	// td_str = $('#'+view+'_datepicker_to_calldate').val();
	// from_date =   $('#'+view+'_datepicker_from_calldate').val();
	// $("input[id*='"+view+"_datepicker_to_']").datetimepicker('option', 'minDate', from_date );
	// $('#'+view+'_datepicker_to_calldate').val(td_str);
	
}

function refreshDatetimeFrom(view)
{
	// fd_str = $('#'+view+'_datepicker_from_calldate').val();
	// to_date = $('#'+view+'_datepicker_to_calldate').val();
	// $("input[id*='"+view+"_datepicker_from_']").datetimepicker('option', 'maxDate', to_date );
	// $('#'+view+'_datepicker_from_calldate').val(fd_str);
}

function refreshDateTo(view)
{
	td_str = $('#'+view+'_datepicker_to_calldate').val();
	from_date =   $('#'+view+'_datepicker_from_calldate').val();
	$("input[id*='"+view+"_datepicker_to_']").datepicker('option', 'minDate', from_date );
	$('#'+view+'_datepicker_to_calldate').val(td_str);
	
}

function refreshDateFrom(view)
{
	fd_str = $('#'+view+'_datepicker_from_calldate').val();
	to_date = $('#'+view+'_datepicker_to_calldate').val();
	$("input[id*='"+view+"_datepicker_from_']").datepicker('option', 'maxDate', to_date );
	$('#'+view+'_datepicker_from_calldate').val(fd_str);
}

function dateCallback(view)
{
	var view = $('#main_tabs_ul .ui-state-active').children().attr('title');

	fd_str = $('#'+view+'_datepicker_from_calldate').val();
	td_str = $('#'+view+'_datepicker_to_calldate').val();

	dif = false

	if (fd_str != null) 	
		from_date = new Date(fd_str.substring(0,4),fd_str.substring(5,7),fd_str.substring(8,10),fd_str.substring(11,13),fd_str.substring(14,16),fd_str.substring(17,19));
	else
		dif = true
	

	if (td_str != null)
		if (td_str.substring(11,13).length == 0)
			to_date = new Date(td_str.substring(0,4),td_str.substring(5,7),td_str.substring(8,10),'23',td_str.substring(14,16),td_str.substring(17,19));
		else
			to_date = new Date(td_str.substring(0,4),td_str.substring(5,7),td_str.substring(8,10),td_str.substring(11,13),td_str.substring(14,16),td_str.substring(17,19));
	else
		dif = true
	
	if (dif !=true)
		dif = to_date > from_date;


	if (dif == true)
	{
		if ($('#'+view+'_clear_update').length)
		{
			$('#'+view+'_div_select_filters').block({message:' <div> <div style = " width:125px; margin: 2px 0px 0px 2px;  float: left;"> Press button update  </div> <div class="ui-icon ui-icon-refresh" style="background-color: black; width: 15px; border:1px solid grey; float: left;"> </div> <div style = " width:75px; float: left; margin: 2px 0px 0px 0px; "> to continue </div> </div>'});
		}
		else
		{
			var execute = view+"_callback('filters');";
			eval(execute);
			var execute = view+"_callback('filtersprimary');";
			eval(execute);
		}
	}
	else
	{
		createMessagesLocal(view+'_result_messages','Please set a normal date range.', 'error', 5000);
	}
}

function resizeToGrid(grid_id, div_id) {
	$('#'+grid_id).setGridWidth($('#'+div_id).css('width').replace('px',''));
}


function reloadGrid(view,grid_id,grid_url){
	param = $('#'+view+'_filters_form').serialize();
	$('#'+grid_id).setGridParam({'url':grid_url+'?'+param});
	$('#'+grid_id).jqGrid().trigger('reloadGrid');
}

function reloadGridParamSimple(grid_id,grid_url,param)
{
	$('#'+grid_id).setGridParam({'url':grid_url+'?'+param});
	$('#'+grid_id).jqGrid().trigger('reloadGrid');
}

function reloadGridParamDouble(grid_id,grid_url,param)
{
	$('#'+grid_id).setGridParam({'url':grid_url+'?'+param});
	$('#'+grid_id).jqGrid().trigger('reloadGrid');
	$('#'+grid_id).jqGrid().trigger('reloadGrid');
}

function serializeToList(param,view_name)
{
	do
	{
		param = param.replace(view_name+'_','')

	}while(param.indexOf(view_name+'_')>0)

	param_list = param.split('&')

	dict_param = new Array()
	for (i in param_list)
	{
		index=param_list[i].indexOf('=')
		if(index>0)
		{
			p = param_list[i]
			name1 = p.substring(0,index)
			name2 = p.substring(index+1,p.length)
			dict_param[name1] = name2
		}	
	}	

	return dict_param
}

function reloadGridParam(grid_id,grid_url,param,col)
{
	col_model = $('#'+grid_id).jqGrid('getGridParam','colModel');

	view_name = grid_id.replace('_table_grid','').replace('_detail','').replace('_client','')


	list_gb = param.split('&');
	group_by = 0
	and_by = 0
	for (i in list_gb)
	{
		list_gb[i] = list_gb[i].replace(view_name+'_','')

		if(list_gb[i].indexOf('group_by=')==0)
		{	
			group_by = list_gb[i].replace('group_by=','')
			group_by = group_by.replace('+',' ')
			name_group_by = $('#'+group_by +'_label1 span').html()
		}
		if(list_gb[i].indexOf('and_by=')==0)
		{	
			and_by = list_gb[i].replace('and_by=','')
			and_by = and_by.replace('+',' ')
			name_and_by = $('#'+and_by+'_label2 span').html()
		}
	}
///////////////////////////////////////
	
	if (group_by == and_by)
	{
		if(col_model[0].name!=group_by)			
			 $('#'+grid_id).jqGrid('hideCol',col_model[0].name);
		else
			 $('#'+grid_id).jqGrid('hideCol',col_model[1].name);
	}
	else
	{
		col_model[0]['name'] = group_by;
		$('#'+grid_id).jqGrid('showCol',col_model[0].name);
		if (and_by != 0)
			col_model[1]['name'] = and_by;
			$('#'+grid_id).jqGrid('showCol',col_model[1].name);
		
	}

//////////////////////////////////////
	$('#'+grid_id).jqGrid().setLabel($('#'+grid_id).jqGrid('getGridParam','colModel')[0].name,col_model[0].name.replace('+',' '));
	if (and_by != null)
		$('#'+grid_id).jqGrid().setLabel($('#'+grid_id).jqGrid('getGridParam','colModel')[1].name,col_model[1].name.replace('+',' '));

	do
	{
		param = param.replace(view_name+'_','')

	}while(param.indexOf(view_name+'_')>0)


	$('#'+grid_id).setGridParam({'url':grid_url+'?'+param});
	$('#'+grid_id).jqGrid().trigger('reloadGrid');


}

function reloadGridParamExpert(grid_id,grid_url,param,col)
{


	col_model = $('#'+grid_id).jqGrid('getGridParam','colModel');

	
	view_name = grid_id.replace('_table_grid','').replace('_detail','').replace('_client','')


	list_gb = param.split('&');

	
	group_by = 0
	and_by = 0
	final_by=0
	for (i in list_gb)
	{
		list_gb[i] = list_gb[i].replace(view_name+'_','')

		if(list_gb[i].indexOf('group_by=')==0)
		{	
			group_by = list_gb[i].replace('group_by=','')
			group_by = group_by.replace('+',' ')
			// console.log('group by == '+group_by)
			name_group_by = $('#'+group_by +'_label1 span').html()
		}
		if(list_gb[i].indexOf('and_by=')==0)
		{	
			and_by = list_gb[i].replace('and_by=','')
			and_by = and_by.replace('+',' ')
			// console.log('and_by == '+and_by)
			name_and_by = $('#'+and_by+'_label2 span').html()
		}
		if(list_gb[i].indexOf('final_by=')==0)
		{	
			final_by = list_gb[i].replace('final_by=','')
			final_by = final_by.replace('+',' ')
			// console.log('final_by == '+final_by)
			name_final_by = $('#'+final_by+'_label2 span').html()
		}
	}
	
	do
	{
		param = param.replace(view_name+'_','')

	}while(param.indexOf(view_name+'_')>0)

	
	$('#'+grid_id).setGridParam({'url':grid_url+'?'+param});
	
	$('#'+grid_id).jqGrid().trigger('reloadGrid');
	traffic_report_col_model = $('#traffic_report_table_grid').jqGrid('getGridParam','colModel');
	col_name1 = traffic_report_col_model[0]['name'];
	col_name2= traffic_report_col_model[1]['name'];
	col_name3= traffic_report_col_model[2]['name'];	
	
	
}
// Buttonset in vertical position
(function( $ ){
	//plugin buttonset vertical
	$.fn.buttonsetv = function() {
		$(':radio, :checkbox', this).wrap('<div style="margin: 1px"/>');
		$(this).buttonset();
		$('label:first', this).removeClass('ui-corner-left').addClass('ui-corner-top');
		$('label:last', this).removeClass('ui-corner-right').addClass('ui-corner-bottom');
		mw = 0; // max witdh
		$('label', this).each(function(index){
			w = $(this).width();
			if (w > mw) mw = w; 
		});
		$('label', this).each(function(index){
			$(this).width(mw);
		});
	};
})( jQuery );

// Function to send the disabled form fields
(function ($) {
  $.fn.serializeDisabled = function () {
	var obj = {};

	$(':disabled[name]', this).each(function () { 
		obj[this.name] = $(this).val(); 
	});
	return $.param(obj);
  }
})(jQuery);

// Create a hash from string
String.prototype.hashCode = function(){
	var hash = 0, i, char;
	if (this.length == 0) return hash;
	for (i = 0; i < this.length; i++) {
		char = this.charCodeAt(i);
		hash = ((hash<<5)-hash)+char;
		hash = hash & hash; // Convert to 32bit integer
	}
	return hash;
};

// Small override for a more usable experience on select2 elements (by patilla)
// If we click on a filter value, it also makes the filter list pop up, not just when we click on the emty space
function select2Enhancer(){
	$('div[id^=s2id] > ul').click(function(){
		$(this).parent().select2("open");
	});
}



///*********************************************************************************
// IMPORT: NOT DELETE, THIS FUNCTION ARE NOT USED IN INTERNATIONAL BUT IS NECESARY CHECK WITH STONEDASHBOARD
///*********************************************************************************

// //THIS FUNCTION NOT USSING
// function checkPassword(id_password, id_icon, URL) {
// 	$("#new_password1 span").html('hola');
// 	$("#"+id_password).keyup(function(){
// 		var pass = $("#"+id_password).val();
// 			if(isValidPassword(pass,8) == true){          
// 				$("#"+ id_icon).html('<img src="'+URL+'img/success_small.png"/>');   
// 			} 
// 			else {
// 				$("#" + id_icon).html('<img class="checks_pass" src="'+URL+'img/error_small.png"/>');
// 			}
// 	});

// }


//update date 
// function updateDate()
// {
// 	var timenow = new Date(),   
// 	timebefore = new Date ( timenow );
// 	timebefore.setMinutes ( timenow.getMinutes() - 60 );


// 	timenow = dateFormat(timenow, "yyyy-mm-dd HH:MM:ss");
// 	timebefore = dateFormat(timebefore, "yyyy-mm-dd HH:MM:ss")
// 	return timenow

// 	// from.value = timebefore;
// 	// to.value = timenow;
// }



// TODOMAS THIS FUNCTION NOT USING
// function reloadGridId(view,grid_id,grid_url,row_id){
// 	param = $('#'+view+'_filters_form').serialize();
// 	$('#'+grid_id).setGridParam({'url':grid_url+'?'+'row_id='+row_id});
// 	$('#'+grid_id).jqGrid().trigger('reloadGrid');
// }
// TODOMAS THIS FUNCTION NOT USING
// function reloadGridVal(view,grid_id,grid_url,col_name1,col_name2,val1,val2){
// 	param = $('#'+view+'_filters_form').serialize();
// 	$('#'+grid_id).setGridParam({'url':grid_url+'?'+param+'&val1='+val1+'&val2='+val2+'&col_name1='+col_name1+'&col_name2='+col_name2});
// 	$('#'+grid_id).jqGrid().trigger('reloadGrid');
// }
// TODOMAS THIS FUNCTION NOT USING
// function reloadGridGroupVal(view,grid_id,grid_url,param){
// 	// param = $('#'+view+'_filters_form').serialize();
// 	$('#'+grid_id).setGridParam({'url':grid_url+'?'+param});
// 	$('#'+grid_id).jqGrid().trigger('reloadGrid');
// }
// TODOMAS THIS FUNCTION NOT USING
// function reloadGridValDate(view,grid_id,grid_url,col_name1,col_name2,val1,val2,date_from,date_to){
// 	param = $('#'+view+'_filters_form').serialize();
// 	$('#'+grid_id).setGridParam({'url':grid_url+'?'+param+'&val1='+val1+'&val2='+val2+'&col_name1='+col_name1+'&col_name2='+col_name2+'&from_calldate='+date_from+'&to_calldate='+date_to});
// 	$('#'+grid_id).jqGrid().trigger('reloadGrid');
// }

// TODOMAS THIS FUNCTION NOT USING
// function reloadGridParam(grid_id,grid_url,param)
// {
// 	$('#'+grid_id).setGridParam({'url':grid_url+'?'+param});
// 	$('#'+grid_id).jqGrid().trigger('reloadGrid');
// }


// TODOMAS THIS FUNCTION NOT USING
// function reloadGridGroup_by(view,grid_id,grid_url,col1,col2){

// 	param = $('#'+view+'_div_select_filters').serialize();
// 	$('#'+grid_id).setGridParam({'url':grid_url+'?'+param+'&group_by='+col1});
// 	var col_model = $("#"+grid_id).jqGrid('getGridParam','colModel');


// 	for (i=0;i< col_model.length;i++){

// 		// Set first column value id
// 		col_model[0]['name'] = col1;
// 		// set first column caption
// 		$('#'+grid_id).jqGrid().setLabel(col_model[0]['name'],col1);

// 		// Set second column if not null
// 		if (col2!='None')
// 		{   
// 			col_model[1]['name'] = col2;
// 			$('#'+grid_id).jqGrid().setLabel(col_model[1]['name'],col2);
// 		}
// 	}

// 	$('#'+grid_id).jqGrid().trigger('reloadGrid');
// }



// TODOMAS THIS FUNCTION NOT USING
// // Returns the week number of a given date
// function weekNumber(now) {
// 	  var totalDays = 0;
// 	  years=now.getYear()
// 	  if (years < 1000)
// 	  years+=1900
// 	  var days = new Array(12); // Array to hold the total days in a month
// 	  days[0] = 31;
// 	  days[2] = 31;
// 	  days[3] = 30;
// 	  days[4] = 31;
// 	  days[5] = 30;
// 	  days[6] = 31;
// 	  days[7] = 31;
// 	  days[8] = 30;
// 	  days[9] = 31;
// 	  days[10] = 30;
// 	  days[11] = 31;

// 	  //  Check to see if this is a leap year

// 	   if (Math.round(now.getYear()/4) == now.getYear()/4) {
// 		 days[1] = 29
// 	  }else{
// 		 days[1] = 28
// 	  }

// 	//  If this is January no need for any fancy calculation otherwise figure out the
// 	//  total number of days to date and then determine what week

// 	  if (now.getMonth() == 0) {
// 		 totalDays = totalDays + now.getDate();
// 	  }else{
// 		 var curMonth = now.getMonth();
// 		 for (var count = 1; count <= curMonth; count++) {
// 			 totalDays = totalDays + days[count - 1];
// 		 }
// 		 totalDays = totalDays + now.getDate();
// 	   }
// 	   var week = Math.round(totalDays/7);
// 	   return week;
// 	}


// TODO MAS  THIS FUNCTION NOT USING
// // Rounds a number to dec decimal places
// function roundNumber(num, dec) {
// 	var result = Math.round(num*Math.pow(10,dec))/Math.pow(10,dec);
// 	return result;
// }
// function processFiltersSelect2(id_id, filters){
// 	$('#'+id_id+' select').each(function(){
// 		// Store the current value
// 		var current_value = $(this).val();
// 		console.log('this = ',$(this));

// 		console.log('current_value = ',current_value);

// 		var options = "<option value='None'>--------</option>";
// 		for(i=0;i<filters[$(this).attr('name')].length;i++){
// 			if(filters[$(this).attr('name')][i][0] == current_value){
// 				// console.log(filters[$(this).attr('id')][i][0]);
// 				options += '<option value="' + filters[$(this).attr('name')][i][0] + '" selected="selected">' +  filters[$(this).attr('name')][i][1] + '</option>';
// 			}
// 			else {
// 				options += '<option value="' + filters[$(this).attr('name')][i][0] + '">' +  filters[$(this).attr('name')][i][1] + '</option>';
// 			}	
// 		}
// 		$(this).find('option').remove();
// 		$(this).append(options);
// 	});
// }


//THIS FUNCTION NOT USSING
// function updateQueryset(queryset){
// 	var c = "<center>**QUERYSET**-> 