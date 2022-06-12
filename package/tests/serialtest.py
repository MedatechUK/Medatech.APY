import json , uuid , os , sys

from datetime import datetime
from dateutil.parser import parse

from MedatechUK.Serial import SerialBase , SerialT , SerialF
from MedatechUK.mLog import mLog
from MedatechUK.apy import Response
from MedatechUK.oDataConfig import Config

#region "Custom Serialisation objects"

class order(SerialBase) :

    #region Properties
    @property
    def custname(self):    
        return self._custname
    @custname.setter
    def custname(self, value):
        self._custname = value

    @property
    def ordname(self):    
        return self._ordname
    @ordname.setter
    def ordname(self, value):
        self._ordname = value

    @property
    def orderitems(self):    
        return self._orderitems
    @orderitems.setter
    def orderitems(self, value):        
        self._orderitems = [] 
        if isinstance(value, list):
            for i in range(len(value)):            
                self._orderitems.append(orderitems(**value[i]))
        else:    
            self._orderitems.append(orderitems(**value)) 

    #endregion

    #region "ctor"
    def __init__(self,  **kwargs): 

        #region "Property defaults"
        self.custname = 0
        self.ordname = ""
        self.orderitems = []  

        #endregion  

        #region "Set Meta info"
        SerialBase.__init__(self , SerialF(fname="ZODAT_TRANS", rt=1, typename="ORD"), **kwargs)  
        SerialT(self, "rt")
        SerialT(self, "bubbleid")
        SerialT(self, "typename")
        SerialT(self, "custname" , pCol="TEXT1" , Len=20 , pType="CHAR")
        SerialT(self, "ordname" , pCol="TEXT2" , Len=20 , pType="CHAR")

        #endregion
    
    #endregion

class orderitems(SerialBase) :

    #region properties
    @property
    def partname(self):    
        return self._partname
    @partname.setter
    def partname(self, value):
        self._partname = value
                
    @property
    def qty(self):    
        return self._qty
    @qty.setter
    def qty(self, value):
        self._qty = value
                
    @property
    def duedate(self):  
        return self._duedate

    @duedate.setter
    def duedate(self, value):
        self._duedate = value    

    # Readonly calculated property
    @property
    def pridate(self):
        try :
            d = parse(self._duedate)    
            return int(
                (datetime(
                    d.year, 
                    d.month, 
                    d.day, 
                    d.hour, 
                    d.minute) 
                - datetime(1988, 1, 1)).total_seconds() / 60
            )     
        except:
            return 0        

    #endregion

    #region "ctor"
    def __init__(self,  **kwargs): 

        #region "Property defaults"
        self.partname = ''
        self.qty=0
        self.duedate = ''     
        
        #endregion

        #region "Set Meta info"
        SerialBase.__init__(self , SerialF(fname="ZODAT_LOAD", rt=2) , **kwargs)   
        SerialT(self, "rt")
        SerialT(self, "partname" , pCol="TEXT1" , Len=10 , pType="CHAR")
        SerialT(self, "qty" , pCol="REAL1" , pType="REAL")
        
        # pridate is a readonly function that converts the dudate to a Priority integer
        SerialT(self, "pridate" , pCol="INT2" , pType="INT")

        #endregion
    
    #endregion

def ProcessRequest(request) :
    log = mLog()
    try:
        q = order(**request.data)            
        q.toPri(
            Config(
                env=request.environment , 
                path=os.getcwd()
            ) , 
            q.toFlatOdata, 
            request=request 
        )        
    
    except Exception as e:
        log.logger.critical(str(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]        
        request.response.Status = 500
        request.response.Message = "Internal Server Error"
        request.response.data ={ "error" :
            {
                "type": exc_type,
                "message": str(e),
                "script": fname,
                "line": exc_tb.tb_lineno
            }
        } 

#endregion

#region Examples

if __name__ == '__main__':    

    #region "Create a log file"
    log = mLog()
    log.start( os.getcwd(), "DEBUG" )
    log.logger.debug("Starting {}".format(__file__))                 

    #endregion

    #region "input Message Usage"
    
    if False:
        #region "Create an order"
        x = order( custname = 'CUST123' , ordname = 'ORD1112233' )
        x.orderitems.append(orderitems(partname="ABC" , qty=1.1 , duedate="01/01/2022"))
        x.orderitems.append(orderitems(partname="DEF" , qty=2.2 , duedate="02/01/2022"))
        x.orderitems.append(orderitems(partname="GHI" , qty=3.3 , duedate="03/01/2022"))
        
        # Output as json
        print(x.toJSON())

        # Output as xml, with a root node for XML
        print(x.toXML(root="top"))

        #endregion

    if False:
        #region "Load Order from xml file"    
        with open('test2.xml', 'r') as the_file:        
            q = order(_xml=the_file)
            # Save to json
            q.toFile('test2.json', q.toJSON)

        #endregion
    
    if False:        
        #region "Load Order from json file"    
        with open('test.json', 'r') as the_file:        
            q = order(_json=the_file)
            # Save to xml
            q.toFile('test2.xml', q.toXML, root="root")

        #endregion

    if True:
        #region "Load object from SQL Procedure"
        q = order(                              # Create an order object
            _sql={                              # from SQL
                "proc": "sys_Python",           # from this procedure
                "config" : Config(              # And this configuration
                    env="wlnd" ,                    # the Priority environment
                    path=os.getcwd()                # the location of the config file
                ) , 
                "kwargs": {"ORDNAME" : "123"}    # With these paramaeters
            }
        )
        q.toFile('sql.json', q.toJSON)
        
        #endregion

    #endregion

    #region "Output Method usage"

    if True:
        #region "Send to URL"

        # Create an object to hold the result
        Response = Response()

        q.toURL(
            "https://priority.ntsa.uk/odata/priority/{}/{}/{}".format("tabula.ini" , "wlnd" , "ZODA_TRANS"),
            q.toFlatOdata,
            user="apiuser",
            passw= "123456",
            response=Response       # the apy request/response object. Use:
                                        # for command:      response=Response   (a new response is used)
                                        # for apy usage:    request=request     (the request.response is used)            
        )
        # Display the result
        print( "[{}]: {}".format( Response.Status , Response.Message ))
        print( "response : " + json.dumps(Response.data, sort_keys=False, indent=4 ))

        #endregion
  
    if False:
        #region "Send to oData"

        # Create an object to hold the result
        Response = Response()
        
        # Send to Priority
        q.toPri(                    # Send this object to Priority
            
            Config(                 # Using this configuration
                env="wlnd" ,            # the Priority environment
                path=os.getcwd()        # the location of the config file
            ) , 

            q.toFlatOdata ,         # Method to generate oData Commands
                                        # toFlatOdata - send to oData load form
                                        # toOdata - send to nested Priority forms
                                        # OR a custom method.
            
            response=Response       # the apy request/response object. Use:
                                        # for command:      response=Response   (a new response is used)
                                        # for apy usage:    request=request     (the request.response is used)
        )
        
        # Display the result
        print( "[{}]: {}".format( Response.Status , Response.Message ))
        print( "response : " + json.dumps(Response.data, sort_keys=False, indent=4 ))
        
        #endregion

    if False:
        #region "Send to SQL"
        
        Response = Response()
        
        # Send to Priority
        q.toPriSQL(                    # Send this object to Priority
            
            Config(                 # Using this configuration
                env="wlnd" ,            # the Priority environment
                path=os.getcwd()        # the location of the config file
            ) , 

            q.toSQL ,               # Method to generate sql Commands
                                        # toSQL - send to oData load form                                    
                                        # OR a custom method.
            
            response=Response       # the apy request/response object. Use:
                                        # for command:      response=Response   (a new response is used)
                                        # for apy usage:    request=request     (the request.response is used)
        )
        
        # Display the result
        print( "[{}]: {}".format( Response.Status , Response.Message ))
        print( "response : " + json.dumps(Response.data, sort_keys=False, indent=4 ))

        #endregion

    #endregion    

#endregion