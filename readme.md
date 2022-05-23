# Python API

## Install
To install this package use
```
pip install MedatechUK.APY
```

## Imports

```python

import json , uuid , os , sys
from MedatechUK.Serial import SerialBase , SerialT , SerialF
from MedatechUK.mLog import mLog
from MedatechUK.apy import Response
from MedatechUK.oDataConfig import Config
```

## Business objects

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
        SerialT(self, "duedate" , pCol="INT2" , pType="INT")

        #endregion
    
    #endregion

```


## Example Usage

```python

    #region "Create an order"
    x = order( custname = 'CUST123' , ordname = 'ORD1112233' )
    x.orderitems.append(orderitems(partname="ABC" , qty=1.1 , duedate=818181818))
    x.orderitems.append(orderitems(partname="DEF" , qty=2.2 , duedate=818181818))
    x.orderitems.append(orderitems(partname="GHI" , qty=3.3 , duedate=818181818))

    # Save the order to file    
    x.toFile('test.json', x.toJSON)

    #endregion

    #region "Load Order from file"
    log.logger.debug("Opening {}".format('test.json'))    
    with open('test.json', 'r') as the_file:
        q = order(**json.loads(the_file.read()))

        # Output as json
        #print(q.toJSON())

        # Output as nested oData Commands
        #print(json.dumps(json.loads(q.toOdata()), sort_keys=False, indent=4))

        # Output as flat oData Commands (for Priority loading)
        #print(json.dumps(json.loads(q.toFlatOdata()), sort_keys=False, indent=4))

        # Create an object to hold the result
        Response = Response()
        
        # Send toFlatOdata method to Priority API
        q.toPri(
            Config(
                env="wlnd" , 
                path=os.getcwd()
            ) , 
            q.toFlatOdata , 
            response=Response
        )
        
        # Display the result
        print( "[{}]: {}".format( Response.Status , Response.Message ) )
        print( "response : " + json.dumps(Response.data, sort_keys=False, indent=4 ))

```

## Usage as a web handler
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
