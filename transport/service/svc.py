import win32serviceutil
import win32service
import win32event
import servicemanager

import os , time , sys
from os.path import exists

from MedatechUK.cl import folderWatch , clArg
from MedatechUK.Serial import SerialBase , SerialT , SerialF
from MedatechUK.mLog import mLog

#region Settings Serialiser

class mySettings(SerialBase) :

    #region Properties
    @property
    def defaultConfig(self):    
        return self._defaultConfig
    @defaultConfig.setter
    def defaultConfig(self, value):
        self._defaultConfig = value

    @property
    def Configs(self):    
        return self._Configs
    @Configs.setter
    def Configs(self, value):
        self._Configs = []   
        for i in range(len(value)):
            try:
                self._Configs.append(Config(**value[i]))
            except:
                self._Configs.append(Config(**value))  

    #endregion

    #region "ctor"
    def __init__(self,  **kwargs): 

        #region "Property defaults"
        self.defaultConfig = ""
        self._Configs = []  

        #endregion  

        #region "Set Meta info"
        SerialBase.__init__(self , SerialF(fname="ZODA_TRANS"), **kwargs)  

        #endregion
    
    #endregion

    #region Methods
    def byName(self, Name):
        for c in self._Configs:
            if c.name.upper() == Name.upper():
                return c
        return None

    #endregion

class Config(SerialBase) :

    #region Properties
    @property
    def name(self):    
        return self._name
    @name.setter
    def name(self, value):
        self._name = value

    @property
    def fWatch(self):    
        return self._fWatch
    @fWatch.setter
    def fWatch(self, value):
        self._fWatch = []   
        for i in range(len(value)):
            try:
                self._fWatch.append(fWatch(**value[i]))
            except:
                self._fWatch.append(config(**value))  

    #endregion

    #region "ctor"
    def __init__(self,  **kwargs): 

        #region "Property defaults"
        self.name = ""
        self._fWatch = []   

        #endregion  

        #region "Set Meta info"
        SerialBase.__init__(self , SerialF(fname="ZODA_TRANS"), **kwargs)  

        #endregion
    
    #endregion

class fWatch(SerialBase) :

    #region Properties
    @property
    def folder(self):    
        return self._folder
    @folder.setter
    def folder(self, value):
        self._folder = value

    @property
    def handler(self): 
        return self._handler
    @handler.setter
    def handler(self, value):
        self._handler = value   

    @property
    def env(self): 
        return self._env
    @env.setter
    def env(self, value):
        self._env = value   

    @property
    def ext(self): 
        return self._ext
    @ext.setter
    def ext(self, value):
        self._ext = value   

    #endregion

    #region "ctor"
    def __init__(self,  **kwargs): 

        #region "Property defaults"
        self.folder = ""
        self.handler = ""
        self.env = ""
        self.ext = ""

        #endregion  

        #region "Set Meta info"
        SerialBase.__init__(self , SerialF(fname="ZODA_TRANS"), **kwargs)  

        #endregion
    
    #endregion

    #region Methods
    def kwargs(self):
        kw = {}
        kw["folder"] = self.folder 
        kw["handler"] = self.handler 
        kw["env"] = self.env 
        kw["ext"] = self.ext 
        return kw

    #end region

#endregion

#endregion

class AppServerSvc (win32serviceutil.ServiceFramework):
    
    _svc_name_ = "pyEDI"
    _svc_display_name_ = "pyEDI"

    def __init__(self,args):
        
        #region Create Log
        self.log = mLog()
        self.log.start( os.path.abspath(os.path.dirname(__file__)), "DEBUG" )
        self.log.logger.debug("Starting {}".format(__file__))          
        
        #endregion
        
        self.args = clArg(args=args)
        self.settingsfile = "{}\\{}.json".format(            
            os.path.abspath(
                os.path.dirname(__file__).rstrip("\\")
            ), "pyEDI"
        )
        self.fs = []

        try:
            self.log.logger.debug("Opening settings file {}".format(self.settingsfile))
            if not exists(self.settingsfile):
                raise NameError("Settings file {} not found.".format(self.settingsfile) )

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
                
        except Exception as e:
            self.log.logger.critical(str(e))
            print(str(e))            
        
        win32serviceutil.ServiceFramework.__init__(self,args)
        self.hWaitStop = win32event.CreateEvent(None,0,0,None)
        
        self.stop_requested = False

    def SvcStop(self):
        self.log.logger.debug("Stopping {}...".format(__file__)) 
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        
        self.stop_requested = True

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_,''))
        self.main()

    def main(self):
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

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(AppServerSvc)    
    