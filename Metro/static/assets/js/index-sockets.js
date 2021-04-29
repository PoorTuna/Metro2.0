		const socket = io('https://' + document.domain + ':' + location.port ,{ secure: true });
		// Notify user when connected in logs
		socket.on('connect', function() {
			//console.log("connected to the chat");
			general_message();
		});
		socket.on('disconnect', function() {
			//console.log("disconnected from the chat");
		});

		// Message recieving function
		socket.on("message", function(msg) {
			//console.log("recieved message");
			msg = msg.replace(/&/g, "&amp;").replace(/>/g, "&gt;").replace(/</g, "&lt;").replace(/"/g,"&quot;");
			$("#chat").append('<li>'+msg+'</li>');
		});
		// Private Message recieving function
		socket.on("private_message", function(msg) {
			//console.log("recieved private message");
			msg = msg.replace(/&/g, "&amp;").replace(/>/g, "&gt;").replace(/</g, "&lt;").replace(/"/g,"&quot;");
			$("#chat").append('<li style="color:#FFC30F">'+ "[W] " + msg +'</li>');
		});

		//TTS Message recieving function
		socket.on("announce_message", function(msg) {
			//console.log("recieved private message");
			msg = msg.replace(/&/g, "&amp;").replace(/>/g, "&gt;").replace(/</g, "&lt;").replace(/"/g,"&quot;");
			$("#chat").append('<li>'+ msg +'</li>');
			username = msg.split(":")[0];
			tts.text = username + "says" + msg.slice(username.length + 1);
			speechSynthesis.speak(tts);
		});
		//Delete Messages recieving function
		socket.on("clean_message", function(msg) {
			//console.log("recieved private message");
			$("#chat").empty();
			msg = msg.replace(/&/g, "&amp;").replace(/>/g, "&gt;").replace(/</g, "&lt;").replace(/"/g,"&quot;");
			$("#chat").append('<li>'+ msg +'</li>');
		});


		socket.on("last_title", function(title) {
			//console.log("recieved last title");
			title = title.replace(/&/g, "&amp;").replace(/>/g, "&gt;").replace(/</g, "&lt;").replace(/"/g,"&quot;");
			set_title(title);

		});
		// Gets the member list:
		socket.on("join_private_info", function(member) {
			//console.log("recieved members list");
			member = member.replace(/&/g, "&amp;").replace(/>/g, "&gt;").replace(/</g, "&lt;").replace(/"/g,"&quot;");
			member = member.split("%seperatorXD");
			member_state = member[1];
			if(member_state == "Online" ){
				member_state = "<span class='fas fa-train' style = 'color:lime'></span>";
			}
			else{
				member_state = "<span class='fas fa-train' style = 'color:red'></span>";
			}

			$("#members_list").append(member_state + '<b><span style="color:#1a1a1a">'+ member[0] +'</span></b><br>');

		});
		// Gets the date created and the author:
		socket.on("join_private_info_date_author", function(info) {
			//console.log("recieved members list");
			info = info.replace(/&/g, "&amp;").replace(/>/g, "&gt;").replace(/</g, "&lt;").replace(/"/g,"&quot;");

			$("#billboard_info").append(info);

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
			//console.log("sent message");
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
			$("#chat").empty();
			$("#members_list").empty();
			$("#billboard_info").empty();
		}
		/* Disable button to prevent request spamming */
		$('#cchat_createbtn').on('click', function() {
			$("#cchat_createbtn").attr("disabled", true);
		});

	function delete_server(cid){
		socket.emit("delete_private", cid);
	}	
	
	function general_message(){
		if ($("#chat").length <= 1){
			$("#chat").append('<li>' + 'This station is anonymous. No logs saved.' +'</li>');
		}	
	}