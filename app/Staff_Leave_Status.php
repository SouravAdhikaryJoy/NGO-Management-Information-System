<?php

namespace App;

use Illuminate\Database\Eloquent\Model;

class Staff_Leave_Status extends Model
{
  protected $guarded = ['id'];

    public function staffProfile(){
    return  $this->belongsto('App\StaffProfile','staff_profile_id');
    }
}
