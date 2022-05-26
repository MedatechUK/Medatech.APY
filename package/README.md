# Python API

## Install
To install this package use
```
pip install MedatechUK.APY
```

## Imports

```python

import json , uuid , os , sys

from datetime import datetime
from dateutil.parser import parse

from MedatechUK.Serial import SerialBase , SerialT , SerialF
from MedatechUK.mLog import mLog
from MedatechUK.apy import Response
from MedatechUK.oDataConfig import Config
```

## Custom Business Objects

```python

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
        self._orderitems = value
        for i in range(len(self._orderitems)):
            self._orderitems[i] = orderitems(**self._orderitems[i])

    #endregion

    #region "ctor"
    def __init__(self,  **kwargs): 

        #region "Property defaults"
        self.custname = 0
        self.ordname = ""
        self.orderitems = []  

        #endregion  

        #region "Set Meta info"
        SerialBase.__init__(self , SerialF(fname="ZODA_TRANS", rt=1, typename="ORD"), **kwargs)  
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
        SerialBase.__init__(self , SerialF(fname="ORDERITEMS", rt=2) , **kwargs)   
        SerialT(self, "rt")
        SerialT(self, "partname" , pCol="TEXT1" , Len=10 , pType="CHAR")
        SerialT(self, "qty" , pCol="REAL1" , pType="REAL")
        
        # pridate is a readonly function that converts the dudate to a Priority integer
        SerialT(self, "pridate" , pCol="INT2" , pType="INT")

        #endregion
    
    #endregion

```

## Methods: Create an instance of the object
```python
      
    x = order( custname = 'CUST123' , ordname = 'ORD1112233' )
    x.orderitems.append(orderitems(partname="ABC" , qty=1.1 , duedate="01/01/2022"))
    x.orderitems.append(orderitems(partname="DEF" , qty=2.2 , duedate="02/01/2022"))
    x.orderitems.append(orderitems(partname="GHI" , qty=3.3 , duedate="03/01/2022"))

```

## Methods: File i/o
```python   
 
    # Output as json
    #print(x.toJSON())

    # Output as xml, with a root node for XML
    #print(x.toXML(root="top"))

    #endregion

    #region "Load Order from xml file"    
    with open('test2.xml', 'r') as the_file:        
        q = order(xml=the_file)
        # Save to json
        q.toFile('test2.json', q.toJSON)

    #endregion
    
    #region "Load Order from json file"    
    with open('test.json', 'r') as the_file:        
        q = order(json=the_file)
        # Save to xml
        q.toFile('test2.xml', q.toXML, root="root")

    #endregion

```

## Methods: Send to Priority
```python   
    
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
    
```

## Methods: Usage as a web handler
```python

def ProcessRequest(request) :
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
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]        
        request.Status = 500
        request.response.Message = "Internal Server Error"
        request.response.data ={ "error" :
            {
                "type": exc_type,
                "message": str(e),
                "script": fname,
                "line": exc_tb.tb_lineno
            }
        } 
```

## Output
``` json
200: OK
{
    "@odata.context": "https: //walrus.ntsa.uk/odata/Priority/tabula.ini/wlnd/$metadata#ZODA_TRANS/$entity",
    "TYPENAME": "ABC",
    "BUBBLEID": "154719de-f79b-4ec5-8d24-4fa28c08dc82",
    "CREATEDATE": "2021-09-26T12:54:00+01:00",
    "COMPLETE": "Y",
    "COMPLETEDATE": "2021-09-26T12:54:00+01:00",
    "LOADED": None,
    "LOADDATE": None,
    "LINE": 121,
    "LOADTYPE": 2
}
```
## Example Usage: Web Handler
The default API handler can be used to process any serial (xml/json) data into oData commands for loading into Priority. Specify the appropriate CONTENT_TYPE for your data and POST.

```
POST https://erp.customer.tld / apy / {environment} / {endpoint} . {Loadtype}
```
| Property      |Description                            |
|---------------|---------------------------------------|
| Method        |POST   |
| URL           |The Priority erp domain|
| environment   |The Priority environment that we are using   |
| endpoint      |The endpoint name, which is used as the name of the config file for the oData module. |
| Loadtype      |The code to associate a Priority loading to be used with this data|

```
GET https://erp.customer.tld / apy / {environment} / {endpoint} . {fileExt}
```
| Property      |Description                            |
|---------------|---------------------------------------|
| Method        |GET   |
| URL           |The Priority erp domain|
| environment   |The Priority environment that we are using   |
| endpoint      |The endpoint name, which may be a custom handler (see below), or the name of an FOR XML Scalar query. |
| fileExt       |The extention specifies the CONTENT_TYPE (xml/json).|

## Example Usage: Custom Web Handler

Create a new file in the root, called whatever.py. 
If a request for the endpoint "whatever" is received, the API injects the whatever.py handler, rather than following the default function.
Then, in the whatever.py file, import the *Request Object* (see below) and impliment the *ProcessRequest()* method to handle the event.

```python

from MedatechUK.apy import Request

##  A handler
#   MUST have a ProcessRequest method to 
#   process the apy.Request()

def ProcessRequest(request) :
    request.Response.data = { "id": request.query( "id", "123" ) }

```    

## APY Objects

### Request Object
| Property      |Description                            |
|---------------|---------------------------------------|
| method        |The HTTP verb being used (GET/POST).   |
| content_type  |The content type of the request. If the request is a POST then this obtained from the CONTENT_TYPE of the Request. If the request is a GET then this obtained from the extention of the Request endpoint (xml/json).|
| environment   |The Priority company that we are loading into. The environment variable is set by the request URL.|
| endpoint      |The name of the endpoint.|
| ext           |The file extention of the endpoint.|
| data          |If this is a POST Request the data property holds the data that was posted.|
| config        |A *Config object* (see below) that holds settings for posting to oData. |
| Response      |A *Response Object* (see below) that contains the JSON response to return to the caller. The response is formatted according to the content_type of the request.|

| Method      |Description                            |
|---------------|---------------------------------------|
| query(name,default)|Returns parsed named value parameters from the URL query string. If the named parameter does not exist, then the specified default value is returned instead.|

### Config Object
| Property      |Description                            |
|---------------|---------------------------------------|
| oDataHost     | The URL of the oData service, eg: https://walrus.ntsa.uk |
| tabulaini     | The tabula.ini file to use for the connection |
| ouser         |The oData user, with API licence|
| opass         |The oData passsword|
| connstr       |The database connection string (to validate the environment).|

### Response Object
| Property      |Description                            |
|---------------|---------------------------------------|
| Status        |Integer HTTP response code.            |
| Message       |The HTTP Status message retuned to the client.|
| data          |The (json) data that will be returned to the client. Data will be returned in the format (xml/json) of the origional Request.|
