import os , time , sys
from pathlib import Path

import win32serviceutil , win32service , win32event, servicemanager
import configparser , debugpy

from MedatechUK.APY.mLog import mLog
from MedatechUK.APY.cl import clArg
from MedatechUK.APY.oDataConfig import Config

class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

class AppSvc (win32serviceutil.ServiceFramework):

#region "Properties"
    @property
    def Main(self):
        try: return self._Main
        except: return None
    @Main.setter
    def Main(self, value):
        self._Main = value

    @property
    def Init(self):
        try: return self._Init
        except: return None
    @Init.setter
    def Init(self, value):
        self._Init = value

    @property
    def Folder(self):
        try: return self._Folder
        except: return os.getcwd()
    @Folder.setter
    def Folder(self, value):
        if os.path.isdir(str(value)):
            self._Folder = value
        else: raise "Invalid folder spec."

#endregion

#region "Ctor"
    def __init__(self,args):

        win32serviceutil.ServiceFramework.__init__(self,args)
        self.hWaitStop = win32event.CreateEvent(None,0,0,None)
        self.stop = False

        self.settingsini = str(self.Folder) + "\\settings.ini"
        os.chdir(self.Folder)

        #region "Verify .ini"
        if os.path.isfile(self.settingsini):
            config = configparser.ConfigParser()
            config.read(self.settingsini)
            save = False
            if 'debug' not in config.sections():
                config['debug'] = {}
                save = True
            if not config['debug'].__contains__("verbosity"):
                config['debug']['VERBOSITY'] = 'DEBUG'
                save = True
            if not config['debug'].__contains__("port"):
                config['debug']['PORT'] = '5678'
                save = True
            if not config['debug'].__contains__("FORCE"):
                config['debug']['FORCE'] = 'ON'
                save = True                
        else:
            save = True
            config = configparser.ConfigParser()
            config['debug'] = {}
            config['debug']['VERBOSITY'] = 'DEBUG'
            config['debug']['PORT'] = '5678'
            config['debug']['FORCE'] = 'ON'
        
        if save :
            with open(self.settingsini, 'w') as configfile:
                config.write(configfile)

        #endregion

        config = configparser.ConfigParser(dict_type=AttrDict)
        config.read(self.settingsini)
        self.config = config._sections

        self.log = mLog()
        self.log.start( str(self.Folder) , self.config.debug.verbosity )
        self.log.logger.info("Intialising Service [{}] with Verbosity [{}]...".format(
            self._svc_name_
            , self.config.debug.verbosity
        ))        
        self.log.logger.info("Using Settings file: [{}]".format( self.settingsini ))

        self.clArg = clArg(args=args)
        self.debug = ( 'debug' in self.clArg.kwargs() or self.config.debug.force.lower() == "on" )
        if self.debug:
            self.log.logger.info("debugpy listening on: [{}]".format(self.config.debug.port))
            debugpy.configure(python=str(Path(sys.executable).parent) + "\\python.exe")
            debugpy.listen( int( self.config.debug.port ) )
            # debugpy.wait_for_client() 
            # debugpy.breakpoint() 

        self.debuginit = False
        if self.Init != None:
            if self.debug :
                if 'debug'.lower() in self.clArg.kwargs() :
                    self.debuginit = self.clArg.kwargs()["debug"] == "init".lower()
                if self.debuginit:
                    debugpy.wait_for_client()  
            try :                  
                self.Init(self)
                
            except Exception as error:
                self.log.logger.critical(error)
                self.stop = True
                return

        try:
            Config(
                env = 'test'
                , path = str(self.Folder)
            )
        except Exception as error:
            self.log.logger.critical(error)
            self.stop = True
            return

        self.oDataConfig = Config(
                env = self.config.odata.env
                , path = str(self.Folder)
            )
        
        if self.Main == None:
            self.log.logger.critical("No Main() entry point.")
            self.stop = True
            return
                
        self.log.logger.info("Starting Service [{}]...".format(self._svc_name_ ))
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                        servicemanager.PYS_SERVICE_STARTED,
                        (self._svc_name_,''))
#endregion

#region "Methods"
    def SvcStop(self):
        self.log.logger.info("Service [{}] Stopping...".format(self._svc_name_ ))
        if self.debug: debugpy.wait_for_client.cancel()

        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.stop = True

    def SvcDoRun(self):
        while not self.stop:
            try:
                if self.debug: debugpy.wait_for_client()
                self.Main(self)

            except Exception as error:
                self.log.logger.critical(error)
                raise

            for i in range(50): # 5 seconds
                if not self.stop:
                    time.sleep(.1)
                if self.stop: break

#endregion