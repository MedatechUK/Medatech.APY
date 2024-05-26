## This is a replacement tool for XSD.exe.
## It infers serial classes based on file input.

import json 
from MedatechUK.cl import clArg
from MedatechUK.Serial import infer

if __name__ == '__main__':    

	arg = clArg()
	Output = []

	try:        
		if len(arg.args()) == 0:
			raise NameError("Please specify a filename.")
		if not arg.argExists(0):
			raise NameError("File [{}] not found.".format(arg.args()[0]))
		if arg.byName(["name"])==None:
			raise NameError("Please specify a class -name.".format(arg.args()[0]))
		
	except Exception as e:
		print(e)
		exit()

	with open(arg.args()[0], 'r') as the_file: 		
		inf = infer(json.loads(the_file.read()) , name=arg.byName(["name"]))
		
		inf.imp.append("from MedatechUK.mLog import mLog")
		inf.imp.append("from MedatechUK.oDataConfig import Config")

		Output.append("\n".join(inf.imp)) 				# Imports
		Output.append("")					
		Output.append("\n".join(inf.cls))				# Classes
		Output.append("\n".join(inf.preq))				# Process request Method

		Output.append("if __name__ == '__main__':")		# Main part
		Output.append("    with open(\"{}\", \"r\") as the_file:".format(arg.args()[0]))
		Output.append("        q = {}(_json=the_file)".format(arg.byName(["name"])))
		Output.append("        print(json.dumps(json.loads(q.toFlatOdata()),indent=4, sort_keys=False))")	

	if len(arg.args()) > 1:

		# Output to file
		with open(arg.args()[1], 'w') as out_file: 
			out_file.write("\n".join(Output))

	else:
		# Output to screen
		print("\n".join(Output))