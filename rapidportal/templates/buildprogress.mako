<%inherit file="base.mako" />

<%block name="bodyblock">

</%block>

<%block name="scripts">
<script src="http://cdn.sockjs.org/sockjs-0.3.4.min.js"></script>
<script>
    //var sock = new SockJS('http://localhost:6543/__sockjs__');
    var sock = new SockJS('http://' + window.location.host + '/__sockjs__');
    sock.onopen = function() {
      console.log('open');
    };

    sock.onmessage = function(obj) {
      console.log(obj);
    };

    sock.onclose = function() {
      console.log('close');
    };
</script>
</%block>

