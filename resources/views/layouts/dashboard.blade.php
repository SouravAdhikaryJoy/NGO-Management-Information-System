<?php 
  $User = Auth::user();

 ?>
<!DOCTYPE html>
<html lang="en">

  <head>

    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <meta name="description" content="">
    <meta name="author" content="">

    <title> Dashboard</title>

    <!-- Bootstrap core CSS-->
    <link rel="stylesheet" href="/css/app.css">

     <!-- Custom fonts for this template-->
    <link href="/vendor/fontawesome-free/css/all.min.css" rel="stylesheet" type="text/css">

    <!-- Custom styles for this template-->
    <link href="/css/sb-admin.css" rel="stylesheet">

        <!-- Page level datatable CSS-->
    <link href="/DataTables/datatables.min.css" rel="stylesheet">

  @yield('link')
  </head>

  <body id="page-top">

    @include('inc.nav')


    <div id="wrapper">

      @include('inc.sidebar')
      <div id="content-wrapper">

        <div class="container-fluid">

          
          
          @include('inc.message')
         @yield('content')

        </div>
        <!-- /.container-fluid -->

        <!-- Sticky Footer -->
        <footer class="sticky-footer">
          <div class="container my-auto">
            <div class="copyright text-center my-auto">
              <span>Copyright ©Agrogoti Sangstha</span>
            </div>
          </div>
        </footer>

      </div>
      <!-- /.content-wrapper -->

    </div>
    <!-- /#wrapper -->

    <!-- Scroll to Top Button-->
    <a class="scroll-to-top rounded" href="#page-top">
      <i class="fas fa-angle-up"></i>
    </a>

    <!-- Logout Modal-->
    <div class="modal fade" id="logoutModal" tabindex="-1" role="dialog" aria-labelledby="exampleModalLabel" aria-hidden="true">
      <div class="modal-dialog" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="exampleModalLabel">Ready to Leave?</h5>
            <button class="close" type="button" data-dismiss="modal" aria-label="Close">
              <span aria-hidden="true">×</span>
            </button>
          </div>
          <div class="modal-body">Select "Logout" below if you are ready to end your current session.</div>
          <div class="modal-footer">
            <button class="btn btn-secondary" type="button" data-dismiss="modal">Cancel</button>
            {!! Form::open(['action'=>'Auth\LoginController@logout','method'=>'POST']) !!}
            {!! Form::submit('Logout', ['class'=>'btn btn-primary']) !!}
            {!! Form::close() !!}
          </div>
        </div>
      </div>
    </div>

    <!-- Bootstrap core JavaScript-->
    <script type="text/javascript" src="/js/jquery.min.js"></script>
     
     <script type="text/javascript" src="/bootstrap/js/bootstrap.bundle.min.js"></script>
    <!-- Core plugin JavaScript-->
    <script src="/js/jquery.easing.min.js"></script>

    <!-- datatable plugin all pages-->
    <script src="/DataTables/datatables.js"></script>

    <!-- Custom scripts for all pages-->
    <script src="/js/sb-admin.min.js"></script>

    @yield('js')


  </body>

</html>
