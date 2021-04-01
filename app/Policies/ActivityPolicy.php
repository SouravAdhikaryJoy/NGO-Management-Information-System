<?php

namespace App\Policies;

use App\User;
use App\Activity;
use App\Project;
use Illuminate\Auth\Access\HandlesAuthorization;

class ActivityPolicy
{
    use HandlesAuthorization;

   /**
     * Determine whether the user can create achieveemnt.
     *
     * @param  \App\User  $user
     * @return mixed
     */
    public function view(User $user,Activity $activity)
    {
        if ($user->project_id()==$activity->project_id) {
            return true;
        }
    }
 


    /**
     * Determine whether the user can update the activity.
     *
     * @param  \App\User  $user
     * @param  \App\Activity  $activity
     * @return mixed
     */
    public function update(User $user, Activity $activity)
    {
        if ($user->isSuperAdmin()) {
            return true;
        }
    }

    /**
     * Determine whether the user can delete the activity.
     *
     * @param  \App\User  $user
     * @param  \App\Activity  $activity
     * @return mixed
     */
    public function delete(User $user, Activity $activity)
    {
       if ($user->isSuperAdmin()) {
            return true;
        }
    }

    public function targetCRUD(User $user , Activity $activity){
        if ($user->isSuperAdmin()) {
            return true;
        }
    }
}
