/* After loading the page, softly scroll to the #kofa-scroll-target tag,
   if it exists */
$(document).ready(function (){
    var scroll_target = $('#kofa-scroll-target');
    if (scroll_target.length) {
	$('html,body').animate(
            {
		scrollTop: scroll_target.offset().top
		    - $(window).height() + 2 * scroll_target.height()
            })
    }
});
