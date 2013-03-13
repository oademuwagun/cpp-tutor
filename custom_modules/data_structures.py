import json
#import gdb

""" Codes for some data types """
TYPE_CODE_CHAR = 20
TYPE_CODE_ARRAY = 2


""" Super class for variables and objects """
class Data(object):
	def __init__(self, type=None, address=None):
		self.type = type
		self.address = address

class Variable(Data):
	def __init__(self, name=None, type=None, address=None, value=None, is_return_value=False):
		Data.__init__(self, type, address)
		self.name = name
		self.reference = None
		self.address = str(value.address).split()[0] if value else None
		self.reference_address = None
		self.value = None
		self.is_return_value = is_return_value

		self.__set_value(value)
		#self.__set_address()
		self.__set_reference(value)

	def __set_value(self, val):
		if val != None:
			#Using the type code comparisons was not working for some reason.
			#So I used this method to determine the types
			if str(self.type)=="char" and val != None:
				self.value = str(val).split()[-1]
			else:
				self.value = str(val)
		else:
			self.value = None

	def __set_address(self, value):
		if value != None:
			if self.type == "std::string":
				string_val = String.get_string_value(value)
				self.address = str(string_val[0].address).split()[0]
			else:
				self.address = str(value.address).split()[0]
		else:
			self.address = None			


	def __set_reference(self, value):
		if self.type.code == TYPE_CODE_ARRAY:
			self.reference = Array(name=self.name, value=value)
			self.value=None
		elif str(self.type) == "std::string":
			string_val = String.get_string_value(value)
			string_address = str(string_val).split()[0]
			if string_address == "0x0": 
				self.reference = None
			else:
				self.reference = String(name=self.name, value=value)
			self.value = None


""" Represents complex data structures such as arrays, classes, strings, etc """
class Object(Data):
	def __init__(self, type=None, name=None, value=None):
		Data.__init__(self, type=type, address=None)
		self.name = name if name else ""
		#self.address =  str(address).split()[0] if address else 
		self.members = [] #list of variables in the object
		

class String(Object):
	def __init__(self, name=None, value=None):
		Object.__init__(self,  "string", name, value)
		self.__set_members(value)
		self.__set_address(value)

	@classmethod
	def get_string_value(self, value):
		return value['_M_dataplus']['_M_p']

	def __set_members(self, value):
		#'value_string' is in this format: [ADDRESS] [VALUE]
		#If the string has not been asigned memory. Its address is NULL (0X0)
		string_val = self.get_string_value(value)
		string_address = str(string_val).split()[0]

		#The value when converted to a string is in this format: [ADDRESS] [ACTUAL STRING]. 
		#We obtain the string's length using only the actual string portion
		#Decrement by 2 to account for the enclosing quotes

		#=== Big flaw in this approach ==========#
		string_length = len(str(string_val).split()[-1])-2 

		self.members = [Variable(type=string_val.type.target(), name=self.name+"["+str(i)+"]",\
			address=string_val[i].address, value=string_val[i]) \
			for i in range(string_length) ]

	def __set_address(self, value):
		string_val = String.get_string_value(value)
		self.address = str(string_val[0].address).split()[0]


class Array(Object):
	def __init__(self, name=None, value=None):
		Object.__init__(self, "array", name, value)
		self.__set_members(value)
		self.__set_address(value)

	def __set_members(self, value):
		#Get array length. Current bootleg method. 
		tmp = str(value.type).split()[-1]
		tmp = tmp.replace("[", "")
		tmp = tmp.replace("]", "")
		length = int(tmp)


		self.members = [Variable(type=value.type.target(), name=self.name+"["+str(i)+"]", \
			address=value[i].address, value=value[i]) \
			for i in range(length) ]

	def __set_address(self, value):
		self.address = str(value.address).split()[0]



""" Represents an item in the call stack """
class Frame:
	def __init__(self, name=None, variables=[]):
		self.name = name
		self.variables = variables if variables!=None else []



""" Represent the state at each step of execution """
class State:
	"""Had an issue with having an objects optional paramter"""
	def __init__(self, line_num, globals=[], frames=[]):
		self.line_num = line_num
		self.globals = globals #list of global variables
		self.frames = frames if frames!=None else []

		self.objects = [] # objects if objects!=None else []

		self.return_value = None #Applicable to only the return type state
		self.is_return_state = True #true if a function returns in the state


""" Custom encoder for all the objects """
class DataEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, Data) or isinstance(obj, Frame) or isinstance(obj, State):
			if isinstance(obj,Data):
				obj.type = str(obj.type)
				pass #obj.clean_up_data()
			return vars(obj) #All the variables and their values.
		return json.JSONEncoder.default(self, obj)