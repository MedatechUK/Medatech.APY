# Python API

## About

A Python package of common EDI functions including:
- Logging 
- oData connection settings
- Serialisation
- web handlers

## Install
To install this package use
```
pip install MedatechUK.APY
```

## Imports

### [Logging Class](log.md "Logging Class")

A class to create log files.

```python
from MedatechUK.mLog import mLog

log = mLog()
log.start( os.getcwd(), "DEBUG" )
log.logger.debug("Starting {}".format(__file__)) 

```

### [Config Class](oDataConfig.md "Config Class")

A class for managing oData settings.

```python
from MedatechUK.oDataConfig import Config

c = Config(	                 # Using this configuration
    env="wlnd" ,    	     # the Priority environment
    path=os.getcwd()    	 # the location of the config file
)

```

### [Serial Class](serial.md "Serial Class")

A package for working with serial data.

See also: [Serial object methods](serialmethod.md "Serial object methods")

```python
from MedatechUK.Serial import SerialBase , SerialT , SerialF

# Load an Order from json file
with open('test.json', 'r') as the_file:        
    q = order(json=the_file)
    # Save to xml
    q.toFile('test2.xml', q.toXML, root="root")
	
```

### [APY Class](apy.md "APY Class")

A class for handling HTTP Request/Response.

See Also: [How to set up IIS](iis.md "How to set up IIS")

```python
from MedatechUK.apy import Request , Response

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

