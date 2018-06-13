from pprint import pprint
import re
from datetime import datetime
from common.MaltegoTransform import *
from common.postgresdb import MsploitPostgres
import sys
from common.servicefactory import getserviceentity, getosentity

__author__ = 'Marc Gurreri'
__copyright__ = 'Copyright 2018, msploitego Project'
__credits__ = []
__license__ = 'GPLv3'
__version__ = '0.1'
__maintainer__ = 'Marc Gurreri'
__email__ = 'me@me.com'
__status__ = 'Development'

def dotransform(args):
    mt = MaltegoTransform()
    # mt.debug(pprint(args))
    mt.parseArguments(args)
    ip = mt.getValue()
    mac = mt.getVar("mac")
    machinename = mt.getVar("name")
    os_family = mt.getVar("os_family")
    os_name = mt.getVar("os_name")
    os_sp = mt.getVar("os_sp")
    hostid = mt.getVar("id")
    if not hostid:
        hostid = mt.getVar("hostid")
    db = mt.getVar("db")
    user = mt.getVar("user")
    password = mt.getVar("password").replace("\\", "")
    # workspace = mt.getVar("workspace")
    mpost = MsploitPostgres(user, password, db)
    for service in mpost.getServices(hostid):
        entityname = getserviceentity(service)
        servicename = service.get("servicename")
        if not servicename:
            servicename = "unknown"
        hostservice = mt.addEntity(entityname, "{}/{}:{}".format(servicename, service.get("port"), hostid))
        hostservice.setValue("{}/{}:{}".format(servicename, service.get("port"), hostid))
        hostservice.addAdditionalFields("ip", "IP Address", True, ip)
        hostservice.addAdditionalFields("service.name", "Description", True, "{}/{}:{}".format(servicename, service.get("port"), hostid))
        if machinename:
            hostservice.addAdditionalFields("machinename", "Machine Name", True, machinename)
        if service.get("info"):
            hostservice.addAdditionalFields("banner.text", "Service Banner", True, service.get("info"))
        else:
            hostservice.addAdditionalFields("banner.text", "Service Banner", True, "")

        if servicename in ["http", "https", "possible_wls", "www", "ncacn_http", "ccproxy-http", "ssl/http",
                           "http-proxy"]:
            hostservice.addAdditionalFields("niktofile", "Nikto File", True, '')
        for k,v in service.items():
            if isinstance(v,datetime):
                hostservice.addAdditionalFields(k, k.capitalize(), False, "{}/{}/{}".format(v.day,v.month,v.year))
            elif v and str(v).strip():
                hostservice.addAdditionalFields(k, k.capitalize(), False, str(v))
        hostservice.addAdditionalFields("user", "User", False, user)
        hostservice.addAdditionalFields("password", "Password", False, password)
        hostservice.addAdditionalFields("db", "db", False, db)
    if mac:
        macentity = mt.addEntity("maltego.MacAddress", mac)
        macentity.setValue(mac)
        macentity.addAdditionalFields("ip", "IP Address", True, ip)
    # if machinename and re.match("^[a-zA-z]+", machinename):
    if machinename:
        hostentity = mt.addEntity("msploitego.Hostname", machinename)
        hostentity.setValue(machinename)
        hostentity.addAdditionalFields("ip", "IP Address", True, ip)
    osentityname, osdescription = getosentity(os_family,os_name)
    if os_sp:
        osdescription += " {}".format(os_sp)
    osentity = mt.addEntity(osentityname, osdescription)
    osentity.setValue(osdescription)
    osentity.addAdditionalFields("ip", "IP Address", True, ip)

    mt.returnOutput()
    

dotransform(sys.argv)
# args = ['postgresservices.py',
#  '10.11.1.10',
#  'ipv4-address=10.11.1.10#ipaddress.internal=false#vuln_count=8#workspace=default#address=10.11.1.10#os_family=Windows#purpose=server#service_count=2#os_sp=SP2#created_at=23/1/2018#mac=00:50:56:b8:76:82#workspace_id=18#password=unDwIR39HP8LMSz3KKQMCNYrcvvtCK478l2qhIi7nsE\\=#updated_at=11/6/2018#exploit_attempt_count=11#name=10.11.1.10#os_name=Windows 2003#id=531#state=alive#user=msf#note_count=9#db=msf']
# dotransform(args)