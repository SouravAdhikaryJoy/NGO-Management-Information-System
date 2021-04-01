@extends('layouts.dashboard')
@section('content')
@include('inc.nav_activity')
<br><br>
<div class="row p-2 justify-content-center">

<div class="col-md-10">
 <div class="card">
    <div class="card-body text-center text-uppercase text-info bg-inverse">
      <strong>{{$activity->activity_name}}</strong> 
    </div>
  </div>
  <br><br>
    {!! Form::open(['action' => ['AchievementController@update',$activity->id,$achievement->id], 'method'=>'POST']) !!}
    @method('PUT')
    <div class="form-row">
      <div class="form-group col-md-auto">
        <label for="year">Year</label>
        <input type="number" min="0" name="year" class="form-control" id="year" placeholder="Enter  Year " value={{$achievement->achievement_year}} required>
      </div>
      <div class="form-group col-md-auto">
        <label for="month">Month</label>
        <select id="month" class="form-control" name="month">
          <option value="January" 
          {{$achievement->achievement_month=="January"?'selected':''}} >January</option>
          <option value="February" 
          {{$achievement->achievement_month=="February"?'selected':''}}>February</option>
          <option value="March" 
          {{$achievement->achievement_month=="March"?'selected':''}}>March</option>
          <option value="April" 
          {{$achievement->achievement_month=="April"?'selected':''}}>April</option>

         <option value="May"  
         {{$achievement->achievement_month=="May"?'selected':''}}>May</option>
         <option value="June"  
         {{$achievement->achievement_month=="June"?'selected':''}}>June</option>
         <option value="July" 
         {{$achievement->achievement_month=="July"?'selected':''}}>July</option>
         <option value="August" 
         {{$achievement->achievement_month=="August"?'selected':''}}>August</option>


         <option value="Setember" 
         {{$achievement->achievement_month=="Setember"?'selected':''}}>Setember</option>
         <option value="October" 
         {{$achievement->achievement_month=="October"?'selected':''}}>October</option>
         <option value="November" 
         {{$achievement->achievement_month=="November"?'selected':''}}>November</option>
         <option value="December" 
         {{$achievement->achievement_month=="December"?'selected':''}}>December</option>

        </select>



      </div>

      {{ Form::bsDate('date',$achievement->achievement_date) }}
      

    </div>
    
     <div class="form-row">
      <div class="form-group col-md-6">
        
      {{Form::bsText('place',$achievement->achievement_place,['placeholder'=>'Enter  Place Of Event']) }}
      </div>
      <div class="form-group col-md-6">
        <label for="event_number">Event number</label>
        <input type="number" min="1" name="event_number" class="form-control" id="event_number" placeholder="Enter Number Of Event" value="{{$achievement->achievement_event_number}}">

      </div>

    </div>
    
    
    <div class="form-row">

      <div class="form-group col-md-6">
        <label for="achievement_male_participant_number">Male Participant number</label>
        <input type="number" min="0" name="achievement_male_participant_number" class="form-control" id="event_number" placeholder="Male Participant Number" value="{{$achievement->achievement_male_participant_number}}" required>
      </div>
      <div class="form-group col-md-6">
        <label for="achievement_female_participant_number">Female Participant Number </label>
        <input type="number" min="0" name="achievement_female_participant_number" class="form-control" id="participant_number" placeholder="Female  Participant Number" value="{{$achievement->achievement_female_participant_number}}" required >
      </div>
    </div>




        {{ Form::bsTextArea('event_summary',$achievement->event_summary ,['placeholder'=>'Enter Event Summary']) }}
        {{ Form::bsTextArea('immediate_outcome',$achievement->immediate_outcome,['placeholder'=>'Enter Outcome Of the Event']) }}

        {{ Form::bsTextArea('learning',$achievement->learning,['placeholder'=>'Learning From The Event']) }}
        {{ Form::bsTextArea('challenge',$achievement->challenge,['placeholder'=>'Challenges You Have Faced']) }}



        {{ Form::bsSubmit('Submit') }}

    {!! Form::close() !!}


</div>


</div>


@endsection
