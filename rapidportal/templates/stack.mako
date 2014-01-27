<%inherit file="base.mako" />

<%block name="bodyblock">
        <div id="page-wrapper">
            <div class="row">
                <div class="col-lg-12">
                    <h1 class="page-header">Spin up a new sMAP stack</h1>
                </div>
                <!-- /.col-lg-12 -->
            </div>
            <!-- /.row -->
            <div class="row">
                <div class="col-lg-12">
                    <div class="panel panel-default">
                        <div class="panel-heading">
                            Required fields
                        </div>
                        <div class="panel-body">
                            <div class="row">
                                <div class="col-lg-6">
                                    <form role="form">
                                        <div class="form-group">
                                            <label>sMAP commit or branch</label>
                                            <input class="form-control" id="smap_commit" placeholder="unitoftime">
                                        </div>
                                        <div class="form-group">
                                            <label>ReadingDB commit or branch</label>
                                            <input class="form-control" id="rdb_commit" placeholder="adaptive">
                                        </div>
                                        <div class="form-group" id="inigroup">
                                            <label>Path to INI file (relative to python/)</label>
                                            <input class="form-control" id="ini" placeholder="e.g conf/archiver.ini">
                                        </div>
                                        <label>Service URL</label>
                                        <div class="form-group input-group" id="urlgroup">
                                            
                                            <input type="text" class="form-control" id="url" placeholder="e.g bse-actuation">
                                            <span class="input-group-addon">.rapid.cal-sdb.org</span>
                                        </div>
                                        <div class="form-group">
                                            <label>Service port (will be mapped to port 80)</label>
                                            <input class="form-control" id="port" placeholder="80">
                                        </div>
                                    </form>
                                </div>
                                <!-- /.col-lg-6 (nested) -->
                                <div class="col-lg-6">
                                    <form role="form">
                                        <div class="form-group" id="namegroup">
                                            <label>Author</label>
                                            <input class="form-control" id="author" placeholder="Oski Bear">
                                        </div>
                                        <div class="form-group">
                                            <label>PowerDB2 commit or branch</label>
                                            <input class="form-control" id="pdb_commit" placeholder="master">
                                        </div>
                                        <div class="form-group" id="descgroup">
                                            <label>Description</label>
                                            <input class="form-control" id="description" placeholder="e.g 'BSE actuation test'">
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
        data = {"smap_commit":$("#smap_commit").val(),
                "pdb_commit":$("#pdb_commit").val(),
                "rdb_commit":$("#rdb_commit").val(),
                "ini":$("#ini").val(),
                "url":$("#url").val(),
                "author":$("#author").val(),
                "description":$("#description").val(),
                "port":$("#port").val()};
        if (data.smap_commit == "") data.smap_commit = "unitoftime";
        if (data.rdb_commit == "") data.rdb_commit = "adaptive";
        if (data.pdb_commit == "") data.pdb_commit = "master";
        if (data.port == "") data.port = "80";
        var abort = false;
        if (data.author == "")
        {
            $("#namegroup").addClass("has-error");
            abort = true;
        }
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
        $("#namegroup").removeClass("has-error");
        $("#inigroup").removeClass("has-error");
        $("#urlgroup").removeClass("has-error");
        $("#descgroup").removeClass("has-error");
        
        $.post("/deploy/stack.target",JSON.stringify(data), function(dat, stat, xhr)
        {
            console.log(dat);
            $("#submitbtn").html("Build job submitted");
            $("#submitbtn").prop('disabled', true);
        });
        $("#submitbtn").html("Submitting build job...");
        $("#submitbtn").prop('disabled', true);
    });
</script>
</%block>
