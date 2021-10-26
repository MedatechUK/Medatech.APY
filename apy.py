######################################################
## si@medatechuk.com
## 08/09/21
## 
## Usage:
## from apy import Request
## 
## request = Request()
## if request.method == "POST":
##    request.Response.data = request.data
## 
## if request.method == "GET":
##    request.Response.data = {"id": request.query("id","123")}
## 
## request.Response.Flush()

import os
import sys
import json
import importlib
import urllib.parse as urlparse
import xmltodict
import dicttoxml
import pyodbc
from MedatechUK.oDataConfig import Config
import MedatechUK.odata
import inspect

class Request:

    ## Ctor
    def __init__(self):
            
        ## Set Request defaults
        self.method = os.environ['REQUEST_METHOD'] 
        self.content_type = "application/json"         
        self.content_length = 0
        self.environment = self.query("environment","")
        self.endpoint = self.query("endpoint", "default.json")                                         
        self.ext = "json"
        self.data = {}                                                     
        self.config = {}
        self.serialtype = 'json'
                
        try :  
            ## Generate the resonse object
            self.Response = Response(self) 
            
            ## Locate the root folder
            previous_frame = inspect.currentframe().f_back
            (filename, line_number, function_name, lines, index) = inspect.getframeinfo(previous_frame)
            self.path = os.path.dirname(filename)

            ## Split the endpoint into endpoint and extention
            #   where the endpoint contains a period
            if self.endpoint.find(".") > 0:                                      
                self.ext = (self.endpoint.split(".")[-1]).lower()                 
                self.endpoint = self.endpoint[0:len(self.endpoint)-(len(self.ext)+1)] 
            
            ## Generate the config object
            self.config = Config(request=self)                         

        except Exception as e :
            ## Set the status/message of the response on error            
            self.Response.Status = 500
            self.Response.Message = "Internal Server Error"
            self.Response.data = {"error" : "Bad config: " + str(e)}

        if self.environment != "" and self.cont() :   
            ## Is it a valid environment?
            try:
                cnxn = pyodbc.connect("Driver={SQL Server Native Client 11.0};DATABASE=system;" + self.config.connstr )
                crsr = cnxn.cursor() 
                crsr.execute(
                    "select DNAME from ENVIRONMENT where DNAME <> '' union all select 'system'"
                )       
                f = False              
                for row in crsr.fetchall() :                
                    if row.DNAME.lower() == self.environment.lower() :
                        f = True
                        # Set the environment to the cAsE of the db object
                        self.environment = row.DNAME
                
                # Environment not found
                if not f:
                    self.Response.Status = 400
                    self.Response.Message = "Invalid company."
                    self.Response.data = {"error" : "Company [" + self.environment + "] not found."}   

            except Exception as e:
                self.Response.Status = 500
                self.Response.Message = "Internal Server Error"
                self.Response.data = {"error" : self.endpoint + '.' + self.ext + " threw an exception.", "dberror" : str(e)}  

        ## Set the Content-Type of the request
        #   for GET            
        if self.method == "GET" and self.cont() :                                
            #   Set the response content type based on the file extention    
            #   .xml / .ashx
            if self.ext == "xml" or self.ext == "ashx":
                self.content_type = "application/xml"

            #   .json / unknown enpoint file extention
            else:
                # Default
                self.content_type = "application/json"  

            ##  Import a script to handler the request
            #   Check file exists
            if os.path.isfile(self.endpoint + ".py"):
                # Import the handler
                handler = importlib.import_module(self.endpoint)
                # Process the request with the loaded handler
                handler.ProcessRequest(self)
            
            ## Load from database
            elif self.environment !="" :
                try:
                    cnxn = pyodbc.connect("Driver={SQL Server Native Client 11.0};DATABASE="+ self.environment +";" + self.config.connstr )
                    crsr = cnxn.cursor() 

                    crsr.execute(
                        "select SO.OBJECT_ID as [ObjectID], " +
                        "SCHEMA_NAME(SCHEMA_ID) + '.' + SO.name AS [ObjectName] " +
                        "From sys.objects AS SO " +
                        "INNER JOIN sys.parameters AS P " +
                        "On SO.OBJECT_ID = P.OBJECT_ID " +
                        "WHERE 0=0 " +
                        "And SO.TYPE IN ('FN') " +
                        "And (TYPE_NAME(P.user_type_id)='xml') " +
                        "And (LOWER(SO.name)=LOWER('"+ self.endpoint +"')) " +
                        "And P.is_output=1 "
                    )

                    row = crsr.fetchone()                   
                    sql = "SELECT " + row.ObjectName + " ("
                    crsr.execute(            
                        "SELECT	" +
                        "	P.name AS [ParameterName],	" +
                        "	TYPE_NAME(P.user_type_id) AS [ParameterDataType] " +
                        "FROM sys.objects AS SO	" +
                        "	INNER JOIN sys.parameters AS P 	" +
                        "	ON SO.OBJECT_ID = P.OBJECT_ID	" +
                        "WHERE 0=0	" +
                        "	And SO.OBJECT_ID = "+ str(row.ObjectID) +
                        "	And P.is_output=0" +
                        "order by parameter_id"
                    )
                                                        
                    for row in crsr.fetchall() :
                        if row.ParameterDataType in ["char", "varchar", "text", "nchar", "nvarchar", "ntext"]:
                            sql += "'" + self.query(row.ParameterName[1:],"") + "', "
                        else:
                            sql += self.query(row.ParameterName[1:],"0") + ", "
                    
                    sql = sql[0:len(sql)-2]                    
                    crsr.execute(sql + ')')
                    row = crsr.fetchone()
                    self.Response.data = xmltodict.parse(row[0])                
                
                except Exception as e:
                    self.Response.Status = 404
                    self.Response.Message = "Not found."
                    self.Response.data = {"error" : self.endpoint + '.' + self.ext + " not found.", "dberror" : str(e)}                       
            else:
                self.Response.Status = 404
                self.Response.Message = "Not found. here"
                self.Response.data = {"error" : self.endpoint + '.' + self.ext + " not found.", "dberror" : str(e)} 
                
        ##  Set the Content-Type of the request
        #   for POST            
        elif self.method == "POST" and self.cont() :                                        
            #   Set the response content type based on request content type
            self.content_Length = int(os.environ.get('CONTENT_LENGTH', '0'))             
            if self.content_Length > 0 :
                self.content_type = os.environ['HTTP_CONTENT_TYPE']                             

            #   Check for valid content type
            if self.content_type != "application/xml" and self.content_type != "application/json" :           
                self.content_type = "application/json"     
                self.Response.Status = 400
                self.Response.Message = "Bad Request"
                self.Response.data = {"error" : "Invalid Content type. Use application/xml or application/json"}            
                        
            ##  Deserialise to self.data if no previous error
            if self.cont() :                  
                try:                    
                    if self.content_Length > 0:
                        cl = self.content_Length
                        data = "" # sys.stdin.read(content_Length)   ## Easier, didn't work                 
                        while cl > 0:
                            o = sys.stdin.read(1)       
                            data += o
                            cl += -1                        
                            if "\\n" in ascii(o):    
                                ## Content length returns 2 chars (cr lf) for \n                      
                                #  BUT stdin reads BOTH characters as a single char
                                #  causing a buffer overrun.
                                #  This removes the extra characters.
                                cl += -1                        

                        if self.content_type=="application/json" :          
                            self.data = json.loads(data)
                            self.serialtype = 'json'

                        if self.content_type=="application/xml" :                         
                            self.data = xmltodict.parse(data)
                            self.serialtype = 'xml'

                except Exception as e:                    
                    # Invalid data
                    self.Response.Status = 400
                    self.Response.Message = "Invalid POST"
                    self.Response.data = {"error" : str(e)}
                
            ##  Inject a handler for the request
            #   if the handler exists.
            if self.cont() and os.path.isfile(self.endpoint + ".py"):
                try:
                    # Import the handler
                    handler = importlib.import_module(self.endpoint)
                    # Process the request with the loaded handler
                    handler.ProcessRequest(self)

                except Exception as e :
                    self.Response.Status = 500
                    self.Response.Message = "Injection Failure"
                    self.Response.data = {"error" : str(e), "handler": self.endpoint}

            elif self.cont() :
                try:                                
                    if self.content_Length > 0:                                                                      
                        # Create the oData Loading
                        l = MedatechUK.odata.Load(
                            # Load type is the endpoint extention
                            ltype = self.ext.upper(),
                            # Config file is the name of the endpoint
                            c = self.endpoint + '.' + self.serialtype + ".config",
                            # Pass this request for settings
                            request = self
                        )
                        ## POST the oData to Priority
                        l.post(self.Response)   

                except Exception as e :
                    self.Response.Status = 500
                    self.Response.Message = "Load Fail"
                    self.Response.data = {"error" : str(e)}

    # Get params from the query String
    def query(self, name , default):
        ret = ''
        for k in urlparse.parse_qs(os.environ["QUERY_STRING"]):                        
            if str(k).lower() == str(name).lower():                
                for i in range(len(urlparse.parse_qs(os.environ["QUERY_STRING"])[k])):
                    if len(ret) > 0:
                        ret += ","
                    ret += urlparse.parse_qs(os.environ["QUERY_STRING"])[k][i-1]
                    
        if len(ret) > 0:
            return ret
        else:
            return default  

    # Returns true is the response status is 2**
    def cont(self):
        return (self.Response.Status >= 200 and self.Response.Status <= 299)

class Response:

    ## Ctor
    def __init__(self, Request):
          
        self.request = Request
        self.Status = 200         
        self.Message = "OK"                          
        self.data = {}
    
    ## Flush method: Send response to the client
    def Flush(self):        

        ## redirecting?
        if self.Status == 302:
            print("HTTP/1.1 {} Found".format(str(self.Status)))
            print("Location: {}".format(self.Message))
            print("")

        else:
            ## Write Headers        
            self.ContentHeader()

            ## Write self.data to the response
            if self.request.content_type=="application/xml" :
                ## In XML                
                print(dicttoxml.dicttoxml(self.data).decode('utf-8'))

            else :
                ## In JSON
                print(json.dumps(self.data, indent=4))

        ## Write URL re-write data if debug = 1       
        if self.request.query("debug", "0") == "1":
            self.ContentHeader()

    def redirect(self, url):
        self.Status = 302
        self.Message = url

    ## Output internals as response headers for debugging
    def ContentHeader(self):

        ## Return the error code and message
        #  https://www.w3.org/Protocols/rfc2616/rfc2616-sec6.html
        print('HTTP/1.1 {} {}'.format(str(self.Status), self.Message))
        print("Content-Type: {}".format(self.request.content_type))

        try :
            ## Content header        
            print("Environment: {}".format(self.request.environment))
            print("Endpoint: {}".format(self.request.endpoint))
            print("Endpoint-Type.:{}".format(self.request.ext)  )          
            print("oDataHost: {}".format(self.request.config.oDataHost.split("//")[-1]))
            print("tabulaini: {}".format(self.request.config.tabulaini))
            print("db: {}".format(self.request.config.connstr))

        finally:
            print('')   
