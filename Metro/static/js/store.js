//Delete Messages recieving function
socket.on("buy_palette", function(msg) {
	//console.log("recieved private message");
	$("#chat").empty();
	msg = msg.replace(/&/g, "&amp;").replace(/>/g, "&gt;").replace(/</g, "&lt;").replace(/"/g,"&quot;");
	alert(msg);
});


	function buy_palette(paletteName) {

		socket.emit("buy_palette", paletteName);
	}