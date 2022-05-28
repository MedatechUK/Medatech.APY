# apy.py


## Imports
```python
	from MedatechUK.apy import Request
```

## Example Usage: Create a Handler

Create a new file in the root, called whatever.py. 
If a request for the endpoint "whatever" is received, the API injects the whatever.py handler, rather than following the default function.
Then, in the whatever.py file, import the *Request Object* (see below) and impliment the *ProcessRequest()* method to handle the event.

### A GET Handler
```python
##  A GET handler
#   MUST have a ProcessRequest method to 
#   process the apy.Request()

def ProcessRequest(request) :
    request.Response.data = { "id": request.query( "id", "123" ) }

``` 

### A POST Handler

The following handler uses a *([Serial Object](serial.md "Serial Object"))* to decode the request.

```python
##  A POST handler
#   MUST have a ProcessRequest method to 
#   process the apy.Request()
   
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
```
		
## Calling the Web Handler

```
POST https://erp.customer.tld / apy / {environment} / {endpoint} 
```
| Property      |Description                            |
|---------------|---------------------------------------|
| Method        |POST   |
| URL           |The Priority erp domain|
| environment   |The Priority environment that we are using   |
| endpoint      |The endpoint name, e.g. whatever.py. |

```
GET https://erp.customer.tld / apy / {environment} / {endpoint} . {fileExt}
```
| Property      |Description                            |
|---------------|---------------------------------------|
| Method        |GET   |
| URL           |The Priority erp domain|
| environment   |The Priority environment that we are using   |
| endpoint      |The endpoint name, which may be a custom handler (see below), or the name of an FOR XML Scalar query. |
| fileExt       |The extention specifies the returned CONTENT_TYPE (xml/json).|



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
| config        |A *([Config Object](oDataConfig.md "Config Object"))* that holds settings for posting to oData. |
| Response      |A *Response Object* (see below) that contains the JSON response to return to the caller. The response is formatted according to the content_type of the request.|

| Method      |Description                            |
|---------------|---------------------------------------|
| query(name,default)|Returns parsed named value parameters from the URL query string. If the named parameter does not exist, then the specified default value is returned instead.|

### Response Object
| Property      |Description                            |
|---------------|---------------------------------------|
| Status        |Integer HTTP response code.            |
| Message       |The HTTP Status message retuned to the client.|
| data          |The (json) data that will be returned to the client. Data will be returned in the format (xml/json) of the origional Request.|
