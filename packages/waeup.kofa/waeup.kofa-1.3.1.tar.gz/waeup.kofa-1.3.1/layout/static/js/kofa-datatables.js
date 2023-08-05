$(document).ready(function(){

  $('.dataTable').dataTable( {
    "iDisplayLength": 1000,
    "iDisplayEnd": 1000,
    "aLengthMenu": [ 50, 100, 1000, 5000 ],
  } );

	$('.dataTableFiles').dataTable( {
    "aaSorting": [[ 2, "desc" ]],
    "iDisplayLength": 1000,
    "iDisplayEnd": 1000,
    "aLengthMenu": [ 50, 100, 1000, 5000 ],
	} );

	$('.dataTableManage').dataTable( {
    "aaSorting": [[ 1, "asc" ]],
    "aoColumnDefs":[{ "bSortable": false, "aTargets": [ 0 ] }],
    "iDisplayLength": 1000,
    "iDisplayEnd": 1000,
    "aLengthMenu": [ 50, 100, 1000, 5000 ],
	} );

	$('.dataTableManageFiles').dataTable( {
    "aaSorting": [[ 3, "desc" ]],
    "aoColumnDefs":[{ "bSortable": false, "aTargets": [ 0 ] }],
    "iDisplayLength": 1000,
    "iDisplayEnd": 1000,
    "aLengthMenu": [ 50, 100, 1000, 5000 ],
	} );

});
