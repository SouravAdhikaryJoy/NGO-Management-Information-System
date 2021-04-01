$(document).ready(function(){
    $("form.delete-project").submit(function(){
        return confirm('Are You Sure You Want To Delete The Project Permanently?');
    });
});