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
		self.__raw_address = self.address = value.address if value else None
		self.__raw_value = self.value = None
		self.value_string = None
		self.is_return_value = is_return_value
		self.is_reference_type = False

		self.__set_value(value)
		#self.__set_address()

		if self.is_a_reference():
			self.is_reference_type = True
			self.__set_reference()
			self.value = None 

			

	def __set_value(self, val):
		"""Note. It is very important that """
		print self.type
		if val != None:
			#Using the type code comparisons was not working for some reason.
			#So I used this method to determine the types
			if str(self.type)=="char" and val != None:
				self.value = val
				self.value_string = str(val).split()[-1]
			elif str(self.type)=="std::string":
				self.value = self.get_string_value(val)
				self.value_string = str(self.value)
			else:
				self.value = val
				self.value_string = str(val)
		else:
			self.value = val
			self.value_string = str(val)

	def __set_address(self):
		if self.value != None:
			if self.type == "std::string":
				self.__raw_address = self.address = self.value[0].address

			else:
				self.__raw_address = self.address = self.value.address
		else:
			self.__raw_address = self.address = None			

	def is_a_reference(self):
		reference_types = [TYPE_CODE_ARRAY]
		if self.type:
			if str(self.type) == "std::string" or self.type.code in reference_types:
				return True
			return False

	def __set_reference(self):
		if self.type.code == TYPE_CODE_ARRAY:
			self.convert_to_array()
		elif str(self.type) == "std::string":
			self.convert_to_string()


	def convert_to_array(self):
		#Get array length. Current bootleg method. 
		tmp = str(self.value.type).split()[-1]
		tmp = tmp.replace("[", "")
		tmp = tmp.replace("]", "")
		length = int(tmp)

		array_items = [Variable(type=self.value.type.target(), name=self.name+"["+str(i)+"]", \
			address=self.value[i].address, value=self.value[i]) \
			for i in range(length) ]

		self.reference = Object(type="array", address=self.address, members=array_items)

	def get_string_value(self, value):
		return value['_M_dataplus']['_M_p']

	def convert_to_string(self):
		#'value_string' is in this format: [ADDRESS] [VALUE]
		#If the string has not been asigned memory. Its address is NULL (0X0)
		string_address = self.value_string.split()[0]
		if string_address == "0x0": 
			self.reference = None
			return
		else:
			#The value when converted to a string is in this format: [ADDRESS] [ACTUAL STRING]. 
			#We obtain the string's length using only the actual string portion
			#Decrement by 2 to account for the enclosing quotes
			string_length = len(self.value_string.split()[-1])-2 

			string_items = [Variable(type=self.value.type.target(), name=self.name+"["+str(i)+"]",\
				address=self.value[i].address, value=self.value[i]) \
				for i in range(string_length) ]

			#Return string as an array of characters
			self.reference = Object(type="string", address=string_address, members=string_items)

	#Pre-processing for conversion to json. Unnecessary attributes are removed.
	def clean_up_data(self):
		self.type = str(self.type)
		self.address = str(self.address).split()[0]

		#Clear all raw values
		self.__raw_value = self.__raw_address = None

		"""Will have to review this when we start dealing with pointers"""
		if self.is_reference_type:
			if self.reference:
				self.reference = str(self.reference.address)
			self.value=None
		else:
			self.value = self.value_string
"""
	def is_uninitialized(self):
		if self.__raw_address and len(str(self.__raw_address).split()) == 1:
			return False
		return True """

	def raw_address(self):
		return self.__raw_address

""" Represents complex data structures such as arrays, classes, strings, etc """
class Object(Data):
	def __init__(self, type=None, address=None, members=[]):
		Data.__init__(self, type, address)
		self.address =  str(address).split()[0] if address else None
		self.members = members if members!=None else [] #list of variables in the object


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
			if isinstance(obj, Variable):
				obj.clean_up_data()
			return vars(obj) #All the variables and their values.
		return json.JSONEncoder.default(self, obj)