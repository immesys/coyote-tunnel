<%inherit file="base.mako" />

<%block name="bodyblock">
        <div id="page-wrapper">
            <div class="row">
                <div class="col-lg-12">
                    <h1 class="page-header">SDB Tunnel Broker</h1>
                </div>
                <!-- /.col-lg-12 -->
            </div>
            <!-- /.row -->
            <div class="row">
                <div class="col-lg-12">
                    <div class="panel panel-default">
                        <div class="panel-heading">
                            Allocate a new block
                        </div>
                        <div class="panel-body">
                            <div class="row">
                                <div class="col-lg-6">
                                    <form role="form">
                                        <div class="form-group">
                                            <label>sMAP commit or branch</label>
                                            <input class="form-control" id="commit" placeholder="unitoftime">
                                        </div>
                                        <div class="form-group" id="inigroup">
                                            <label>Path to INI file (relative to python/)</label>
                                            <input class="form-control" id="ini" placeholder="conf/caiso.ini">
                                        </div>
                                        <label>Service URL</label>
                                        <div class="form-group input-group" id="urlgroup">
                                            
                                            <input type="text" class="form-control" id="url" placeholder="e.g prolifix-newapi">
                                            <span class="input-group-addon">.rapid.cal-sdb.org</span>
                                        </div>
                                    </form>
                                </div>
                                <!-- /.col-lg-6 (nested) -->
                                <div class="col-lg-6">
                                    <form role="form">
                                        <div class="form-group" id="namegroup">
                                            <label>Author</label>
                                            <span class="form-control uneditable-input">${name}</span>
                                        </div>
                                        <div class="form-group" id="descgroup">
                                            <label>Description</label>
                                            <input class="form-control" id="description" placeholder="e.g 'Testing Prolifix kludge'">
                                        </div>
                                        <div class="form-group">
                                            <label>Service port (will be mapped to port 80)</label>
                                            <input class="form-control" id="port" placeholder="8080">
                                        </div>
                                    </form>
                                </div>
                            </div>
                        </div>
                    </div>   
                <div class="row">
                <div class="col-lg-12">
                    <div class="panel panel-default">
                        <div class="panel-heading">
                            Optional fields
                        </div>
                        <div class="panel-body">
                            <p>A bunch of stuff will go here, like overriding files and stuff</p>
                            <p>Add your suggestions as issues on github.</p>
                        </div>
                    </div>   
                
                    
                <button type="submit" class="btn btn-default" id="submitbtn">Go forth and do my bidding!</button>
</div>
                    </div>
                    <!-- /.panel -->
                </div>
                <!-- /.col-lg-12 -->
            </div>
            <!-- /.row -->
        </div>
        <!-- /#page-wrapper -->
</%block >

<%block name="scripts">
<script>
    $("#submitbtn").click(function()
    {
        data = {"smap_commit":$("#commit").val(),
                "ini":$("#ini").val(),
                "url":$("#url").val(),
                "description":$("#description").val(),
                "port":$("#port").val()};
        var abort = false;
        if (data.smap_commit == "") data.smap_commit = "unitoftime";
        if (data.port == "") data.port = "8080";
        if (data.ini == "")
        {
            $("#inigroup").addClass("has-error");
            abort = true;
        }
        if (data.url == "")
        {
            $("#urlgroup").addClass("has-error");
            abort = true;
        }
        if (data.description == "")
        {
            $("#descgroup").addClass("has-error");
            abort = true;
        }
        if (abort) return;
        $("#inigroup").removeClass("has-error");
        $("#urlgroup").removeClass("has-error");
        $("#descgroup").removeClass("has-error");
        
        $.post("/deploy/driver.target",JSON.stringify(data), function(dat, stat, xhr)
        {
            if(dat.status == "submitted")
            {
                $("#submitbtn").html("Build job submitted");
                $("#submitbtn").prop('disabled', true);
            }
            else
            {
                $("#submitbtn").prop('disabled', true);
                $("#submitbtn").addClass("btn-danger");
                $("#submitbtn").html(dat["status"]);
            }
        });
        $("#submitbtn").html("Submitting build job...");
        $("#submitbtn").prop('disabled', true);
    });
</script>
</%block>
