$(document).ready(function() {
var canvas=document.getElementById("mycan");
canvas.width = $('#mycan').width();
canvas.height = $('#mycan').height();
var ctx = canvas.getContext("2d");

// Snake Variables
const rows = canvas.width / 3;
const columns = canvas.height / 3;
const scale = canvas.width / rows;
const playerColor = window.getComputedStyle(document.getElementById("funny")).getPropertyValue('color');
const player2Color = window.getComputedStyle(document.getElementById("funny2")).getPropertyValue('color');

var snake; 
// Snake Object
function Player(type){
	this.place = [];
	this.type = type;
	this.draw = function(){
		if(this.type == "1"){
			ctx.fillStyle = playerColor;
			// draw each part of the x
			for( let i = 0; i < this.place.length; i++){
				ctx.fillRect(this.place[i].x,this.place[i].y, scale, scale);
			}
			//draw the first part of the snake
			ctx.fillRect(this.x,this.y, scale, scale);
		}
		if(this.type == "2"){
			ctx.fillStyle = player2Color;
			// draw each part of the o
			for( let i = 0; i < this.place.length; i++){
				ctx.fillRect(this.place[i].x,this.place[i].y, scale, scale);
			}
			//draw the first part of the snake
			ctx.fillRect(this.x,this.y, scale, scale);
		}

	}
	this.update = function(){

		this.tail[this.total-1] = {x: this.x, y: this.y};

		this.x += this.xSpeed;
		this.y += this.ySpeed;
		if(this.x > canvas.width){
			snakeLost();
		}
		if(this.x < 0){
			snakeLost();
		}
		if(this.y > canvas.height){
			snakeLost();
		}
		if(this.y < 0){
			snakeLost();
		}

	this.win = function(fruit){
		if ((this.x == fruit.x) && (this.y == fruit.y))
		{
			return true;
		}
		else{
			return false;
		}

	}

	}
}

//This function will call itself once.
(function init(){
	player1 = new Player("1");
	player2 = new Player("2");
	fruit.pickLocation();
}());

function check_win(){
	//Eating function
	if(snake.total >= 10){
		ttcWin();
	}
}

function ttcLost(){
	exit_game('exit');
	player1.place = [];
	player2.place = [];
	alert("You Lost!");
	location.reload();
}
function ttcWin(){
	socket.emit("game_win", "snake");
	exit_game('exit');
	player1.place = [];
	player2.place = [];
	alert("You Won!");
	location.reload();
}

window.setInterval(function(){
	player1.draw();
	player2.draw();
	check_eat();
	check_win();
},150);

window.addEventListener("click", function(event){
// event.clientX;
// event.clientY;

});

});