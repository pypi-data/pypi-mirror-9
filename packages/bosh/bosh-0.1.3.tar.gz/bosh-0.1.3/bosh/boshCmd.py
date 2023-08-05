
import sys
from bosrv.request import connect
from exc.ttypes import *
import json
import traceback

def getinfo(connargs,command, argument):
    import time
    now = time.time()
    addr_info = connargs['origin']
    result_str = ""
    try:
        with connect(addr_info, int(connargs["timeout"])) as conn:
            token, cli = conn
            try:
                if command == "get_table_list":
                    exec_ret = cli.get_table_list(token,"/"+connargs["workspace"])
                    parsed = json.loads(exec_ret)
                    print "Tables:\n" + json.dumps(parsed, indent=8, sort_keys=False)

                elif command == "get_table_schema":
                    exec_ret = cli.get_table_schema(token, argument , "/"+connargs["workspace"])
                    parsed = json.loads(exec_ret)
                    print "Tables:\n" + json.dumps(parsed, indent=8, sort_keys=False)
                    #print "Attributes: " + exec_ret
                elif command == "get_table_relation":
                    exec_ret = cli.get_table_relation(token, argument , connargs["workspace"])
                    parsed = json.loads(exec_ret)
                    print "Tables:\n" + json.dumps(parsed, indent=8, sort_keys=False)
                    #print "Relations:\n" + exec_ret
                elif command == "get_mbt_list":
                    exec_ret = cli.get_mbt_list(token, "/")
                    parsed = json.loads(exec_ret)
                    print "matrice:\n" + json.dumps(parsed, indent=8, sort_keys=False)
                elif command == "get_mbt_info":
                    exec_ret = cli.get_mbt_info(token, argument , "/")
                    parsed = json.loads(exec_ret)
                    print "matrice:\n" + json.dumps(parsed, indent=8, sort_keys=False)
                elif command == "get_qbo_list":
                    exec_ret = cli.get_qbo_list(token, connargs["workspace"])
                    parsed = json.loads(exec_ret)
                    print "associates:\n" + json.dumps(parsed, indent=8, sort_keys=False)
                elif command == "get_qbo_info":
                    exec_ret = cli.get_qbo_info(token, argument , "/"+connargs["workspace"])
                    parsed = json.loads(exec_ret)
                    print "matrice:\n" + json.dumps(parsed, indent=8, sort_keys=False)

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
