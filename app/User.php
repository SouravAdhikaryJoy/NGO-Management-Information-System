<?php

namespace App;
use App\Project;
use Illuminate\Notifications\Notifiable;
use Illuminate\Contracts\Auth\MustVerifyEmail;
use Illuminate\Foundation\Auth\User as Authenticatable;

class User extends Authenticatable
{
    use Notifiable;

    /**
     * The attributes that are mass assignable.
     *
     * @var array
     */
    protected $fillable = [
        'name', 'email', 'password',
    ];

    /**
     * The attributes that should be hidden for arrays.
     *
     * @var array
     */
    protected $hidden = [
        'password', 'remember_token',
    ];

    public function profile(){
        return $this->hasOne('App\UserProfile');
    }
    public function notifications(){
        return $this->hasMany('App\Notification');
    }




    /*
    Access:--> superAdmin, projectAdmin, projectAgent,Moderator,chiefAccountant,Accountant 

 */

    public function isSuperAdmin(){
       return $this->profile->access== "superAdmin";
    }
    public function isProjectAdmin(){
       return $this->profile->access== "projectAdmin";
    }
    public function isProjectAgent(){
       return $this->profile->access== "projectAgent";
    }
    public function isModerator(){
       return $this->profile->access== "Moderator";
    }
    public function isChiefAccountant(){
       return $this->profile->access== "chiefAccountant";
    }
    public function isAccountant(){
       return $this->profile->access== "Accountant";
    }

    public function project_id(){
       return $this->profile->project_id;
    }

    public function project(){
        if ($this->project_id()) {
            return Project::find($this->project_id()); 
        }
    }
}
