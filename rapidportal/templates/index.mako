

<%inherit file="base.mako" />

<%block name="bodyblock">


        <div id="page-wrapper">
            <div class="row">
                <div class="col-lg-12">
                    <h1 class="page-header"> Dashboard</h1>
                </div>
                <!-- /.col-lg-12 -->
            </div>
            <!-- /.row -->
            <div class="row">
                <div class="col-lg-12">
                    <div class="panel panel-default">
                        <div class="panel-heading">
                            <i class="fa fa-bar-chart-o fa-fw"></i> Currently running artfacts
                            <div class="pull-right">
                                <div class="btn-group">
                                    <a class="btn btn-default btn-xs" href="https://github.com/immesys/coyote-tunnel/issues/new">
                                        Report something broken
                                        </span>
                                    </a>
                                </div>
                            </div>
                        </div>
                        <!-- /.panel-heading -->
                        <div class="panel-body">
                            <div class="row">
                                <div class="col-lg-12">
                                    <div class="table-responsive">
                                        <table class="table table-bordered table-hover table-striped">
                                            <thead>
                                                <tr>
                                                    <th>Type</th>
                                                    <th>Author</th>
                                                    <th>Description</th>
                                                    <th>Status</th>
                                                    <th>SSH port</th>
                                                    <th>URL</th>
                                                    <th>Manage</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                % for r in services:
                                                    <tr>
                                                        <td>${r["type"] | h}</td>
                                                        <td>${r["author"] | h}</td>
                                                        <td>${r["description"] | h}</td>
                                                        <td>${r["state"] | h}</td>
                                                        <td><a href="ssh://${r["url"] | u}.rapid.cal-sdb.org:${r["ssh"]}/">${r["ssh"]}</a></td>
                                                        <td><a href="http://${r["url"] | u}.rapid.cal-sdb.org">${r["url"] | u}.rapid.cal-sdb.org</a></td>
                                                        <td><a href="/manage/${r["jobid"]}"><i class="fa fa-wrench"></i></a></td>
                                                    </tr>
                                                % endfor
                                            </tbody>
                                        </table>
                                    </div>
                                    <!-- /.table-responsive -->
                                </div>
                            </div>
                            <!-- /.row -->
                        </div>
                        <!-- /.panel-body -->
                    </div>
                </div>
            </div>
            <!-- /.row -->
        </div>
        <!-- /#page-wrapper -->

</%block>

<%block name="scripts">
    <!-- Page-Level Demo Scripts - Dashboard - Use for reference -->
    <script src="js/demo/dashboard-demo.js"></script>
</%block>

