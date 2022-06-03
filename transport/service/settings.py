import os

from MedatechUK.Serial import SerialBase , SerialT , SerialF

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