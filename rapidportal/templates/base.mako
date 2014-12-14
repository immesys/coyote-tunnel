<!DOCTYPE html>
<html>

<head>

    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>Storm Pervasive Mesh</title>

    <!-- Core CSS - Include with every page -->
    <link href="/static/css/bootstrap.min.css" rel="stylesheet">
    <link href="/static/font-awesome/css/font-awesome.css" rel="stylesheet">

    <!-- Page-Level Plugin CSS - Dashboard -->
    <link href="/static/css/plugins/morris/morris-0.4.3.min.css" rel="stylesheet">
    <link href="/static/css/plugins/timeline/timeline.css" rel="stylesheet">

    <!-- SB Admin CSS - Include with every page -->
    <link href="/static/css/sb-admin.css" rel="stylesheet">
    <%block name="header" />
</head>

<body>
    <nav class="navbar navbar-default navbar-static-top" role="navigation" style="margin-bottom: 0">
            <div class="navbar-header">
                <a class="navbar-brand" href="index.html">Storm Pervasive Mesh</a>
            </div>
            <!-- /.navbar-header -->
    </nav>
    <div id="wrapper">
        <nav class="navbar-default navbar-static-side" role="navigation">
            <div class="sidebar-collapse">
                <ul class="nav" id="side-menu">
                    <li class="well">
                        <div style="display">
                        <img style="display" class="img-thumbnail" src="${pic}" height="80px">
                        </div>
                        <div style="display">
                        <h2 style=""><small> <i class="fa fa-github fa-fw"></i> ${name}</small></h2>
                        </div>
                    </li>
                    <li>
                        <a href="/deauth"><i class="fa fa-sign-out fa-fw"></i> Log out</a>
                    </li>
                    <li>
                        <a href="/"><i class="fa fa-dashboard fa-fw"></i> Dashboard</a>
                    </li>
		    <li>
			<a href="/broker/allocate"><i class="fa fa-sitemap fa-fw"></i> Register new tunnel</a>
		    </li>
		    <li>
			<a href="/broker/update"><i class="fa fa-gears"></i> Configure existing tunnel</a>
		    </li>
		    <li>
			<a href="/broker/register"><i class="fa fa-laptop"></i> Register new DNS record</a>
		    </li>
                </ul>
                <!-- /#side-menu -->
            </div>
            <!-- /.sidebar-collapse -->
        </nav>
        <!-- /.navbar-static-side -->
    <%block name="bodyblock" />
    
    </div>
   
    <!-- Core Scripts - Include with every page -->
    <script src="/static/js/jquery-1.10.2.js"></script>
    <script src="/static/js/bootstrap.min.js"></script>
    <script src="/static/js/plugins/metisMenu/jquery.metisMenu.js"></script>

    <!-- Page-Level Plugin Scripts - Dashboard -->
    <script src="/static/js/plugins/morris/raphael-2.1.0.min.js"></script>

    <!-- SB Admin Scripts - Include with every page -->
    <script src="/static/js/sb-admin.js"></script>

    <%block name="scripts" />
</body>

</html>
