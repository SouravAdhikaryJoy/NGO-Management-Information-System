<?php

namespace App;

use Illuminate\Database\Eloquent\Model;

class Project extends Model
{
  public function activity(){
    return $this->hasMany('App\Activity');
  }


  public function targets()
  {
      return $this->hasManyThrough('App\Target','App\Activity','project_id','activity_id');
  }
  public function achievements()
  {
      return $this->hasManyThrough('App\Achievement','App\Activity',
        'project_id','activity_id','id','id');
  }

  public function profile(){
    return $this->hasMany('App\UserProfile');
  }

  
}
