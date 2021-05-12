var audio = document.getElementById("metro_ambience");
var not_played = true ;
audio.volume = 0.2;

document.addEventListener("click", function(event) {
	if(not_played){
		not_played = false;
		audio.play();
	}

});