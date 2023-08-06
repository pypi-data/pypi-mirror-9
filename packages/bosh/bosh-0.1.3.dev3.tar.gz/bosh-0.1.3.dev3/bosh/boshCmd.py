
import sys
from bosrv.request import connect
from exc.ttypes import *
import json
import traceback

def setinfo(connargs,command, argument):
    import time
    now = time.time()
    addr_info = connargs['origin']
    try:
        with connect(addr_info, int(connargs["timeout"])) as conn:
            token, cli = conn
            try:
                 exec_ret = cli.admin_execute(token," ".join([command,argument]),"/"+connargs["workspace"],connargs["opts"])
            except:
                traceback.print_exc()
                exec_ret = ""
                result_str = "Unexpected error:" + str(sys.exc_info()[0])
            end = time.time()
            print 'time: %ss' %  str(round((end - now),2))
            return "======================"
   
    except:
        traceback.print_exc()
        return "======================"
   



def getinfo(connargs,command, argument):
    import time
    now = time.time()
    addr_info = connargs['origin']
    result_str = ""
    try:
        with connect(addr_info, int(connargs["timeout"])) as conn:
            token, cli = conn
            try:
                 exec_ret = cli.admin_execute(token," ".join([command,argument]),"/"+connargs["workspace"],connargs["opts"])
                 parsed=json.loads(exec_ret)
                 print json.dumps(parsed,indent=8,sort_keys=False)
            except:
                traceback.print_exc()
                exec_ret = ""
                result_str = "Unexpected error:" + str(sys.exc_info()[0])
            end = time.time()

            print 'time: %ss' %  str(round((end - now),2))
            return "======================"
    except:
        traceback.print_exc()
        return "======================"
