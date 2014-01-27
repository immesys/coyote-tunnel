<%inherit file="base.mako" />

<%block name="bodyblock">
        <div id="page-wrapper">
            <div class="row">
                <div class="col-lg-12">
                    <h1 class="page-header">Manage instance</h1>
                </div>
                <!-- /.col-lg-12 -->
            </div>
            <!-- /.row -->
            <div class="row">
                <div class="col-lg-12">
                    <div class="panel panel-default">
                        <div class="panel-heading">
                            Log files
                        </div>
                        <div class="panel-body">
                            <div class="row">
                                <div class="table-responsive">
                                        <table class="table table-bordered table-hover table-striped">
                                            <thead>
                                                <tr>
                                                    <th>Label</th>
                                                    <th>Creation date</th>
                                                    <th>Link</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                % for r in logfiles:
                                                    <tr>
                                                        <td>${r["label"] | h}</td>
                                                        <td>${r["date"] | h}</td>
                                                        <td><a href="/logfile/${r["uuid"]}">read</a></td>
                                                    </tr>
                                                % endfor
                                            </tbody>
                                        </table>
                                </div>
                            </div>
                        </div>
                    </div>   
           
            <div class="row">
                <div class="col-lg-12">
                    <div class="panel panel-default">
                        <div class="panel-heading">
                            Realtime stats
                        </div>
                        <div class="panel-body">
                            <p>Still acquiring these serverside...</p>
                        </div>
                    </div>
                </div>
            </div>   
        </div>
        <!-- /#page-wrapper -->
</%block >

<%block name="scripts">
</%block>
