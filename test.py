from MedatechUK.odata import Load
from MedatechUK.odata import oResponse

# Create the oData Loading
l = Load(
    # The oData loading code in Priority
    # For web requests the Load type is 
    # the endpoint extention
    ltype = "ABC",
    
    # The config file stores the data required 
    # in order to unpack the same serial data
    # into the same fields in Priority for every 
    # load. For web requests the Config file is the
    # name of the endpoint defined by the request URL
    c = "newTransactions" + ".config",

    # The oData module has 3 run modes, allowing
    # processing of data from file, object or APY request:    
    #   request = apy.Request ) Either
    #   f = "filename"      ) Or
    #   o = object          ) Or
    f = 'newTransactions.json',
    
    # The Priority company into which we will load data
    # The environment variable is set by the request URL
    # when the run mode is request.
    # Set this *ONLY* when using file/object run modes.
    env = "wlnd"
)

# Get a response structure to hold the oData result
r = oResponse()

# POST the oData to Priority
l.post(r)   

# Display the result from the oData service
print("{}: {}\n{}".format(r.Status, r.Message, r.data))