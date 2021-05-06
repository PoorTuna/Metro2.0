
navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia;
navigator.getUserMedia({video:false,audio:true},record_voice,console.log);

function record_voice(stream){
  ctx = new AudioContext();
  mic = ctx.createMediaStreamSource(stream);
  spe = ctx.createAnalyser();
  spe.fftSize = 256;
  bufferLength = spe.frequencyBinCount;
  dataArray = new Uint8Array(bufferLength);
  spe.getByteTimeDomainData(dataArray);
  mic.connect(spe);
  spe.connect(ctx.destination);
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
setInterval(function(){ console.log(ctx); }, 10);
