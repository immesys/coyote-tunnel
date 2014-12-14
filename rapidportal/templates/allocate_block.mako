<%inherit file="base.mako" />
<%block name="bodyblock">

<div id="page-wrapper">
    <div class="row">
        <div class="col-lg-12">
            <h1 class="page-header"> Register a new tunnel</h1>
        </div>
        <!-- /.col-lg-12 -->
    </div>
    <!-- /.row -->
    <div class="row" id="confirmationrow">
        <div class="col-lg-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <i class="fa fa-question fa-fw"></i> Confirmation
                </div>
                <div class="panel-body">
                    <div class="row">
                        <div class="col-lg-12">
                        
                            <p>Are you sure you want to allocate a new IPv6 and IPv4 tunnel?</p>
                            <p>This is not the same as updating an existing tunnel.</p>
                            <a href="#" class="btn btn-success btn-lg" id="okbtn">Yeah of course, why else would I be here?</a>
                            <a href="/" class="btn btn-danger btn-lg">Now that you ask, not really...</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div class="row" id="resultsrow" style="display:none">
        <div class="col-lg-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <i class="fa fa-question fa-fw"></i> Results
                </div>
                <div class="panel-body">
                    <div class="row">
                        <div class="col-lg-12" id="resbodyloading">
                            <div style="text-align:center">
                            <img src='/static/gray_load.gif'>
                            </div>
                        </div>
                        
                        <div class="col-lg-12" id="resbodyresults" style="display:none">
                            <div class="table-responsive">
                                <table class="table table-bordered table-hover table-striped">
                                    <thead>
                                        <tr>
                                            <th>Field</th>
                                            <th>Value</th>
                                            <th>Description</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr>
                                            <td>Broker public IPv4</td>
                                            <td>50.18.70.36</td>
                                            <td>The IPv4 of the broker server</td>
                                        </tr>
                                        <tr>
                                            <td>Owner</td>
                                            <td id="tdowner"></td>
                                            <td>The person who is held responsible for these subnets</td>
                                        </tr>
                                        <tr>
                                            <td>Key</td>
                                            <td id="tdkey"></td>
                                            <td>The secret key required to update these tunnels</td>
                                        </tr>
                                        <tr>
                                            <td>IPv6 block</td>
                                            <td id="td6block"></td>
                                            <td>The IPv6 block that will be forwarded over this tunnel</td>
                                        </tr>
                                        <tr>
                                            <td>Client IPv6</td>
                                            <td id="td6client"></td>
                                            <td>The IPv6 address you should assign to your tunnel endpoint</td>
                                        </tr>
                                        <tr>
                                            <td>Broker IPv6</td>
                                            <td id="td6broker"></td>
                                            <td>The IPv6 address of the broker side tunnel endpoint</td>
                                        </tr>
                                        <tr>
                                            <td>IPv4 block</td>
                                            <td id="td4block"></td>
                                            <td>The IPv4 block that will be forwarded over this tunnel</td>
                                        </tr>
                                         <tr>
                                            <td>Broker IPv4</td>
                                            <td id="td4broker"></td>
                                            <td>The IPv4 address of the broker side tunnel endpoint</td>
                                        </tr>
                                        <tr>
                                            <td>Client IPv4</td>
                                            <td id="td4client"></td>
                                            <td>The IPv4 address you should assign to your tunnel endpoint</td>
                                        </tr>
                                        <tr>
                                            <td>Update URL</td>
                                            <td id="tdupdate"></td>
                                            <td>The URL you should curl periodically to keep the tunnel alive</td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                            <h3>Automatic configuration script</h3>
                            <p>To automatically set up your side of the tunnel on Linux, you can do the following:</p>
                            <pre id="config">
                            </pre>
                            <p>If you're on a mac then you're on your own</p>
                        </div>
                        
                        
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    
</div>
</%block>

<%block name="scripts">
<script>
    console.log("Binding click");
    $("#okbtn").click(function()
    {
        console.log("cliky");
        $("#resultsrow").show();
        $.getJSON("/api/allocate",{},function(data, status, xhr)
        {
            if (status != "success" || data["status"] != "ok")
            {
                console.log(data);
                $("#resbodyloading").html("<h2>Some badness happened</h2>");
            }
            else
            {
                var res = data;
                
                $("#resbodyloading").hide();
                $("#tdowner").html(res["owner"]);
                $("#tdkey").html(res["key"]);
                $("#td6block").html(res["inet6_block"]);
                $("#td6client").html(res["client_ip6"]);
                $("#td6broker").html(res["broker_ip6"]);
                $("#td4block").html(res["inet4_block"]);
                $("#td4client").html(res["client_ip4"]);
                $("#td4broker").html(res["broker_ip4"]);
                $("#tdupdate").html("<a href='"+res["update_url"]+"'>"+res["update_url"]+"</a>");
                $("#config").html("curl -v "+res["update_url"]+"\n curl -v "+res["config_url_linux"]+" | sudo bash");
                $("#resbodyresults").show();
                console.log("All good:");
                console.log(data);
            }
        });
    });
</script>
</%block>
