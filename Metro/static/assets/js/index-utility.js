	var tts = new SpeechSynthesisUtterance();
		/* SideNav function */

		function openNav() {
			document.getElementById("mySidenav").style.width = "250px";
		}

		/* Set the width of the side navigation to 0 and the left margin of the page content to 0 */
		function closeNav() {
			document.getElementById("mySidenav").style.width = "0";
		}

		/* Auto Scroll Function */
		var userHasNotScrolled = true;
		
		function disable_auto_scroll(){
			userHasNotScrolled = false;
		}

		function auto_scroll(){
			var $panel = $('.mainbox');
			var shouldScroll = $panel[0].scrollHeight - $panel.height() <= $panel.scrollTop() + 50;
			if (userHasNotScrolled){
				if (shouldScroll) {
						$panel.scrollTop($panel[0].scrollHeight);
				}
			}
			userHasNotScrolled = true;
		}
		setInterval(auto_scroll, 10);
		
		// function change_voices(){
		// 	var synth = window.speechSynthesis;
		// 	var voices = synth.getVoices();
		// 	console.log(voices);
		// 	tts.voice = voices[2];
		// }

		