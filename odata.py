######################################################
## si@medatechuk.com
## 14/08/21
##
## Create a new load object
## request = POST   ) Either
## f = file         ) Or
## o = object       ) Or
## env = company    MANDATORY is file or Object
## c = config       MANDATORY: created if missing 
## ltype = LoadType MANDATORY: the type of loading
## ex = exclude     Exlude namespaces from parse
## 
## Usage:
## l = Load(
##     ltype = "TST",
##     f = sys.argv[1], ## First param on command line
##     c = sys.argv[2] ## Second param on command line    
## )  
## l.save('odata.json') ## Save to file
## l.post() ## Post to Priority
##
## Constants.py:
##  oDataHost ="walrus.ntsa.uk"
##  tabulaini ="tabula.ini"
##  ouser ="apiuser"
##  opass ="123456"
##  Environment = "wlnd"

from datetime import datetime
import sys
import json
from types import SimpleNamespace
import os
import os.path
import uuid
from http.client import HTTPSConnection
from base64 import b64encode
import inspect

from MedatechUK.oDataConfig import Config
import MedatechUK.PriDate

class oRecord:
    ## Ctor
    def __init__(self , recordtype , line):

        ## Set Default Property values
        self.recordtype = recordtype
        self.line = line
        ## An arraty of Name/Value pairs for Properties in this record
        self.oProps = [] 

class oProp:
    ## Ctor
    def __init__(self , name , value):
        
        ## Set Default Property values
        self.name = name
        self.value = value

class Rec:    
    ## Ctor
    def __init__(self , rt, name):
        
        ## Set Default Property values
        self.rt = rt ## The record type
        self.name = name ## The record name
        self.props = [] ## The array or propeerties in this Record Type

        # Init NEXT values for each Priority type
        self.text = 0
        self.real = 0
        self.int = 0
        self.bool = 0
    
    ## Methods called by child props for NEXT type
    def nexttext(self):
        self.text = self.text + 1
        return str(self.text)
    def nextreal(self):
        self.real = self.real + 1
        return str(self.real)
    def nextint(self):
        self.int = self.int + 1
        return str(self.int)
    def nextbool(self):
        self.bool = self.bool + 1
        return str(self.bool)

class Prop:   

    ## Ctor
    def __init__(self , property , type , parent):
        
        ## Set Default Property values
        self.property = property
        self.type = 'unknown'
        
        ## Use existing type if parent record already 
        ## contains this property.
        if not len(parent.props) == 0:
            for n in parent.props:
                if n.property == property:
                    self.type = n.type
                    return ## quit __init__

        ## It's a new property in the the record.
        ## Call the records NEXT function for the 
        ## next type number.
        if type == float:
            self.type = "REAL" + parent.nextreal()
        elif type == str:            
            self.type = "TEXT" + parent.nexttext()
        elif type == int:            
            self.type = "INT" + parent.nextint()
        elif type == datetime:            
            self.type = "INT" + parent.nextint()            
        elif type == bool:
            self.type = "CHAR" + parent.nextbool()           
        else:
            print("Warning! Unknown type: " + type)            

class Load:    

    ## Ctor
    def __init__(self, **kwargs): 
        
        ## Set Default Property values       
        self.line = 1
        self.records = [] ## Holds Record type data        
        self.odata = [] ## Holds the oData records
        self.config = {} ## Hold the configuration
        self.data = {} ## Hold the oData Commands
        self.patch = {} ## Hold the oData PATCH Commands
        self.BubbleID = str(uuid.uuid4()) ## The transaction identifier
        self.json = {} # The json data from file/object
        self.ex = {} # The excluded namespaces / columns
        self.path = ""

        ## Determine data source
        for arg in kwargs.keys():

            ## The excluded namespaces / columns
            if arg =='ex' :
                self.ex = kwargs[arg]

            ## Data from request
            if arg == 'request' :                  
                ## print("Opening from [{}] Request to [{}] ...".format(kwargs[arg].content_type , kwargs[arg].endpoint))
                try:                                               
                    # print(kwargs[arg].config.ouser)
                    #print(kwargs[arg].data)
                    self.path = kwargs[arg].path
                    self.json = json.loads(json.dumps(kwargs[arg].data), object_hook=lambda d: SimpleNamespace(**d))    
                    #print(self.json)                                                        
                    self.oDataHost = kwargs[arg].config.oDataHost
                    self.url = '/odata/priority/{}/{}/ZODA_TRANS'.format(kwargs[arg].config.tabulaini , kwargs[arg].config.environment)
                    self.headers = { 
                        'Authorization' : 'Basic %s' %  b64encode(bytearray(kwargs[arg].config.ouser + ":" + kwargs[arg].config.opass,'ascii')).decode("ascii") ,
                        'Content-Type': 'application/json',
                        "User-Agent": "MedatechUK Python Client",
                    }

                except Exception as e :                        
                    kwargs[arg].Response.Status = 500
                    kwargs[arg].Response.Message = "Bad Config: " + str(e)

            ## The environment is specified
            if arg == 'env' : 
                
                ## Locate the root folder
                previous_frame = inspect.currentframe().f_back
                (filename, line_number, function_name, lines, index) = inspect.getframeinfo(previous_frame)
                self.path = path=os.path.dirname(filename)
                c = Config(env=kwargs[arg],path=self.path)               
                self.oDataHost = c.oDataHost
                self.url = '/odata/priority/{}/{}/ZODA_TRANS'.format(c.tabulaini , c.environment)
                self.headers = { 
                    'Authorization' : 'Basic %s' %  b64encode(bytearray(c.ouser + ":" + c.opass,'ascii')).decode("ascii") ,
                    'Content-Type': 'application/json',
                    "User-Agent": "MedatechUK Python Client",
                }  
        
        for arg in kwargs.keys():
            ## Data from file
            if arg == 'f' :                 
                try:
                    # print("Opening from file: [{}] ... ".format(kwargs[arg]))
                    with open(self.path + "\\" + kwargs[arg], "r") as o:   
                        self.json = json.loads(o.read(), object_hook=lambda d: SimpleNamespace(**d)) 

                except Exception as e :                        
                    kwargs[arg].Response.Status = 500
                    kwargs[arg].Response.Message = "Bad Config: " + str(e)

            ## Data from object
            if arg == 'o' :  
                try:               
                    # print("Opening from object ... ")
                    self.json = json.loads(kwargs[arg].read(), object_hook=lambda d: SimpleNamespace(**d))    

                except Exception as e :                        
                    kwargs[arg].Response.Status = 500
                    kwargs[arg].Response.Message = "Bad Config: " + str(e)

        ## Recurse through data to create config        
        self.makeConfig(self.json, 'root')           
        
        ## Write config (if missing)
        self.writeConfig(kwargs['c'])      
                
        ## Load the config
        with open(self.path + "\\" + kwargs['c'], "r") as f:            
            self.config = json.loads(f.read(), object_hook=lambda d: SimpleNamespace(**d))   
                
        ## print("Parsing object ... ")        
        self.parse(self.json, 'root')
        
        ## Build POST request body
        self.data['TYPENAME'] = kwargs['ltype']
        self.data['BUBBLEID'] = self.BubbleID
        self.data['ZODA_LOAD_SUBFORM'] = []
        for r in self.odata:        
            self.data['ZODA_LOAD_SUBFORM'].append({})
            self.data['ZODA_LOAD_SUBFORM'][-1]['RECORDTYPE'] = str(r.recordtype)
            for p in r.oProps:
                self.data['ZODA_LOAD_SUBFORM'][-1][p.name] = p.value  
        
        ## Build PATCH request body  
        self.patch['COMPLETE'] = "Y"

    ##                
    ## Add a path to the loading
    def Add(self , path):
        thisrt = 0
        for r in self.records:

            if r.rt > thisrt:
                ## Count RTs
                thisrt = r.rt
            
            if r.name == path:
                ## Found record type, return
                return r

        ## Record Type not found: Add.
        self.records.append( Rec( thisrt + 1 , path) )
        return self.records[-1]

    ## Return the RecordType of a path
    def rt(self, path):
        for r in self.records: 
            if r.name == path:
                return r.rt
        return -1

    ## Return the property
    def prop(self, rt, name, v):
        for property, value in vars(self.config.config.row).items():            
            if int(property) == int(rt):                
                for source, dest in vars(value).items():
                    if source == name:
                        return oProp(dest , v)

    ## Recurse json to create config data
    def makeConfig(self, x, path): 
        #print(x)       
        rt = []    
        try:
            for property, value in vars(x).items():  
                # Excluded?
                if not property in self.ex:             
                    # If it's not a namespace or list      
                    if type(value) is not SimpleNamespace and type(value) is not list:
                        # Add the column at this location
                        if MedatechUK.PriDate.isDate(value):
                            # If the value is a date then initialise with data value
                            self.Add(path).props.append(Prop(property , type(datetime.now()), self.Add(path)))                
                        else:
                            self.Add(path).props.append(Prop(property , type(value), self.Add(path)))                    

            for property, value in vars(x).items(): 
                # Excluded?
                if not property in self.ex:            
                    th = path + "." + property           
                    # IS it a namespace? 
                    if type(value) is SimpleNamespace:              
                        if th not in rt:
                            rt.append(th)            
                        self.makeConfig(value, th)
                    
            for property, value in vars(x).items():       
                # Excluded?
                if not property in self.ex:
                    th = path + "." + property  
                    # IS it a List?
                    if type(value) is list:
                        for i in value:             
                            if th not in rt:
                                rt.append(th)                                           
                            self.makeConfig(i, th) 
        except Exception as e:
            #print(x)
            self.Add(path).props.append(Prop("TEXT1" , type("TEXT1"), self.Add(path)))   

    ## Write the config file
    def writeConfig(self , fn):
    
        ## Does the config file already exist?
        if not os.path.isfile(fn):
    
            ## Create the config file
            ## print("Creating config [{}] ... ".format(fn))
            rw = {}
            rw['config'] = {}
            rw['config']['rt'] = {}
            rw['config']['row'] = {}    
            for r in self.records:
                rw['config']['rt'][r.rt] = r.name
                rw['config']['row'][r.rt] = {}
                for p in r.props:
                    rw['config']['row'][r.rt][p.property] = p.type
                
                with open(fn, 'w') as f:
                    json.dump(rw, f)                     

    def configRows(self , path):
        for property, value in vars(self.config).items():              
            for property, value in vars(value).items():
                if property == 'row':
                    for ROWID, value in vars(value).items():
                        if int(ROWID) == int(self.rt(path)):
                            return value

    ## Parse the data using the config
    def parse(self , x , path):

        rt = []
        addline = False

        for p, v in vars(x).items():    
            ## Not namespace or list - a column    
            if type(v) is not SimpleNamespace and type(v) is not list and not p in self.ex:
                if not addline:
                    ## Create new oRecord in the oData, if one doesn't exist
                    addline = True
                    self.odata.append(oRecord(self.rt(path) , self.line))            

                for property, value in vars(self.configRows(path)).items():
                    if property == p:                   
                        if value[0:3] == "INT" and MedatechUK.PriDate.isDate(v):                            
                            self.odata[-1].oProps.append(oProp(value, MedatechUK.PriDate.IntDate(v)))
                        elif value[0:4] == "CHAR":
                            if v:
                                self.odata[-1].oProps.append(oProp(value,"Y"))
                            else:
                                self.odata[-1].oProps.append(oProp(value,"N"))
                        else:
                            self.odata[-1].oProps.append(oProp(value,v))
    
        if not p in self.ex:
            ## Increment line counter if it's a new line
            if addline:
                self.line += 1
                
        for property, value in vars(x).items():   
            # Excluded?
            if not property in self.ex:                       
                th = path + "." + property    
                # Am I a namespace?        
                if type(value) is SimpleNamespace:              
                    if th not in rt:
                        rt.append(th)            
                    self.parse(value, th)
                
        for property, value in vars(x).items():      
            # Excluded?
            if not property in self.ex:                 
                th = path + "." + property  
                # Am I a list?        
                if type(value) is list:
                    for i in value:             
                        if th not in rt:
                            rt.append(th)   
                        try:                 
                            test = vars(x).items()
                            self.parse(i, th)
                        except:       
                            self.odata.append(oRecord(self.rt(th) , self.line))                             
                            self.odata[-1].oProps.append(oProp("TEXT1", i ))        
                            self.line += 1                            
            
    ## Save the odata to a file
    def save(self , fn):
        ## print("Saving to [{}] ... ".format(fn))
        with open(fn, 'w') as f:
            json.dump(self.data, f)            

    ## Post to Priority
    def post(self, Response):
        ## print("POSTing to [{}] ... ".format(self.oDataHost))
        c = HTTPSConnection(self.oDataHost)   
        # print(self.url) 
        # print(self.headers)     
        # print(self.data)     
        c.request( 
            'POST', 
            self.url , 
            headers=self.headers, 
            body=json.dumps(self.data) 
        )
        res = c.getresponse()            
        if res.status == 201: # Created
            data = json.loads(res.read())             
            # print("PATCHing to [{}] ... ".format(self.oDataHost))                    
            c.request( 
                'PATCH', 
                self.url + "(BUBBLEID='"+ data['BUBBLEID'] + "',LOADTYPE=" + str(data['LOADTYPE']) + ")", 
                headers=self.headers, 
                body=json.dumps(self.patch) 
            )
            res = c.getresponse()
            if res.status != 200: # PATCHed
                Response.Status = res.status   
                Response.Message = "PATCH Failed: " + res.reason  
                # If the response is text, create a response with the text
                if res.getheader("Content-Type","").find("text/plain") > -1:                             
                    Response.data = {"error": str(res.read().decode('utf-8')) }                
                else: # Create reponse from json 
                    Response.data = json.load(res)

            else:
                ## Sucsess!
                Response.Status = 200
                Response.Message = "OK"
                Response.data = json.load(res)

        else:   
            Response.Status = res.status
            Response.Message = "POST Failed: " + res.reason   
            # If the response is text, create a response with the text         
            if res.getheader("Content-Type","").find("text/plain") > -1:                             
                Response.data = {"error": str(res.read().decode('utf-8')) }

            else: # Create reponse from json 
                Response.data = json.load(res)   

class oResponse:

    ## Ctor
    def __init__(self):
                  
        self.Status = 200         
        self.Message = "OK"                          
        self.data = {}