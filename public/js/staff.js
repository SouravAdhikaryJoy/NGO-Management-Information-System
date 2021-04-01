
	$('#check').change(function() {
    if($(this).is(":checked")) {
        $('#closing_date').hide();
    }
else{
        $('#closing_date').show();
    }                                          
});


