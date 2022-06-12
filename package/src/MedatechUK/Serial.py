import json , uuid , os
from base64 import b64encode
from http.client import HTTPSConnection
import xmltodict , dicttoxml
from xml.dom.minidom import parseString
from datetime import datetime
import pyodbc
import re

from MedatechUK.oDataConfig import Config
from MedatechUK.mLog import mLog
from MedatechUK.apy import Response

#region "Form Class"
class SerialF :

    #region Properties
    @property
    def fname(self):    
        return self._fname
    @fname.setter
    def fname(self, value):
        self._fname = value

    @property
    def rt(self):    
        return str(self._rt)
    @rt.setter
    def rt(self, value):
        self._rt = value

    @property
    def typename(self):    
        return str(self._typename)
    @typename.setter
    def typename(self, value):
        self._typename = value

    @property
    def bubbleid(self):    
        return str(self._bubbleid)

    #endregion

    #region "ctor"
    def __init__(self, **kwargs):
        self.fname = ''
        self.rt = 1
        self._bubbleid = uuid.uuid4()
        self.typename = ""

        for arg in kwargs.keys():    
            if ( hasattr( self , arg ) ):
                setattr( self , arg , kwargs[arg] )   
    
    #endregion

#endregion

#region "Type Class"
class SerialT :
    
    #region Propereties
    @property
    def pType(self):    
        return self._pType
    @pType.setter
    def pType(self, value):
        self._pType = value

    @property
    def Len(self):    
        return self._Len
    @Len.setter
    def Len(self, value):
        self._Len = value

    @property
    def pCol(self):    
        return self._pCol
    @pCol.setter
    def pCol(self, value):
        self._pCol = value

    #endregion

    #region "ctor"
    def __init__(self, this, att , **kwargs):
        
        self.pCol = att
        self.pType = 'CHAR'
        self.Len = 40
        
        for arg in kwargs.keys():    
            if ( hasattr( self , arg ) ):
                setattr( self , arg , kwargs[arg] )              

        if (att=="rt"):
            self.pCol="RECORDTYPE" 
            self.pType="CHAR"
        
        if (att=="bubbleid"):
            self.pCol="BUBBLEID" 
            self.pType="CHAR"
        
        if (att=="typename"):
            self.pCol="TYPENAME" 
            self.pType="CHAR"
            self.len = 3

        this.props[att] = self
    
    #endregion

    #region "Methods"
    def oData(self, this):
        return {
            'CHAR': chr(34) + self.pCol + chr(34) + " : " + chr(34) + str(this) + chr(34) ,
            'INT': chr(34) + self.pCol + chr(34) + " : " + str(this) ,
            'REAL': chr(34) + self.pCol + chr(34) + " : " + str(this) ,
        }.get(self._pType.upper(), chr(34) + self.pCol + chr(34) + " : " + chr(34) + str(this) + chr(34))

    def SQLColumn(self, this):
        return self.pCol.upper()

    def SQLValue(self, this):
        return {
            'CHAR': chr(39) + str(this) + chr(39) ,
            'INT':  str(this) ,
            'REAL': str(this) ,
        }.get(self._pType.upper(), chr(39) + str(this) + chr(39))

    def XML(self, this):
        return "<" + self._pCol + ">" + str(this) + "</" + self._pCol + ">"

    #endregion

#endregion 

#region "Base Class"

class SerialBase :

    #region Properies
    @property
    def props(self):    
        return self._props
    @props.setter
    def props(self, value):
        self._props = value

    #endregion

    #region "ctor"
    def __init__(self, form , **kwargs):
        self.form = form
        self.props = {}
        self.log = mLog() 
        self.ret = {}  

        #region Create instance from input
        for arg in kwargs.keys():  
            if arg.upper() == '_XML':   
                self.log.logger.debug("Create instance from [{}] file {}".format(arg.upper().lstrip("_") , kwargs[arg].name))
                t = xmltodict.parse(
                    kwargs[arg].read(),
                    dict_constructor=dict
                )
                self = self.__init__(**json.loads(json.dumps(t[list(t)[0]]))) #

            elif arg.upper() == '_SQL':                                   
                self.log.logger.debug("Create instance from [{}] procedure {}".format(arg.upper().lstrip("_") , kwargs['_sql']['proc']))
                self = self.__init__(
                    **json.loads(
                        json.dumps(
                            self.fromSQL(
                                kwargs['_sql']['config'] , 
                                kwargs['_sql']['proc'] , 
                                **kwargs['_sql']['kwargs'] 
                            )                    
                        )
                    )
                ) #

            elif arg.upper() == '_JSON':
                self.log.logger.debug("Create instance from [{}] file {}".format(arg.upper().lstrip("_") , kwargs[arg].name))
                self = self.__init__(**json.loads(kwargs[arg].read()))
        
        #endregion

        #region Set Attributes
            elif ( hasattr( self , arg ) ) :
                try:
                    setattr( self , arg , kwargs[arg] )
                except:
                    pass
            elif ( hasattr( self , arg.lstrip('@') ) ) :
                try:
                    setattr( self , arg.lstrip('@') , kwargs[arg] )
                except e:
                    print(e)

        #endregion

    def fromSQL(self, config, endpoint, **kwargs):
        try:
            self.log.logger.debug("Opening DB query: [{}] in [{}].".format( endpoint , config.environment ))
            cnxn = pyodbc.connect("Driver={SQL Server Native Client 11.0};DATABASE=system;" + config.connstr )
            crsr = cnxn.cursor() 
            sql = ["select SO.OBJECT_ID as [ObjectID], " , 
                "SCHEMA_NAME(SCHEMA_ID) + '.' + SO.name AS [ObjectName] " ,
                "From sys.objects AS SO " ,
                "INNER JOIN sys.parameters AS P " ,
                "On SO.OBJECT_ID = P.OBJECT_ID " ,
                "WHERE 0=0 " ,
                "And SO.TYPE IN ('P') " ,
                "And (TYPE_NAME(P.user_type_id)='xml') " ,
                "And (LOWER(SO.name)=LOWER('"+ endpoint +"')) " ,
                "And P.is_output=1 "]
                
            crsr.execute(
                ('\n'.join(sql))
            )

            row = crsr.fetchone()       
            if row != None :                           
                sql = ["SELECT	" ,
                "	P.name AS [ParameterName],	" ,
                "	TYPE_NAME(P.user_type_id) AS [ParameterDataType] " ,
                "FROM sys.objects AS SO	" ,
                "	INNER JOIN sys.parameters AS P 	" ,
                "	ON SO.OBJECT_ID = P.OBJECT_ID	" ,
                "WHERE 0=0	" ,
                "	And SO.OBJECT_ID = "+ str(row.ObjectID) ,
                "	And P.is_output=0" ,
                "order by parameter_id"
                ]
                crsr.execute(    
                    '\n'.join(sql)
                )
                ObjectName = row.ObjectName
                par = []
                for row in crsr.fetchall() :
                    if not kwargs.__contains__(row.ParameterName[1:]) and not row.ParameterName[1:] == "ENV":
                        raise NameError("Missing parameter {}".format(row.ParameterName[1:]))
                    
                    if row.ParameterDataType in ["nchar", "nvarchar", "ntext"]:
                        if row.ParameterName[1:].upper() == "ENV":
                            par.append("N'{}'".format(config.environment))                            
                        else:
                            par.append("N'{}'".format(kwargs[(row.ParameterName[1:])]))
                    
                    elif row.ParameterDataType in ["char", "varchar", "text"]:
                        if row.ParameterName[1:].upper() == "ENV":
                            par.append("'{}'".format(config.environment))
                        else:                            
                            par.append("'{}'".format(kwargs[(row.ParameterName[1:])]))
                    
                    else:                      
                        par.append("{}".format( kwargs[(row.ParameterName[1:],"0")]))
                
                par.append("@Output_XML OUT ")

                sql = [
                    "DECLARE  @Output_XML xml ",
                    "EXEC {} {}".format(ObjectName , ", ".join(par)) ,                    
                    "SELECT @Output_XML"
                ]
                crsr.execute("\n".join(sql))
                
                row = crsr.fetchone()
                ret = xmltodict.parse(row[0])    
                return ret[list(xmltodict.parse(row[0]))[0]]

            else:
                raise NameError("Invalid SQL Procedure {}".format(endpoint))
        
        except Exception as e:
            raise e
        
    #endregion

    #region "Output Methods"

    def toFile(self, fn , method, **kwargs):
        self.log.logger.debug("Writing file [{}] {}".format( fn , method(**kwargs)))
        with open(fn, 'w') as the_file:            
            the_file.write(method(**kwargs)) 

    #region "Built in toFile() methods"

    def toXML(self , this = 0, root="root"):         
        ret = ""  
        l = 0     
        if (this==0):            
            l = 1
            this = self
            ret += "<{}>".format(root) 

        if isinstance(this, list):            
            for i in this:
                ret += "{}{}{}".format(
                    "<{}>".format( 
                        type(i).__name__ 
                    ) ,
                    self.toXML(i) ,
                    "</{}>".format( 
                        type(i).__name__ 
                    )
                )
        else:
            for p in range(3):
                for key in [key for key in this.__dict__ if key not in ["_props","form","log","ret"]]:  
                    if isinstance(this.__dict__[key], list) and p==2:      
                        ret += self.toXML(this.__dict__[key])

                    elif hasattr(getattr(this , key), "props") and p==1:
                        if(hasattr(this,"props")):                            
                            ret += "{}{}{}".format(
                                "<{}>".format( 
                                    key.lstrip('_') 
                                ) , 
                                self.toXML(this.__dict__[key]) , 
                                "</{}>".format( 
                                    key.lstrip('_') 
                                ) 
                            )
                        
                    elif p==0:
                        if(hasattr(this,"props")) and this.props.__contains__(key.lstrip('_')):
                            ret += "{}{}{}".format(
                                "<{}>".format(
                                    key.lstrip('_') 
                                ) ,
                                str(this.__dict__[key]) ,
                                "</{}>".format(
                                    key.lstrip('_')
                                )
                            )
                
        if(l!=0):
            ret += "</{}>".format( root ) 
            return parseString(ret).toprettyxml()            
        
        else:
            return ret

    def toJSON(self):        
        return json.dumps(self, default=lambda o: {
            key.lstrip('_'): 
            value for key, value in o.__dict__.items() if not key in ["_props" , "form" , "log" , "ret"]
            }, 
                sort_keys=False, 
                indent=4
        )   

    #endregion
  
    def toPri(self, config, method, **kwargs):            
        
        ## This function will PATCH a completion request ONLY
        ## if the fornname of the upper level is 'ZODA_TRANS'

        # Set the response object
        if kwargs.__contains__("request"):
            # The call contains a request - populate it's response
            ret = kwargs["request"].response
        elif kwargs.__contains__("response"):
            # The call contains a response - populate directly
            ret = kwargs["response"]
            
        url = '/odata/priority/{}/{}/{}'.format(config.tabulaini , config.environment , "ZODA_TRANS")
        headers= { 
                'Authorization' : 'Basic %s' %  b64encode(bytearray(config.ouser + ":" + config.opass,'ascii')).decode("ascii") ,
                'Content-Type': 'application/json',
                "User-Agent": "MedatechUK Python Client",
            }
        data = json.loads(method())
        self.log.logger.debug("POSTing to [{}{}] ".format( config.oDataHost, url ))                 
        self.log.logger.debug("Headers:\n{}".format( json.dumps(headers ,  indent = 4) ))
        self.log.logger.debug("Data:\n{}".format( json.dumps(data, indent = 4) ))        

        r = HTTPSConnection(config.oDataHost)  
        r.request( 
            'POST', 
            url , 
            json.dumps(data),
            headers,              
        )
        res = r.getresponse()             
        if res.status == 201: # Created
            self.log.logger.debug("[{}] OK".format( res.status ))

            # If we're using the oData loading form, send a PATCH
            # to identify that all data has been sent.
            if self.form.fname != 'ZODA_TRANS':
                self.log.logger.debug("[{}] {}".format( res.status , res.reason ))
                ret.Status = res.status
                ret.Message = res.reason
                ret.data = json.load(res)
                self.log.logger.debug("Result: {}".format( json.dumps(ret.data  , indent = 4 )))

            else:
                data = json.loads(res.read())    

                patch = {}
                patch['COMPLETE'] = "Y"

                r.request( 
                    'PATCH', 
                    url + "(BUBBLEID='"+ data['BUBBLEID'] + "',LOADTYPE=" + str(data['LOADTYPE']) + ")", 
                    headers=headers, 
                    body=json.dumps(patch) 
                )
                
                self.log.logger.debug("PATCHing to [{}] ... ".format( url + "(BUBBLEID='"+ data['BUBBLEID'] + "',LOADTYPE=" + str(data['LOADTYPE']) + ")" ))  
                res = r.getresponse()

                if res.status != 200: # PATCHed
                    self.log.logger.critical("[{}] Fail: {}".format( res.status , res.reason ))
                    ret.Status = res.status   
                    ret.Message = "PATCH Failed: " + res.reason  
                    
                    # If the response is text, create a response with the text         
                    if res.getheader("Content-Type","").find("text/plain") > -1:                             
                        er = str(res.read().decode('utf-8'))
                        ret.data = {"error": er }     
                        self.log.logger.critical("{}".format( er ))              

                    elif res.getheader("Content-Type","").find("text/html") > -1:
                            ret.data = {"error": "Priority service not responding." }     
                            self.log.logger.critical("{}".format( "Priority service not responding." ))   

                    else:
                        # Create reponse from json 
                        ret.data = json.load(res)  
                        self.log.logger.critical( "{}".format( json.dumps(ret.data , indent = 4 ) ) )

                else:
                    ## Sucsess!
                    self.log.logger.debug("[{}] {}".format( res.status , res.reason ))
                    ret.Status = res.status
                    ret.Message = res.reason
                    ret.data = json.load(res)
                    self.log.logger.debug("Result: {}".format( json.dumps(ret.data , indent = 4 ) ))

        else:   
            ret.Status = res.status
            ret.Message = "POST Failed: " + res.reason   
            self.log.logger.critical( "[{}] Fail: {}".format( res.status , res.reason ) )            

            # If the response is text, create a response with the text         
            if res.getheader("Content-Type","").find("text/plain") > -1:                             
                er = str(res.read().decode('utf-8'))
                ret.data = {"error": er }     
                self.log.logger.critical("{}".format( er ))              

            elif res.getheader("Content-Type","").find("text/html") > -1:
                    ret.data = {"error": "Priority service not responding." }     
                    self.log.logger.critical("{}".format( "Priority service not responding." ))   

            else:
                # Create reponse from json 
                ret.data = json.load(res)  
                self.log.logger.critical( "{}".format( json.dumps(ret.data  , indent = 4 ) ) )
    
    #region "Built in toPri() oData methods"

    def toOdata(self , this = 0):         
        ret = ""  
        l = 0     
        if (this==0):            
            l = 1
            this = self
            ret +=("{ ") 

        if isinstance(this, list):
            ret +=("[ ")
            for i in this:
                ret +=("{ ")
                ret +=self.toOdata(i)
                ret +=(" }")
                if(this[-1]!=i):
                    ret += (" , ")
            ret +=(" ]")
            
        else:
            f = 0
            for key in this.__dict__ :  
                if (key != "_props" and key !="form"and key !="log"):
                    if isinstance(this.__dict__[key], list):      
                        ret += ' , ' +chr(34)+ (this.__dict__[key][-1].form.fname) +chr(34)+ ' : '
                        ret += self.toOdata(this.__dict__[key])
                    
                    else:
                        if(hasattr(this,"props")) :
                            if(f==0):
                                f = 1
                            else :
                                ret +=(", ")
                            ret +=(this.props[key.lstrip('_')].oData(this.__dict__[key]))        

            # Iterate through readonly properties
            for key in this.props:
                if (key != "rt" and key !="bubbleid" and key !="typename"):
                    if not this.__dict__.__contains__("_" + key):
                        if(f==0):
                            f = 1
                        else :
                            ret +=(", ")
                        ret +=(this.props[key.lstrip('_')].oData(getattr(this, key)))   

        if(l!=0):
            ret += " }"

        return ret

    def toFlatOdata(self , this = 0): 
    
        ## Returns the object as oData commands for flat loading     
        ret = ""  
        l = 0     
        if (this==0):            
            l = 1
            this = self
            ret +=("{ ")             
            ret +=(this.props["bubbleid"].oData(this.form.bubbleid) )  + ", "            
            ret +=(this.props["typename"].oData(this.form.typename) )  + ", " + chr(34) + "ZODA_LOAD_SUBFORM" + chr(34) + " : ["            

        if isinstance(this, list):            
            for i in this:                               
                ret += self.toFlatOdata(i)                              
                if(this[-1]!=i) and ret[len(ret)-4:] != " } ,":
                    ret += (" } ,")

        else:
            f = 0
            ret += " { "
            if(this.props.__contains__("rt")) :
                if(f==0): 
                    f = 1
                else :
                    ret +=(", ")
                ret +=(this.props["rt"].oData(this.form.rt) ) 
            
            # Iterate through readonly properties
            for key in [key for key in this.props if key not in ["rt","bubbleid","bubbleid","typename"]]:
                if not this.__dict__.__contains__("_" + key):
                    if(f==0):
                        f = 1
                    else :
                        ret +=(", ")
                    ret +=(this.props[key.lstrip('_')].oData(getattr(this, key))) 

            for p in range(3):
                for key in [key for key in this.__dict__ if key not in ["_props","form","log","ret"]]:                
                    if isinstance(this.__dict__[key], list) and p==2:      
                        if ret[len(ret)-4:] != " } ,":
                            ret+=" } ,"
                        ret += self.toFlatOdata(this.__dict__[key])                            

                    elif hasattr(getattr(this , key), "props") and p==1:
                        if ret[len(ret)-4:] != " } ,":
                            ret+=" } ,"
                        ret += self.toFlatOdata(this.__dict__[key])
                        
                    elif p==0:
                        if(hasattr(this,"props")) and this.props.__contains__(key.lstrip('_')):
                            if(f==0):
                                f = 1
                            else :
                                ret +=(", ")
                            ret +=(this.props[key.lstrip('_')].oData(this.__dict__[key]))                                                 
            
        if(l!=0):
            if ret[len(ret)-4:] == " } ,":
                ret=ret[0:len(ret)-4]  
            
            ret += " } ] }"

        return ret    

    #endregion

    def toSQL(self , this = 0):        

        ## Returns the object as SQL commands 
         
        names = {}
        l = 0     
        if (this==0):     
            self.ret = {}       
            l = 1
            this = self            
        
            names[len(names)] = ({"name" : "BUBBLEID", "value" : this.props["bubbleid"].SQLValue(this.form.bubbleid)})
            names[len(names)] = (
                {
                    "name" : "LOADTYPE", 
                    "value" : "( select TYPE from ZODAT_TYPE where TYPENAME = {} )".format(
                        this.props["typename"].SQLValue(this.form.typename)
                    )
                }
            )
            names[len(names)] = (
                {
                    "name" : "LINE", 
                    "value" : "( SELECT MAX(LINE)+1 FROM ZODAT_TRANS )"
                }
            )
            
            self.ret[len(self.ret)] = names
            self.ret[len(self.ret)-1]["TABLE"] = this.form.fname
            names = {}
        
        names[len(names)] = (
            {
                "name" : "PARENT", 
                "value" : "( SELECT LINE FROM ZODAT_TRANS WHERE BUBBLEID = {})".format(
                    self.ret[0][0].get("value")
                )                 
            }
        )
        names[len(names)] = (
            {
                "name" : "LINE", 
                "value" : "{}".format(str(len(self.ret)))
            }
        )        

        if isinstance(this, list):            
            for i in this:      
                if len(names) > 2:  
                    self.ret[len(self.ret)] = names 
                    self.ret[len(self.ret)-1]["TABLE"] = i.form.fname   
                    names = {}                   
                self.toSQL(i)                              

        else:                        
            names[len(names)] = ({"name" : "RECORDTYPE", "value" : this.props["rt"].SQLValue(this.form.rt)})                 
            
            # Iterate through readonly properties
            for key in this.props:
                if (key != "rt" and key !="bubbleid" and key !="typename"):
                    if not this.__dict__.__contains__("_" + key):                                              
                        names[len(names)] = (
                            {
                                "name" : this.props[key.lstrip('_')].SQLColumn(getattr(this, key)), 
                                "value" : this.props[key.lstrip('_')].SQLValue(getattr(this, key)) 
                            }
                        )        

            for p in range(3):
                for key in this.__dict__ :                      
                    if (key != "_props" and key !="form" and key !="log"):
                        # print("{} {}".format(p,key))

                        if isinstance(this.__dict__[key], list) and p==2: 
                            if len(names) > 2:  
                                self.ret[len(self.ret)] = names
                                self.ret[len(self.ret)-1]["TABLE"] = this.form.fname
                                names = {}
                            self.toSQL(this.__dict__[key])                   

                        elif hasattr(getattr(this , key), "props") and p==1:
                            if len(names) > 2:
                                self.ret[len(self.ret)] = names
                                self.ret[len(self.ret)-1]["TABLE"] = this.form.fornname
                                names = {}
                            self.toSQL(this.__dict__[key])  
                            
                        elif p==0:
                            if(hasattr(this,"props")) and this.props.__contains__(key.lstrip('_')):
                                names[len(names)] = (
                                    {
                                        "name" : this.props[key.lstrip('_')].SQLColumn(this.__dict__[key]), 
                                        "value" : this.props[key.lstrip('_')].SQLValue(this.__dict__[key]) 
                                    }
                                )                                                      

            if len(names) > 2:
                self.ret[len(self.ret)] = names
                self.ret[len(self.ret)-1]["TABLE"] = this.form.fname
                names = {}

        if (l!=0):   
            if len(self.ret) >2 :
                self.ret[1]["TABLE"] = self.ret[2]["TABLE"]

            ins = ""
            ins += "if exists(select TYPE from ZODAT_TYPE where TYPENAME = {})\nbegin\n".format(this.props["typename"].SQLValue(this.form.typename))
            ins += "\tset identity_insert ZODAT_TRANS  on\n" 
            for e in range(len(self.ret)) :                
                ins += "\tINSERT INTO {} ( ".format(self.ret[e]["TABLE"])                 
                
                for f in range(len(self.ret[e])-1) : 
                    try:
                        a = self.ret[e][f]["name"]
                        if f==0:
                            ins += "{}".format( self.ret[e][f].get("name") ) 
                        else:
                            ins += ", {}".format( self.ret[e][f].get("name") ) 
                    except:
                        pass

                ins += " ) VALUES ( "                
                for f in range(len(self.ret[e])-1) : 
                    try:
                        a = self.ret[e][f]["name"]
                        if f==0:
                            ins += "{}".format( self.ret[e][f].get("value") ) 
                        else:
                            ins += ", {}".format( self.ret[e][f].get("value") ) 
                    except:
                        pass               

                ins += " )\n" 
            
            d = datetime.now()
            ins += "\tUPDATE ZODAT_TRANS SET COMPLETE = 'Y' , COMPLETEDATE = {} WHERE BUBBLEID = {}\n".format(                              
                int(
                    (datetime(
                        d.year, 
                        d.month, 
                        d.day, 
                        d.hour, 
                        d.minute) 
                    - datetime(1988, 1, 1)).total_seconds() / 60
                ) ,
                self.ret[0][0].get("value")
            )
            ins += "\tset identity_insert ZODAT_TRANS  off\n"
            ins += "end"
            return ins

    #region "Built in toSQL() methods"

    def toPriSQL(self, config, method, **kwargs):

        # Set the response object
        if kwargs.__contains__("request"):
            # The call contains a request - populate it's response
            ret = kwargs["request"].response
        elif kwargs.__contains__("response"):
            # The call contains a response - populate directly
            ret = kwargs["response"]
                 
        # Environment Check
        if not config.CheckEnviroment():
            self.log.logger.critical("Bad environment [{}].".format( config.environment ))
            ret.Status = 400
            ret.Message = "Invalid company."
            ret.data = {"error" : "Company [" + config.environment + "] not found."}          

        else:
            ## Environment OK            
            try:
                cnxn = config.cnxn()

            except Exception as e:                
                ret.Status = 500
                ret.Message = "SQL Error" 
                ret.data = {"error" : str(e) }          
            
            try:
                crsr = cnxn.cursor() 
                self.log.logger.debug("use {}; {}".format(config.environment , method()))
                crsr.execute(
                    "use {}; {}".format(config.environment , method())
                )                         
                
                ret.Status = 200
                ret.Message = "OK"
                ret.data = {"error" : "No errors found" }          

            except Exception as e:
                self.log.logger.critical("TSQL Error: {}".format( str(e) ))
                ret.Status = 400
                ret.Message = "SQL Error" 
                ret.data = {"error" : str(e) }  

    #endregion      
    
    def toURL(self, url, method, **kwargs): 

        # Set the response object
        if kwargs.__contains__("request"):
            # The call contains a request - populate it's response
            ret = kwargs["request"].response
        elif kwargs.__contains__("response"):
            # The call contains a response - populate directly
            ret = kwargs["response"]
        else:
            ret = Response()

        verb = "POST"
        if kwargs.__contains__("method"):
            verb = kwargs("method")

        host = url.split("://")[1].split("/")[0]
        url = url.split(host)[1]

        headers = {}
        headers["User-Agent"] = "MedatechUK Python Client"
        if not kwargs.__contains__("Content-Type"):
            headers["Content-Type"] = "application/json"
        else:
            headers["Content-Type"] = kwargs["Content-Type"]

        if kwargs.__contains__("user") and kwargs.__contains__("passw"):
            headers["Authorization"] = 'Basic %s' %  b64encode(bytearray(kwargs["user"] + ":" + kwargs["passw"],'ascii')).decode("ascii")

        self.log.logger.debug("POSTing to [{}{}] ".format( host, url ))                 
        self.log.logger.debug("Headers:\n{}".format( json.dumps(headers ,  indent = 4) ))
        self.log.logger.debug("Data:\n{}".format( method() ))   

        r = HTTPSConnection(host)  
        r.request( 
            verb.upper(), 
            url , 
            method(),
            headers,              
        )
        res = r.getresponse()       

        if str(res.status)[0] == "2": # OK
            self.log.logger.debug("[{}] {}".format( res.status , res.reason ))
            ret.Status = res.status
            ret.Message = res.reason
            ret.data = json.load(res)
            self.log.logger.debug("Result: {}".format( json.dumps(ret.data  , indent = 4 )))
            
        else:   
            ret.Status = res.status
            ret.Message = "POST Failed: " + res.reason   
            self.log.logger.critical( "[{}] Fail: {}".format( res.status , res.reason ) )            

            # If the response is text, create a response with the text         
            if res.getheader("Content-Type","").find("text/plain") > -1:                             
                er = str(res.read().decode('utf-8'))
                ret.data = {"error": er }     
                self.log.logger.critical("{}".format( er ))              

            elif res.getheader("Content-Type","").find("text/html") > -1:
                    ret.data = {"error": "Priority service not responding." }     
                    self.log.logger.critical("{}".format( "Priority service not responding." ))   

            else:
                # Create reponse from json 
                ret.data = json.load(res)  
                self.log.logger.critical( "{}".format( json.dumps(ret.data  , indent = 4 ) ) )
    
    #endregion

#endregion

#region infer object from file
class infer():

    #region "Ctor"
    def __init__(self, data, **kwargs):

        rt=0
        self.mycls = {}
        self.mylen = {}
        self.cls = []        
        self.imp = []
        self.preq = []

        self.recurse(data, kwargs['name'])

        self.imp.append("import json")
        self.imp.append("from MedatechUK.Serial import SerialBase , SerialT , SerialF")			
        self.imp.append("from MedatechUK.mLog import mLog")

        for k in self.mycls.keys():
            rt += 1
            baseclass = ("class {}(SerialBase) :\n".format(k))		
            props = []
            ctr = []
            met = []

            if rt==1:
                met.append("    SerialT(self, \"rt\")")
                met.append("    SerialT(self, \"bubbleid\")")
                met.append("    SerialT(self, \"typename\")")
                baseinit = "    SerialBase.__init__(self , SerialF(fname=\"ZODA_TRANS\", rt={}, typename=\"ORD\"), **kwargs)  ".format(rt)

                self.preq = [                    
                    "def ProcessRequest(request) :" ,
                    "    log = mLog()" ,
                    "    try:" ,
                    "        q = {}(**request.data) ".format(k) ,
                    "        q.toPri(" ,
                    "            Config(" ,
                    "                env=request.environment , " ,
                    "                path=os.getcwd()" ,
                    "            ) , " ,
                    "            q.toFlatOdata, " ,
                    "            request=request ",
                    "        )        ",
                    "    ",
                    "    except Exception as e:",
                    "        log.logger.critical(str(e))",
                    "        exc_type, exc_obj, exc_tb = sys.exc_info()",
                    "        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]",
                    "        request.response.Status = 500" ,
                    "        request.response.Message = \"Internal Server Error\"" ,
                    "        request.response.data ={ \"error\" :",
                    "            {",
                    "                \"type\": exc_type,",
                    "                \"message\": str(e),",
                    "                \"script\": fname,",
                    "                \"line\": exc_tb.tb_lineno",
                    "            }",
                    "        } ",
                    ""
                ]

            else:
                met.append("    SerialT(self, \"rt\")")
                baseinit = "    SerialBase.__init__(self , SerialF(fname=\"ZODA_LOAD\", rt={}), **kwargs)  ".format(rt)
            
            xi = 0
            xr = 0 
            xt = 0

            for e, j in enumerate(self.mycls[k],1):

                if isinstance(self.mycls[k][j], list):
                    prop = [
                        "    ",
                        "@property" ,
                        "def {}(self):".format(j) ,
                        "    return self._{}".format(j) ,
                        "@{}.setter".format(j) ,
                        "def {}(self, value):".format(j) , 
                        "    self._{} = [] ".format(j) ,
                        "    if isinstance(value, list):",
                        "        for i in range(len(value)):",
                        "            self._{}.append({}(**value[i]))".format(j,j),
                        "    else:",
                        "        self._{}.append({}(**value))".format(j,j),
                        ""
                    ]                
                    ctr.append("    self.{} = []".format(j))

                elif self.mycls[k][j][0] == "$":
                    prop = [
                        "    ",
                        "@property" ,
                        "def {}(self):".format(j) ,
                        "   return self._{} ".format(j) ,
                        "@{}.setter".format(j),
                        "def {}(self, value):".format(j),
                        "   self._{} = {}(**value)".format(j,j),
                        ""
                    ]
                    ctr.append("    self.{} = {}{}".format(j , "{" , "}"))				

                else:
                    prop = [
                        "    ",
                        "@property" ,
                        "def {}(self):".format(j) ,
                        "   return self._{} ".format(j) ,
                        "@{}.setter".format(j),
                        "def {}(self, value):".format(j),
                        "   self._{} = value".format(j),
                        ""
                    ]				
                    if self.mycls[k][j] == 'INT':
                        xi+=1
                        met.append("    SerialT(self, \"{}\" , pCol=\"{}{}\" , pType=\"INT\")".format(j,self.mycls[k][j],xi))
                        ctr.append("    self.{} = 0".format(j))

                    elif self.mycls[k][j] == 'REAL':
                        xr+=1
                        met.append("    SerialT(self, \"{}\" , pCol=\"{}{}\" , pType=\"REAL\")".format(j,self.mycls[k][j],xr))
                        ctr.append("    self.{} = 0.0".format(j))

                    else :
                        xt +=1
                        met.append("    SerialT(self, \"{}\" , pCol=\"{}{}\" , Len={} , pType=\"CHAR\")".format(j,self.mycls[k][j],xt,self.mylen[k][j]))
                        ctr.append("    self.{} = \"\"".format(j))

                props.append("\n    ".join(prop))

            ctor = [
                "    #region \"ctor\"",
                "def __init__(self,  **kwargs): ",
                "",
                "    #region \"Property defaults\"" ,
                "{}".format("\n    ".join(ctr)), 
                "",
                "    #endregion",
                "",                    
                "    #region \"Set Meta info\"",
                baseinit,
                "{}".format("\n    ".join(met)),   
                "",
                "    #endregion",
                "",
                "#endregion"			
            ]   

            self.cls.append(baseclass)		
            self.cls.append("    #region Properties")   
            self.cls.append("".join(props))
            self.cls.append("    #endregion\n")            
            self.cls.append("\n    ".join(ctor))
            self.cls.append("")                        

    #endregion

    #region Methods    
    def isINT(self,Value):
        if isinstance(Value,int):
            return True
        else:
            return not re.fullmatch("[0-9]+", str(Value)) == None

    def isREAL(self,Value):        
        return not re.fullmatch("[0-9]+\.[0-9]+", str(Value)) == None

    def rowType(self,NewValue, OldType=None):	
        if OldType==None:
            if self.isREAL(NewValue):
                ret = "REAL"
            elif self.isINT(NewValue):
                if len(str(NewValue))> 5:
                    ret = "TEXT"
                else:
                    ret = "INT"		
            else:
                ret = "TEXT"
        else:
            if OldType in ["INT","REAL"] and not (self.isINT(NewValue) or self.isREAL(str(NewValue))):
                ret = "TEXT"
            elif OldType in ["INT"] and self.isREAL(str(NewValue)):
                ret = "REAL"		
            else:
                ret = OldType

        return ret

    def recurse(self ,data, name):
        if not isinstance(data, dict):
            pass      

        else:
            for k in data.keys(): 
                # print(k , data[k] )
                if isinstance(data[k], list):
                    if not name in list(self.mycls.keys()):
                        self.mycls[name] = {}
                        self.mylen[name] = {}

                    self.mycls[name][k] = []
                    self.mylen[name][k] = []

                    for l in data[k]:
                        self.recurse(l, k)
                
                elif hasattr(data[k], "keys"):
                    if not name in list(self.mycls.keys()):
                        self.mycls[name] = {}		
                        self.mylen[name] = {}
                    self.mycls[name][k] = "$"

                    if not k in list(self.mycls.keys()):
                        self.mycls[k] = {}		
                        self.mylen[k] = {}		

                    for i in data[k].keys():
                        if hasattr(data[k][i], "keys"):
                            self.mycls[k][i] = "$"
                            self.recurse(data[k][i], i)
                        else:    
                            self.mycls[k][i] = self.rowType(data[k][i])                        
                            self.mylen[k][i] = len(str(data[k][i]))

                else:
                    if not name in list(self.mycls.keys()):
                        self.mycls[name] = {}
                        self.mylen[name] = {}
                    
                    if not k in list(self.mycls[name]):
                        self.mycls[name][k] = self.rowType(data[k])
                        self.mylen[name][k] = len(str(data[k]))

                    else:
                        self.mycls[name][k] = self.rowType(data[k] , self.mycls[name][k])
                        if len(data[k]) > self.mylen[name][k]:
                            self.mylen[name][k] = len(str(data[k]))

    #endregion

#endregion