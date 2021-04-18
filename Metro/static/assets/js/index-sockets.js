		const socket = io('https://' + document.domain + ':' + location.port ,{ secure: true });
		// Notify user when connected in logs
		socket.on('connect', function() {
			console.log("connected to global chat");
		});

		// Message recieving function
		socket.on("message", function(msg) {
			console.log("recieved message");
			msg = msg.replace(/&/g, "&amp;").replace(/>/g, "&gt;").replace(/</g, "&lt;").replace(/"/g,"&quot;");
			$("#chat").append('<li>'+msg+'</li>');
			tts.text = msg;
			//speechSynthesis.speak(tts);
		});
		// Private Message recieving function
		socket.on("private_message", function(msg) {
			console.log("recieved private message");
			msg = msg.replace(/&/g, "&amp;").replace(/>/g, "&gt;").replace(/</g, "&lt;").replace(/"/g,"&quot;");
			$("#chat").append('<li style="color:#FFC30F">'+ "[W] " + msg +'</li>');
			tts.text = msg;
			//speechSynthesis.speak(tts);
		});

		socket.on("last_title", function(title) {
			console.log("recieved last title");
			title = title.replace(/&/g, "&amp;").replace(/>/g, "&gt;").replace(/</g, "&lt;").replace(/"/g,"&quot;");
			set_title(title);

		});

		//Connect html input and js socketio to send messages 
		$('#sendbutton').on('click', function() {
			send_msg();
		});

		//Allow users to press enter when using input instead of clicking the button
		$(document).ready(function() {
		var input = document.getElementById("myMessage");
		input.addEventListener("keyup", function(event) {
			// Number 13 is the "Enter" key on the keyboard
			if (event.keyCode === 13) {
				// Cancel the default action, if needed
				event.preventDefault();
				// Trigger the button element with a click
				send_msg();
			}
		});
		
			});

		/* Send Message */
		function send_msg(){
			if($('#myMessage').val()){
			/* Send Message */
			console.log("sent message");
			socket.emit("message", $('#myMessage').val());
			$('#myMessage').val("");

			}
		}
		/* Set Title on top nav */
		function set_title(title){
			document.querySelector("#footertitle span").innerText = title;
		}
		/* Send chatname */
		function join_chat(cid){
			socket.emit("join_private", cid);
		}
		/* Disable button to prevent request spamming */
		$('#cchat_createbtn').on('click', function() {
			$("#cchat_createbtn").attr("disabled", true);
		});

	function delete_server(cid){
		socket.emit("delete_prviate", cid);
	}