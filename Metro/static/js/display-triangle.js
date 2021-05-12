$(document).ready(function() {
	var triangle_img = document.getElementById("error_triangle");
	var train = document.getElementById("error_train");
	var not_displayed = true;
	
	function triangle_display(){
	 	if (train.offsetLeft >= window.innerWidth / 2){
			triangle_img.style.display = "block";
			not_displayed = false;
	 }
	}
	if(not_displayed){
	setInterval(triangle_display, 100);
	}
});