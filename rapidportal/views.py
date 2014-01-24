from pyramid.view import view_config

#Yeah yeah yeah, this is a terrible idea. I expect <= 1 concurrent user though and I am writing
#this at 1:42 AM so spare me the asynchronisity is amazing lecure.
import threading
import subprocess
import pymongo
import uuid

client = pymongo.MongoClient()
db = client.rapid

def spawn_driver_job(params):
    #We can block
    output = subprocess.check_output("/srv/bake_driver_docklet.sh", env={"SMAPID":params["commit"], "URL":params["url"], "INI":params["ini"]})
    params["bake_output"] = output
    rapid.bake_outputs.save(params)

@view_config(route_name='home', renderer='rapidportal:templates/index.mako')
def home(request):
    return {'project': 'rapidportal'}
    
@view_config(route_name='driver', renderer='rapidportal:templates/driver.mako')
def driver(request):
    return {'project': 'rapidportal'}
    
@view_config(route_name='drivertarget', renderer='json')
def drivertarget(request):
    obj = request.json_body
    jobid = str(uuid.uuid4())
    obj["jobid"] = jobid
    #todo verify
    
    #create build entry in DB
    
    t = threading.Thread(target=spawn_driver_job, args=obj)
    t.start()
    return {'foo':'bar'}
