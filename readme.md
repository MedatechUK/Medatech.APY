# Python API

## Example Usage

```python

from MedatechUK.odata import Load
from MedatechUK.odata import oResponse

# Create the oData Loading
l = Load(
    # The oData loading code in Priority
    # For web requests the Load type is 
    # the endpoint extention
    ltype = "ABC",
    
    # The config file stores the data required 
    # in order to unpack the same serial data
    # into the same fields in Priority for every 
    # load. For web requests the Config file is the
    # name of the endpoint defined by the request URL
    c = "glossary" + ".config",

    # The oData module has 3 run modes, allowing
    # processing of data from file, object or APY request:    
    #   request = apy.Request ) Either
    #   f = "filename"      ) Or
    #   o = object          ) Or
    f = 'glossary.json',
    
    # The Priority company into which we will load data
    # The environment variable is set by the request URL
    # when the run mode is request.
    # Set this *ONLY* when using file/object run modes.
    env = "wlnd"
)

# Get a response structure to hold the oData result
r = oResponse()

# POST the oData to Priority
l.post(r)   

# Display the result from the oData service
print("{}: {}\n{}".format(r.Status, r.Message, r.data))

```
## Output
```
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
