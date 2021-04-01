<?php

namespace App;

use Illuminate\Database\Eloquent\Model;

class StaffProfile extends Model
{
  protected $guarded = ['id'];

    public function staff_leave_status(){
    return  $this->hasOne('App\Staff_Leave_Status','staff_profile_id');
    }
}
