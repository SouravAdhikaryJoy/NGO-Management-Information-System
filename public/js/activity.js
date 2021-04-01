//delete Target
$(document).ready(function(){
    $("form.delete-activity").submit(function(){
        return confirm('Are You Sure You Want To Delete The Target Permanently?');
    });
});
