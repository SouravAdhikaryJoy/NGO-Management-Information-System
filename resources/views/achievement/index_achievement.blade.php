@extends('layouts.dashboard')
@section('link')

  <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.19/css/jquery.dataTables.min.css"/>
@endsection
@section('content')
@include('inc.nav_activity')
<br><br>
<div class="row">
  <div class="col-md-12">

    <div class="card justify-content-center">
      <div class="card-header text-center text-uppercase card-success">
        <strong>Summary:</strong> {{$activity->activity_name}}      
      </div>
      <div class="card-block">
        <table class="table table-hover table-bordered text-center style="width:100%"">
          <thead class="table-info">
            <th>Year</th>
            <th>Quarter</th>
            <th>Targeted Event Number</th>
            <th>Achieved Event Number</th>
            <th>Targeted Participant Number</th>
            <th>Achieved Participant Number</th>
          </thead>
          <tbody>
            @foreach($summary as $each)
            <tr>
            <td>{{$each->target_year}}</td>
            <td>{{$each->target_quarter}}</td>
            <td>{{$each->target_event_number}}</td>
            <td>{{$each->achievement_event_number}}</td>
            <td>{{$each->target_participant_number}}</td>
            <td>{{$each->achievement_male_participant_number + $each->achievement_female_participant_number}}</td>
            
           
            </tr>
            @endforeach

          </tbody>

        </table>
      </div>
      
    </div>


<br><br><br>

    <div class="card text-center">
      <div class="card-header">
        <h4>{{$activity->activity_name}}</h4>
  </div>
      <div class="card-block">
        <div class="table-responsive-md">

        <table id="DataTable" class="table table-striped " style="width:100%">
                <thead>
                    <tr>

                        <th>Year</th>
                        <th>Quater</th>
                        <th>Date</th>


                        <th>Event Number</th>
                        
                        <th>Male Participant</th>
                        <th>Female Participant</th>
                        <th>Total Participant</th>
                        <th>Status</th>
                        <th></th>
                        <th></th>
                        <th></th>

                    </tr>
                </thead>
                <tbody>
                @foreach($achievements as $achievement)
                    <tr>
                        <td>{{$achievement->achievement_year}} </td>
                        <td>Quarter- {{$achievement->achievement_quarter}}</td>
                        <td>{{$achievement->achievement_date}}</td>
                        <td>{{$achievement->achievement_event_number}}</td>
                        <td>{{$achievement->achievement_male_participant_number}}</td>
                        <td>{{$achievement->achievement_female_participant_number}}</td>
                        <td>{{$achievement->achievement_male_participant_number + $achievement->achievement_female_participant_number }}</td>

                        <td class="{{$achievement->approved>0?'text-success':'text-danger'}}">{{$achievement->approved>0?"APPROVED":"NOT APPROVED"}}</td>
                        
                        <td><a href="{{action('AchievementController@show',[$activity->id,$achievement->id])}}" class="btn btn-outline-info float-right">
                            Show
                          </a>
                        </td>
                        <td>
                          @can('update',$achievement)
                          <a href="{{action('AchievementController@edit',[$activity->id,$achievement->id])}}" class="btn btn-outline-info float-right">
                            Edit
                          </a>
                          @endcan
                          </td>
                        <td>
                          @can('update',$achievement)
                          {!! Form::open(['action' => ['AchievementController@destroy',$activity->id,$achievement->id], 'method'=>'POST','class'=>'delete-achievement']) !!}
                              {{ Form::hidden('_method','DELETE')}}
                              {{ Form::bsSubmit('DELETE',['class'=>'btn btn-outline-danger float-right delete']) }}
                          {!! Form::close() !!}
                          @endcan
                        </td>
                    </tr>
                  @endforeach
                </tbody>
            </table>
          </div>
      </div>
    </div>

</div>

</div>


@endsection
@section('js')
  
  <script>
  $(document).ready(function() {
    $('#DataTable').DataTable( {
  responsive: true
} );

  } );//DataTable

  </script>
  <script type="text/javascript" src="/js/achievement.js"></script>
@endsection
