<?php

namespace App;

use Illuminate\Database\Eloquent\Model;

class Achievement extends Model
{
  public function activity(){
    return $this->belongsto('App\Activity','activity_id');
  }
  
}
