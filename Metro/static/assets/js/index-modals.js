$(document).ready(function() {
	var footer_text;
	
	function prevent_general_menu(){
		if(footer_text == "general"){
			$("#options_topfooter").hide();
		}
		else{
			$("#options_topfooter").show();
		}
	}

	document.addEventListener("click", function(event) {
		footer_text = document.querySelector("#footertitle span").innerText;
		prevent_general_menu();
	});

});


function close_cchat_modal(){
	$('cchat_modal').modal('hide');
}

function close_amchat_modal(){
	$('amchat_modal').modal('hide');
}

function close_ddsettings_modal(){
	$('ddsettings_modal').modal('hide');
}

function close_ddinfo_modal(){
	$('ddsinfo_modal').modal('hide');
}
		
function close_confirm_delete_modal(){
	$('confirm_delete_modal').modal('hide');
}