<%inherit file="base.mako" />

<%block name="bodyblock">
        <div id="page-wrapper">
            <div class="row">
                <div class="col-lg-12">
                    <h1 class="page-header">Spin up a new sMAP driver</h1>
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
                                            <input class="form-control" id="commit" placeholder="unitoftime">
                                        </div>
                                        <div class="form-group">
                                            <label>Path to INI file (relative to python/)</label>
                                            <input class="form-control" id="ini" placeholder="conf/caiso.ini">
                                        </div>
                                        <label>Service URL</label>
                                        <div class="form-group input-group">
                                            
                                            <input type="text" class="form-control" id="url" placeholder="e.g prolifix-newapi">
                                            <span class="input-group-addon">.rapid.cal-sdb.org</span>
                                        </div>
                                    </form>
                                </div>
                                <!-- /.col-lg-6 (nested) -->
                                <div class="col-lg-6">
                                    <form role="form">
                                        <div class="form-group">
                                            <label>Author</label>
                                            <input class="form-control" id="author" placeholder="Oski Bear">
                                        </div>
                                        <div class="form-group">
                                            <label>Description</label>
                                            <input class="form-control" id="description" placeholder="e.g 'Testing Prolifix kludge'">
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
                "author":$("#author").val(),
                "description":$("#description").val()};
        $.post("/deploy/driver.target",JSON.stringify(data), function(dat, stat, xhr)
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
