# Serial Base Methods.

The following examples are based on the [order / orderitems class](serial.md "order / orderitems class").

## Create an Object instance
```python
x = order( custname = 'CUST123' , ordname = 'ORD1112233' )
x.orderitems.append(orderitems(partname="ABC" , qty=1.1 , duedate="01/01/2022"))
x.orderitems.append(orderitems(partname="DEF" , qty=2.2 , duedate="02/01/2022"))
x.orderitems.append(orderitems(partname="GHI" , qty=3.3 , duedate="03/01/2022"))

```

## File I/O examples

### Save Object Instance: 
```python
.toFile('{FILENAME}, {METHOD}, root="{ROOT}")
```

| Property      |Description                            |
|---------------|---------------------------------------|
|FILENAME| The name of the file to save to|
|METHOD| The method that will return serial data to be written|
|ROOT| The top level xml node (if method is toXML) Optional|

### Load Object Instance
```python
with open('{FILENAME}', 'r') as the_file:        
    q = {OBJECT}({SERIALTYPE}=the_file)
```
| Property      |Description                            |
|---------------|---------------------------------------|
|FILENAME| The name of the file to load|
|OBJECT| The object that will load the data|
|SERIALTYPE| _json OR _xml|

### Load from XML, save as JSON
```python      
    with open('test2.xml', 'r') as the_file:        
        q = order(_xml=the_file)
        # Save to json
        q.toFile('test2.json', q.toJSON)
```

### Load from JSON, save as XML
```python      
    with open('test.json', 'r') as the_file:        
        q = order(_json=the_file)
        # Save to xml
        q.toFile('test2.xml', q.toXML, root="root")

```

## POST to Priority oData
Using the *[Configuration](serial.md "Config Object")* and *[Response Object](apy.md "Response Object")*

See [Example](../transport/cl#running-our-exe "Example").
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

## POST to Priority Using SQL
We can use the same structure to write our object as SQL commands to the server descibed in our *[Config](oDataConfig.md "Config Object")*:

See [Example](../transport/cl#writing-to-sql "Example").
```python
    Response = Response()
    
    # Send to Priority
    q.toPriSQL(                    # Send this object to Priority SQL
        
        Config(                 # Using this configuration
            env="wlnd" ,            # the Priority environment
            path=os.getcwd()        # the location of the config file
        ) , 

        q.toSQL ,         # Method to generate sql Commands
                                    # toSQL - send to oData load form                                    
                                    # OR a custom method.
        
        response=Response       # the apy request/response object. Use:
                                    # for command:      response=Response   (a new response is used)
                                    # for apy usage:    request=request     (the request.response is used)
    )

```
	
## Usage as a web handler
Using the *[Request Object](apy.md "Request Object")*
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