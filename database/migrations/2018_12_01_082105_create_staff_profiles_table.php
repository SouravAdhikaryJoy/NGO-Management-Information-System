<?php

use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;

class CreateStaffProfilesTable extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        Schema::create('staff_profiles', function (Blueprint $table) {
            $table->increments('id');

            $table->string('name');
            $table->string('designation')->nullable();
            $table->string('staff_id')->nullable();

            $table->string('nid')->nullable();
            $table->string('phone_no')->nullable();
            $table->string('email')->nullable();

            $table->string('project_name')->nullable();
            $table->string('working_place')->nullable();

            $table->string('joining_date')->nullable();
            $table->string('closing_date')->nullable();

            $table->text('special_comment')->nullable();
            $table->text('experience')->nullable();

            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        Schema::dropIfExists('staff_profiles');
    }
}
