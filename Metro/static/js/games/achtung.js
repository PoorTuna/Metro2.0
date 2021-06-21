$(document).ready(function() {
var canvas=document.getElementById("mycan");
canvas.width = $('#mycan').width();
canvas.height = $('#mycan').height();
var ctx = canvas.getContext("2d");

// Achtung Variables
var curr_player = "1"; // get from socket io events
const scale = 20;
const rows = canvas.width / scale;
const columns = canvas.height / scale;
const player1Color = window.getComputedStyle(document.getElementById("color")).getPropertyValue('color');
const player2Color = window.getComputedStyle(document.getElementById("color2")).getPropertyValue('color');
const player3Color = window.getComputedStyle(document.getElementById("color3")).getPropertyValue('color');
const player4Color = window.getComputedStyle(document.getElementById("color4")).getPropertyValue('color');

var player1_score = document.getElementById("p1score");
var player2_score = document.getElementById("p2score");
var player3_score = document.getElementById("p3score");
var player4_score = document.getElementById("p4score");

socket.emit("game_player_position", "True");

socket.on("game_player_position", function(cmd){
	curr_player = cmd;

});

socket.on("score_update", function(ply){
	if(ply == "1"){
		players[0].score += 1;
		player1_score.innerText = players[0].score;
	}
	else if(ply == "2"){
		players[1].score += 1;
		player2_score.innerText = players[1].score;
	}
	else if(ply == "3"){
		players[2].score += 1;
		player3_score.innerText = players[2].score;
	}
	else if(ply == "4"){
		players[3].score += 1;
		player4_score.innerText = players[3].score;
	}

});

var players = []; 
var players_init_pos = [];
// Player Object
function Player(x,y,color,dir){
	this.x = x;
	this.y = y;
	this.xSpeed = dir;
	this.ySpeed = 0;
	this.total = 0;
	this.tail = [];
	this.dead = 0;
	this.score = 0;
	this.playerColor = "";
	
	if(color == 0){
		this.playerColor = player1Color;
	}
	else if(color == 1){
		this.playerColor = player2Color;
	}
	else if(color == 2){
		this.playerColor = player3Color;
	}
	else if(color == 3){
		this.playerColor = player4Color;
	}

	this.draw = function(){
		ctx.fillStyle = this.playerColor;
		// draw each part of the snake's tail
		for( let i = 0; i < this.tail.length; i++){
			ctx.fillRect(this.tail[i].x,this.tail[i].y, scale, scale);
		}
		//draw the first part of the player
		ctx.fillRect(this.x,this.y, scale, scale);
	}
	this.update = function(){
		this.tail[this.total] = {x: this.x, y: this.y};
		this.total += 1

		this.x += this.xSpeed;
		this.y += this.ySpeed;

		if(this.x > canvas.width){
			this.dead = 1;
		}
		if(this.x < 0){
			this.dead = 1;
		}
		if(this.y > canvas.height){
			this.dead = 1;
		}
		if(this.y < 0){
			this.dead = 1;
		}
		for( let i = 0; i < this.tail.length; i++){
			if (this.x == this.tail[i].x && this.y == this.tail[i].y){
				this.dead = 1;
			}

		}

	}
	this.death = function(player){
		if (player.tail.length > 0){
			for( let i = 0; i < player.tail.length; i++){
				if (this.x == player.tail[i].x && this.y == player.tail[i].y){
					this.dead = 1;
				}

			}
		}
	}

		this.changeDirection = function(kp){
			// A or LeftArrow 
			if((kp==65)||(kp==37)){
				this.xSpeed = scale * -1;
				this.ySpeed = 0;
			}
			// D or RightArrow 
			if((kp==68)||(kp==39)){
				this.xSpeed = scale * 1;
				this.ySpeed = 0;
			}
			// W or UpArrow 
			if((kp==87)||(kp==38)){
				this.ySpeed = scale * -1;
				this.xSpeed = 0;
			}
			// S or DownArrow 
			if((kp==83)||(kp==40)){
				this.ySpeed = scale * 1;
				this.xSpeed = 0;
			}

	}
}

//This function will call itself once.
(function init(){
	players_init_pos = [[scale, scale],[scale * (rows - 2), scale, 1],[scale, scale * (columns - 2)],[scale * (rows - 2), scale * (columns - 2)]];
	players.push( new Player(players_init_pos[0][0], players_init_pos[0][1], 0, scale) );
	players.push( new Player(players_init_pos[1][0], players_init_pos[1][1], 1, scale * -1) );
	players.push( new Player(players_init_pos[2][0], players_init_pos[2][1], 2, scale) );
	players.push( new Player(players_init_pos[3][0], players_init_pos[3][1], 3, scale * -1) );
	
}());

function check_win(){
	for (let i = 0 ; i < 4 ; i++){
		if(players[i].score >= 10){
				alert("Player" + i + "Won!");
		}
	}
}
function roundOver(){
	let deadCount = 0;
	for (let i = 0 ; i < 4 ; i++){
		if(players[i].dead){
			deadCount += 1;
		}
	}
	if(deadCount >= 3){
		for (let i = 0 ; i < 4 ; i++){
			if(!players[i].dead){
				if (parseInt(curr_player) - 1 == i){
					socket.emit("score_update", i+1);
				}
			}
			
			players[i].x = players_init_pos[i][0];
			players[i].y = players_init_pos[i][1];
			players[i].dead = 0;
			players[i].tail = [];
			players[i].total = 0;
			if (i == 0 || i == 2){
				players[i].xSpeed = scale;
			}
			else{
				players[i].xSpeed = scale * -1;
			}
			players[i].ySpeed = 0;
		}
	}
}
function playerLost(){
	exit_game('exit');
	alert("You Lost! your score was:" + players[parseInt(curr_player) - 1]);
	setTimeout(function(){ location.reload(true); }, 1000);
	players[parseInt(curr_player) - 1].total = 0;
}
function playerWin(){
	socket.emit("game_win", "achtung");
	exit_game('exit');
	alert("You Won! your score was:" + player.total);
	setTimeout(function(){ location.reload(true); }, 1000);
	players[parseInt(curr_player)].total = 0;

}

window.setInterval(function(){
	ctx.clearRect(0,0,canvas.width,canvas.height);
	for(let i = 0 ; i < 4 ; i++){
		if(players[i]){
			players[i].draw();
			if(!players[i].dead){
			players[i].update();
			}
			for(let x = 0 ; x < 4 ; x++){
				if(x != i && players[x]){
					
					players[i].death(players[x]);
				}
			}
		}
	}
	roundOver();
	check_win();
},150);

window.addEventListener("keydown", function(event){
	socket.emit("game_update", curr_player + ":" + event.keyCode);
});

socket.on("game_update", function(cmd){
	if (cmd.split(":").length == 2){
		cmd = cmd.split(":");
		if(isNaN(cmd[1])){
			players[parseInt(curr_player)].changeDirection(parseInt(cmd[1]) - 1);
		}
	}

});


});