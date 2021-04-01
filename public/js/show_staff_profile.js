//delete from profile
$(document).ready(function(){
    $("form.delete-staff-profile").submit(function(){
        return confirm('Are You Sure You Want To Delete The Profile Permanently?');
    });
});


//save leave status
function save_staff_leave_status(id){

  $(document).ready(function(){
  $('#save_staff_leave_status').click(function(){
     var earned_enjoy = $('#earned_enjoy').text();
     var earned_due = $('#earned_due').text();

     var casual_enjoy = $('#casual_enjoy').text();
     var casual_due = $('#casual_due').text();

     var medical_enjoy = $('#medical_enjoy').text();
     var medical_due = $('#medical_due').text();

     var maternity_enjoy = $('#maternity_enjoy').text();
     var maternity_due= $('#maternity_due').text();

     var paternity_enjoy = $('#paternity_enjoy').text();
     var paternity_due= $('#paternity_due').text();

     var study_enjoy = $('#study_enjoy').text();
     var study_due = $('#study_due').text();
     var _token = $('input[name=_token]').val();

     console.log(earned_enjoy);

     $.ajax({
              type: "PUT",
              url:'/leave/'+id,
              data: {
                earned_enjoy: earned_enjoy,
                earned_due: earned_due,

                casual_enjoy: casual_enjoy,
                casual_due: casual_due,

                medical_enjoy: medical_enjoy,
                medical_due: medical_due,

                maternity_enjoy: maternity_enjoy,
                maternity_due: maternity_due,

                paternity_enjoy: paternity_enjoy,
                paternity_due: paternity_due,

                study_enjoy: study_enjoy,
                study_due: study_due,

                _token:_token,

              },
              success: function() {
                  $('div.saved-fade-out').html("<p class='alert alert-success' id='saved-fade-out'>Saved successfully</p>");
                  $('#saved-fade-out').fadeOut(3000);

              }
          });
  });
  });


}
