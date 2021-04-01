<?php

namespace App;

use Illuminate\Database\Eloquent\Model;

class Activity extends Model
{
  protected $guarded = [];
  
    public function project(){
      return $this->belongsto('App\Project');
    }
    public function achievements(){
      return $this->hasMany('App\Achievement','activity_id');
    }
    public function targets(){
      return $this->hasMany('App\Target','activity_id');
    }
}
