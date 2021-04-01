@extends('layouts.dashboard')
@section('link')
  <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.19/css/jquery.dataTables.min.css"/>
@endsection
@section('content')
@include('inc.nav_project')
<br><br>
<div class="row">
  <div class="col-md-12">
    <div class="card text-center">
      <div class="card-header">
        <h4>PROJECT: {{$project->project_name}}</h4>
        <button type="button" class="btn btn-primary float-left" data-toggle="modal" data-target="#modal">
          Add Activity
        </button>
      </div>
      <div class="card-block">
        <div class="table-responsive-md">


        <table id="DataTable" class="table table-striped table-hover" style="width:100%">
                <thead>
                    <tr>
                        <th>Activity Name</th>
                        <th></th>
                    </tr>
                </thead>
                <tbody>
                @foreach($activities as $activity)
                    <tr>
                        <td><a href="{{action('ActivityController@show',[$activity->project_id,$activity->id])}}">{{$activity->activity_name}}</a> </td>
                        <td>
                          <button type="button" class="btn btn-outline-info float-right" data-toggle="modal" data-target="#modal_edit_{{$activity->id}}">
                            Edit Activity
                          </button>
                          <!-- Modal -->
                          <div class="modal fade" id="modal_edit_{{$activity->id}}" tabindex="-1" role="dialog" aria-labelledby="exampleModalCenterTitle" aria-hidden="true">
                            <div class="modal-dialog modal-dialog-centered" role="document">
                              <div class="modal-content">
                                <div class="modal-header">
                                  <h5 class="modal-title" id="exampleModalLongTitle">Edit Activity</h5>
                                  <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                                    <span aria-hidden="true">&times;</span>
                                  </button>
                                </div>
                                <div class="modal-body">
                          {!! Form::open(['action' => ['ActivityController@update',$project->id,$activity->id], 'method'=>'POST']) !!}
                            {{ Form::hidden('_method','PUT')}}
                          {{ Form::bsText('activity_name',$activity->activity_name,['placeholder'=>'Enter Activity Name *' ]) }}

                                </div>
                                <div class="modal-footer">
                                  <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
                                  {{ Form::bsSubmit('Save') }}

                                  {!! Form::close() !!}
                                </div>
                              </div>
                            </div>
                          </div><!-- Modal End -->


                        </td>
                        <td>
                          {!! Form::open(['action' => ['ActivityController@destroy',$project->id,$activity->id], 'method'=>'POST','class'=>'delete-activity']) !!}
                              {{ Form::hidden('_method','DELETE')}}
                              {{ Form::bsSubmit('DELETE',['class'=>'btn btn-outline-danger float-left delete']) }}
                          {!! Form::close() !!}
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


<!-- Modal -->
<div class="modal fade" id="modal" tabindex="-1" role="dialog" aria-labelledby="exampleModalCenterTitle" aria-hidden="true">
  <div class="modal-dialog modal-dialog-centered" role="document">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title" id="exampleModalLongTitle">Add New Activity</h5>
        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
      </div>
      <div class="modal-body">
{!! Form::open(['action' => ['ActivityController@store',$project->id], 'method'=>'POST']) !!}
{{ Form::bsText('activity_name','',['placeholder'=>'Enter Activity Name *' ]) }}

      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
        {{ Form::bsSubmit('ADD') }}

        {!! Form::close() !!}
      </div>
    </div>
  </div>
</div><!-- Modal End -->




@endsection
@section('js')


 
  <script>
  $(document).ready(function() {
    $('#DataTable').DataTable( {
  responsive: true
} );

  } );//DataTable

  </script>
  <script type="text/javascript" src="/js/activity.js"></script>
@endsection
