import os
import sys
import traceback
from bosrv.connect import connect
from bosrv.ttypes import *
from exc.ttypes import *

def shell(host, port, token, command, timeout):
    import time
    now = time.time()
    addr_info = (
            str(host),
            int(port)
            )
    result_str = ""
    with connect(addr_info, int(timeout)) as cli:
        try:
            exec_ret = cli.aux_execute(token, command, True)
        except:
            traceback.print_exc()
            exec_ret = ""
            result_str = "Unexpected error:" + str(sys.exc_info()[0])
        end = time.time()
        table_str = ""


        if (exec_ret != ""):
            import json
            limit = 100 # decide the limit of records returned per fetch
            result_table = [] # the destination storage for the result table

            #now = time.time()
            while not result_table or result_table[-1] != -1:
                try:
                    temp = cli.cursor_fetch(
                            token,
                            exec_ret,
                            RangeSpec(page=limit)
                            )
                    row = json.loads(temp)
                    result_table.extend(row)
                except:
                    print "except : " + temp


            else:
                cli.cursor_close(token,exec_ret)
                result_table.pop()
            key_index = 0

            result_str = "result:\n"
            result_str += "size:" + str(len(result_table)) + "\n"

            for record in result_table:
                result_str += str(record)
                result_str += "\n"
                table_str += str(record) + ","

        print "send: \"" + command + "\" to " + host + ":" + str(port) + "\n" + result_str + '\ntime: %ss' %  str(round((end - now),2)) + "\n"
        return "======================"
