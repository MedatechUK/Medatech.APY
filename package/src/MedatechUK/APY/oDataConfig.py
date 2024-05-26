######################################################
## si@medatechuk.com
## 12/09/21
## https://github.com/MedatechUK/Medatech.APY
##
## Load configuration file containg settings for the
## loading. This may be either the IIS web.config or
## from a file called constants.py in the root dir.
##
## Example constant.py:
#    oDataHost ="walrus.ntsa.uk"
#    tabulaini ="tabula.ini"
#    ouser ="apiuser"
#    opass ="123456"
#    Environment = "wlnd"

import os, json
import xmltodict
import inspect
import pyodbc
import configparser

from MedatechUK.mLog import mLog

class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

class Config:

    ## Ctor
    def __init__(self, **kwargs):

        ## Register for log
        self.log = mLog()

        ## Init Vars
        self.config = {}
        self.oDataHost = ''
        self.tabulaini = ''
        self.ouser = ''
        self.opass = ''
        self.path = ""
        self.connstr = 'Server=localhost\PRI,1433;Trusted_Connection=Yes;MultipleActiveResultSets=true;'

        for arg in kwargs.keys():
            ## If it's a request then take the environment
            #  from the request object
            if arg == 'request' :
                self.log.logger.debug("Opening [{}].".format( self.path + '\web.config' ))
                self.path = kwargs[arg].path
                self.environment = kwargs[arg].environment

                ## Try the web.config first
                if os.path.isfile(self.path + "\web.config"):
                    self.SettingfromWebConfig()
                else:
                    raise ("Not found [{}\\web.config].".format( self.path ))

            ## If there's no request (i.e. not a web integration)
            #  use the odata environment
            if arg == 'env':
                match kwargs[arg].lower():
                    case 'test' :
                        self.log.logger.debug("Verifying settings at [{}].".format( self.path + '\settings.ini' ))
                    case _ :
                        self.log.logger.debug("Opening [{}].".format( self.path + '\settings.ini' ))
                        
                self.path = kwargs['path']
                self.environment = kwargs[arg]
                self.settingsini = self.path + "\\settings.ini"

                #region "Verify .ini"
                save = False
                if os.path.isfile(self.settingsini):
                    config = configparser.ConfigParser()
                    config.read(self.settingsini)
                    if 'odata' not in config.sections():
                        config['odata'] = {}
                        save = True
                    if not config['odata'].__contains__("odatahost"):
                        config['odata']['oDataHost'] = 'priority.localhost'
                        save = True
                    if not config['odata'].__contains__("tabulaini"):
                        config['odata']['tabulaini'] = 'tabula.ini'
                        save = True
                    if not config['odata'].__contains__("ouser"):
                        config['odata']['ouser'] = 'apiuser'
                        save = True
                    if not config['odata'].__contains__("opass"):
                        config['odata']['opass'] = 'password'
                        save = True
                    if not config['odata'].__contains__("ENV"):
                        config['odata']['ENV'] = 'demo'
                        save = True

                    if 'db' not in config.sections():
                        config['db'] = {}
                        save = True
                    if not config['db'].__contains__("server"):
                        config['db']['SERVER'] = 'localhost\PRI'
                        save = True
                    if not config['db'].__contains__("credentials"):
                        config['db']['CREDENTIALS'] = 'Trusted_Connection=Yes'
                        save = True

                else:
                    save = True
                    config = configparser.ConfigParser()
                    config['odata'] = {}
                    config['odata']['oDataHost'] = 'priority.localhost'
                    config['odata']['tabulaini'] = 'tabula.ini'
                    config['odata']['ouser'] = 'apiuser'
                    config['odata']['opass'] = 'password'
                    config['odata']['ENV'] = 'demo'
                    config['db'] = {}
                    config['db']['SERVER'] = 'localhost\PRI'
                    config['db']['CREDENTIALS'] = 'Trusted_Connection=Yes'
                    with open(self.settingsini, 'w') as configfile:
                        config.write(configfile)

                if save :
                    with open(self.settingsini, 'w') as configfile:
                        config.write(configfile)
                    raise NameError("Made [{}]: Please config.".format( self.settingsini ))

                #endregion
                 
                self.SettingfromConstants()

    ## Load setting from the IIS web.config
    def SettingfromWebConfig(self):
        ## Load the config file        
        with open(self.path + '\web.config') as fd:
            self.config = xmltodict.parse(fd.read(), process_namespaces=True)

        ## Get the oData settings from the web.config
        for k in self.config['configuration']['appSettings']['add']:
            match k['@key'].upper():
                case "ODATAHOST": self.oDataHost = k['@value'].split("//")[1]
                case 'TABULAINI': self.tabulaini = k['@value']
                case 'OUSER': self.ouser = k['@value']
                case 'OPASS': self.opass = k['@value']

        ## Get the Priority Database connection string from the web.config
        if str(type(self.config['configuration']['connectionStrings']['add'])) =="<class 'list'>":
            for k in self.config['configuration']['connectionStrings']['add']:
                if k['@name'].upper() == 'PRIORITY':
                    self.connstr = k['@connectionString']
        if str(type(self.config['configuration']['connectionStrings']['add'])) =="<class 'collections.OrderedDict'>":
            if self.config['configuration']['connectionStrings']['add']['@name'].upper() == 'PRIORITY':
                self.connstr = self.config['configuration']['connectionStrings']['add']['@connectionString']

    def SettingfromConstants(self):
        ## Load settings from file settings.ini        
        config = configparser.ConfigParser(dict_type=AttrDict)
        config.read(self.path + '//settings.ini')

        self.oDataHost = config._sections.odata.odatahost
        self.tabulaini =  config._sections.odata.tabulaini
        self.ouser =  config._sections.odata.ouser
        self.opass =  config._sections.odata.opass
        self.connstr = "SERVER={};{};MARS_Connection=Yes".format(
            config._sections.db.server
            , config._sections.db.credentials
        )
        self.config = config._sections

    def CheckEnviroment(self):
        self.log.logger.info("Checking environment [{}].".format( self.environment ))
        try:
            cnxn = self.cnxn()
        except:
            return False

        crsr = cnxn.cursor()
        crsr.execute("select DNAME from ENVIRONMENT where DNAME <> '' union all select 'system'")
        for row in [row for row in crsr.fetchall() if row.DNAME.lower() == self.environment.lower()] :
            # Set the environment to the cAsE of the db object
            self.environment = row.DNAME
            self.log.logger.info("Environment [{}] OK!".format( self.environment ))
            return True

        # Environment not found
        return False

    def cnxn(self):
        cnstr = ''
        # Find installed driver
        for dr in [dr for dr in pyodbc.drivers() if "for SQL Server" in dr]:
            cnstr = "Driver={{{}}};DATABASE=system;{}".format( dr , self.connstr )
            try:
                return pyodbc.connect(cnstr)
            except Exception as e:
                self.log.logger.critical("Could not connect to {}.".format(cnstr))
                raise

        self.log.logger.critical("No pyodbc driver installed.")
        raise TypeError("No pyodbc driver")

                  