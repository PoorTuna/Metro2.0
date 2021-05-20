$(document).ready(function() {
var canvas=document.getElementById("mycan");
canvas.width = $('#mycan').width();
canvas.height = $('#mycan').height();
var ctx = canvas.getContext("2d");
const curr_player = "1"; // GET A MESSAGE THAT DEFINES THIS THROUGH THE SOCKETS and change controls depending on the player

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
			this.y += scale * -1;
		}
		// S or DownArrow 
		if((kp==83)||(kp==40)){
			this.y += scale * 1;
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
					console.log("lmao");
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
		console.log("retd2");
		ball.resetLocation();
	}
	if(ball.x <= 0){
		// call player 1 lost
		ball.xSpeed = scale;
		console.log("retd");
		ball.resetLocation();
	}

	if(player.score >= 10){
		pongWin();
	}
}

function pongLost(){
	//Eating function
	alert("You Lost! your score was:" + player.score);
}
function pongWin(){
	//Eating function
	alert("You Won! your score was:" + player.score);
}

window.setInterval(function(){
	//Clean player,player2
	ctx.clearRect(canvas.width - scale * 2 - 1,0,canvas.width,canvas.height);
	ctx.clearRect(0,0,2*scale + 1,canvas.height);
	//Player 1
	player.update();
	player.draw();
	//Player 2
	player2.update();
	player2.draw();

	ball.collision(player);
	ball.collision(player2);
	check_win();
},0);

window.setInterval(function(){
	ctx.clearRect(scale * 2,0,rows * scale - 2 * scale,canvas.height);

	ball.draw();
	ball.update();
},150);



window.addEventListener("keydown", function(event){
	player.changeDirection(event.keyCode);
	player2.changeDirection(event.keyCode);
});

});