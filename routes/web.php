<?php

/*
|--------------------------------------------------------------------------
| Web Routes
|--------------------------------------------------------------------------
|
| Here is where you can register web routes for your application. These
| routes are loaded by the RouteServiceProvider within a group which
| contains the "web" middleware group. Now create something great!
|
*/
Route::resource('staff','StaffProfileController');
Route::resource('leave','StaffLeaveStatusController');

Route::resource('project','ProjectController');
Route::resource('project/{project}/activity','ActivityController');
Route::resource('activity/{activity}/achievement','AchievementController');
Route::put('activity/{activity}/achievement/{achievement}/approve','AchievementController@updateApproval');
Route::resource('activity/{activity}/target','TargetController');
Route::resource('user','UserProfileController')->middleware('can:update,App\User');
Route::resource('notification','NotificationController');




Auth::routes(['register' => false]);
Route::get('/', 'HomeController@index')->name('home');


//myaccountController
Route::get('/myaccount','MyaccountController@show');

Route::get('/myaccount/password','MyaccountController@editPassword');
Route::put('/myaccount/password','MyaccountController@updatePassword');

Route::get('/myaccount/email','MyaccountController@editEmail');
Route::put('/myaccount/email','MyaccountController@updateEmail');
//myaccountController end



