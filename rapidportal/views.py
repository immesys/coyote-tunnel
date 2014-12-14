from pyramid.view import view_config

#Yeah yeah yeah, this is a terrible idea. I expect <= 1 concurrent user though and I am writing
#this at 1:42 AM so spare me the asynchronisity is amazing lecure.
import threading
import subprocess
import pymongo
import uuid
import json
import os
import datetime
from pyramid.response import Response
from authomatic import Authomatic
from authomatic.adapters import WebObAdapter
from authomatic.providers import oauth2
import pyramid.httpexceptions as exc

FIDCONF = { "gh": 
        {
            "class_": oauth2.GitHub,
            "consumer_key":"63bf25fc93bf09b57e60",
            "consumer_secret":"e8cc33a313e9dab6b4a43f03e0a65df622af2800",
            "access_headers":{"User-Agent":"RapidPortal Server"},
        }
    }
    
authomatic = Authomatic(config=FIDCONF, secret='foobizbar') 


from pyramid.response import FileResponse, Response
import tempfile

client = pymongo.MongoClient()
db = client.rapid


def tstamp():
    return str(datetime.datetime.now())

def logentry(jobid, label, typ, content=None, path=None):
    """This is for complete entries, as opposed to files"""
    ud = str(uuid.uuid4())
    db.logs.save({"uuid":ud, "jobid":jobid, "label":label, "type":typ, "content":content, "date":tstamp(), "containerurl":path}) 

def load_so(request):
    if "skey" not in request.session:
        request.session["skey"] = str(uuid.uuid4())
    rv = db.sessions.find_one({"skey":request.session["skey"]})
    if rv is None:
        return {"skey":request.session["skey"], "auth":False}
    return rv
        
def save_so(so):
    db.sessions.save(so)
           
def spawn_job(params, typ):
    
    #We can block
    bj = db.services.find_one({"jobid":params["jobid"]})
    try:
        ev = os.environ.copy()
        if typ=="driver":
            targetscript = "bake_driver_docklet.sh"
            ev.update({"SMAPID":params["smap_commit"], 
                       "SMAPURL":params["smap_url"],
                       "INIID":params["ini_commit"],
                       "INIURL":params["ini_url"],
                       "INI":params["ini"]})
        elif typ=="stack":
            targetscript = "bake_stack_docklet.sh"
            ev.update({"SMAPID":params["smap_commit"], "PDBID":params["pdb_commit"],"RDBID":params["rdb_commit"],"INI":params["ini"]})
        else:
            bj["state"] = "build exception"
            db.services.save(bj)
            return
        output = subprocess.check_output(["bash",targetscript], cwd="/home/immesys/Dockerfiles/smap_rapid/", env=ev)
        
        logentry(params["jobid"], "build", "full", output)
        
        #"URL":params["url"], 
        bid = output.splitlines()[-1].strip()
        did = subprocess.check_output(["docker","run","-p","22","-t","-i","-d",bid,"supervisord"]).strip()
        logentry(params["jobid"],"launch","full",did)
        params["dockerid"] = did
        dobj = subprocess.check_output(["docker","inspect",did])
        dobj = json.loads(dobj)[0]
        bj["state"] = "Launched" if dobj["State"]["Running"] else "run failed"
        bj["ssh"] = dobj["HostConfig"]["PortBindings"]["22/tcp"][0]["HostPort"]
        bj["containerid"] = did
        db.services.save(bj)
        #Bind the URL
        print "binding URL"
        print "spawn params:",params
        output = subprocess.check_output(["python","modprox.py","--add","--url",params["url"]+".rapid.cal-sdb.org",
                                          "--name",did,"--port",params["port"],"--regen"], cwd="/home/immesys/Dockerfiles/tools/", env=ev)
        print "modprox: \n",output    
    except Exception as e:
        bj["state"] = "build exception"
        db.services.save(bj)
        print repr(e)
    
@view_config(route_name='home', renderer='rapidportal:templates/index.mako')
def home(request):
    so = load_so(request)
    if not so["auth"]:
        raise exc.HTTPFound(request.route_url("auth"))
        
    services = db.services.find({})
    return {"services":services, "pic":so["picture"],  "name":so["userfullname"]}
    
@view_config(route_name='driver', renderer='rapidportal:templates/driver.mako')
def driver(request):
    so = load_so(request)
    if not so["auth"]:
        raise exc.HTTPFound(request.route_url("auth"))
        
    return {"pic":so["picture"],  "name":so["userfullname"]}

@view_config(route_name='stack', renderer='rapidportal:templates/stack.mako')
def stack(request):
    so = load_so(request)
    if not so["auth"]:
        raise exc.HTTPFound(request.route_url("auth"))
        
    return {"pic":so["picture"], "name":so["userfullname"]}
    
def generictarget(request, typ):
    #so = load_so(request)
    #if not so["auth"]:
    #    raise exc.HTTPClientError()
        
    obj = request.json_body
    print "object is:",obj
    print "typ is",typ
    try:
        
        obj2 = {"description":str(obj["description"]),
                "author":str(obj["author"]),  #so["userfullname"],
                "url":str(obj["url"]),
                "smap_commit":str(obj["smap_commit"]),
                "ini":str(obj["ini"]),
                "instanceid":str(obj["uuid"]),
                "port":str(int(obj["port"]))}
        if typ == "stack":
            obj2["pdb_commit"] = str(obj["pdb_commit"])
            obj2["rdb_commit"] = str(obj["rdb_commit"])
        elif typ == "driver":
            obj2["smap_url"] = str(obj["smap_url"])
            obj2["ini_url"] = str(obj["ini_url"])
            obj2["ini_commit"] = str(obj["ini_commit"])
        obj = obj2
    except Exception as e:
        print e
        return {"status":"Parameter error"}
   
    subprocess.call(["python","/home/immesys/Dockerfiles/tools/rmsrv.py",str(obj["url"])])
    testjob = db.services.find_one({"instanceid":obj["instanceid"]})
    if testjob is not None:
        return {"status":"Failed the Steve test"}
 
    jobid = str(uuid.uuid4())
    obj["jobid"] = jobid
    obj["state"] = "building"
    obj["type"] = typ
    obj["ssh"] = 0
    
    logentry(jobid, "supervisord","embedded",path="/var/log/supervisor/supervisord.log")
    logentry(jobid, "sshd", "embedded", path="/var/log/supervisor/sshd.log")
    if typ == "stack":
        logentry(jobid, "apache2","embedded",path="/var/log/supervisor/apache2.log")
        logentry(jobid, "postgres", "embedded", path="/var/log/supervisor/postgres.log")
        logentry(jobid, "readingdb", "embedded", path="/var/log/supervisor/readingdb.log")
        logentry(jobid, "archiver","embedded", path="/var/log/supervisor/archiver.log")
    elif typ == "driver":
        logentry(jobid, "driver", "embedded", path="/var/log/supervisor/driver.log")
        
    #todo check that URL is unique + valid
    db.services.save(obj)
    t = threading.Thread(target=spawn_job, args=[obj, typ])
    t.start()
    return {"status":"submitted"}
        
@view_config(route_name='drivertarget', renderer='json')
def drivertarget(request):
    return generictarget(request, "driver")

@view_config(route_name='stacktarget', renderer='json')
def stacktarget(request):
    return generictarget(request, "stack")  

@view_config(route_name='manage', renderer="rapidportal:templates/manage.mako")
def manage(request):
    so = load_so(request)
    if not so["auth"]:
        raise exc.HTTPFound(request.route_url("auth"))
        
    jobid = request.matchdict["uuid"]
    obj = db.services.find_one({"jobid":jobid})
    if obj is None:
        return {"found":False}  
    logs = db.logs.find({"jobid":jobid})
    return {"logfiles":logs, "pic":so["picture"], "name":so["userfullname"]}
    
@view_config(route_name='auth')
def login(request):
    response = Response()
    result = authomatic.login(WebObAdapter(request, response), "gh")
    if result:
        if result.error:
            print "got error :/"
        elif result.user:
            if not (result.user.name and result.user.username):
                print "Had to update for name"
                result.user.update()
            print "Username: ",result.user.username
            print "User name: ",result.user.name
            print "ID: ",result.user.id
            print "Picture:" ,result.user.picture
            print dir(result.user)
            so = load_so(request)
            so["auth"] = True
            so["username"] = result.user.username
            so["userfullname"] = result.user.name
            so["userid"] = result.user.id
            so["picture"] = result.user.picture
            save_so(so)
            raise exc.HTTPFound(request.route_url("home"))
            
    return response
    
    
@view_config(route_name='deauth')
def logout(request):
    so = load_so(request)
    so["auth"] = False
    save_so(so)
    raise exc.HTTPFound("https://github.com/logout")

@view_config(route_name='logfile')
def logfile(request):
    so = load_so(request)
    if not so["auth"]:
        raise exc.HTTPFound(request.route_url("auth"))
        
    uuid = request.matchdict["uuid"]
    obj = db.logs.find_one({"uuid":uuid})
    
    if obj is None:
        return "No such log found"
    sobj = db.services.find_one({"jobid":obj["jobid"]})
    
    if obj["type"] == "full":
        return Response(body=obj["content"],content_type="text", charset="utf-8") 
    elif obj["type"] == "embedded":
        dn = tempfile.mkdtemp()
       # tfile = os.path.join(dn,"logfile")
        output = subprocess.check_output(["docker","cp",sobj["containerid"]+":"+obj["containerurl"], dn])
        print "log retrieval: ",output
        response = FileResponse(os.path.join(dn, os.path.basename(obj["containerurl"])),content_type="text")
     
        return response
        
        
@view_config(route_name='broker_allocate', renderer="rapidportal:templates/allocate_block.mako")
def ba_allocate_block(request):
    so = load_so(request)
    if not so["auth"]:
        raise exc.HTTPFound(request.route_url("auth"))
    return {"pic":so["picture"], "name":so["userfullname"]}
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
