import os
import sys
import traceback
from bosrv.request import connect
from bosrv.ttypes import *
from exc.ttypes import *
import tools


def shell(connargs, shell_name, command):
    import time
    now = time.time()
    result_str = ""
    addr_info = connargs['origin']
    parsedict=tools.postactionParser(command)
    if parsedict["ERR_msg"]!=None:
        print parsedict["ERR_msg"]
        return parsedict["ERR_msg"]

    command=parsedict["command"]
    out_command=parsedict["out_command"]
    pipes_command=parsedict["pipes_command"]
    doInvoke=parsedict["doInvoke"]
    result_table = []


    limit = os.environ.get("RPC_LIMIT")
    display_limit = os.environ.get("DISPLAY_LIMIT")

    limit = int(limit) if limit else 10000
    display_limit= int(display_limit) if display_limit else 10000

    try:
        with connect(addr_info, int(connargs["timeout"])) as conn:
            token, cli = conn
        #with connect(addr_info, int(timeout)) as cli:
            try:
                if shell_name == "sql":
                    print "In workspace:"+connargs["workspace"]
                    exec_ret = cli.sql_execute(token, command, "/"+connargs["workspace"],connargs["opts"])
                elif shell_name == "la":
                    exec_ret = cli.aux_execute(token, command, "/"+connargs["workspace"],connargs["opts"])
                elif shell_name == "assoc":
                    print "In workspace:"+connargs["workspace"]
                    exec_ret = cli.assoc_execute(token, command, connargs["workspace"],connargs["opts"])
            except:
                traceback.print_exc()
                exec_ret = ""
                result_str = "Unexpected error:" + str(sys.exc_info()[0])
            end = time.time()
            #table_str = ""

            dump_start=time.time()
            if (exec_ret != ""):
                import json
                line_count=0
                isDump=False
                eol = None
                while eol != -1:
                    try:
                        tmpJson = cli.cursor_fetch(
                                token,
                                exec_ret,
                                RangeSpec(page=limit)
                                )

                        temp=json.loads(tmpJson)
                        eol, rows = temp # if eol == -1, then no more data to read

                        if not isDump:
                            result_table.extend(rows)
                        else:
                            tools.dump2Csv(rows,out_command,line_count)
                            line_count+=len(rows)

                        if len(result_table) > display_limit:
                            confirmStr= "Size of data exceeded display limit, dump to csv format? (yes/no)"
                            for index,line in enumerate(result_table):
                                if index>10:
                                    break
                                print line
                            import fileinput
                            print confirmStr
                            while True:
                                choice=raw_input()
                                if choice=="yes" or choice=="y":
                                    break
                                elif choice=="no" or choice=="n":
                                    cli.cursor_close(token,exec_ret)
                                    print 'execution time: %ss' %  str(round((end - now),2))
                                    return ""
                                else:
                                    print confirmStr
                            tools.dump2Csv(result_table,out_command,line_count,status="init")
                            line_count+=len(result_table)
                            result_table=[]
                            isDump=True
                    except:
                        print "except : " + str(sys.exc_info()[0])
                        traceback.print_exc()
                        break
                else:
                    cli.cursor_close(token,exec_ret)
                    print

                key_index = 0
                result_str = "result:\n"
                #result_str += "size:" + str(len(result_table)) + "\n"
                if isDump:
                    outfile=out_command if out_command!=None else "dump_result.csv"
                    if ".csv" not in outfile:
                        outfile+=".csv"
                    result_str+="dump to "+outfile+"\n"
                else:
                    for record in result_table:
                    #print str(record).decode('unicode-escape')
                        result_str += str(record).decode('unicode-escape')
                        result_str += "\n"
                        #table_str += str(record) + ","
                result_str += "size:"
                result_str += str(len(result_table)) if len(result_table)>0 else str(line_count)
                result_str += "\n"

                if pipes_command:
                    if isDump:
                        print "The result set is too large, pipe operation is cancelled."
                    else:
                        tools.runPipes(result_table,pipes_command)

                if out_command:
                    if isDump:
                        print "The result set is too large, dump to csv format only."
                    else:
                        outfile=tools.redirectFiles(result_table,out_command)
                        if outfile=="BADINPUT":
                            return "*** cancel outputting the file"
                        if doInvoke:
                            tools.invokeFiles(outfile)

            dump_end=time.time()
            #print "send: \"" + command + "\" to " + host + ":" + str(port) + "\n" + result_str + '\ntime: %ss' %  str(round((end - now),2)) + "\n"
            print "send: \"" + command + "\" to " + connargs["host"] + ":" + str(connargs["port"]) + "\n"
            print result_str
            print 'execution time: %ss' %  str(round((end - now),2))
            print 'dump data time: %ss' %  str(round((dump_end-dump_start),2)) + "\n"
            print "======================"
            if len(result_table) > 0:
                return result_table
            else:
                return ""

    except:
        traceback.print_exc()
        print "======================"
        return ""
