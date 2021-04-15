$(document).ready(function() {
	var footer_text;
	function prevent_general_add(){
		if(footer_text == "general"){
			$("#footertitle").attr("data-target", "");
		}
		else{
			$("#footertitle").attr("data-target", "#amchat_modal");
		}
	}

	document.addEventListener("click", function(event) {
		footer_text = document.querySelector("#footertitle span").innerHTML;
		prevent_general_add();
	});

});