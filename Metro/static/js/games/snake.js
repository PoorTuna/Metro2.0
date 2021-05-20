$(document).ready(function() {
var canvas=document.getElementById("mycan");
canvas.width = $('#mycan').width();
canvas.height = $('#mycan').height();
var ctx = canvas.getContext("2d");

// Snake Variables
const scale = 20;
const rows = canvas.width / scale;
const columns = canvas.height / scale;
const snakeColor = window.getComputedStyle(document.getElementById("funny")).getPropertyValue('color');
const fruitColor = window.getComputedStyle(document.getElementById("funny2")).getPropertyValue('color');

var snake; 
// Snake Object
function Snake(){
	this.x = 0;
	this.y = 0;
	this.xSpeed = scale;
	this.ySpeed = 0 ;
	this.total = 0;
	this.tail = [];

	this.draw = function(){
		ctx.fillStyle = snakeColor;
		// draw each part of the snake's tail
		for( let i = 0; i < this.tail.length; i++){
			ctx.fillRect(this.tail[i].x,this.tail[i].y, scale, scale);
		}
		//draw the first part of the snake
		ctx.fillRect(this.x,this.y, scale, scale);
	}
	this.update = function(){
		for( let i = 0; i < this.tail.length - 1 ; i++){

			this.tail[i] = this.tail[i + 1];
		}

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

	this.eat = function(fruit){
		if ((this.x == fruit.x) && (this.y == fruit.y))
		{
			return true;
		}
		else{
			return false;
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
// Fruit Object
function Fruit(){
	this.x = 0;
	this.y = 0;

	this.draw = function(){
		ctx.fillStyle = fruitColor;
		ctx.fillRect(this.x,this.y, scale, scale)

	}

	this.pickLocation = function(){
		this.x = (Math.floor(Math.random() * rows - 1) +  1) * scale;
		this.y = (Math.floor(Math.random() * columns - 1) + 1) * scale;

	}

}
//This function will call itself once.
(function init(){
	snake = new Snake();
	fruit = new Fruit();
	fruit.pickLocation();
}());

function check_eat(){
	//Eating function
	if(snake.eat(fruit)){
		fruit.pickLocation();
		snake.total += 1;
	}
}
function check_win(){
	//Eating function
	if(snake.total >= 10){
		snakeWin();
	}
}

function snakeLost(){
	//Eating function
	alert("You Lost! your score was:" + snake.total);
}
function snakeWin(){
	//Eating function
	alert("You Won! your score was:" + snake.total);
	//socket stuff goes here and in snakelost
}

window.setInterval(function(){
	ctx.clearRect(0,0,canvas.width,canvas.height)
	fruit.draw();
	snake.update();
	snake.draw();
	check_eat();
	check_win();
},150);

window.addEventListener("keydown", function(event){
	snake.changeDirection(event.keyCode);
});

});