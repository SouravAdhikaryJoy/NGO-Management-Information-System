<?php

use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;

class CreateAchievementsTable extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        Schema::create('achievements', function (Blueprint $table) {
            $table->increments('id');

            $table->integer('activity_id');//activity has many achievement
            $table->string('achievement_year');
            $table->integer('achievement_quarter');
            $table->integer('achievement_event_number')->default(1);
            $table->integer('achievement_male_participant_number')->default(0);
            $table->integer('achievement_female_participant_number')->default(0);
            $table->string('achievement_month')->nullable();
            $table->string('achievement_date')->nullable();
            $table->string('achievement_place')->nullable();

            $table->text('event_summary')->nullable();
            $table->text('immediate_outcome')->nullable();
            $table->text('learning')->nullable();
            $table->text('challenge')->nullable();

            $table->boolean('approved')->default(false);
            $table->string('submitted_by_name')->nullable();
            $table->integer('submitted_by_id')->nullable();
            $table->string('approved_by_name')->nullable();
            $table->integer('approved_by_id')->nullable();
            

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
        Schema::dropIfExists('achievements');
    }
}
