<?php

namespace App\Policies;

use App\User;
use App\Achievement;
use Illuminate\Auth\Access\HandlesAuthorization;

class AchievementPolicy
{
    use HandlesAuthorization;

    /**
     * Determine whether the user can view the achievement.
     *
     * @param  \App\User  $user
     * @param  \App\Achievement  $achievement
     * @return mixed
     */
    public function view(User $user, Achievement $achievement)
    {
        
    }

    

    /**
     * Determine whether the user can update the achievement.
     *
     * @param  \App\User  $user
     * @param  \App\Achievement  $achievement
     * @return mixed
     */
    public function update(User $user, Achievement $achievement)
    {
        if ($user->project_id()==$achievement->activity->project_id){
            if ($achievement->approved ==0  && $achievement->submitted_by_id == $user->id) {
                return true;
            }
        }
        
        
    }

    /**
     * Determine whether the user can delete the achievement.
     *
     * @param  \App\User  $user
     * @param  \App\Achievement  $achievement
     * @return mixed
     */
    public function delete(User $user, Achievement $achievement)
    {
        if ($user->project_id()==$achievement->activity->project_id){
            if ($achievement->approved ==0 && $achievement->submitted_by_id == $user->id) {
                return true;
            }
        }
        
    }

    public function approve(User $user, Achievement $achievement)
    {
        if ($user->isProjectAdmin()) {
                return true;
            }
    }

    /**
     * Determine whether the user can restore the achievement.
     *
     * @param  \App\User  $user
     * @param  \App\Achievement  $achievement
     * @return mixed
     */
    public function restore(User $user, Achievement $achievement)
    {
        //
    }

    /**
     * Determine whether the user can permanently delete the achievement.
     *
     * @param  \App\User  $user
     * @param  \App\Achievement  $achievement
     * @return mixed
     */
    public function forceDelete(User $user, Achievement $achievement)
    {
        //
    }
}
