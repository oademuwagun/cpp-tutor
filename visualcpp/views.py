from django.shortcuts import render
from django.template import Context
import logging, json, pickle
import subprocess as sub
from data_structures import Variable, Object, Frame, State, DataEncoder


# Get an instance of a logger
logger = logging.getLogger(__name__)
EXECUTABLE_FILE_NAME = "code"
SOURCE_FILE_NAME = EXECUTABLE_FILE_NAME+".cpp"
RESULT_FILE_NAME = "result"

def index(request):
    return render(request, "visualcpp/index.html")

def execute(request):
	context = Context()
	if request.method == "POST":
		if "code" in request.POST:
			code = request.POST.get("code").strip()
			
			with open(SOURCE_FILE_NAME, "w") as source_file:
				source_file.write(code) 

			command_string = "g++ -g %s -o %s" %(SOURCE_FILE_NAME, EXECUTABLE_FILE_NAME) 
			process = sub.Popen(command_string, stdin=sub.PIPE, stdout=sub.PIPE, stderr=sub.PIPE, shell=True)
			output, errors = process.communicate()
			errors = errors.splitlines() #Convert the error string to a list

			#If there are no errors, run the code and analyze
			if len(errors) == 0 :
				return_code = sub.call("./analyze.py", stdin=sub.PIPE, stdout=sub.PIPE, stderr=sub.PIPE, shell=True) 

				with open(RESULT_FILE_NAME) as result_file:
					result_of_analysis = pickle.load(result_file)

				context["result_size"] = len(result_of_analysis)
				context["visualization"] = json.dumps(result_of_analysis, cls=DataEncoder)

			context["errors"] = errors
			context["output"] = output.splitlines()
			context["code"] = code
	else:
		pass
		#context = Context()
	return render(request, "visualcpp/index.html", context)
