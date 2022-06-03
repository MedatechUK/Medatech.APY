# Python Service

## Introduction

Our service is going to use the [folderWatch function](../../../main/docs/cl.md "folderWatch function").

First we need some settings that will hold:
- the list of places our service should look for files
- an instruction about what to do with files that it finds

Also we want our service to use the [clArg Class](../../../main/docs/cl.md "clArg Class") class to pass a -mode value, to allow us to specify which configuration we want to use (live or sandbox).

We store these settings using a [Serial Class](../../../main/docs/serial.md "Serial Class") with this structure:

> defaultconfig name

> > config 1

> > > settings 1

> > > settings ...n

> > config 2

> > > settings 1

> > > settings ...n

## Creating the settings file (settings.py)

We can use the following to create and save our setting file.
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

When the service starts we load our setting file and use it to create an array of location we are monitoring

Here we use the [clArg Class](../../../main/docs/cl.md "clArg Class") to see if a -mode value was specified, otherwise use the default.

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

Note that the check method of the [folderWatch class](../../../main/docs/cl.md "folderWatch class") is called with the services location, which is passed to the .exe with the -cwd parameter, so logs from the called .exe are routed to the services log, rather than to the location of the .exe.
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