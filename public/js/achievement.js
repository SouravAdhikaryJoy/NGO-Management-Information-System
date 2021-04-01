//delete achievement
$(document).ready(function(){
    $("form.delete-achievement").submit(function(){
        return confirm('Are You Sure You Want To Delete The Achievement Permanently?');
    });
});
