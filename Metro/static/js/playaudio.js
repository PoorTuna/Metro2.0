var audio = document.getElementById("metro_ambience");
var audio2 = document.getElementById("metro_ambience2");
var not_played = true;
audio.volume = 0.5;
audio2.volume = 0.5;
const rndInt = Math.floor(Math.random() * 2) + 1;

(function init_sound(){
	if(rndInt == 1){
		audio2.pause();
	}
	else{
		audio.pause();
	}
}());

document.addEventListener("click", function(event) {
	if(not_played){
		not_played = false;
		if(rndInt == 1){
			audio.play();
		}
		else{
			audio2.play();
		}
	}

});