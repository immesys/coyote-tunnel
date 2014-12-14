<%inherit file="base.mako" />
<%block name="bodyblock">

<div id="page-wrapper">
    <div class="row">
        <div class="col-lg-12">
            <h1 class="page-header"> Update an existing tunnel</h1>
        </div>
        <!-- /.col-lg-12 -->
    </div>
    <!-- /.row -->
    <div class="row">
        <div class="col-lg-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <i class="fa fa-terminal fa-fw"></i> Console instructions
                </div>
                <div class="panel-body">
                    <div class="row">
                        <div class="col-lg-12">
                            <p>Updating the tunnel endpoint IP address is necessary whenever your public IP address has changed.</p>
                            <p>At the moment, we only have support for updating the endpoint via the REST API, which is a simple curl command (or you can type it in your web browser). If you know what your public IP address is, you can use the form:</p>
                            <pre>curl http://storm.pm/u/[your tunnel uuid]?ip=[your public ip address]</pre>
                            <p>If you are behind a NAT and you don't know what the public IP address is, you can use the public IP address of the computer doing the GET request with the 'auto' parameter:</p>
                            <pre>curl http://storm.pm/u/[your tunnel uuid]?ip=auto</pre>
                            <p>If you have lost your tunnel UUID, you can look it up in the table below</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div class="row">
        <div class="col-lg-12">
            <div class="panel panel-default">
                <div class="panel-heading">
                    <i class="fa fa-terminal fa-fw"></i> Your tunnels
                </div>
                <div class="panel-body">
                    <div class="row">
                        <div class="col-lg-12">
                            <table class="table table-bordered table-hover table-striped">
                                <thead>
                                    <tr>
                                        <th>IPv6 block</th>
                                        <th>IPv6 client endpoint</th>
                                        <th>IPv6 server endpoint</th>
                                        <th>IPv4 sit endpoint</th>
                                        <th>UUID</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    % for r in tunnels:
                                        <tr>
                                            <td>${r["ip6"]|h}/64</td>
                                            <td>${r["client_router6"]|h}/127</td>
                                            <td>${r["broker_router6"]|h}/127</td>
                                            <td>${r["remote_ipv4"]|h}</td>
                                            <td>${r["key"]|h}</td>
                                        </tr>
                                    % endfor
                                </tbody>
                            </table>
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
</script>
</%block>
