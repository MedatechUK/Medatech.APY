# Python Service Transport

## Introduction

This example extends the [epdm example](../../../main/docs/epdm.md "epdm example").

Once we have built our [.exe](../../../../tree/main/transport/cl "Command Line Transport"), we need a progam that will check for new files and pass them to our EPDM program for processing.

We want this program to keep checking for new files, regardless if anyone is logged in on the machine. 

To do this we need to use a Windows service. Services are terminate and stay resident programs, managed by Windows.

## Python as a service
To create a service we first need to install pywin32.

	pip install pywin32

Install your script as a service.

	py yourscript.py install

Update changes to your script.

	py yourscript.py update

Debug your service (with command line parameters).

	py yourscript.py debug -m sandbox

## Folder monitoring
We're going to monitor for new files using the [folderWatch package](../../../main/docs/cl.md#folderWatch "folderWatch package").

Also we want our service to use the [clArg Class](../../../main/docs/cl.md "clArg Class") class to pass a -mode value, to allow us to specify which configuration we want to use (for example, live or sandbox).

## Our Settings file

We want our service to be able to check multiple locations, and be able to define a handler and environment for each location.

So we'll need some settings that will hold:
- the list of places our service should look for files
- an instruction about what to do with files that it finds

We're going to store these settings using a [Serial Class](../../../main/docs/serial.md "Serial Class") with the following structure:

- defaultconfig name
	- config 1
	 	- settings 1
		- settings 2
		- settings ...n
	- config 2
	 	- settings 1
		- settings 2
		- settings ...n
	- config n
	 	- settings 1
		- settings 2
		- settings ...n

### Constructing the settings file (settings.py)
We can use the following Python code to create an instance of our setting class, and [save our settings file](../../../main/docs/serialmethod.md "Serial Package").
```python
if __name__ == '__main__': 

    # Create a Setting file.
    q = mySettings(defaultConfig="sandbox")
    q.Configs.append(Config(name="sandbox"))
    q.Configs[-1].fWatch.append(
        fWatch(
            folder="\\\\walrus\\nas\\PriorityMobile\\python\\apy\\SolidWorks\\" , 
            handler="\\\\walrus\\nas\\PriorityMobile\\python\\apy\\solidworks.exe" , 
            env="wlnd" , 
            ext="xml"
        )
    )    

    # Save the setting file.
    print(q.toJSON())
    q.toFile(
        "{}\{}.json".format(
            os.path.abspath(
                os.path.dirname(__file__).rstrip("\\")
            ) , "pyEDI"
        ) , q.toJSON
    )    
```

This creates a settings file:
```json
{
    "defaultConfig": "sandbox",
    "Configs": [
        {
            "name": "sandbox",
            "fWatch": [
                {
                    "folder": "\\\\walrus\\nas\\PriorityMobile\\python\\apy\\SolidWorks\\",
                    "handler": "\\\\walrus\\nas\\PriorityMobile\\python\\apy\\solidworks.exe",
                    "env": "wlnd",
                    "ext": "xml"
                }
            ]
        }
    ]
}

```

## The service (svc.py)

When the service starts we load our setting file and use it to create an array of locations to monitor.

Here we are using the [clArg Class](../../../main/docs/cl.md "clArg Class") to see if a -mode value was specified, otherwise use the default.

```python
with open(self.settingsfile, 'r') as the_file:        
    settings = mySettings(_json=the_file)
    if self.args.byName(["m","mode"]) == None:
        # Use the default config if none is specified on the command line
        c = settings.byName(settings.defaultConfig)
    else :
        # Use the specified mode
        c = settings.byName(self.args.byName(["m","mode"]))
    # Check mode exists
    if c == None:
        raise NameError("Mode [{}] does not exist.".format( self.args.byName(["m","mode"]) ) )

for w in c.fWatch:
    self.fs.append(folderWatch(**w.kwargs()))

```

Then, every 15 seconds, we iterate through the array of locations, checking for new files.

Note that the check method of the [folderWatch package](../../../main/docs/cl.md#folderWatch "folderWatch package") is called with the services location, which is passed to the .exe with the -cwd parameter, so logs from the called .exe are routed to the log of the service, rather than to the location of the .exe.
```python
while not self.stop_requested:
    for w in self.fs:
        try:
            w.check(            
                os.path.abspath(
                    os.path.dirname(__file__).rstrip("\\")
                )
            )

        except Exception as e:
            self.log.logger.warning(str(e))
                    
    for i in range(150):
        if not self.stop_requested:
            time.sleep(.1)
```

## The [log](../../../main/docs/log.md "logging package") file of the service
```
12:58:16 DEBUG svc.py Starting C:\pyedi\svc.py
12:58:16 DEBUG svc.py Opening settings file C:\pyedi\pyEDI.json
12:58:16 INFO svc.py > cl.py fWatch folder \\walrus\nas\PriorityMobile\python\apy\SolidWorks\ for xml with handler \\walrus\nas\PriorityMobile\python\apy\solidworks.exe in env wlnd.
12:58:16 INFO svc.py > cl.py Found file \\walrus\nas\PriorityMobile\python\apy\SolidWorks\example.xml.
12:58:16 INFO svc.py > cl.py shell: \\walrus\nas\PriorityMobile\python\apy\solidworks.exe -e wlnd -cwd C:\pyedi \\walrus\nas\PriorityMobile\python\apy\SolidWorks\example.xml
12:58:18 DEBUG Solidworks.py Starting C:\Windows\TEMP\_MEI62842\Solidworks.py
12:58:19 DEBUG Solidworks.py > oDataConfig.pyc Opening [C:\pyedi\web.config].
12:58:19 DEBUG Solidworks.py > Serial.pyc POSTing to [priority.ntsa.uk/odata/priority/tabula.ini/wlnd/ZODA_TRANS] 
12:58:19 DEBUG Solidworks.py > Serial.pyc Headers:
{
    "Authorization": "Basic YXBpdXNlcjoxMjM0NTY=",
    "Content-Type": "application/json",
    "User-Agent": "MedatechUK Python Client"
}
12:58:19 DEBUG Solidworks.py > Serial.pyc Data:
{
    "BUBBLEID": "b87c352d-12fa-4b66-93f4-cf584d45c38d",
    "TYPENAME": "SW",
    "ZODA_LOAD_SUBFORM": [
        {
            "RECORDTYPE": "1",
            "TEXT2": "C200",
            "TEXT3": "EC Cramer CCC452",
            "TEXT1": "A03"
        }
    ]
}
12:58:23 DEBUG Solidworks.py > Serial.pyc [201] OK
12:58:23 DEBUG Solidworks.py > Serial.pyc PATCHing to [/odata/priority/tabula.ini/wlnd/ZODA_TRANS(BUBBLEID='b87c352d-12fa-4b66-93f4-cf584d45c38d',LOADTYPE=10)] ... 
12:58:23 DEBUG Solidworks.py > Serial.pyc [200] OK
12:58:23 DEBUG Solidworks.py > Serial.pyc Result: {
    "@odata.context": "https://priority.ntsa.uk/odata/Priority/tabula.ini/wlnd/$metadata#ZODA_TRANS/$entity",
    "TYPENAME": "SW",
    "BUBBLEID": "b87c352d-12fa-4b66-93f4-cf584d45c38d",
    "CREATEDATE": "2022-06-05T12:58:00+01:00",
    "COMPLETE": "Y",
    "COMPLETEDATE": "2022-06-05T12:58:00+01:00",
    "LOADED": null,
    "LOADDATE": null,
    "LINE": 584,
    "LOADTYPE": 10
}
12:58:24 DEBUG Solidworks.py > oDataConfig.pyc Opening [C:\pyedi\web.config].
12:58:24 DEBUG Solidworks.py > Serial.pyc POSTing to [priority.ntsa.uk/odata/priority/tabula.ini/wlnd/ZODA_TRANS] 
12:58:24 DEBUG Solidworks.py > Serial.pyc Headers:
{
    "Authorization": "Basic YXBpdXNlcjoxMjM0NTY=",
    "Content-Type": "application/json",
    "User-Agent": "MedatechUK Python Client"
}
12:58:24 DEBUG Solidworks.py > Serial.pyc Data:
{
    "BUBBLEID": "e7d1b005-4d11-4be9-b008-a9bcbdd33a66",
    "TYPENAME": "SW",
    "ZODA_LOAD_SUBFORM": [
        {
            "RECORDTYPE": "1",
            "TEXT2": "EK960",
            "TEXT3": "Hardener Momentive EK960",
            "TEXT1": "B01"
        }
    ]
}
12:58:24 DEBUG Solidworks.py > Serial.pyc [201] OK
12:58:24 DEBUG Solidworks.py > Serial.pyc PATCHing to [/odata/priority/tabula.ini/wlnd/ZODA_TRANS(BUBBLEID='e7d1b005-4d11-4be9-b008-a9bcbdd33a66',LOADTYPE=10)] ... 
12:58:24 DEBUG Solidworks.py > Serial.pyc [200] OK
12:58:24 DEBUG Solidworks.py > Serial.pyc Result: {
    "@odata.context": "https://priority.ntsa.uk/odata/Priority/tabula.ini/wlnd/$metadata#ZODA_TRANS/$entity",
    "TYPENAME": "SW",
    "BUBBLEID": "e7d1b005-4d11-4be9-b008-a9bcbdd33a66",
    "CREATEDATE": "2022-06-05T12:58:00+01:00",
    "COMPLETE": "Y",
    "COMPLETEDATE": "2022-06-05T12:58:00+01:00",
    "LOADED": null,
    "LOADDATE": null,
    "LINE": 585,
    "LOADTYPE": 10
}
12:58:24 DEBUG Solidworks.py > oDataConfig.pyc Opening [C:\pyedi\web.config].
12:58:24 DEBUG Solidworks.py > Serial.pyc POSTing to [priority.ntsa.uk/odata/priority/tabula.ini/wlnd/ZODA_TRANS] 
12:58:24 DEBUG Solidworks.py > Serial.pyc Headers:
{
    "Authorization": "Basic YXBpdXNlcjoxMjM0NTY=",
    "Content-Type": "application/json",
    "User-Agent": "MedatechUK Python Client"
}
12:58:24 DEBUG Solidworks.py > Serial.pyc Data:
{
    "BUBBLEID": "e131ee5b-7b9b-4f9d-a0b5-9cc32d28d805",
    "TYPENAME": "SW",
    "ZODA_LOAD_SUBFORM": [
        {
            "RECORDTYPE": "1",
            "TEXT2": "BOM Test",
            "TEXT3": "Test",
            "TEXT1": "A02"
        },
        {
            "RECORDTYPE": "2",
            "TEXT1": "C200",
            "REAL1": 0.6
        },
        {
            "RECORDTYPE": "2",
            "TEXT1": "EK960",
            "REAL1": 1.0
        }
    ]
}
12:58:24 DEBUG Solidworks.py > Serial.pyc [201] OK
12:58:24 DEBUG Solidworks.py > Serial.pyc PATCHing to [/odata/priority/tabula.ini/wlnd/ZODA_TRANS(BUBBLEID='e131ee5b-7b9b-4f9d-a0b5-9cc32d28d805',LOADTYPE=10)] ... 
12:58:24 DEBUG Solidworks.py > Serial.pyc [200] OK
12:58:24 DEBUG Solidworks.py > Serial.pyc Result: {
    "@odata.context": "https://priority.ntsa.uk/odata/Priority/tabula.ini/wlnd/$metadata#ZODA_TRANS/$entity",
    "TYPENAME": "SW",
    "BUBBLEID": "e131ee5b-7b9b-4f9d-a0b5-9cc32d28d805",
    "CREATEDATE": "2022-06-05T12:58:00+01:00",
    "COMPLETE": "Y",
    "COMPLETEDATE": "2022-06-05T12:58:00+01:00",
    "LOADED": null,
    "LOADDATE": null,
    "LINE": 586,
    "LOADTYPE": 10
}
12:58:24 INFO svc.py > cl.py Moving file from \\walrus\nas\PriorityMobile\python\apy\SolidWorks\example.xml to C:\pyedi\log\2022-06\05\\

```