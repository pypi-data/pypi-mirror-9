(function($){
	$.fn.BottomTop = function(pos,cssClass,anchor) {

		var easingType = 'easeInOutCubic';
		var min = -1;
		var inDelay = 500;
		var outDelay = 500;
		var scrollSpeed = 750;
		var containerIDhash = '#' + pos;

		// Auto Link
		$('body').append('<a href="#'+anchor+'" id="'+pos+'" class="'+cssClass+'" />');
    if (anchor == 'bottom') {
  		$(containerIDhash).hide().click(function(){
  			$('html, body').animate({scrollTop:$(bottom).offset().top}, scrollSpeed, easingType);
  			return false;
  		})
      }
    if (anchor == '') {
  		$(containerIDhash).hide().click(function(){
  			$('html, body').animate({scrollTop:0}, scrollSpeed, easingType);
  			return false;
  		})
      }

		$(window).scroll(function() {
			var sd = $(window).scrollTop();

			if ( sd > min )
				$(containerIDhash).fadeIn(inDelay);
			else
				$(containerIDhash).fadeOut(Outdelay);
		});

};
})(jQuery);


$(document).ready(function(){
	$('.top').BottomTop('toTop-right','scroll-up','');
});

$(document).ready(function(){
	$('.bottom').BottomTop('toBottom-right','scroll-down','bottom');
});