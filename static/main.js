/**
 * Returns the current datetime for the message creation.
 */
function getCurrentTimestamp() {
	return new Date();
}

/**
 * Renders a message on the chat screen based on the given arguments.
 * This is called from the `showUserMessage` and `showBotMessage`.
 */
function renderMessageToScreen(args) {
	// local variables
	let displayDate = (args.time || getCurrentTimestamp()).toLocaleString('en-IN', {
		month: 'short',
		day: 'numeric',
		hour: 'numeric',
		minute: 'numeric',
	});
	let messagesContainer = $('.messages');

	// init element
	let message = $(`
	<li class="message ${args.message_side}">
		<div class="avatar"></div>
		<div class="text_wrapper">
			<div class="text">${args.text}</div>
			<div class="timestamp">${displayDate}</div>
		</div>
	</li>
	`);

	// add to parent
	messagesContainer.append(message);

	// animations
	setTimeout(function () {
		message.addClass('appeared');
	}, 0);
	messagesContainer.animate({ scrollTop: messagesContainer.prop('scrollHeight') }, 300);
}

/* Sends a message when the 'Enter' key is pressed.
 */
$(document).ready(function() {
    $('#user_input').keydown(function(e) {
        // Check for 'Enter' key
        if (e.key === 'Enter') {
            // Prevent default behaviour of enter key
            e.preventDefault();
			// Trigger send button click event
            $('#send_button').click();
        }
    });
});

/**
 * Displays the user message on the chat screen. This is the right side message.
 */
function showUserMessage(message, datetime) {
	renderMessageToScreen({
		text: message,
		time: datetime,
		message_side: 'right',
	});
}

/**
 * Displays the chatbot message on the chat screen. This is the left side message.
 */
function showBotMessage(message, datetime) {
	renderMessageToScreen({
		text: message,
		time: datetime,
		message_side: 'left',
	});
}

/**
 * Get input from user and show it on screen on button click.
 */
$('#send_button').on('click', function (e) {
	
	var user_input = $('#user_input').val();
	if (user_input.trim() !== '') {
		callAjax(user_input)
	}else{
		$('#user_input').focus();
	}
	
});

$(document).on('click', '.btn-list', function(){
	var user_input = $(this).attr('query');
	$('#user_input').val(user_input);
	callAjax(user_input);
});

function callAjax(user_input){
	$.ajax({
		url: '/process',
		type: 'POST',
		data: { 'data': user_input },
		success: function(response) {
			// get and show message and reset input
			showUserMessage($('#user_input').val());
			$('#user_input').val('');
			
			// show bot message
			setTimeout(function () {
				showBotMessage(response);
			}, 300);
			
		},
		error: function(error) {
			console.log(error);
		}
	});
}

/**
 * Set initial bot message to the screen for the user.
 */
$(window).on('load', function () {
	let first_message = 'Welcome 👋<br/>I am your Personal Assistant, How can I help you?';
	let button_message = '<button type="button" query="leave balance" class="btn btn-primary btn-list pull-right">Leave Balance</button><br/>\
	<button type="button" query="apply leave" class="btn btn-secondary btn-list pull-right">Apply Leave</button><br/>\
	<button type="button" query="provision" class="btn btn-success btn-list pull-right">Deploy Resources on AWS</button>';
	showBotMessage(first_message);
	showUserMessage(button_message);
});