# Command Line transport

## Introduction

This example expands upon the [EPDM Tutorial](../../../main/docs/epdm.md "EPDM Class") to use [command line arguments](../../../main/docs/cl.md "command line arguments").

We use [pyinstaller](https://pyinstaller.org/ "pyinstaller") to create a .exe file from a python script.
```
pip install pyinstaller

pyinstaller --onefile your_program.py

```

When we run our program we want to be able to pass in the following [command line arguments](../../../main/docs/cl.md "command line arguments"):
- /cwd {The current working directory}
- /env {The Priority environment in which to run the loading}

## Imports
```python
from MedatechUK.cl import clArg

```

## Validating the command line parameters
Before we do anything, we must verify that we have required parameters and that referenced files exist.
```python
try:     

    #region Check Arguments   
    if len(arg.args()) == 0 :
        raise NameError("No file specified.")

    if not exists(arg.args()[0]):
        raise NameError("File {} does not exist.".format(arg.args()[0]))

    if arg.byName(["e" , "env"]) == None:
        raise NameError("No environment specified.")

    #endregion

    with open(arg.args()[0], 'r') as the_file:        
        q = xmlTransactions(_xml=the_file)
        for t in q.transactions:
            recurse(t.document)

except Exception as e:
    log.logger.critical(str(e))
    print(e)
	
```

## Setting the current working directory

We want to use the command line parameter -cwd to set the current working directory:

We can use the arg.byName(['cwd','path'] methods to find a parameter called EITHER cwd or path.
```python

if __name__ == '__main__':    

    arg = clArg()

    #region "Create a log file"
    log = mLog()    
    if arg.byName(["cwd" , "path"]) != None:
        if not exists(arg.byName(["cwd" , "path"])):
            raise NameError("Specified working directory {} is missing.".format(arg.byName(["cwd" , "path"])))
        else:
            os.chdir(arg.byName(["cwd" , "path"]))
    
    log.start( os.getcwd() , "DEBUG" )            
    log.logger.debug("Starting {}".format(__file__))     

```

## Setting the -env (environment) parameter

We want to use the command line parameter -env to set the Priority company for the loading:

We can use the arg.byName(['e','env'] methods to find a parameter called EITHER e or env.

This is used to set the enviroment of the Priority system with the [Serial Class](../../../main/docs/serial.md "Serial Class").
```python
    # Create an object to hold the result    
    r = Response()    
    # region Send to Priority
    q.toPri(                    # Send this object to Priority        
        Config(                 # Using this configuration
            env=arg.byName(['e','env']) ,            # the Priority environment
            path=os.getcwd()        # the location of the config file
        ) , 
        q.toFlatOdata ,         # Method to generate oData Commands
                                    # toFlatOdata - send to oData load form
                                    # toOdata - send to nested Priority forms
                                    # OR a custom method.        
        response=r              # the apy request/response object. Use:
                                    # for command:      response=Response   (a new response is used)
                                    # for apy usage:    request=request     (the request.response is used)
    )
	
```

See also: [Running the EPDM as a service](../../../main/transport/service "Service Transport").
