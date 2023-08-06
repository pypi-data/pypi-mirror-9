(function() {
	"use strict";
	if ($(window).width() < 768) {
		$(window).load(function() {
			// Re-allign data center information in the mobile app
			// to the top. To be changed later to correctly reallign
			// using native views api.
			$("div.additional-info").insertBefore("div.basic-info");
		})
	}
})();
