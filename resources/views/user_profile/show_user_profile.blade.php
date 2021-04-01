@extends('layouts.dashboard')
@section('link')

@endsection
@section('content')
<br><br>
<div class="row  justify-content-center">
<div class="col-md-10">
  <div class="card text-center">
              <div class="card-header">

                <h4>USER PROFILE </h4>
                <a href="/user/" role="button" class="btn btn-outline-info float-right">GO BACK</a>

              </div>
              <div class="card-block">
                  <div class="table-responsive-md">
                <table class="table table-striped table-bordered" style="width:100%">

                    <tbody>
                      <tr>
                        <th>Name</th>
                        <td>{{$userProfile->name}}</td>
                      </tr>
                      <tr>
                        <th>Designation</th>
                        <td>{{$userProfile->designation}}</td>
                      </tr>

                      <tr>
                        <th>Email</th>
                        <td>{{$userProfile->user->email}}</td>
                      </tr>
                      @if($userProfile->project_id != 0)
                       <tr>
                        <th>Project</th>
                        <td><a href="/project/{{$project->id}}/">{{$project->project_name}}</a></td>
                      </tr>
                      @endif
                      <tr>
                        <th>Access Level</th>
                        <td>{{$userProfile->access}}</td>
                      </tr>
                    </tbody>
                  <tfoot>

                  </tfoot>
                </table>
                 </div>
              </div>
              <div class="card-footer text-muted">

                <button type="button" id="edit" name="button" class="btn btn-outline-info float-right">
                  <a href="{{action('UserProfileController@edit',[$userProfile->id])}}">
                    EDIT
                  </a>
                </button>
                {!! Form::open(['action' => ['UserProfileController@destroy',$userProfile->id], 'method'=>'POST','class'=>'delete-staff-profile']) !!}
                    {{ Form::hidden('_method','DELETE')}}
                    {{ Form::bsSubmit('DELETE',['class'=>'btn btn-outline-danger float-left delete']) }}
                {!! Form::close() !!}


              </div>
          </div>
        </div>
        </div>
          <br><br>
    <!--END OF PROFILE AND START OF Update Staff Leave Status -->

@endsection
@section('js')

<script type="text/javascript" src="/js/show_staff_profile.js"></script>

@endsection
