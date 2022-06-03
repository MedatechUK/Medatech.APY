import win32serviceutil
import win32service
import win32event
import servicemanager

import os , time , sys
from os.path import exists

from MedatechUK.cl import folderWatch , clArg
from MedatechUK.mLog import mLog

import settings

class AppServerSvc (win32serviceutil.ServiceFramework):
    
    _svc_name_ = "pyEDI"
    _svc_display_name_ = "pyEDI"

    def __init__(self,args):
        
        self.log = mLog()
        self.log.start( os.path.abspath(os.path.dirname(__file__)), "DEBUG" )
        self.log.logger.debug("Starting {}".format(__file__))          
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
    