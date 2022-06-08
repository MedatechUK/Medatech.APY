import json , uuid , os , sys

from datetime import datetime
from dateutil.parser import parse
from os.path import exists

from MedatechUK.Serial import SerialBase , SerialT , SerialF
from MedatechUK.mLog import mLog
from MedatechUK.apy import Response
from MedatechUK.oDataConfig import Config
from MedatechUK.epdm import xmlTransactions
from MedatechUK.cl import clArg

class ECO(SerialBase):

    #region Properties
    @property
    def child(self): 
        return self._child
    @child.setter
    def child(self, value):
        self._child = []
        for i in range(len(value)):
            if len(value) > 1 :
                self._child.append(ECOChild(**value[i]))
            else :
                self._child.append(ECOChild(**value))

    @property
    def Number(self): 
        return self._Number
    @Number.setter
    def Number(self, value):
        self._Number = value    

    @property
    def Part_Family(self): 
        return self._Part_Family
    @Part_Family.setter
    def Part_Family(self, value):
        self._Part_Family = value   

    @property
    def Part_Type(self): 
        return self._Part_Type
    @Part_Type.setter
    def Part_Type(self, value):
        self._Part_Type = value   

    @property
    def Revision(self): 
        return self._Revision
    @Revision.setter
    def Revision(self, value):
        self._Revision = value   

    @property
    def Description(self): 
        return self._Description
    @Description.setter
    def Description(self, value):
        self._Description = value   

    @property
    def Factory_Unit(self): 
        return self._Factory_Unit
    @Factory_Unit.setter
    def Factory_Unit(self, value):
        self._Factory_Unit = value   
    
    @property
    def PDFLocation(self): 
        return self._PDFLocation
    @PDFLocation.setter
    def PDFLocation(self, value):
        self._PDFLocation = value   

    @property
    def ECO_Details(self): 
        return self._ECO_Details
    @ECO_Details.setter
    def ECO_Details(self, value):
        self._ECO_Details = value   

    @property
    def ECO_Reason(self): 
        return self._ECO_Reason
    @ECO_Reason.setter
    def ECO_Reason(self, value):
        self._ECO_Reason = value   

    @property
    def Code(self): 
        return self._Code
    @Code.setter
    def Code(self, value):
        self._Code = value   

    @property
    def State(self): 
        return self._State
    @State.setter
    def State(self, value):
        self._State = value   

    @property
    def Reference_Count(self): 
        return self._Reference_Count
    @Reference_Count.setter
    def Reference_Count(self, value):
        self._Reference_Count = value   

    @property
    def Assigned_To(self): 
        return self._Assigned_To
    @Assigned_To.setter
    def Assigned_To(self, value):
        self._Assigned_To = value   

    @property
    def Conversion_Ratio(self): 
        return self._Conversion_Ratio
    @Conversion_Ratio.setter
    def Conversion_Ratio(self, value):
        self._Conversion_Ratio = value   

    @property
    def Buy__Sell_Unit(self): 
        return self._Buy__Sell_Unit
    @Buy__Sell_Unit.setter
    def Buy__Sell_Unit(self, value):
        self._Buy__Sell_Unit = value    

    #endregion

    #region "ctor"
    def __init__(self,  **kwargs): 

        #region "Property defaults"
        self._Number = ''        
        self._Part_Family = ''     
        self._Part_Type = ''
        self._Description = ''
        self._Buy__Sell_Unit = ''
        self._Reference_Count = 0.0
        self._Conversion_Ratio = 0.0
        self._Assigned_To = ''
        self._State = ''
        self._Code = ''
        self._Factory_Unit = ''
        self._ECO_Reason = ''
        self._ECO_Details = ''
        self._PDFLocation = ''
        self._Revision = ''
        self._child = []
        
        #endregion

        #region "Set Meta info"
        SerialBase.__init__(self , SerialF(fname="ZODA_TRANS", rt=1 , typename="SW") , **kwargs)  

        SerialT(self, "rt")
        SerialT(self, "bubbleid")
        SerialT(self, "typename")        
        SerialT(self, "Revision" , pCol="TEXT1" )
        SerialT(self, "Number" , pCol="TEXT2" )
        SerialT(self, "Description" , pCol="TEXT3" )
   
        #endregion
    
    #endregion

class ECOChild(SerialBase):

    #region Properties
    @property
    def Number(self): 
        return self._Number
    @Number.setter
    def Number(self, value):
        self._Number = value    

    @property
    def Part_Family(self): 
        return self._Part_Family
    @Part_Family.setter
    def Part_Family(self, value):
        self._Part_Family = value   

    @property
    def Part_Type(self): 
        return self._Part_Type
    @Part_Type.setter
    def Part_Type(self, value):
        self._Part_Type = value   

    @property
    def Revision(self): 
        return self._Revision
    @Revision.setter
    def Revision(self, value):
        self._Revision = value   

    @property
    def Description(self): 
        return self._Description
    @Description.setter
    def Description(self, value):
        self._Description = value   

    @property
    def Factory_Unit(self): 
        return self._Factory_Unit
    @Factory_Unit.setter
    def Factory_Unit(self, value):
        self._Factory_Unit = value   
    
    @property
    def PDFLocation(self): 
        return self._PDFLocation
    @PDFLocation.setter
    def PDFLocation(self, value):
        self._PDFLocation = value   

    @property
    def ECO_Details(self): 
        return self._ECO_Details
    @ECO_Details.setter
    def ECO_Details(self, value):
        self._ECO_Details = value   

    @property
    def ECO_Reason(self): 
        return self._ECO_Reason
    @ECO_Reason.setter
    def ECO_Reason(self, value):
        self._ECO_Reason = value   

    @property
    def Code(self): 
        return self._Code
    @Code.setter
    def Code(self, value):
        self._Code = value   

    @property
    def State(self): 
        return self._State
    @State.setter
    def State(self, value):
        self._State = value   

    @property
    def Reference_Count(self): 
        return self._Reference_Count
    @Reference_Count.setter
    def Reference_Count(self, value):
        self._Reference_Count = value   

    @property
    def Assigned_To(self): 
        return self._Assigned_To
    @Assigned_To.setter
    def Assigned_To(self, value):
        self._Assigned_To = value   

    @property
    def Conversion_Ratio(self): 
        return self._Conversion_Ratio
    @Conversion_Ratio.setter
    def Conversion_Ratio(self, value):
        self._Conversion_Ratio = value   

    @property
    def Buy__Sell_Unit(self): 
        return self._Buy__Sell_Unit
    @Buy__Sell_Unit.setter
    def Buy__Sell_Unit(self, value):
        self._Buy__Sell_Unit = value    

    #endregion

    #region "ctor"
    def __init__(self,  **kwargs): 

        #region "Property defaults"
        self._Number = ''        
        self._Part_Family = ''     
        self._Part_Type = ''
        self._Description = ''
        self._Buy__Sell_Unit = ''
        self._Reference_Count = 0.0
        self._Conversion_Ratio = 0.0
        self._Assigned_To = ''
        self._State = ''
        self._Code = ''
        self._Factory_Unit = ''
        self._ECO_Reason = ''
        self._ECO_Details = ''
        self._PDFLocation = ''
        self._Revision = ''
        
        #endregion

        #region "Set Meta info"
        SerialBase.__init__(self , SerialF(fname="child", rt=2 ) , **kwargs)  

        SerialT(self, "rt")
        SerialT(self, "Number" , pCol="TEXT1" )
        SerialT(self, "Reference_Count" , pCol="REAL1" , pType="REAL")            
   
        #endregion
    
    #endregion
        
def readConfig(configuration):

    q = ECO(**configuration.kwargs())
    if len(configuration.references) > 0 :
        for s in configuration.references :
            q.child.append(ECOChild(**s.configuration.kwargs()))
    
    print(q.toSQL())

    if False:
        # Create an object to hold the result    
        r = Response()    
        # region Send to Priority
        q.toPri(                    # Send this object to Priority        
            Config(                 # Using this configuration
                env=arg.byName(['e','env']) ,            # the Priority environment
                path=os.getcwd()        # the location of the config file
            ) , 
            q.toFlatOdata ,         # Method to generate oData Commands
                                        # toFlatOdata - send to oData load form
                                        # toOdata - send to nested Priority forms
                                        # OR a custom method.        
            response=r              # the apy request/response object. Use:
                                        # for command:      response=Response   (a new response is used)
                                        # for apy usage:    request=request     (the request.response is used)
        )

        #endregion
        
        # Display the result
        print( "[{}]: {}".format( r.Status , r.Message ))
        print( "response : " + json.dumps( r.data , sort_keys=False, indent=4 ))

def recurse(document):

    if len(document.configuration.references) > 0 :
        for d in document.configuration.references :
            recurse(d)
        readConfig(document.configuration)
    else:
        readConfig(document.configuration)        

if __name__ == '__main__':    

    arg = clArg()

    #region "Create a log file"
    log = mLog()    
    if arg.byName(["cwd" , "path"]) != None:
        if not exists(arg.byName(["cwd" , "path"])):
            raise NameError("Specified working directory {} is missing.".format(arg.byName(["cwd" , "path"])))
        else:
            os.chdir(arg.byName(["cwd" , "path"]))
    
    log.start( os.getcwd() , "DEBUG" )            
    log.logger.debug("Starting {}".format(__file__))                 

    #endregion    
    
    try:     
    
        #region Check Arguments   
        if len(arg.args()) == 0 :
            raise NameError("No file specified.")

        if not exists(arg.args()[0]):
            raise NameError("File {} does not exist.".format(arg.args()[0]))

        if arg.byName(["e" , "env"]) == None:
            raise NameError("No environment specified.")

        #endregion

        with open(arg.args()[0], 'r') as the_file:        
            q = xmlTransactions(_xml=the_file)
            for t in q.transactions:
                recurse(t.document)

    except Exception as e:
        log.logger.critical(str(e))
        print(e)