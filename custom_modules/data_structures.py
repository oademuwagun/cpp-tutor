import json
import gdb

class DataEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, Data) or isinstance(obj, Frame) or isinstance(obj, State):
			if isinstance(obj, Variable):
				obj.clean_up_data()
			return vars(obj) #All the variables and their values.
		return json.JSONEncoder.default(self, obj)

class Data(object):
	def __init__(self, type=None, address=None):
		self.type = type
		self.address = address

class Variable(Data):
	def __init__(self, name=None, type=None, address=None, value=None, is_return_value=False):
		Data.__init__(self, type, address)
		self.name = name
		self.reference = None
		self.__raw_address = self.address = None
		self.__raw_value = self.value = None
		self.is_return_value = is_return_value
		self.is_reference_type = False

		try:
			self.__set_value(value)
			self.__set_address()

			if self.__is_a_reference():
				self.is_reference_type = True
				print "Setting reference"
				try:
					self.__set_reference()
					self.value = None #self.address
				except:
					#self.reference = None
					self.value = None
				print "Reference"
		except:
			pass
			return			

	def __set_value(self, val):
		print self.type
		if val != None:
			if self.type==gdb.TYPE_CODE_CHAR and val != None:
				self.value = str(val).split()[-1]
			elif self.type=="std::string":
				self.value = self.get_string_value(val)
			else:
				self.value = val
		else:
			self.value = val

	def __set_address(self):
		if self.value != None:
			if self.type == "std::string":
				self.__raw_address = self.address = self.value[0].address
				print "Okay"
				print self.name
			else:
				print "Wood"
				print self.name
				self.__raw_address = self.address = self.value.address
		else:
			print "DSDF"
			print self.name
			self.__raw_address = self.address = None			

	def __is_a_reference(self):
		reference_types = [gdb.TYPE_CODE_ARRAY]
		if str(self.type) == "std::string" or self.type.code in reference_types:
			return True
		else:
			return False

	def __set_reference(self):
		if self.value.type.code == gdb.TYPE_CODE_ARRAY:
			self.reference = self.convert_to_array()
		elif str(self.value.type) == "std::string":
			self.reference = self.convert_to_string()


	def convert_to_array(self):
		#Get array length. Current bootleg method. 
		tmp = str(self.value.type).split()[-1]
		tmp = tmp.replace("[", "")
		tmp = tmp.replace("]", "")
		length = int(tmp)

		array_items = [Variable(type=self.value.type.target(), name=self.name+"["+str(i)+"]", \
			address=self.value[i].address, value=self.value[i]) \
			for i in range(length) ]

		return Object(type="array", address=self.address, members=array_items)

	def get_string_value(self, value):
		return value['_M_dataplus']['_M_p']

	"""Permanently modifies values. So can't be meant to be called once"""
	def convert_to_string(self):

		#The value when converted to a string is in this format: [ADDRESS] [ACTUAL STRING]. 
		#We obtain the string's length using only the actual string portion
		string_length = len(str(self.value).split()[-1])

		string_items = [Variable(type=self.value.type.target(), name=self.name+"["+str(i)+"]",\
			address=self.value[i].address, value=self.value[i]) \
			for i in range(string_length) ]

		#Return string as an array of characters
		return Object(type="string", address=self.address, members=string_items)

	#Pre-processing for conversion to json. Unnecessary attributes are removed.
	def clean_up_data(self):
		self.type = str(self.type)
		self.address = str(self.address).split()[0]

		#Clear all raw values
		self.__raw_value = self.__raw_address = None

		"""Will have to review this when we start dealing with pointers"""

		if self.is_reference_type:
			if self.reference:
				try:
					self.reference = str(self.value.address).split()[0]
				except:
					print "DDASD"
					self.reference =None
			self.value=None
		else:
			self.value = str(self.value)

	def is_uninitialized(self):
		if self.__raw_address and len(str(self.__raw_address).split()) == 1:
			return False
		return True

	def raw_address(self):
		return self.__raw_address



class Object(Data):
	def __init__(self, type=None, address=None, members=[]):
		Data.__init__(self, type, address)
		self.address = "" #str(address) if address else None
		self.members = members if members!=None else [] #list of variables in the object


class Frame:
	def __init__(self, name=None, variables=[]):
		self.name = name
		self.variables = variables if variables!=None else []

class State:
	"""Had an issue with having an objects optional paramter"""
	def __init__(self, line_num, globals=[], frames=[]):
		self.line_num = line_num
		self.globals = globals #list of global variables
		self.frames = frames if frames!=None else []

		self.objects = [] # objects if objects!=None else []

		self.return_value = None #Applicable to only the return type state
		self.is_return_state = True #true if a function returns in the state
