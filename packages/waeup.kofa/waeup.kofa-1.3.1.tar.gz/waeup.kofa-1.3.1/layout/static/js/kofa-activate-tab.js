$(document).ready(function(){

/*
Activate current tab, if any, but jump to top, if hash value contains '-top'
*/

  var anchor = window.location.hash.replace('-top','');
  $('a[href="' + anchor + '"]').trigger('click');

});