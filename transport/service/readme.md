# Python Service

## Introduction

This example extends the [epdm example](../../../main/docs/epdm.md "epdm example").

Once we have [built our .exe](../../../main/transports/cl "Command Line Transport"), we need to check for new files to process.

We want this program to keep checking for new file, regardless of if anyone is logged in on the machine. 

To achieve this we need a service.

## Python as a service
To create a service we first need to install pywin32.
```
pip install pywin32

```
### Install your script as a service.
```
py yourscript.py install

```
### Update changes to your script.
```
py yourscript.py install

```
### Debug your service (with command line parameters).
```
py yourscript.py debug -m sandbox

```

## Our Settings file

We want our service to be able to check multiple locations, and be able to define a handler and environment for each location.

So we'll need some settings that will hold:
- the list of places our service should look for files
- an instruction about what to do with files that it finds

We're going to store these settings using a [Serial Class](../../../main/docs/serial.md "Serial Class") with this structure:

> defaultconfig name

> > config 1

> > > settings 1

> > > settings ...n

> > config 2

> > > settings 1

> > > settings ...n

## Folder monitoring
We're going to monitor for new files using the [folderWatch package](../../../main/docs/cl.md#folderWatch "folderWatch package").

Also we want our service to use the [clArg Class](../../../main/docs/cl.md "clArg Class") class to pass a -mode value, to allow us to specify which configuration we want to use (live or sandbox).

## Constructing the settings file (settings.py)
We can use the following Python code to create an instance of our setting class, and [save our settings file](../../../main/docs/serialmethods.md "Serial Package").
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