# Command Line transport

## Introduction

This example expands upon the [EPDM Tutorial](../../../main/docs/epdm.md "EPDM Class"), converting our script into an .exe and implimenting [command line arguments](../../../main/docs/cl.md "command line arguments").

We use [pyinstaller](https://pyinstaller.org/ "pyinstaller") to create a .exe file from a python script.
```
pip install pyinstaller

pyinstaller --onefile your_program.py

```

When we run our EPDM program we want to be able to pass in the following [arguments](../../../main/docs/cl.md "command line arguments"):
- /cwd {The current working directory}
- /env {The Priority environment in which to run the loading}
- {File_Name} : The file to load ([positional](../../../main/docs/cl.md "command line arguments") argument [0])

## Imports
```python
from MedatechUK.cl import clArg

```

## Validating the command line parameters
Before we do anything, we must verify that 
- we have a positional argument
- that argument is an extant file
- that we have an environment (-env) specified.
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

## Setting the -cwd (current working directory)

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

## Running our .exe
Build the .exe with:
	
	pyinstaller --onefile solidworks.py

And execute it:
```
M:\python\apy>solidworks.exe -e wlnd example.xml

[200]: OK
response : {
    "@odata.context": "https://priority.ntsa.uk/odata/Priority/tabula.ini/wlnd/$metadata#ZODA_TRANS/$entity",
    "TYPENAME": "SW",
    "BUBBLEID": "fe62189e-6aab-4dcc-a511-77842fe1ff77",
    "CREATEDATE": "2022-06-05T11:52:00+01:00",
    "COMPLETE": "Y",
    "COMPLETEDATE": "2022-06-05T11:52:00+01:00",
    "LOADED": null,
    "LOADDATE": null,
    "LINE": 581,
    "LOADTYPE": 10
}
[200]: OK
response : {
    "@odata.context": "https://priority.ntsa.uk/odata/Priority/tabula.ini/wlnd/$metadata#ZODA_TRANS/$entity",
    "TYPENAME": "SW",
    "BUBBLEID": "738bf9b3-ca01-4c98-ab36-39a1dbe5c609",
    "CREATEDATE": "2022-06-05T11:52:00+01:00",
    "COMPLETE": "Y",
    "COMPLETEDATE": "2022-06-05T11:52:00+01:00",
    "LOADED": null,
    "LOADDATE": null,
    "LINE": 582,
    "LOADTYPE": 10
}
[200]: OK
response : {
    "@odata.context": "https://priority.ntsa.uk/odata/Priority/tabula.ini/wlnd/$metadata#ZODA_TRANS/$entity",
    "TYPENAME": "SW",
    "BUBBLEID": "3cf13eef-44f6-4758-9828-354d9983ae54",
    "CREATEDATE": "2022-06-05T11:52:00+01:00",
    "COMPLETE": "Y",
    "COMPLETEDATE": "2022-06-05T11:52:00+01:00",
    "LOADED": null,
    "LOADDATE": null,
    "LINE": 583,
    "LOADTYPE": 10
}

```
See also: [Running the EPDM as a service](../../../main/transport/service "Service Transport").
