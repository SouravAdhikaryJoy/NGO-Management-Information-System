<?php

namespace App\Policies;

use App\User;
use App\Project;
use Illuminate\Auth\Access\HandlesAuthorization;

class ProjectPolicy
{
    use HandlesAuthorization;

    /**
     * Determine whether the user can view the project.
     *
     * @param  \App\User  $user
     * @param  \App\Project  $project
     * @return mixed
     */
     


    public function view(User $user, Project $project)
    {
        if ($user->project_id() == $project->id) {
            return true;
        }
        elseif ($user->isModerator()) {
            return true;
        }
    }

    /**
     * Determine whether the user can create projects.
     *
     * @param  \App\User  $user
     * @return mixed
     */
    public function create(User $user )
    {
        if ($user->isModerator()) {
            return true;
        }
    }

    /**
     * Determine whether the user can update the project.
     *
     * @param  \App\User  $user
     * @param  \App\Project  $project
     * @return mixed
     */
    public function update(User $user, Project $project)
    {
         if ($user->isModerator()) {
            return true;
        }
    }

    /**
     * Determine whether the user can delete the project.
     *
     * @param  \App\User  $user
     * @param  \App\Project  $project
     * @return mixed
     */
    public function delete(User $user, Project $project)
    {
        if ($user->isSuperAdmin()) {
            return true;
        }
    }

    public function create_activity(User $user, Project $project)
    {
        if ($user->isSuperAdmin()) {
            return true;
        }
    }
    
}
