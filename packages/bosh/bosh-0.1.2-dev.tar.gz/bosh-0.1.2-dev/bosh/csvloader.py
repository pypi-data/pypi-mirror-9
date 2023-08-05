'''
Created on Sep 9, 2014

@author: eugene
'''
import sys
from bosrv.request import connect
from exc.ttypes import *
import traceback
import sys

def dequote(s):
    if (s[0] == s[-1]) and s[0] == '\"':
	s = replaceSingleQuote(s)
        return "\'" + s[1:-1].replace("\",\"" , "\',\'") + "\'"
    return s

def addSingleQuote(s):
	s = replaceSingleQuote(s)
	return "\'" + s.replace("," , "\',\'") + "\'"

def replaceSingleQuote(s):
	return s.replace("'","%27")

def replaceSymbol(itemlist):
       newlist=[];
       # try:
       #       teststr=unicode(itemlist).encode("utf-8")
       # except:
       #       print itemlist
       # return
       for item in itemlist:
            item=item.strip().strip("'")
            item=item.replace("'","%27")
            item=item.replace("\\","%5C")
        #    try:
        #       item=unicode(item).encode("utf-8")
        #    except:
        #       print item
        #       sys.exit(0)   
            newlist.append(item)
       return newlist


def printLine(csv_file):
        try:
           f=open(csv_file,'rU')
        except:
           return

	import csv
        reader=csv.reader(f)
        for line in reader:
              newline=replaceSymbol(line)
    #          print newline
              if(newline=="FALSE"):return

        f.close() 

def csvload(connargs, csv_file, bt_name ,insert_line=30000 ):
	errorfile = open('errorinsert.txt', 'w')

	addr_info= "bo://:" + connargs["token"] + "@" + connargs["host"] + ":" + str(connargs["port"])
	import time
	now = time.time()
	with connect(addr_info, False, None) as conn:
    		token, cli = conn
   
		try:		
			f = open(csv_file,'rU')
		except IOError:
        		print 'cannot open file'
			return
		except:
			return

		print ('open ' + csv_file + ' insert to ' + bt_name)
		insert_prefix = 'INSERT INTO ' + bt_name + " VALUES "
		line_count = 0
	    
#		first_line = f.readline()
#		check_double_qoute = first_line.count('\"') 
#		check_comma = first_line.count(',')
	   
#		remove_double_quote = False
#		if(check_double_qoute >= 2*check_comma):
#			remove_double_quote = True
#			print ("Double quoted csv file")

#		f.seek(0)
                import csv
                reader=csv.reader(f)		
		data_str = ""
                animate={1:"|",2:"/",3:"-",0:"\\"}
		for line in reader:
			line_count += 1
	                	
#			if (remove_double_quote == False):
#				data_str += "(" + addSingleQuote(line.rstrip()) + ")"
#			else:
#				data_str += "(" + dequote(line.rstrip()) + ")"
#		
                        
                        data_str += "('"+"','".join(replaceSymbol(line))+"')"
          		if (line_count % insert_line) == 0 and line_count != 1:
				try:
					cli.sql_execute(token,insert_prefix + data_str , connargs["workspace"],connargs["opts"])
				except:
					traceback.print_exc()
		   			print "Unexpected error:" + str(sys.exc_info()[0])
					print line_count	
					errorfile.write(data_str)
					errorfile.write('\n=========================================\n')
				data_str = ""
			else:
				data_str += ","
                        sys.stdout.write('\r')
                        animate_token=animate[line_count%4]
                        sys.stdout.write(animate_token+" processing: "+str(line_count)+" lines")			
                        sys.stdout.flush()

		if (line_count % insert_line) != 0:
			try:
				cli.sql_execute(token,insert_prefix + data_str[:len(data_str)-1] , connargs["workspace"],connargs["opts"])
			except:
				traceback.print_exc()
	   			print "Unexpected error:" + str(sys.exc_info()[0])

		f.close()
		end = time.time()
                
		return '\ninsertion done. total %i rows , time: %ss' %  (line_count, round((end - now),2))
	return

if __name__ == '__main__':

	if(len(sys.argv) < 6):
                if(sys.argv[1]):
                      printLine(sys.argv[1])
                      exit()
		print ("csvloader.py <host> <port> <token> <csv filename> <bigtable name>")
		exit()
        

	testing_csvload(sys.argv[1], sys.argv[2] , sys.argv[3], sys.argv[4], sys.argv[5])
	print ("test done.")
