<?php

use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;

class CreateStaffLeaveStatusesTable extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        Schema::create('staff__leave__statuses', function (Blueprint $table) {
            $table->increments('id');
            $table->integer('staff_profile_id');

            $table->integer('earned_enjoy')->default(0);
            $table->integer('earned_due')->default(0);

            $table->integer('casual_enjoy')->default(0);
            $table->integer('casual_due')->default(0);

            $table->integer('medical_enjoy')->default(0);
            $table->integer('medical_due')->default(0);

            $table->integer('maternity_enjoy')->default(0);
            $table->integer('maternity_due')->default(0);

            $table->integer('paternity_enjoy')->default(0);
            $table->integer('paternity_due')->default(0);

            $table->integer('study_enjoy')->default(0);
            $table->integer('study_due')->default(0);

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
        Schema::dropIfExists('staff__leave__statuses');
    }
}
