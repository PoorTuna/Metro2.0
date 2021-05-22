$(document).ready(function() {
var canvas=document.getElementById("mycan");
canvas.width = $('#mycan').width();
canvas.height = $('#mycan').height();
var ctx = canvas.getContext("2d");
var curr_player; // GET A MESSAGE THAT DEFINES THIS THROUGH THE SOCKETS and change controls depending on the player
var cmd_player;
var command;
var finished = false;

var player1_score = document.getElementById("p1score");
var player2_score = document.getElementById("p2score");

// Assign places for the game:
socket.emit("game_player_position", "True");

socket.on("game_player_position", function(cmd){
	curr_player = cmd;
});


// Pong Variables
const scale = 20;
const rows = Math.trunc(canvas.width / scale); // realised it's the other way around
const columns = Math.trunc(canvas.height / scale);
const playerColor = window.getComputedStyle(document.getElementById("funny")).getPropertyValue('color');
const ballColor = window.getComputedStyle(document.getElementById("funny2")).getPropertyValue('color');

var player; 
// Player Object
function Player(x,y){
	this.x = x;
	this.y = y;
	this.score = 0;

	this.draw = function(){
		ctx.fillStyle = playerColor;
		ctx.fillRect(this.x,this.y, scale, scale * 5);
	}
	this.update = function(){

		if(this.y + scale * 5 > canvas.height){
			this.y = canvas.height - scale*5;
		}
		if(this.y < 0){
			this.y = 0;
		}


	}


	this.changeDirection = function(kp){
		// W or UpArrow 
		if((kp==87)||(kp==38)){
			socket.emit("game_update", curr_player + ":" + "up");
		}
		// S or DownArrow 
		if((kp==83)||(kp==40)){
			socket.emit("game_update", curr_player + ":" + "down");
		}

	}
}
// Ball Object
function Ball(){
	this.x = Math.trunc((rows / 2)) * scale;
	this.y = Math.trunc((columns / 2)) * scale;
	this.xSpeed = scale;
	this.ySpeed = scale;

	this.draw = function(){
		ctx.fillStyle = ballColor;
		ctx.fillRect(this.x,this.y, 20, 20);

	}
	this.update = function(){
		
		this.y += this.ySpeed;
		this.x += this.xSpeed;

		if(this.y + scale >= canvas.height){
			this.y = canvas.height - scale * 2;

			this.ySpeed = scale * -1
		}
		if(this.y < 0){
			this.y = scale;
			this.ySpeed = scale;
		}

	}

	this.resetLocation = function(){
		this.x = Math.trunc((rows / 2)) * scale;
		this.y = Math.trunc((columns / 2)) * scale;

	}
	this.collision = function(player){
		//first is to player 2, second to player 1
		if((this.x + scale == player.x) || (this.x - scale == player.x))
		{
			if((this.y >= player.y) && (this.y <= player.y + scale * 5)){
				//Hit on the bottom part
				if ((this.y >= player.y + scale * 3) && (this.y <= player.y + scale * 5)){
					this.ySpeed = scale * - 1;
					if (this.x + scale == player.x){
						this.xSpeed = scale * -1;
						this.x += scale * -1;
					}
					if (this.x - scale == player.x){
						this.xSpeed = scale;
						this.x += scale;
					}

				}
				//Hit on the top part
				if ((this.y >= player.y) && (this.y <= player.y + scale * 3)){
					this.ySpeed = scale;
					if (this.x + scale == player.x){
						this.xSpeed = scale * -1;
						this.x += scale * -1;
					}
					if (this.x - scale == player.x){
						this.xSpeed = scale;
						this.x += scale;
					}

				}
			}
		}

	}


}
//This function will call itself once.
(function init(){
	player = new Player(scale,(columns / 2 )* scale);
	player2 = new Player((rows-2) * scale,(columns / 2 )* scale);
	ball = new Ball();
}());

function check_win(){
	//Eating function
	if(ball.x + scale >= rows * scale){
		// call player 2 lost
		ball.xSpeed = scale * -1;
		if(curr_player == "1"){
		socket.emit("score_update", "1")
		}
		
		ball.resetLocation();
	}
	if(ball.x <= 0){
		// call player 1 lost
		ball.xSpeed = scale;
		if(curr_player == "1"){
		socket.emit("score_update", "2")
		}

		ball.resetLocation();
	}

	if(curr_player == "1"){
		if(player.score >= 10){
			pongWin();
		}

		if(player2.score >= 10){
			pongLost();
		}
	}

	if(curr_player == "2"){
		if(player.score >= 10){
			pongLost();
		}

		if(player2.score >= 10){
			pongWin();
		}
	}

}

function pongLost(){
	//Eating function
	alert("You Lost! your score was:" + player.score);
		exit_game('exit')
		location.reload();
}
function pongWin(){
	//Eating function
	socket.emit("game_win", "pong");
	exit_game('exit');
	alert("You Won! your score was:" + player.score);
	location.reload();
	player.score = 0;
	player2.score = 0;
}

window.setInterval(function(){
	if(!finished){
		//Clean player,player2
		ctx.clearRect(canvas.width - scale * 2 - 1,0,canvas.width,canvas.height);
		ctx.clearRect(0,0,2*scale + 1,canvas.height);
		//Player 1
		player.update();
		player.draw();
		//Player 2
		player2.update();
		player2.draw();

		//Collision
		ball.collision(player);
		ball.collision(player2);
		check_win();
	}

},0);

window.setInterval(function(){
	//Clean ball
	ctx.clearRect(scale * 2,0,rows * scale - 2 * scale,canvas.height);
	//Ball
	if(!finished){
	ball.draw();
	ball.update();
	}

},75);



window.addEventListener("keydown", function(event){
	player.changeDirection(event.keyCode);
	player2.changeDirection(event.keyCode);
});

socket.on("score_update", function(ply){
	if(ply == "1"){
		player.score += 1;
		player1_score.innerText = player.score;
	}
	else if(ply == "2"){
		player2.score += 1;
		player2_score.innerText = player.score;
	}

});

socket.on("game_update", function(cmd){
	if (cmd.split(":").length == 2){
		cmd_player = cmd.split(":")[0];
		command = cmd.split(":")[1];
		if (cmd_player == "1"){
			if (command == "up"){
				player.y += scale * -1;
			}
			if (command == "down"){
				player.y += scale * 1;
			}
		}
		else if(cmd_player == "2"){
			if (command == "up"){
				player2.y += scale * -1;
			}
			if (command == "down"){
				player2.y += scale * 1;
			}
		}
	}
});


});
