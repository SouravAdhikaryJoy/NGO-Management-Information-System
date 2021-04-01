@extends('layouts.dashboard')
@section('link')

@endsection
@section('content')
@include('inc.nav_activity')

<br><br>
<div class="row  justify-content-center">
<div class="col-md-12">
<div class="card">
  <div class="card-header text-center">
    <small class=" align-text-top float-right {{$achievement->approved>0?'text-success':'text-danger'}}">{{$achievement->approved>0?"APPROVED":"NOT APPROVED"}}</small>
    <h2>{{$activity->activity_name}}</h2>
    <h6>Date:{{$achievement->achievement_date}}</h6>
      <h6>Place:{{$achievement->achievement_place}}</h6>

  </div>
  <div class="card-block p-2 m-2">
    <strong>Year:</strong> {{$achievement->achievement_year}} <br><br>
    <strong>Quarter:</strong> {{$achievement->achievement_quarter}}<br><br>

  <strong> Male Participant Number:</strong>  {{$achievement->achievement_male_participant_number}}<br>
<br>
  <strong>Female Participant Number:</strong>   {{$achievement->achievement_female_participant_number}}<br>
<br>
  <strong>Event Summary:</strong>
    <p>{{$achievement->event_summary}}</p><br>
  <strong>Immediate Outcome:</strong>
    <p>{{$achievement->immediate_outcome}}</p><br>
  <strong> Learning:</strong>
    <p>{{$achievement->learning}}</p><br>
<strong>Challenges:</strong>
    <p>{{$achievement->challenge}}</p><br>

  </div>

  <div class="card-footer">
    Submitted By :{{$achievement->submitted_by_name}}
 @can('approve',$achievement)
    {!! Form::open(['action' => ['AchievementController@updateApproval',$activity->id,$achievement->id], 'method'=>'POST']) !!}
    @method('PUT')
    <?php 
      $submit = $achievement->approved>0?"Disapprove":"Approve";
     ?>
    {!! Form::submit($submit, ['class'=> $achievement->approved>0?'btn btn-danger float-right':'btn btn-success float-right']) !!}

    {!! Form::close() !!}
    @endcan
  </div>

</div>


</div>
</div>

@endsection
