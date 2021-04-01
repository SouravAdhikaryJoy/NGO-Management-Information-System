<?php

namespace App;

use Illuminate\Database\Eloquent\Model;

class Target extends Model
{
  public function activity(){
    return $this->belongsto('App\Activity','activity_id');
  }
  public function project(){
    return $this->belongsto('App\Project');
  }
}
