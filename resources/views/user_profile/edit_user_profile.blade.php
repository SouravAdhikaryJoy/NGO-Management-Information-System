@extends('layouts.dashboard')
@section('content')
<div class="row justify-content-center">
    <div class="col-md-8">
        <div class="card">
            <div class="card-header">
                Edit User {{$userProfile->name}}
            </div>
            <div class="card-body">
                {!! Form::open(['action'=>['UserProfileController@update',$userProfile->id],'method'=>'POST']) !!}
                @method('PUT')
                {{ Form::bsText('name',$userProfile->name,['placeholder'=>'Enter Name','required' ]) }}
                {{ Form::bsText('designation',$userProfile->designation,['placeholder'=>'Enter Name' ,'required']) }}
                <div class="form-group">
                    <label for="Access">Access</label>
                    <select id="Access" class="form-control" name="access">
                        <option value="noAccess" 
                        {{$userProfile->access==="noAccess"?'selected':''}} 
                        >
                        No Access</option>
                        <option value="superAdmin" {{$userProfile->access==="superAdmin"?'selected':''}} >Super Admin</option>
                        <option value="projectAdmin" {{$userProfile->access==="projectAdmin"?'selected':''}} >Project Admin</option>
                        <option value="projectAgent" {{$userProfile->access==="projectAgent"?'selected':''}} >Field Agent</option>
                        <option value="Moderator" {{$userProfile->access==="Moderator"?'selected':''}} >Moderator</option>
                        <option value="chiefAccountant" {{$userProfile->access==="chiefAccountant"?'selected':''}} >Chief Accountant</option>
                        <option value="Accountant" {{$userProfile->access==="Accountant"?'selected':''}} >Accountant</option>
                    </select>
                </div>
                <div class="form-group" id="Project">
                    <label for="Project">Project</label>
                    <select id="Project" class="form-control" name="project">
                        <option value="0" {{$userProfile->project_id==0?'selected':''}}>No Project</option>
                        @foreach($projects as $project)
                        <option value="{{$project->id}}" 
                          {{$userProfile->project_id==$project->id?'selected':''}}>{{$project->project_name}}</option>
                        @endforeach    
                    </select>
                </div>

               
            </div>
            <div class="card-footer">
                
             
                {{ Form::bsSubmit('Save') }}
                {!! Form::close() !!}
            </div>
        </div>
    </div>
</div>
@endsection