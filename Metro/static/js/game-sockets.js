		const socket = io('https://' + document.domain + ':' + location.port ,{ secure: true });
		var tts = new SpeechSynthesisUtterance();
		var game_id;
		var game_name;
		var join_modal = document.getElementById("join_game_modal_id");

		
		// Notify user when connected in logs
		socket.on('connect', function() {
			//console.log("connected to the chat");
			socket.emit("connect_game", "1")
		});
		socket.on('disconnect', function() {
			//console.log("disconnected from the chat");
			socket.emit("disconnect_game", "0")
		});

		// Message recieving function
		socket.on("game_message", function(msg) {
			//console.log("recieved message");
			msg = msg.replace(/&/g, "&amp;").replace(/>/g, "&gt;").replace(/</g, "&lt;").replace(/"/g,"&quot;");
			$("#chat").append('<li style="color:var(--metro_energy)">'+msg+'</li>');
		});
		// Private Message recieving function
		socket.on("private_message", function(msg) {
			//console.log("recieved private message");
			msg = msg.replace(/&/g, "&amp;").replace(/>/g, "&gt;").replace(/</g, "&lt;").replace(/"/g,"&quot;");
			$("#chat").append('<li style="color:var(--metro_primary)">'+ "[W] " + msg +'</li>');
		});

		//TTS Message recieving function
		socket.on("announce_message", function(msg) {
			//console.log("recieved private message");
			msg = msg.replace(/&/g, "&amp;").replace(/>/g, "&gt;").replace(/</g, "&lt;").replace(/"/g,"&quot;");
			$("#chat").append('<li>'+ msg +'</li>');
			username_time = msg.split(":")[1]; // the username with time pos 1 and not 0 because of time format Hour:Minute ":" <--- !!!

			username = username_time.split("|")[1]; // the username after time has been cut

			tts.text = username + "says" + msg.slice(username_time.length + 2);
			console.log(tts.text);
			speechSynthesis.speak(tts);
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
			$("#members_list").append(member_state + '<b><span style="color:#1a1a1a">'+ member[0]+'</span></b><br>');

		});

		// Gets the member list:
		socket.on('join_request', function(request) {
			request = request.split("|");

			game_id = request[2];
			game_name = request[1];
			document.getElementById("join_username").innerText = request[0];
			document.getElementById("join_game_name").innerText = request[1];
			$("#chat").append('<li style="color:var(--metro_primary)">'+ "[W]" + "[ " + request[0] + "]"+ " has invited you to a game of " + request[1] + '<a href="javascript:void(0)" data-toggle="modal" data-target="#join_game_modal_id" style="color:var(--metro_energy)">' +  "Click here </a>" +'</li>');

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
			socket.emit("game_message", $('#myMessage').val());
			$('#myMessage').val("");
			}
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

		function choose_game(name){
			socket.emit("game_choose", name);
			$("#choose_game_table").hide();
			$("#choose_game_table").innerText = "Creating a Station...";
			setTimeout(function(){ location.reload(true); }, 1000);
		}

		function start_game(name){
			socket.emit("game_start", name);
			setTimeout(function(){ location.reload(true); }, 1000); /* Reload for everyone in the room */
		}

		function check_start(name){
			socket.emit("allow_start", name);
		}
		

		function exit_game(name){
			socket.emit("game_exit", name);
			setTimeout(function(){ location.reload(true); }, 1000); /* Reload for everyone in the room */
		}

		function check_count(){
			socket.emit("allow_start", "something");
		}

		function modal_join_game(){
			socket.emit("join_private_game", game_id + "|" + game_name);
			setTimeout(function(){ location.reload(true); }, 1000);
			
		}

		socket.on("allow_start", function(msg){
			start_game('start');
		});

		socket.on("player_joined", function(pname){
			$("#players").append("</br></li>" + pname + "</li>");
		});
		