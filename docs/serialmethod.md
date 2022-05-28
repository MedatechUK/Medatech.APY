# serial.py

The following examples are based on the [order / orderitems class](serial.md "order / orderitems class")

## Create an Object instance

x = order( custname = 'CUST123' , ordname = 'ORD1112233' )
x.orderitems.append(orderitems(partname="ABC" , qty=1.1 , duedate="01/01/2022"))
x.orderitems.append(orderitems(partname="DEF" , qty=2.2 , duedate="02/01/2022"))
x.orderitems.append(orderitems(partname="GHI" , qty=3.3 , duedate="03/01/2022"))


## Save Object: 
```python
.toFile('{FILENAME}, {METHOD}, root="{ROOT}")
'''

| Property      |Description                            |
|---------------|---------------------------------------|
|FILENAME| The name of the file to save to|
|METHOD| The method that will return serial data to be written|
|ROOT| The top level xml node (if method is toXML)|

## Load Object
```python
with open('test.json', 'r') as the_file:        
    q = {OBJECT}({SERIALTYPE}=the_file)
```
| Property      |Description                            |
|---------------|---------------------------------------|
|OBJECT| The object that will load the data|
|SERIALTYPE| json OR xml|

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