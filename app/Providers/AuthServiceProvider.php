<?php

namespace App\Providers;

use Illuminate\Support\Facades\Gate;
use Illuminate\Foundation\Support\Providers\AuthServiceProvider as ServiceProvider;

class AuthServiceProvider extends ServiceProvider
{
    /**
     * The policy mappings for the application.
     *
     * @var array
     */
    protected $policies = [
        'App\Model' => 'App\Policies\ModelPolicy',
        'App\Project'=> 'App\Policies\ProjectPolicy',
        'App\Activity'=> 'App\Policies\ActivityPolicy',                
        'App\Target'=> 'App\Policies\TargetPolicy',
        'App\Achievement'=> 'App\Policies\AchievementPolicy',
        'App\StaffProfile'=> 'App\Policies\StaffProfilePolicy',



    ];

    /**
     * Register any authentication / authorization services.
     *
     * @return void
     */
    public function boot()
    {
        $this->registerPolicies();

        Gate::before(function ($user, $ability) {
             if ($user->isSuperAdmin()) {
                 return true;
                }
         });
    }
}
