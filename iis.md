# IIS Setup

First, install [IIS URL re-writer](https://www.iis.net/downloads/microsoft/url-rewrite "IIS URL re-writer").

Then in IIS manager, add a new application to Priority and open it's web.config file.

## web.config

### Add Python CGI
Specify the location of the Python binary as the scriptProcessor.
```xml
<handlers>
      <add name="Python" path="*.py" verb="*" modules="CgiModule" scriptProcessor="&quot;c:\Program Files\Python39\python.exe&quot; %s %s" resourceType="File" requireAccess="Script" />
```

### Default Document
Then set the defalt document for the site to be default.py. This is the landing page that will begin processing the request.
```xml
<defaultDocument>
  <files>
    <add value="default.py" />
  </files>      
</defaultDocument>
```

### Set the re-write rules
These rules convert the incoming URL:
```
/{PRIORITY_COMPANY}/{SOME+PAGE}.py
```
into a request to:
```
default.py?environment={PRIORITY_COMPANY}&endpoint={SOME+PAGE}
```

Add the following rewrite rules to the web.config.
```xml
<rewrite>
  <rules>    
    <rule name="API Rewrite endpoint">
      <match url="^([0-9a-z_-]+).([a-z]+)$" />
      <action type="Rewrite" url="default.py?endpoint={R:1}.{R:2}" />
    </rule>   
    <rule name="API Rewrite env and endpoint">
      <match url="^([0-9a-z_-]+)/(.*$)" />
      <action type="Rewrite" url="default.py?environment={R:1}&amp;endpoint={R:2}" />
    </rule>         
  </rules>
</rewrite>
```

### Set oData settings

Finally, configure the oData setting in the appSetting. See [oData Configuration](oDataConfig.md "oData Configuration").
```xml
  <appSettings>
    <add key="oDataHost" value="https://priority.someurl" />
    <add key="tabulaini" value="***********" />
    <add key="ouser" value="***********" />
    <add key="opass" value="***********" />
  </appSettings>
  <connectionStrings>
    <add connectionString="Server=127.0.0.1\PRI,1433;Trusted_Connection=Yes;MultipleActiveResultSets=true;" name="priority" />

  </connectionStrings>
```  