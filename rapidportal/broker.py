from pyramid.view import view_config
import json
import pymongo
client = pymongo.MongoClient()
db = client.coyote
import time
import iptools
import uuid
import re
import subprocess
import os
import MySQLdb
import socket
import thread
import socket

mysqldb_pyramid = MySQLdb.connect(host="localhost", user="coyote", passwd="coyote", db="pdns")
mysqldb_udp4 = MySQLdb.connect(host="localhost", user="coyote", passwd="coyote", db="pdns")
mysqldb_udp6 = MySQLdb.connect(host="localhost", user="coyote", passwd="coyote", db="pdns")

from views import load_so

routing_prefix_offset = 8
#This this is the base from which up to 50k /64's will be allocated
routing_prefix = 0x20010470488500000000000000000000 + (routing_prefix_offset<<64)
#This is the base from which up to 50k /127's will be allocated
p2p_prefix     = 0x20010470488500010000000000000000 + (routing_prefix_offset<<48)

inet_prefix = 0x64400000 + (routing_prefix_offset << 6)
inet_p2p_prefix = 0x64AF0000 + (routing_prefix_offset << 4)

broker_ipv4="50.18.70.36"
broker_local_ipv4="10.200.136.214"

def _set_record6(name, ip, key, mdb):
    name = name.lower()
    r = db.dns.find_one({"name":name, "t":6})
    if r is not None:
        if r["key"] != key:
           return "You are not the owner of this name"
    fqdn = name+".m.storm.pm"
    l = iptools.ipv6.ip2long(ip)
    if l is None:
        return "Bad IPv6 address"
    cur = mdb.cursor()
    cur.execute("DELETE FROM records WHERE name=%s",[fqdn])
    cur.execute("INSERT INTO records(domain_id, name, type, content, ttl, auth) VALUES (1, %s, 'AAAA', %s, 120, 1)", [fqdn, ip])
    mdb.commit()
    db.dns.save({"name":name,"t":6,"key":key})
    return "success"

def _set_record4(name, ip, key, mdb):
    name = name.lower()
    r = db.dns.find_one({"name":name, "t":4})
    if r is not None:
        if r["key"] != key:
           return "You are not the owner of this name"
    fqdn = name+".m.storm.pm"
    l = iptools.ipv4.ip2long(ip)
    if l is None:
        return "Bad IPv4 address"
    cur = mdb.cursor()
    cur.execute("DELETE FROM records WHERE name=%s",[fqdn])
    cur.execute("INSERT INTO records(domain_id, name, type, content, ttl, auth) VALUES (1, %s, 'A', %s, 120, 1)", [fqdn, ip])
    mdb.commit()
    db.dns.save({"name":name,"t":4,"key":key})
    return "success"
            
def get_block(owner, ip, useragent, username):
    key = str(uuid.uuid4())
    new_block = {"owner":owner, "username":username, "creatingip":ip,"agent":useragent, "date":time.time(), "key":key}
    curs = db.blocks.find().sort("number", pymongo.DESCENDING)
    if curs.count() == 0:
        new_num = 1
    else:
        new_num = curs[0]["number"] + 1
        if new_num > 16000:
            return None, None
    new_block["number"] = new_num
    new_block["ip6"] = iptools.ipv6.long2ip(routing_prefix + (new_num<<64))
    new_block["ip4"] = iptools.ipv4.long2ip(inet_prefix + (new_num << 6))
    new_block["client_router6"] = iptools.ipv6.long2ip(p2p_prefix + (new_num << 48))
    new_block["broker_router6"] = iptools.ipv6.long2ip(p2p_prefix + (new_num << 48) + 1)
    new_block["client_router4"] = iptools.ipv4.long2ip(inet_p2p_prefix + (new_num << 2) + 2)
    new_block["broker_router4"] = iptools.ipv4.long2ip(inet_p2p_prefix + (new_num << 2) + 1)
    new_block["remote_ipv4"] = "0.0.0.0"
    new_block["active"] = False    
    
    #Crude race resolution    
    i = db.blocks.save(new_block)
    curs = db.blocks.find({"number":new_num})
    if curs.count() != 1:
        db.blocks.remove({"_id":i})
        return get_block(owner, ip, useragent, username)
    else:
        return (new_block, key)

def tun_down(key):
    block = db.blocks.find_one({"key":key})
    if block is None:
        return
    tunname6 = "broker6_"+hex(block["number"]+routing_prefix_offset)[2:]
    tunname4 = "broker4_"+str(block["number"]+routing_prefix_offset)
    #Check if tun6 exists
    print "doing tundown",key
    try:
        subprocess.check_call(["ip","link","show",tunname6])
        #We only get here if the tunnel exists
        subprocess.check_call(["ip","link","set",tunname6,"down"])
        subprocess.call(["ip","route","del",block["ip6"]+"/64"])
        subprocess.call(["ip","route","del",block["client_router6"]+"/127"])
        subprocess.check_call(["ip","tunnel","del",tunname6])
    except Exception as e:
        print "We got an exception on tel6 del:",e
        pass #We assume that all worked ok
    #Check if tun4 exists
    try:
        subprocess.check_call(["ip","link","show",tunname4])
        #We only get here if the tunnel exists
        subprocess.check_call(["ip","link","set",tunname4,"down"])
        subprocess.call(["ip","route","del",block["ip4"]+"/26"])
        subprocess.check_call(["ip","tunnel","del",tunname4])
    except Exception as e:
        print "We got an exception on tel4 del",e
        pass #We assume that all worked ok
        
def tun_up(key):
    block = db.blocks.find_one({"key":key})
    if block is None:
        return
    tunname6 = "broker6_"+hex(block["number"]+routing_prefix_offset)[2:]
    tunname4 = "broker4_"+str(block["number"]+routing_prefix_offset)
    #Do tunnel 6
    try:
        print "Trying tunup",["ip","tunnel","add",tunname6,"mode","sit","remote",block["remote_ipv4"],
            "local",broker_local_ipv4,"ttl","255"]
        subprocess.check_call(["ip","tunnel","add",tunname6,"mode","sit","remote",block["remote_ipv4"],
            "local",broker_local_ipv4,"ttl","255"])  
        print "Tyrying link up"
        subprocess.check_call(["ip","link","set",tunname6,"up"])
        subprocess.check_call(["ip","addr","add",block["broker_router6"]+"/127","dev",tunname6])
        subprocess.check_call(["ip","route","add",block["ip6"]+"/64","dev",tunname6])
     #   subprocess.check_call(["ip","route","add",block["client_router6"]+"/127","dev",tunname6])
        print "Tunnel should be up:",tunname6
    except Exception as e:
        print "whoops6"
        raise e
        
    #Do tunnel 4
    try:
        subprocess.check_call(["ip","tunnel","add",tunname4,"mode","gre","remote",block["remote_ipv4"],
            "local",broker_local_ipv4,"ttl","255"])  
        subprocess.check_call(["ip","link","set",tunname4,"up"])
        print "link up"
        subprocess.check_call(["ip","addr","add",block["broker_router4"]+"/26","dev",tunname4])
        print "addr added"
        subprocess.check_call(["ip","route","add",block["ip4"]+"/26","via",block["client_router4"],"dev",tunname4])
        print "Tunnel should be up:",tunname4
    except Exception as e:
        print "whoops4"
        raise e
        
@view_config(route_name='api_allocate', renderer='string')
def allocate(request):
    so = load_so(request)
    if not so["auth"]:
        raise exc.HTTPClientError()
        
    print repr(request.POST)
    owner = so["userfullname"]
    block, key = get_block(owner, request.remote_addr, request.remote_user, so["username"])
    if block is None:
        rv = {"status":"error", "message":"No more blocks to allocate (guess we got DoS'd)"}
        return json.dumps(rv, indent=2)
    rv = {"status":"ok","owner":owner, "key": key,
            "inet6_block":block["ip6"]+"/64",
            "inet4_block":block["ip4"]+"/26", 
            "client_ip6":block["client_router6"]+"/127", 
            "broker_ip6":block["broker_router6"]+"/127",
            "client_ip4":block["client_router4"]+"/30",
            "update_url":"http://storm.pm/u/"+key+"?ip=auto",
            "config_url_linux":"http://storm.pm/c/nix/"+key,
            "broker_ip4":block["broker_router4"]+"/30"}
    return json.dumps(rv, indent=2)

@view_config(route_name='api_update', renderer='string')
def update(request):
    key = request.matchdict['key']
    block = db.blocks.find_one({"key":key})
    if block is None:
        rv = {"status":"error", "message":"Key is invalid"}
        return json.dumps(rv, indent=2)
    try:
        ip = request.params.getone("ip")
        if ip == "auto":
            ip = request.remote_addr
            if ip == "127.0.0.1":
                print "Trying forwarded ip"
                ip = request.environ['HTTP_X_REAL_IP']
            print "The IP is:",ip
        l = iptools.ipv4.ip2long(ip)
        if l is None:
            rv = {"status":"error", "message":"IP is malformed"}
            return json.dumps(rv, indent=2)
        reboot = "remote_ipv4" not in block or block["remote_ipv4"] != ip
    except Exception as e:
        raise e
        rv = {"status":"error", "message":"Missing 'ip' field e.g '128.32.37.1"}
        return json.dumps(rv, indent=2)
    block["remote_ipv4"] = ip
    block["active"] = True
    db.blocks.save(block)
    tun_down(key)
    tun_up(key)
    rv = {"status":"success", "configurl":"http://storm.pm/c/nix/%s" % key}
    return json.dumps(rv, indent=2)

@view_config(route_name="linuxconfigscript", renderer='string')
def configscript(request):
    key = request.matchdict['key']
    block = db.blocks.find_one({"key":key})
    if block is None:
        rv = """echo "\xb1[32;1mInvalid config key\xb1[0m"\n"""
    else:
        rv = """# Storm Tunnel Broker auto config script
ip tunnel add storm-pm6 mode sit remote {remote} ttl 255
ip link set storm-pm6 up
ip addr add {client6}/127 dev storm-pm6
ip route add ::/0 dev storm-pm6

ip tunnel add storm-pm4 mode gre remote {remote} ttl 255
ip link set storm-pm4 up
ip addr add {client4}/26 dev storm-pm4
ip route add 100.64.0.0/10 dev storm-pm4
\n""".format(remote=broker_ipv4, client6=block["client_router6"], client4=block["client_router4"])
    return rv
    
@view_config(route_name='api_retire', renderer='string')
def retire(request):
    key = request.matchdict['key']
    block = db.blocks.find_one({"key":key})
    if block is None:
        rv = {"status":"error", "message":"Key is invalid"}
        return json.dumps(rv, indent=2)
    block["active"] = False
    db.blocks.save(block)
    tun_down(key)
    rv = {"status":"success"}
    return json.dumps(rv, indent=2)
              
@view_config(route_name='api_register6', renderer='string')
def register6(request):
    key = request.matchdict['key']
    block = db.blocks.find_one({"key":key})
    if block is None:
        rv = {"status":"error", "message":"Key is invalid"}
        return json.dumps(rv, indent=2)
    try:
        hostname = request.POST.getone("host")
        validre = "^([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])(\.([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9]))*$"
        if not re.match(validre, hostname):
            rv = {"status":"error", "message":"Hostname is invalid"}
            return json.dumps(rv, indent=2)
    except:
        rv = {"status":"error", "message":"Missing 'host' field e.g 'border.410'"}
        return json.dumps(rv, indent=2)
        
    try:
        ip = request.POST.getone("ip")
        num = iptools.ipv6.ip2long(ip)
        if num is None:
            rv = {"status":"error", "message":"IP is malformed"}
            return json.dumps(rv, indent=2)
        if (num >> 80) != routing_prefix >> 80:
            rv = {"status":"error", "message":"IP is not in block"}
            return json.dumps(rv, indent=2)
        if ((num >> 64) & 0xFFFF) - routing_prefix_offset != block["number"]:
            rv = {"status":"error", "message":"IP is not in block"}
            return json.dumps(rv, indent=2)
    except:
        rv = {"status":"error", "message":"Missing 'ip' field e.g '2001:470:8036:f00::ba5"}
        return json.dumps(rv, indent=2)
    print "Would register %s = %s" %(hostname, block)
    msg = _set_record6(hostname, ip, block["key"],mysqldb_pyramid)
    if msg == "success":
        rv = {"status":"success", "hostnames":hostname+".m.storm.pm", "ip":ip}
        return json.dumps(rv, indent=2)
    else:
        rv = {"status":"error", "message":msg}
        return json.dumps(rv, indent=2)

@view_config(route_name='api_register4', renderer='string')
def register4(request):
    key = request.matchdict['key']
    block = db.blocks.find_one({"key":key})
    if block is None:
        rv = {"status":"error", "message":"Key is invalid"}
        return json.dumps(rv, indent=2)
    try:
        hostname = request.POST.getone("host")
        validre = "^([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])(\.([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9]))*$"
        if not re.match(validre, hostname):
            rv = {"status":"error", "message":"Hostname is invalid"}
            return json.dumps(rv, indent=2)
    except:
        rv = {"status":"error", "message":"Missing 'host' field e.g 'border.410'"}
        return json.dumps(rv, indent=2)
        
    try:
        ip = request.POST.getone("ip")
        num = iptools.ipv4.ip2long(ip)
        if num is None:
            rv = {"status":"error", "message":"IP is malformed"}
            return json.dumps(rv, indent=2)
        if ((num >> 4) & 0xFFF) - routing_prefix_offset != block["number"]:
            rv = {"status":"error", "message":"IP is not in block"}
            return json.dumps(rv, indent=2)
    except:
        rv = {"status":"error", "message":"Missing 'ip' field e.g '100.64.3.4'"}
        return json.dumps(rv, indent=2)
    print "Would register %s = %s" %(hostname, block)
    msg = _set_record4(hostname, ip, block["key"],mysqldb_pyramid)
    if msg == "success":
        rv = {"status":"success", "hostnames":hostname+".m.storm.pm", "ip":ip}
        return json.dumps(rv, indent=2)
    else:
        rv = {"status":"error", "message":msg}
        return json.dumps(rv, indent=2)
    
@view_config(route_name='whoami', renderer='string')
def whoami(request):
    return request.remote_addr

@view_config(route_name='init_tunnels', renderer='string')
def init_tunnels(request):
    if request.remote_addr != "127.0.0.1":
        rv = {"status":"error", "message":"Access denied"}
        return json.dumps(rv, indent=2)
    all_blocks = db.blocks.find({"active":True})
    rvl = []
    for block in all_blocks:
        print "Trying to bring up tunnel:",block["key"]
        rvl += block["ip6"]
        tun_down(block["key"])
        tun_up(block["key"])
    rv = {"status":"success", "tunnels":rvl}
    return json.dumps(rv, indent=2)

def barray_to_long(arr):
    rv = 0
    for c in arr:
        rv <<= 8
        rv += ord(c)
    return rv

def udp_dispatch(data, addr, mode, sock):
    print "udp dispatch addr: ", addr
    def ret(x):
        sock.sendto(x, addr)

    try:
        u = uuid.UUID(bytes=data[1:17])
        block = db.blocks.find_one({"key":str(u)})
        if block is None: #invalid key
            return ret(data[0]+"\x01")

        if data[0] == 0x01: #update auto
            if mode != 4:
                return ret("\x01\x02")
            db.blocks.update({"$set":{"remote_ipv4":[addr[0]]}})
            return ret("\x01\x00")
        if data[0] == 0x02: #update specific
            raddr = iptools.ipv4.long2ip(barray_to_long(data[17:21]))
            if raddr is None:
                return ret("\x02\x02")
            db.blocks.update({"$set":{"remote_ipv4":raddr}})
            return ret("\x02\x00")
        if data[0] == 0x03: #update AAAA
            suffix = barray_to_long(data[17:25])
            prefix = iptools.ipv6.ip2long(block["ip6"])
            addrn = prefix+suffix
            gaddr = iptools.ipv6.long2ip(prefix+suffix)
            #check IP is in the block
            if (addrn >> 80) != routing_prefix >> 80:
                return ret("\x03\x03")
            if ((addrn >> 64) & 0xFFFF) - routing_prefix_offset != block["number"]:
                return ret("\x03\x03")
            #check the hostname is not insane
            name = data[26:ord(data[25])]
            validre = "^([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])(\.([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9]))*$"
            if not re.match(validre, name):
                return ret("\x03\x02")
            r = _set_record6(name, gaddr, str(u), mysqldb_udp4 if mode == 4 else mysqldb_udp6)
            if r != "success":
                return ret("\x03\x04")
            return ret("\x03\x00")
        if data[0] == 0x04: #update AAAA auto
            if mode != 6:
                return ret("\x04\x05")
            addrn = iptools.ipv6.ip2long(addr[0])
            #check IP is in the block
            if (addrn >> 80) != routing_prefix >> 80:
                return ret("\x04\x03")
            if ((addrn >> 64) & 0xFFFF) - routing_prefix_offset != block["number"]:
                return ret("\x04\x03")
            #check the hostname is not insane
            name = data[18:ord(data[17])]
            validre = "^([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])(\.([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9]))*$"
            if not re.match(validre, name):
                return ret("\x04\x02")
            r = _set_record6(name, addr[0], str(u), mysqldb_udp4 if mode == 4 else mysqldb_udp6)
            if r != "success":
                return ret("\x04\x04")
            return ret("\x04\x00")




    except BaseException as be:
        print ("Encountered error on UDP dispatch:", be)

def udp_backend4():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", 410))
    while True:
        data, addr = sock.recvfrom(1024)
        udp_dispatch(data,addr, 4, sock)

def udp_backend6():
    sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    sock.bind(("2001:470:4885::", 410))
    while True:
        data, addr = sock.recvfrom(1024)
        udp_dispatch(data,addr, 6, sock)

def launch_udp_backend():
    thread.start_new_thread(udp_backend4)
    thread.start_new_thread(udp_backend6)
