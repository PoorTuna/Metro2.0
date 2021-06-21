$(document).ready(function() {
var canvas=document.getElementById("mycan");
canvas.width = $('#mycan').width();
canvas.height = $('#mycan').height();
var ctx = canvas.getContext("2d");

// TTC Variables
var curr_player; // get from socket io events
const scale = 3;
const scaled_width = Math.trunc(canvas.width / scale);
const scaled_height = Math.trunc(canvas.height / scale);

const playerColor = window.getComputedStyle(document.getElementById("color")).getPropertyValue('color');
const player2Color = window.getComputedStyle(document.getElementById("color2")).getPropertyValue('color');

var elements = []; 
var myturn = "0";

socket.emit("game_player_position", "True");

socket.on("game_player_position", function(cmd){
	curr_player = cmd;
	if(curr_player == "1"){
	myturn = "1";
}
});


// TTC Object
function Player(x,y){
	this.type = "0"; // x = 1 or o = 2 or None = 0
	this.x = x;
	this.y = y;
	this.draw = function(){
		if(this.type == "1"){
			// draw each part of the x
			ctx.fillStyle = playerColor;
			ctx.fillRect(this.x,this.y, scaled_width, scaled_height);
			ctx.strokeStyle = player2Color;
			ctx.beginPath();

			ctx.moveTo(this.x, this.y);
    	ctx.lineTo(this.x + scaled_width, this.y + scaled_height);
			ctx.moveTo(this.x + scaled_width, this.y);
    	ctx.lineTo(this.x, this.y + scaled_height);
    	ctx.stroke();
		}
		if(this.type == "2"){
			ctx.fillStyle = player2Color;
			ctx.fillRect(this.x,this.y, scaled_width, scaled_height);
			ctx.strokeStyle = playerColor;
			ctx.beginPath();
			ctx.arc(this.x + scaled_width / 2,this.y + scaled_height / 2,scaled_height / 2,0,2*Math.PI);
			ctx.stroke();
		}

	}

}


//This function will call itself once.
(function init(){
	let plusy = 0;
	let plusx = 0;
	for ( let i = 0 ; i < 9 ; i++){
		elements[i] = new Player(plusx,plusy);
		plusx += scaled_width;
		if( (i + 1) % 3 == 0){
			plusx = 0;
			plusy += scaled_height;
		}
	}
}());

function borders(){
// This function creates the borders / the lines.
	ctx.strokeStyle = playerColor;
	ctx.beginPath();
	
	ctx.moveTo(scaled_width, 0);
  ctx.lineTo(scaled_width, canvas.height);

	ctx.moveTo(scaled_width * 2, 0);
  ctx.lineTo(scaled_width * 2, canvas.height);


	ctx.moveTo(0, scaled_height);
  ctx.lineTo(canvas.width, scaled_height);

	ctx.moveTo(0, scaled_height * 2);
  ctx.lineTo(canvas.width, scaled_height * 2);

  ctx.stroke();
} 


function check_win(){
	//Win function
	let win_tgl = "0";
	let win_type = "";
	if (elements[0].type == elements[1].type && elements[1].type == elements[2].type && elements[0].type != "0"){
		win_tgl = "1";
		win_type = elements[0].type;
	}
	if (elements[0].type == elements[3].type && elements[3].type == elements[6].type && elements[0].type != "0"){
		win_tgl = "1";
		win_type = elements[0].type;
	}
	if (elements[0].type == elements[4].type && elements[4].type == elements[8].type && elements[0].type != "0"){
		win_tgl = "1";
		win_type = elements[0].type;
	}
	if (elements[1].type == elements[4].type && elements[4].type == elements[7].type && elements[1].type != "0"){
		win_tgl = "1";
		win_type = elements[1].type;
	}

	if (elements[2].type == elements[4].type && elements[4].type == elements[6].type && elements[2].type != "0"){
		win_tgl = "1";
		win_type = elements[2].type;
	}
	if (elements[2].type == elements[5].type && elements[5].type == elements[8].type && elements[2].type != "0"){
		win_tgl = "1";
		win_type = elements[2].type;
	}
	if (elements[3].type == elements[4].type && elements[4].type == elements[5].type && elements[3].type != "0"){
		win_tgl = "1";
		win_type = elements[3].type;
	}
	if (elements[6].type == elements[7].type && elements[7].type == elements[8].type && elements[6].type != "0"){
		win_tgl = "1";
		win_type = elements[6].type;
	}
	if(win_tgl != "0"){
		if(win_type == curr_player){
			ttcWin();
		}
		else{
			ttcLost();
		}

	}
}
function check_tie(){
	let is_tie = true;
	for(let i = 0 ; i < elements.length ; i++){
		if (elements[i].type == "0"){
			is_tie = false;
		}
	}
	if(is_tie){
		ttcTie();
	}
}

function ttcLost(){
	exit_game('exit');
	for(let i = 0 ; i < elements.length ; i++){
		elements[i].type = "0";
	}
	alert("You Lost!");
	setTimeout(function(){ location.reload(true); }, 1000);
}
function ttcWin(){
	socket.emit("game_win", "tictactoe");
	exit_game('exit');
	for(let i = 0 ; i < elements.length ; i++){
		elements[i].type = "0";
	}
	alert("You Won!");
	setTimeout(function(){ location.reload(true); }, 1000);
}

function ttcTie(){
	exit_game('exit');
	for(let i = 0 ; i < elements.length ; i++){
		elements[i].type = "0";
	}
	alert("It's a Tie!");
	setTimeout(function(){ location.reload(true); }, 1000);
}

window.setInterval(function(){
	for (let i = 0 ; i < 9 ; i++){
		elements[i].draw();
	}
	borders();
	check_win();
	check_tie();
},150);

window.addEventListener("click", function(event){
	if(myturn == "1"){ // get by socket io events
		for( let i = 0 ; i < elements.length ; i++){
			let rect = canvas.getBoundingClientRect();
			let x = event.clientX - rect.left;
			let y = event.clientY - rect.top;

			if((x >= elements[i].x && x <= elements[i].x + scaled_width) && (y >= elements[i].y && y <= elements[i].y + scaled_height)){
				if(elements[i].type == "0"){
					myturn = "0";
					socket.emit("game_update", curr_player + ":" + i )
					elements[i].type = curr_player;
				}
			}
		}
	}
});

socket.on("game_update", function(cmd){
	if (cmd.split(":").length == 2){
		if (cmd.split(":")[0] != curr_player){
		elements[cmd.split(":")[1]].type = cmd.split(":")[0];
		myturn = "1";
		}
	}
});



});
