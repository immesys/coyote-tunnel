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

mysqldb = MySQLdb.connect(host="localhost", user="coyote", passwd="coyote", db="pdns")
cur = mysqldb.cursor()

from views import load_so

routing_prefix_offset = 8
#This this is the base from which up to 50k /64's will be allocated
routing_prefix = 0x20010470488900000000000000000000 + (routing_prefix_offset<<64)
#This is the base from which up to 50k /127's will be allocated
p2p_prefix     = 0x20010470488900010000000000000000 + (routing_prefix_offset<<48)

inet_prefix = 0x64400000 + (routing_prefix_offset << 6)
inet_p2p_prefix = 0x64AF0000 + (routing_prefix_offset << 4)

broker_ipv4="50.18.70.36"

def set_record6(name, ip, key):
    name = name.lower()
    if re.match(r"^(([a-z0-9\-]{1,63}\.?)+(\-[a-z0-9]+)){1,255}$", name) is None:
        return "Bad DNS name"
    r = db.dns.find_one({"name":name, "t":6})
    if r is not None:
        if r["key"] != key:
           return "You are not the owner of this name"
    fqdn = name+".m.storm.pm"
    l = iptools.ipv6.ip2long(ip)
    if l is None:
        return "Bad IPv6 address"
    cur.execute("DELETE FROM records WHERE name=%s",[fqdn])
    cur.execute("INSERT INTO records(domain_id, name, type, content, ttl, auth) VALUES (1, %s, AAAA, %s, 120, 1)", [fqdn, ip])
    db.dns.save({"name":name,"t":6,"key":key})

def set_record4(name, ip, key):
    name = name.lower()
    if re.match(r"^(([a-z0-9\-]{1,63}\.?)+(\-[a-z0-9]+)){1,255}$", name) is None:
        return "Bad DNS name"
    r = db.dns.find_one({"name":name, "t":4})
    if r is not None:
        if r["key"] != key:
           return "You are not the owner of this name"
    fqdn = name+".m.storm.pm"
    l = iptools.ipv4.ip2long(ip)
    if l is None:
        return "Bad IPv4 address"
    cur.execute("DELETE FROM records WHERE name=%s",[fqdn])
    cur.execute("INSERT INTO records(domain_id, name, type, content, ttl, auth) VALUES (1, %s, A, %s, 120, 1)", [fqdn, ip])
    db.dns.save({"name":name,"t":4,"key":key})
    return "success"
            
def get_block(owner, ip, useragent):
    key = str(uuid.uuid4())
    new_block = {"owner":owner, "creatingip":ip,"agent":useragent, "date":time.time(), "key":key}
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
    new_block["active"] = False    
    
    #Crude race resolution    
    i = db.blocks.save(new_block)
    curs = db.blocks.find({"number":new_num})
    if curs.count() != 1:
        db.blocks.remove({"_id":i})
        return get_block(owner, ip, useragent)
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
            "local",broker_ipv4,"ttl","255"]
        subprocess.check_call(["ip","tunnel","add",tunname6,"mode","sit","remote",block["remote_ipv4"],
            "local",broker_ipv4,"ttl","255"])  
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
            "local",broker_ipv4,"ttl","255"])  
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
    block, key = get_block(owner, request.remote_addr, request.remote_user)
    if block is None:
        rv = {"status":"error", "message":"No more blocks to allocate (guess we got DoS'd)"}
        return json.dumps(rv, indent=2)
    rv = {"status":"ok","owner":owner, "key": key,
            "inet6_block":block["ip6"]+"/64",
            "inet4_block":block["ip4"]+"/26", 
            "client_ip6":block["client_router6"]+"/127", 
            "broker_ip6":block["broker_router6"]+"/127",
            "client_ip4":block["client_router4"]+"/30",
            "update_url":"http://rapid.cal-sdb.org/u/"+key+"?ip=auto",
            "config_url_linux":"http://rapid.cal-sdb.org/c/nix/"+key,
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
    if reboot:
        tun_down(key)
        tun_up(key)
    rv = {"status":"success", "configurl":"http://rapid.cal-sdb.org/c/nix/%s" % key}
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
        if ((num >> 64) & 0xFFFF) - routing_prefix_offset != block["number"]:
            rv = {"status":"error", "message":"IP is not in block"}
            return json.dumps(rv, indent=2)
    except:
        rv = {"status":"error", "message":"Missing 'ip' field e.g '2001:470:8036:f00::ba5"}
        return json.dumps(rv, indent=2)
    print "Would register %s = %s" %(hostname, block)
    hns = set_record6(hostname, ip, block["key"])
    rv = {"status":"success", "hostnames":hns, "ip":ip}
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
    hns = set_record4(hostname, ip, block["key"])
    rv = {"status":"success", "hostnames":hns, "ip":ip}
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
    
    
