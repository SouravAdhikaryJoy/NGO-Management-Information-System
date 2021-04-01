<?php

namespace App\Policies;

use App\User;
use App\StaffProfile;
use Illuminate\Auth\Access\HandlesAuthorization;

class StaffProfilePolicy
{
    use HandlesAuthorization;

    /**
     * Determine whether the user can view the staff profile.
     *
     * @param  \App\User  $user
     * @param  \App\StaffProfile  $staffProfile
     * @return mixed
     */
    public function view(User $user, StaffProfile $staffProfile)
    {
        if ($user->isModerator()) {
            return true;
        }
    }

    /**
     * Determine whether the user can create staff profiles.
     *
     * @param  \App\User  $user
     * @return mixed
     */
    public function create(User $user)
    {
        if ($user->isModerator()) {
            return true;
        }
    }

    /**
     * Determine whether the user can update the staff profile.
     *
     * @param  \App\User  $user
     * @param  \App\StaffProfile  $staffProfile
     * @return mixed
     */
    public function update(User $user, StaffProfile $staffProfile)
    {
        //
    }

    /**
     * Determine whether the user can delete the staff profile.
     *
     * @param  \App\User  $user
     * @param  \App\StaffProfile  $staffProfile
     * @return mixed
     */
    public function delete(User $user, StaffProfile $staffProfile)
    {
        //
    }

    /**
     * Determine whether the user can restore the staff profile.
     *
     * @param  \App\User  $user
     * @param  \App\StaffProfile  $staffProfile
     * @return mixed
     */
    public function restore(User $user, StaffProfile $staffProfile)
    {
        //
    }

    /**
     * Determine whether the user can permanently delete the staff profile.
     *
     * @param  \App\User  $user
     * @param  \App\StaffProfile  $staffProfile
     * @return mixed
     */
    public function forceDelete(User $user, StaffProfile $staffProfile)
    {
        //
    }
}
