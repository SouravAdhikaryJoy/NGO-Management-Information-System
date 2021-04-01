<?php

namespace App;

use Illuminate\Database\Eloquent\Model;

class UserProfile extends Model
{
    public function user(){
    	return $this->belongsto('App\User');
    }

    public function project(){
    	return $this->belongsto('App\Project');
    }
}
