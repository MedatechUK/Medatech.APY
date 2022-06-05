# Python web

## Introduction

This example demonstrates the use of the [python apy](../../../main/docs/apy.md "python apy").

Note that [IIS URL re-writer](https://www.iis.net/downloads/microsoft/url-rewrite "IIS URL re-writer") is required.

## The default page (default.py)

The default is the landing page that creates an request object for your handler.

Read more about creating handlers [here](../../../main/docs/apy.md "python apy").

## The iis configuraation (web.Config)

### Add Python CGI
Specify the location of the Python binary as the scriptProcessor.
```xml
<handlers>
    <add 
	  	name="Python" 
		path="*.py" 
		verb="*" 
		modules="CgiModule" 
		scriptProcessor="&quot;c:\Program Files\Python39\python.exe&quot; %s %s" 
		resourceType="File" 
		requireAccess="Script" 
	/>
</handlers>
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
/{PRIORITY_COMPANY}/{SOME_PAGE}.py
```
into a request to:
```
default.py?environment={PRIORITY_COMPANY}&endpoint={SOME_PAGE}
```

These values are used by the apy. See [APY Class](apy.md "APY Class")

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

### Full web.config listing

Here's the full web.cofig listing for reference.
```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  <appSettings>
    <add key="oDataHost" value="https://priority.someurl" />
    <add key="tabulaini" value="***********" />
    <add key="ouser" value="***********" />
    <add key="opass" value="***********" />
  </appSettings>
  <connectionStrings>
    <add connectionString="Server=127.0.0.1\PRI,1433;Trusted_Connection=Yes;MultipleActiveResultSets=true;" name="priority" />
  </connectionStrings>
  <system.webServer>
    <handlers>
      <add name="Python" path="*.py" verb="*" modules="CgiModule" scriptProcessor="&quot;c:\Program Files\Python39\python.exe&quot; %s %s" resourceType="File" requireAccess="Script" />
    </handlers>
    <defaultDocument>
      <files>
        <add value="default.py" />
      </files>      
    </defaultDocument>
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
  </system.webServer>
  <!--
    For a description of web.config changes see http://go.microsoft.com/fwlink/?LinkId=235367.

    The following attributes can be set on the <httpRuntime> tag.
      <system.Web>
        <httpRuntime targetFramework="4.6.1" />
      </system.Web>
  -->
  <system.web>    
    <compilation debug="true" targetFramework="4.6.1" />

  </system.web>
</configuration>

```