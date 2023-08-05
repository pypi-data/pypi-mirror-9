$(function() {
  $( ".datepicker" ).datepicker({ dateFormat: 'yy-mm-dd',
                                  duration: 'fast'
  });
});

$(function() {
  $( ".datepicker-le" ).datepicker({dateFormat: 'dd/mm/yy',
	duration: 'fast'
	});
  });

$(function() {
  $( ".datepicker-de" ).datepicker({dateFormat: 'dd.mm.yy',
	duration: 'fast'
	});
  });

$(function() {
  $( ".datepicker-us" ).datepicker({dateFormat: 'mm/dd/yy',
	duration: 'fast'
	});
  });

$(function() {
  $( ".datepicker-year" ).datepicker({ dateFormat: 'yy-mm-dd',
	duration: 'fast',
	changeYear: true,
	yearRange: '1900:2020'
	});
});

$(function() {
  $( ".datepicker-le-year" ).datepicker({dateFormat: 'dd/mm/yy',
	duration: 'fast',
	changeYear: true,
	yearRange: '1900:2020'
	});
  });

$(function() {
  $( ".datepicker-de-year" ).datepicker({dateFormat: 'dd.mm.yy',
	duration: 'fast',
	changeYear: true,
	yearRange: '1900:2020'
	});
  });

$(function() {
  $( ".datepicker-us-year" ).datepicker({dateFormat: 'mm/dd/yy',
	duration: 'fast',
	changeYear: true,
	yearRange: '1900:2020'
	});
  });
