<?php

namespace App\Providers;
use Form;

use Illuminate\Support\ServiceProvider;

class FormServiceProvider extends ServiceProvider
{
    /**
     * Bootstrap services.
     *
     * @return void
     */
    public function boot()
    {
      Form::component('bsText', 'components.form.text', ['name', 'value' => null, 'attributes' => []]);
      Form::component('bsDate', 'components.form.date', ['name', 'value' => null, 'attributes' => []]);
      Form::component('bsTextArea', 'components.form.textArea', ['name', 'value' => null, 'attributes' => []]);
      Form::component('bsNumber', 'components.form.number', ['name', 'value' => null, 'attributes' => []]);
      Form::component('bsEmail', 'components.form.email', ['name', 'value' => null, 'attributes' => []]);
      Form::component('bsPassword', 'components.form.password', ['name', 'value' => null, 'attributes' => []]);

      Form::component('bsSubmit', 'components.form.submit', ['value' => null, 'attributes' => []]);
      Form::component('hidden', 'components.form.hidden', ['value' => null, 'attributes' => []]);

    }

    /**
     * Register services.
     *
     * @return void
     */
    public function register()
    {
        //
    }
}
