(function($) {

	if ($.ZTFY === undefined) {
		$.ZTFY = {};
	}

	$.ZTFY.captcha = {

		initCaptcha: function() {
			var data = $(this).data();
			var now = new Date();
			var target = '@@captcha.jpeg?id=' + data.captchaId + unescape('%26') + now.getTime();
			$(this).attr('src', target)
				   .off('click')
				   .on('click', $.ZTFY.captcha.initCaptcha);
		}
	}

})(jQuery);
