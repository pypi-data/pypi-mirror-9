import sys
import cmd
import os

import rpcshell

import re
import boshCmd
import csvloader
from urlparse import urlparse
import texttable
import tools
import getpass
import traceback

d_type = "postgresql"
d_host = ""
d_port = ""
d_user = ""
d_pass = ""
d_db = ""
db_access_str = ""





def load_database_url(db_url):
    if db_url != "" and db_url != None:
        global d_type, d_host, d_port, d_user, d_pass, d_db, db_access_str
        url_object = urlparse(db_url)
        d_type = url_object.scheme
        if d_type == "postgres":
            d_type = "postgresql"
        d_host = url_object.hostname
        d_port = url_object.port
        d_user = url_object.username
        d_pass = url_object.password
        d_db = url_object.path[1:]

        db_access_str = '"' + "type=" + str(d_type) + " host=" + str(d_host) + " port=" + str(d_port) + " user=" + str(d_user) + " password=" + str(d_pass) + " db=" + str(d_db) + '"'
        #print "DATABASE_URL :" + db_access_str
    else:
        print "DATABASE_URL is empty"
        db_access_str = ""
    return db_access_str

def dbinput():
    global d_type, d_host, d_port, d_user, d_pass, d_db, db_access_str
    dbtype = raw_input(">>> database type [" + d_type + "] : " )
    if dbtype != "":
        d_type = dbtype
    host = raw_input(">>> host [" + d_host + "] : " )
    if host != "":
        d_host = host
    port = raw_input(">>> port [" + d_port + "] : " )
    if port != "":
        d_port = port
    username = raw_input(">>> username [" + d_user + "] : " )
    if username != "":
        d_user = username
    password = getpass.getpass(">>> Password (hidden) : ")
    if password != "":
        d_pass = password
    dbname = raw_input(">>> database name [" + d_db + "] : " )
    if dbname != "":
        d_db = dbname

    db_access_str = '"' + "type=" + str(d_type) + " host=" + str(d_host) + " port=" + str(d_port) + " user=" + str(d_user) + " password=" + str(d_pass) + " db=" + str(d_db) + '"'
    return db_access_str

class baseCmd(cmd.Cmd):
    def emptyline(self):
        pass
    def do_EXIT(self, line):
        return True
    def do_exit(self, line):
        return True
    def do_QUIT(self, line):
        return True
    def do_quit(self, line):
        return True
    def do_sethost(self, line):
        if line != "":
            self.connargs["host"] = line
    def do_setport(self, line):
        if line != "":
            self.connargs["port"] = line
    def do_settimeout(self, line):
        if line != "":
            self.connargs["timeout"] = line
    def do_CSVLOADER(self, line):
        self.do_csvloader(line)
    def do_csvloader(self, line):
        if line != "":
            input_line = line.split();
            if len(input_line) >= 2:
                print csvloader.csvload(self.connargs, input_line[0] , input_line[1])
            else:
                print "csvloader <csv_file> <bt_name>"
    def do_psql(self, line):
        db_url = os.environ.get('DATABASE_URL')
        load_database_url(db_url)
        print
        tools.psql_run(d_host, d_port, d_user, d_pass, d_db)

    def do_info(self, line):
        print "host : " + self.connargs["host"]
        print "port : " + str(self.connargs["port"])
        print "timeout : " + str(self.connargs["timeout"])

    def help_psql(self):
        print "\trun postgresql client. psql required"
    def help_csvloader(self):
        print "\tload a local CSV file into a server-side BigObject table\n\tex. csvloader <csv_file> <bt_name>"
    def help_sethost(self):
        print "\tset host name"
    def help_setport(self):
        print "\tset port"
    def help_settimeout(self):
        print "\tset timeout value"

class associateCmd(cmd.Cmd):
    assocword = [ 'association', 'with', 'from' , 'by' , 'where' , 'query' , 'tables' , 'from', 'by', 'group by' , 'where' , 'tree' , 'table' , 'fact' , 'dim']
    def __init__(self):
        cmd.Cmd.__init__(self)
        try:
            import readline
            readline.set_history_length(80)
            try:
                readline.read_history_file()
            except IOError:
                readline.write_history_file()
        except ImportError:
            try :
                import pyreadline as readline
                readline.set_history_length(80)
                try:
                    readline.read_history_file()
                except IOError:
                    readline.write_history_file()
            except ImportError:
                pass

    def completedefault(self, text, line, begidx, endidx):
        if not text:
            completions = self.assocword[:]
        else:
            completions = [ f
            for f in self.assocword
            if f.startswith(text)
            ]
        return completions
    def default(self, line):
        split_command = line.split('=')
        #if len(split_command) == 2:
        #       var_name=split_command[0]
        #       cmd_line=split_command[1]
        if len(split_command) >= 2 and len(split_command[0].split()) == 1:
            var_name=split_command[0].strip()
            cmd_line=line[line.find('=') + 1:]
        else:
            cmd_line = line

        cmdWords=["find","query","row","column","get","show"]

        for word in cmdWords:
            if word.upper()+" " in line:
                line=line.replace(word.upper(),word)

#OLD FIND
#               if line.strip().replace(" ","").find("=find") != -1:
#                        if "where " in line:
#                             where_str_origin=cmd_line[cmd_line.find("where")+5:]
#                             cmd_line=cmd_line.replace(where_str_origin,self.cond_parser(where_str_origin,[" AND "," OR "," and "," or "]))
#
#                       return_data = rpcshell.shell(self.connargs, "assoc" , cmd_line)
#                       globals()[var_name] = return_data

        if line.strip().replace(" ","").find("=find") != -1:
            varlist=self.eval_var(cmd_line)
            for var in varlist:
                cmd_line=cmd_line.replace("$"+var,self.replace_var(var))
            cmd_line = self.mock_serverparser(cmd_line) 
            return_data = rpcshell.shell(self.connargs, "assoc" ,  cmd_line)
            globals()[var_name]=return_data

        elif line.strip().replace(" ","").find("=get") != -1:
            varlist=self.eval_var(cmd_line)
            for var in varlist:
               cmd_line=cmd_line.replace("$"+var,self.replace_var(var))
            return_data = rpcshell.shell(self.connargs, "assoc" , cmd_line)
            globals()[var_name]=return_data



        elif line.strip().replace(" ","").find("=query") != -1:
            #if cmd_line.find('$') != -1
            #       var_va = cmd_line[cmd_line.find('$') + 1:cmd_line.find(' ',cmd_line.find('$'))]
            #       cmd_line = cmd_line.replace("$"+var_va , str(globals()[var_va])[1:-1])
            #       #print line
            strEnd=len(cmd_line) if cmd_line.find(" from")==-1 else cmd_line.find(" from")
            query_str_origin=cmd_line[cmd_line.find("query ") + 5 : strEnd]
            query_str=self.replace_var(query_str_origin)
            cmd_line= "query "+query_str+cmd_line[strEnd:]

            return_data = rpcshell.shell(self.connargs, "assoc" , cmd_line)
            globals()[var_name] = return_data
            #self.var_list.add(var_name)

        elif line.strip().replace(" ","").find("=row") != -1:
            temp_str=line[line.find("=row") + 4:]
            split_temp = temp_str.split()
            exec_str = var_name + "="
            repeated_str = "[" + split_temp[0] + "]"
            exec_str += "map(a.__getitem__," + repeated_str + ")"
            #print exec_str
            exec(exec_str) in globals()
            # a=[['a','b'],['c','d'],['e','f']]
            # b=row 1,2 in a

        elif line.strip().replace(" ","").find("=$getentry(") != -1:
            arg_start = line.find( "(" , line.find("$") )
            arg_end = line.find( ")" , arg_start)
            arg_list = [ x.strip() for x in line[arg_start + 1: arg_end].split(",")]
            if len( arg_list ) == 2:
                  local_var = arg_list[0]
                  try:
                     row_id, col_id = [ x.strip() for x in arg_list[1].strip('[').strip(']').split(':')]
                  except:
                     print "entry format: [rowid:colid]"
                     return
                  if local_var not in self.get_bosh_global_var_with_filter():
                         print "Local variable: {0} not found".format(local_var)
                  elif row_id and col_id:
                         try:
                            globals()[var_name]=[ globals()[local_var][int(row_id)][int(col_id)] ]
                         except ValueError:
                            print "Index must be an integer"
                         except IndexError:
                            print "Index out of range"
                         except:
                            traceback.print_exc()
                  check_unicode_string = "if isinstance(" + var_name + "[0], basestring)==True:" + var_name + "=[row.encode('ascii','replace') for row in " + var_name + "]"
                  try:
                         exec(check_unicode_string) in globals()
                         print globals()[var_name]
                  except:
                         traceback.print_exc()


 
            else:      
                   print "usage: $getentry(<localvar>, [rowid:colid])"

        elif line.strip().replace(" ","").find("=$getcolumn(") != -1:
            arg_start = line.find( "(" , line.find("$") )
            arg_end = line.find( ")" , arg_start)
            arg_list = [ x.strip() for x in line[arg_start + 1: arg_end].split(",")]
            if len( arg_list ) == 2:
                  local_var = arg_list[0]
                  index = arg_list[1]
                  if local_var not in self.get_bosh_global_var_with_filter():
                         print "Local variable: {0} not found".format(local_var)
                  elif index:
                         try:
                            globals()[var_name]=list( zip(*globals()[local_var])[int(index)] )
                         except ValueError:
                            print "Index must be an integer"
                         except IndexError:
                            print "Index out of range"
                         except:
                            traceback.print_exc()
                  check_unicode_string = "if isinstance(" + var_name + "[0], basestring)==True:" + var_name + "=[row.encode('ascii','replace') for row in " + var_name + "]"
                  try:
                         exec(check_unicode_string) in globals()
                         print globals()[var_name]
                  except:
                         traceback.print_exc()


            else:      
                   print "usage: $getcolumn(<localvar>, <col_id>)"

        elif line.strip().replace(" ","").find("=$getrow(") != -1:
            arg_start = line.find( "(" , line.find("$") )
            arg_end = line.find( ")" , arg_start)
            arg_list = [ x.strip() for x in line[arg_start + 1: arg_end].split(",")]
            if len( arg_list ) == 2:
                  local_var = arg_list[0]
                  index = arg_list[1]
                  if local_var not in self.get_bosh_global_var_with_filter():
                         print "Local variable: {0} not found".format(local_var)
                  elif index:
                         try:
                            globals()[var_name]= globals()[local_var][int(index)]
                         except ValueError:
                            print "Index must be an integer"
                         except IndexError:
                            print "Index out of range"
                         except:
                            traceback.print_exc()
                  check_unicode_string = "{0}=map(lambda x:  x.encode('ascii','replace') if isinstance(x,basestring) else x,{1})".format(var_name,var_name)
                  try:
                       exec(check_unicode_string) in globals()
                       print globals()[var_name]
                  except:
                       traceback.print_exc()


            else:      
                   print "usage: $getrow(<localvar>, <row_id>)"


        elif line.strip().replace(" ","").find("=column") != -1:
            line=line.replace("$","")
            temp_str=line[line.find("column") + 7:]
            split_temp = re.split(r'[, ]', temp_str)
            #print split_temp
            #print split_temp[:-2]
            exec_str = var_name + "="
            repeated_str = ""
            for sp in split_temp[:-2]:
                repeated_str += "[__row["+ sp + "]"
                repeated_str += " for __row in "
                repeated_str += split_temp[-1] + "],"
            if len(split_temp[:-2]) > 1:
                exec_str += "[list(__merge_i) for __merge_i in zip("
                exec_str += repeated_str[:-1] + ")]"
            else:
                exec_str += repeated_str[:-1]
            try:
                exec(exec_str) in globals()
            except:
                traceback.print_exc()
            #check_unicode_string = "if isinstance(" + var_name + "[0], unicode)==True:" + var_name + "=" + var_name +".encode('ascii','replace')"
            check_unicode_string = "if isinstance(" + var_name + "[0], basestring)==True:" + var_name + "=[row.encode('ascii','replace') for row in " + var_name + "]"
            try:
                exec(check_unicode_string) in globals()
            except:
                traceback.print_exc()

            #print exec_str
            # a=[['a','b',1],['d','e',2]]
            # b=column 1,2 in a
            # [list(wa) for wa in zip([row[1] for row in a],[row[0] for row in a])]
        else:
            try:
                exec(line) in globals()
            except:
                traceback.print_exc()

        #elif line.find("=query") != -1:
        #       return_data = rpcshell.shell(self.host, self.port ,self.token, "assoc" , cmd_line, self.timeout)
        #       globals()[var_name] = return_data
        #       self.var_list.add(var_name)

        #if line.find("=create") != -1:
        #if line.find("=query") != -1:
        #if line.find("associate") != -1:
        #       tools.parse_associate_string_for_display(line)
        #       print rpcshell.shell(self.host, self.port ,self.token, "assoc" , line, self.timeout)
        #else:
        #       print "*** Unknown syntax: " + line

    #def do_testv(self, line):
    #       for var_temp in self.get_bosh_global_var_with_filter():
    #               if var_temp in line:
    #                       print "found"
    def do_LISTVAR(self, line):
        self.do_listvar(line)

    def do_listvar(self, line):
        #print "all variables: " + str(list(self.var_list))
        print "all variables: "
        print self.get_bosh_global_var_with_filter()


    def do_CREATE(self, line):
        self.do_create(line)
    def do_create(self, line):
        print rpcshell.shell(self.connargs, "assoc" , "create " + line)
    def do_BUILD(self, line):
        self.do_build(line)
    def do_build(self, line):
        varlist=self.eval_var(line)
        for var in varlist:
            line=line.replace("$"+var,self.replace_var(var))
        line = self.mock_serverparser(line) 
        rpcshell.shell(self.connargs, "assoc" , "build " + line)

    def do_ask(self, line):
        if "about" in line:
            stoplist=["where","for","top","bottom"]
            stopPoslist=[ len(line) if line.find(stopstr)==-1 else line.find(stopstr) for stopstr in stoplist ]
            about_str_origin=line[line.find("about")+5:min(stopPoslist)]
            about_str_origin=about_str_origin.strip(" ()")
            about_str=self.replace_var(about_str_origin)
            line=line.replace(about_str_origin, about_str)

        rpcshell.shell(self.connargs, "assoc","ask "+line)

    def do_query(self, line):
        strEnd=len(line) if line.find(" from")==-1 else line.find(" from")
        query_str_origin=line[line.find("query ") + 1 : strEnd]
        query_str=self.replace_var(query_str_origin)
        line= query_str+line[strEnd:]
        #print globals()
        #if line.find('$') != -1:
        #       var_va = line[line.find('$') + 1:line.find(' ',line.find('$'))]
        #       line = line.replace("$"+var_va , str(globals()[var_va])[1:-1])
        #       #print line
        rpcshell.shell(self.connargs, "assoc" , "query " + line)
    #def do_set(self, line):
    #       if line[:9] == "algorithm":
    #               if line[10:] in associateCmd.algorithm_set:
    #                       self.algorithm = line[10:]
    #                       print "algorithm : " + self.algorithm

    def do_SETPROMPT(self, line):
        self.prompt = line
    def do_setprompt(self, line):
        self.prompt = line

    def do_BOURL(self,line):
        self.do_bourl(line)
    def do_bourl(self,line):
        if self.bosrv_url != line:
            url_object = urlparse(line)
            self.bosrv_url=line
            self.connargs["origin"] = line
            self.connargs["token"] = url_object.password if url_object.password !=None else self.connargs["token"]
            self.connargs["host"] = url_object.hostname if url_object.hostname !=None else self.connargs["host"]
            self.connargs["port"] = url_object.port if url_object.port !=None else self.connargs["port"]

    def do_USE(self,line):
        self.do_use(line)
    def do_use(self,line):

        cmdSplits=line.split()
        if cmdSplits[0] != "workspace":
            print "usage: use workspace <workspace_name>"
            return
        wsStr=cmdSplits[1]
        if wsStr=="default" or wsStr=="":
            self.connargs["workspace"]=""
        else:
            self.connargs["workspace"]=wsStr
            sqlStr="create workspace "+wsStr
            rpcshell.shell(self.connargs,"sql",sqlStr)
        print "switch to workspace:" +str(wsStr)


    def do_INFO(self, line):
        self.do_info(line)
    def do_info(self, line):
        print "host : " + self.connargs["host"]
        print "port : " + str(self.connargs["port"])
        print "timeout : " + str(self.connargs["timeout"])
        #print "algorithm : " + self.algorithm

    def do_SHOW(self,line):
        self.do_show(line)

    def do_show(self, line):
        print boshCmd.getinfo(self.connargs, "show {0}".format(line) , "" )

    def do_DESC(self, line):
        self.do_desc(line)
    def do_desc(self, line):
        if line[:12] == "association ":
            print boshCmd.getinfo(self.connargs, "desc association" , line[12:])
        #elif line[:7] == "matrix ":
        #       print boshCmd.getinfo(self.host, self.port ,self.token, "get_mbt_info" , line[7:], self.timeout)
        elif line != "":
            print boshCmd.getinfo(self.connargs, "desc" , line)
        else:
            print "desc [association] <name>"

    #def do_list(self, line):
    #       name = line.split()
    #       #print name[0] + "   " + name[1]
    #       rpcshell.shell(self.host, self.port ,self.token, "la" , "create tree listattribute from " + name[0] + " group by " + name[1], self.timeout)
    #       rpcshell.shell(self.host, self.port ,self.token, "la" , "select distinct # from listattribute", self.timeout)

    #def do_analyze(self, line):
    #       if line != "":
    #               if line.startswith('distinct'):
    #                       print rpcshell.shell(self.host, self.port ,self.token, "la" , "select " + line, self.timeout)
    #               else:
    #                       print rpcshell.shell(self.host, self.port ,self.token, "sql" , "select " + line, self.timeout)
    #def do_get(self, line):
    #       if line != "":
    #               if line.startswith('distinct'):
    #                       print rpcshell.shell(self.host, self.port ,self.token, "la" , "select " + line, self.timeout)
    #               else:
    #                       print rpcshell.shell(self.host, self.port ,self.token, "sql" , "select " + line, self.timeout)

    ########################################################
    # add get / catch(find) / drop for testing
    ########################################################
    def do_FIND(self,line):
        self.do_find(line)
    def do_find(self, line):
            varlist=self.eval_var(line)
            for var in varlist:
                line=line.replace("$"+var,self.replace_var(var))
            line = self.mock_serverparser(line) 
            rpcshell.shell(self.connargs, "assoc" , "find " + line)

    def do_SET(self,line):
        self.do_set(line)
    def do_set(self,line):
        boshCmd.setinfo(self.connargs, "set", line)
    
    def do_GET(self,line):
        self.do_get(line)
    def do_get(self, line):
        varlist=self.eval_var(line)
        for var in varlist:
              line=line.replace("$"+var,self.replace_var(var))
        rpcshell.shell(self.connargs, "assoc" , "get " + line)
    
    def do_DROP(self,line):
        self.do_drop(line)
    def do_drop(self, line):
        rpcshell.shell(self.connargs, "assoc" , "drop " + line)
    ########################################################

    def do_EXIT(self, line):
        return True
    def do_exit(self, line):
        return True
    def do_QUIT(self, line):
        return True
    def do_quit(self, line):
        return True
    def emptyline(self):
        pass

    def do_SQL(self, line):
        self.do_sql(line)
    def do_sql(self, line):
        if line != "":
            print "perform sql command : " + line
            rpcshell.shell(self.connargs, "sql" , line)
        else:
            newcmd = sqlCmd()
            newcmd.connargs = self.connargs
            newcmd.prompt = self.prompt[:len(self.prompt)-1] + ":*sql>"
            newcmd.draw_texttable()
            newcmd.cmdloop()

    def do_ADMIN(self, line):
        self.do_admin(line)
    def do_admin(self, line):
        newcmd = baseCmd()
        newcmd.connargs = self.connargs
        newcmd.prompt = self.prompt[:len(self.prompt)-1] + ":admin>"
        newcmd.cmdloop()

    def do_PRINT(self,line):
        self.do_print(line)
    def do_print(self,line):
        command=line.split(">>")
        if len(command)==2:
            doInvoke=False
            outfile=str()
            if "@" in command[1]:
                outfile=command[1][command[1].find("@")+1:].strip()
                if len(outfile)==0:
                    return "*** FILENAME required after \">>@\""
                doInvoke=True
            else:
                outfile=command[1].strip()
            outfile=tools.redirectFiles(globals()[command[0].strip()],outfile)
            if outfile=="BADINPUT":
                return "*** cancel outputting the file"
            if doInvoke:
                tools.invokeFiles(outfile)

        else:
            try:
                exec("print "+line) in globals()
            except:
                traceback.print_exc()


    def writehist(self):
        try:
            import readline
            readline.set_history_length(80)
            readline.write_history_file()
        except ImportError:
            try:
                import pyreadline as readline
                readline.set_history_length(80)
                readline.write_history_file()
            except ImportError:
                pass

    def get_bosh_global_var_with_filter(self):
        f = ['re', 'readline', 'd_pass', 'cmd', 'getpass', 'rpcshell', 'd_port', 'tools', 'dbinput', 'd_host', 'csvloader', 'load_database_url', 'main', 'sys', 'd_db', 'sqlCmd', 'texttable', 'baseCmd', 'associateCmd', 'traceback', 'urlparse', 'd_user', 'os', 'd_type', 'db_access_str', 'boshCmd']
        return [v for v in globals().keys() if not v.startswith('_') and not v in f]

    def eval_var( self, cmd_str, lead_char = "\$"):
        pattern = lead_char + "(\w+)"
        return re.findall ( pattern ,cmd_str )
 
  
    def cond_parser(self,ori_str,kwlist,delimiter="or"):
        stackdict=self.stack_parser(ori_str)
        cond_list=list();
        if(len(stackdict)!=0):
            cond_key=max(stackdict,key=int)
            cond_list=stackdict[cond_key]
        else:
            cond_list=[ori_str]
        new_str=ori_str
        
        for cond_str in cond_list:
            tmp_str=self.replace_cond(cond_str,kwlist,delimiter=delimiter)
            new_str=new_str.replace(cond_str,tmp_str)

        return new_str


    def mock_serverparser(self,cmd_str,filter_keyword="filter",start_char=":",end_char=";"):
        if filter_keyword in cmd_str:
           start = cmd_str.find( start_char, cmd_str.find( filter_keyword ) )
           end = cmd_str.find( end_char, start )
           cond_stmt = cmd_str[start+len( start_char ):end]
           stackdict=self.stack_parser(cond_stmt)
           if(len(stackdict)!=0):
               cond_list=stackdict[max(stackdict,key=int)]
           else:
               cond_list=[cond_stmt]
           final_str=cmd_str
           for cond_str in cond_list:
              tmp_str=self.cmd_parser(cond_str,[" AND "," and "," OR "," or "],delimiter="or")
              final_str=final_str.replace(cond_str,tmp_str)
           return final_str
        else:
           return cmd_str
           
    def cmd_parser(self,cond_str,kwlist,delimiter="or"):
        pattern="|".join(kwlist)
        atomcond_list=re.split(pattern,cond_str)
        new_str=cond_str
        for atomcond_str in atomcond_list:
            atompattern="|".join(["=","\\bin\\b"])
            tmp_split=re.split(atompattern,atomcond_str)
            if len(tmp_split)>=2:
                prefixStr=tmp_split[0]+"="
                varStr=tmp_split[1]
                tmp_str=self.var_parser(varStr,prefix=prefixStr,joinstr=delimiter)
                new_str=new_str.replace(atomcond_str,tmp_str)
                
        return new_str


              
    def var_parser(self,ori_str,prefix="",joinstr=","):
        joinstr=" "+joinstr+" "
        split_temp = re.split(r'[,]', ori_str)
        result_list=list()
        replace_list=list()
        for split_value in split_temp:
            split_value=split_value.strip()
            if split_value!="": result_list.append(split_value)
        new_str=joinstr.join(prefix+str(element)+" " for element in result_list)
        quote=str()
        if len(replace_list)>0 :
            if isinstance(replace_list[0],basestring):
                quote="'"
        new_str+=joinstr.join(" "+prefix+quote+str(element)+quote for element in replace_list)

        return new_str

  



    def replace_cond(self,cond_str,kwlist,delimiter="or"):
        pattern="|".join(kwlist)
        atomcond_list=re.split(pattern,cond_str)
        new_str=cond_str
        for atomcond_str in atomcond_list:
            atompattern="|".join(["=","\\bin\\b"])
            tmp_split=re.split(atompattern,atomcond_str)
            if len(tmp_split)>=2:
                prefixStr=tmp_split[0]+"="
                varStr=tmp_split[1]
                tmp_str=self.replace_var(varStr,prefix=prefixStr,joinstr=delimiter)
                new_str=new_str.replace(atomcond_str,tmp_str)
            elif len(tmp_split)==1:
                varStr=tmp_split[0]
                tmp_str=self.replace_var(varStr,prefix="",joinstr=",")
                new_str=new_str.replace(atomcond_str,tmp_str)
                
        return new_str


    

    def stack_parser(self,ori_str):
        stackdict=dict();
        stack=[];
        for i, char in enumerate(ori_str):
            if char=="(":
                stack.append(i)
            elif char==")":
                start=stack.pop()
                depth=len(stack)
                token=ori_str[start+1:i]
                if depth not in stackdict:
                    stackdict[depth]=[]
                stackdict[depth].append(token)
        return stackdict

    def replace_var(self,ori_str,prefix="",joinstr=","):
        joinstr=" "+joinstr+" "
        split_temp = re.split(r'[,]', ori_str)
        result_list=list()
        replace_list=list()
        for split_value in split_temp:
            split_value=split_value.strip()
            if split_value=="":continue
            if split_value in self.get_bosh_global_var_with_filter():
                if  hasattr(globals()[split_value], '__iter__'):
                    replace_list.extend(globals()[split_value])
                else:
                    replace_list.append(globals()[split_value])

            else:
                result_list.append(split_value)
        new_str=joinstr.join(prefix+str(element)+" " for element in result_list)
        quote=str()
        if len(replace_list)>0 :
            if isinstance(replace_list[0],basestring):
                quote="'"
        new_str+=joinstr.join(" "+prefix+quote+str(element)+quote for element in replace_list)

        return new_str



    def help_column(self):
        print "\tex. b=column 1 in a \n\tb=column 2,4 in a"
    def help_row(self):
        print "\tex. b=row 1 in a \n\tb=row 2,4 in a"
    def help_sql(self):
        print "\trun star-sql shell"
    def help_admin(self):
        print "\trun admin shell"
    #def help_get(self):
    #       print "\t An alias of analyze"

    def help_find(self):
        tools.print_help_string('assoc_find')
    #def help_analyze(self):
    #       tools.print_help_string('assoc_analyze')
    def help_create(self):
        tools.print_help_string('assoc_associate')
    def help_query(self):
        tools.print_help_string('assoc_query')
    def help_show(self):
        print "\tlist resource in the shell\n\tex. show [tables | association ]"
    def help_desc(self):
        print "\tshow meta-information of a resource\n\tex. desc [association] <name>"

class sqlCmd(cmd.Cmd):
    SELECTword = [ 'from', 'by', 'group by' , 'where' , 'sum' , 'count' , 'distinct' ]
    def complete_select(self, text, line, begidx, endidx):
        if not text:
            completions = self.SELECTword[:]
        else:
            completions = [ f
            for f in self.SELECTword
            if f.startswith(text)
            ]
        return completions
    CREATEword = [ 'from', 'by', 'group by' , 'where' , 'tree' , 'table' , 'fact' , 'dim']
    def complete_create(self, text, line, begidx, endidx):
        if not text:
            completions = self.CREATEword[:]
        else:
            completions = [ f
            for f in self.CREATEword
            if f.startswith(text)
            ]
        return completions

    def draw_texttable(self):
        table = texttable.Texttable()
        table.set_cols_align(["l"])
        table.set_cols_valign(["b"])
        table.add_rows([ ["Welcome to Star-SQL"],
                ["Star-SQL is a small subset of SQL for datasets in star schema or snowflake schema.\nIt is aimed to address analytic problems rather than transactional problems.\nType \"help\" for more information."],
                ["Type \"enableColor\" if your terminal support ANSI escape code."],
                ["Draw charts in Excel or HTML files! Type \"help syntaxout\" for examples."]
         ])
        print table.draw() + "\n"

    def emptyline(self):
        pass

    def do_SHOW(self, line):
        self.do_show(line)
    def do_show(self, line):
        if line == "tables" or line == "TABLES":
            print boshCmd.getinfo(self.connargs, "show tables" , "")
        else:
            print "list tables: 'show tables'"

    #def do_starschema(self, line):
    #    if line != "":
    #        print boshCmd.getinfo(self.connargs, "starschema" , line)

    def do_desc(self, line):
        if line != "":
            print boshCmd.getinfo(self.connargs, "desc" , line)

    def do_settimeout(self, line):
        if line != "":
            self.connargs["timeout"] = line
    def do_info(self, line):
        print "host : " + self.connargs["host"]
        print "port : " + str(self.connargs["port"])
        print "timeout : " + str(self.connargs["timeout"])

    def do_SELECT(self, line):
        self.do_select(line)
    def do_select(self, line):
        if line != "":
            if line.startswith('distinct'):
                print rpcshell.shell(self.connargs, "la" , "select " + line)
            else:
                print rpcshell.shell(self.connargs, "sql" , "select " + line)
    def do_CREATE(self,line):
        self.do_create(line)
    def do_create(self, line):
        if line != "":
            if line.startswith('tree') or line.startswith('fulltree'):
                print rpcshell.shell(self.connargs, "la" , "create " + line)
            else:
                print rpcshell.shell(self.connargs, "sql" , "create " + line)

    def do_INSERT(self, line):
        self.do_insert(line)
    def do_insert(self, line):
        if line != "":
            print rpcshell.shell(self.connargs, "sql" , "insert " + line)

    def do_UPDATE(self, line):
        self.do_update(line)
    def do_update(self, line):
        if line != "":
            print rpcshell.shell(self.connargs, "sql" , "update " + line)

    def do_DROP(self, line):
        self.do_drop(line)
    def do_drop(self, line):
        if line != "":
            print rpcshell.shell(self.connargs, "sql" , "drop " + line)

    def do_COPY(self, line):
        self.do_copy(line)
    def do_copy(self, line):
        db_url = os.environ.get('DATABASE_URL')
        db_access_str = load_database_url(db_url)

        if line != "":
            if line.find("DATABASE") != -1 and db_access_str != "":
                line = line.replace("DATABASE" , db_access_str)
                #print "line: " + line
            elif line.find("DATABASE") != -1 and db_access_str == "":
                print "input your database information"
                db_access_str = dbinput()
                line = line.replace("DATABASE" , db_access_str)
            print rpcshell.shell(self.connargs, "sql" ,"copy " + line)

    def do_LOAD(self, line):
        self.do_load(line)
    def do_load(self, line):
        db_url = os.environ.get('DATABASE_URL')
        db_access_str = load_database_url(db_url)

        if line != "":
            if line.find("DATABASE") != -1 and db_access_str != "":
                line = line.replace("DATABASE" , db_access_str)
                #print "line: " + line
            elif line.find("DATABASE") != -1 and db_access_str == "":
                print "input your database information"
                db_access_str = dbinput()
                line = line.replace("DATABASE" , db_access_str)
            print rpcshell.shell(self.connargs, "sql" ,"load " + line)
    def do_EXIT(self, line):
        return True
    def do_exit(self, line):
        return True
    def do_QUIT(self, line):
        return True
    def do_quit(self, line):
        return True

    def do_disableColor(self, line):
        tools.docSql.disableColor()

    def do_enableColor(self, line):
        tools.docSql.enableColor()
    def help_select(self):
        tools.print_help_string('sql_select')

    def help_create(self):
        tools.print_help_string('sql_create')

    def help_insert(self):
        tools.print_help_string('sql_insert')

    def help_update(self):
        tools.print_help_string('sql_update')

    def help_desc(self):
        #print "\tlist table's attribute\n\tdesc <table name>"
        tools.print_help_string('sql_desc')
    def help_show(self):
        #print "\tlist all BigObject tables in workspace\n\tshow tables"
        tools.print_help_string('sql_show')
    #def help_starschema(self):
        #print "\tshow table's metainfo including related tables\n\tstarschema <table name>"
    #   tools.print_help_string('sql_starschema')
    def help_copy(self):
        tools.print_help_string('sql_copy')

    def help_load(self):
        tools.print_help_string('sql_load')

    def help_syntaxout(self):
        tools.print_help_string('sql_syntaxout')


def main():
    host = "localhost"
    port = "9090"
    token = ""
    bo_url = os.environ.get('BIGOBJECT_URL')
    if bo_url != None:
        url_object = urlparse(bo_url)
        token = url_object.password
        host = url_object.hostname
        port = url_object.port
    else:
        bo_url="bo://localhost:9090"    

    newcmd = associateCmd()
    newcmd.bosrv_url = bo_url
    newcmd.connargs={}
    newcmd.connargs["host"] = host
    newcmd.connargs["port"] = port
    newcmd.connargs["token"] = token
    newcmd.connargs["timeout"] = 9999
    newcmd.connargs["workspace"]= ""
    newcmd.connargs["opts"]=""
    newcmd.connargs["origin"]=bo_url
    newcmd.prompt = "bosh>"
    newcmd.intro = "\nWelcome to the BigObject shell\n\nenter 'help' for listing commands\nenter 'quit'/'exit' to exit bosh"

    try:
        newcmd.cmdloop()
    except KeyboardInterrupt:
        print "exiting by KeyboardInterrupt"
        newcmd.writehist()
    print "Thanks for using bosh..."

if __name__ == '__main__':
    main()
