# [svc.py](../package/src/MedatechUK/svc.py "svc.py")
This package contains a debugable inheritable Windows Service, based on [pywin32](https://pypi.org/project/pywin32/ "pywin32")

## Imports
```python
from pathlib import Path
import win32serviceutil , debugpy
from MedatechUK.svc import AppSvc

```
## Overriding Methods
To inherit the package you must specify a method to handle the Main() and -optionally- the Init() functions.

The Init() function is called before the service starts and is used to do any configuration or setup required by the service. If the Init() errors, the service will halt immediately.

The Main() function is called in a loop once when your service has started, until the service stops.

## Debugging
This package uses [debugpy](https://github.com/microsoft/debugpy "debugpy") to allow your to attach a debugger to your service.

To connect a dubugger to the Main(), start your service with the parameter -debug.

To connect a dubugger to the your init, start your service with the parameter -debug init.

Note that the in -debug mode, the Main() function is not called until the degugger connects.

Note that when connecting a debugger to the Init() function, the service will not start properly as it's waiting for a connection before the service is actually running.

To connect the debug, add the following configuration to your .vscode/lauunch.json file.
```json
        {
            "name": "Python Debugger: Attach",
            "type": "debugpy",
            "request": "attach",            
            "connect": {
              "host": "localhost",
              "port": 5678
            },
            "justMyCode": false
          }
```

Note that the port specified in the launcher.json must match the port specified in the settings.ini of your service. 
This defaults to 5678, but may be changed.

## Objects exposed by the Service

### self.log
Returns a [Logging Class](https://github.com/MedatechUK/Medatech.APY/blob/main/docs/log.md "Logging Class") created in the self.Folder location.
```python
self.log.logger.debug("Log this message.")  ## Log Message.
```

### self.clArg
Returns [Command Line Arguments](https://github.com/MedatechUK/Medatech.APY/blob/main/docs/cl.md "Command Line Arguments") from the service start.
```python
self.clArg.byName(['env','e']) ## Returns the value of -e or -env
```

### self.oDataConfig
Returns a [Config Class](https://github.com/MedatechUK/Medatech.APY/blob/main/docs/oDataConfig.md "Config Class") of oData settings from the settings.ini file
```python
self.svc.oDataConfig ## returns the oData configuration from settings.ini, 
                     ## using config['odata']['env'] as the environment.
```

### self.Config
Read a property from the Settings.ini.
```python
self.config.debug.verbosity  ## The verbosity value from ['debug']['VERBOSITY'] 
```

Note that the service itself uses the settings.ini, and -if missing- the file will be created on serice start in the current working directory, with the following defaults:
| INI   | Property      |Description                     | Default      |
|--------|--------------|--------------------------------|--------------|
| debug  |VERBOSITY     | Debugging level  | DEBUG |
|        |PORT 	        | Debug port | 5678  |
|        |FORCE         | Force the service to be in debug mode | ON |
| odata  |oDataHost     | The URL of the priority Service  | priority.localhost |
|        |tabulaini     | The tabula config to use  | tabula.ini |
|        |ouser         | The API user for oData | apiuser |
|        |opass         | The users password for oData | password |
|        |ENV           | The priority environment  | demo |
| db     |server        | SQL database and instance name  | localhost\PRI |
|        |credentials   | SQL credentials  | Trusted_Connection=Yes |

Note that the default debug.force value is ON. This means that by default the service run in debug mode even without the -debug option. Only set this to OFF after testing is complete.

## Example Service
```python
class MySVC(AppSvc):    
    _svc_name_ = "testSVC"
    _svc_display_name_ = "Test Service"    

    def __init__(self , args):    
        self.Main = MySVC.main   ## Set the Main Service Method
        self.Init = MySVC.init   ## Set the Init Method (optional)
        self.Folder = Path(__file__).parent         
        AppSvc.__init__(self , args)

    def init(self):
        if self.debuginit: debugpy.breakpoint() # -debug init
        
        ## Do servce setup
        self.log.logger.info("Log data from setting.ini like [{}] and [{}].".format( 
            self.config.file.suffix
            , self.config.file.path
        ))         

    def main(self):       
        if self.debug: debugpy.breakpoint # -debug          
        
        ## Main service - run on loop
        self.log.logger.debug(self.clArg.byName(['env','e']))

if __name__ == '__main__':    
    win32serviceutil.HandleCommandLine(MySVC)    

```    