# Python API

## About

A Python package of common EDI functions.

## Install

To install this package use:
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

### [Command Line Arguments](cl.md "Command Line Arguments")

A package of command line tools, including parsing the [sys.argv](https://docs.python.org/3/library/sys.html "sys.argv") function in Python.

```
progname.exe -arg value -arg2 "value two"
```

```python
arg.byName(['arg','a']) = "value"
arg.byName(['arg2','a2']) = "value two"
arg.byName(['arg3','a3']) = None

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

See Also: the [http transport example](../transport/web "http Transport")

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
...

```

### [AppSvc Class](svc.md "AppSvc Class")

This package contains an inheritable Windows Service.

```python
class MySVC(AppSvc):    
    _svc_name_ = "testSVC"
    _svc_display_name_ = "Test Service"    

    def __init__(self , args):    
        self.Main = MySVC.main   
        self.Init = MySVC.init   
        self.Folder = Path(__file__).parent         
        AppSvc.__init__(self , args)

    def init(self):
        if self.debuginit: debugpy.breakpoint() # -debug init
        # Do servce setup

    def main(self):       
        if self.debug: debugpy.breakpoint # -debug          
        
        # Main service    
        self.log.logger.debug(self.clArg.byName(['env','e']))

if __name__ == '__main__':    
    win32serviceutil.HandleCommandLine(MySVC)    

```  

### [EPDM Class](epdm.md "EPDM Class")

A package for working with EPDM (Solid Works) serial data.

See Also: [Making the EPDM example executable](../transport/cl "Command Line Transport").

See Also: [Running the EPDM executable from a service](../transport/service "Service Transport").

```python
from MedatechUK.epdm import xmlTransactions

# Load an EPDM file.
try:
    with open('example.xml', 'r') as the_file:        
        q = xmlTransactions(_xml=the_file)
        for t in q.transactions:
            recurse(t.document)

except Exception as e:
    log.logger.critical(str(e))
	
```