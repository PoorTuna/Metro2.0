navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia;
navigator.getUserMedia({video:false,audio:true},record_voice,console.log);

var destination
function record_voice(stream){
	window.AudioContext = window.AudioContext || window.webkitAudioContext;
  ctx = new AudioContext();
  mic = ctx.createMediaStreamSource(stream);
  spe = ctx.createAnalyser();
  spe.fftSize = 256;
  bufferLength = spe.frequencyBinCount;
  dataArray = new Uint8Array(bufferLength);
  spe.getByteTimeDomainData(dataArray);
  mic.connect(spe);
  //spe.connect(ctx.destination); // Connect the mic input to the speaker
	//console.log(stream);
	//send_voice(stream);
	//ctx.decodeAudioData(bufferLength, console.log, console.log);

}


var click_type = 0;
document.addEventListener('click', function(e) {
	if(click_type == 0){
		ctx.suspend();
		click_type = 1;
	}

	else{
		ctx.resume();
		click_type = 0;
	}

});

// function send_voice(voice){
// 	socket.emit("send_voice", voice);
// }

// socket.on("recv_voice", function(voice) {
// 	console.log(voice);
// });