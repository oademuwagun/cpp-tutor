#!/usr/bin/gdb -x
import gdb
import sys
import pickle
from data_structures import Variable, Object, Frame, State, DataEncoder
import json

states = []
EXECUTABLE_FILE_NAME = "code"
SOURCE_FILE_NAME = EXECUTABLE_FILE_NAME +".cpp"
STATES_OUTPUT_FILE = "result"

class CustomFinishBreakpoint(gdb.FinishBreakpoint):
	__all_frames_with_breakpoint = set([])

	@classmethod
	def frame_has_finish_bp(self, frame):
		return frame in __all_frames_with_breakpoint

	def __init__(self, frame):
		super(gdb.FinishBreakpoint, self).__init__(frame)
		__all_frames_with_breakpoint.add(frame)

	def stop (self):
		print "normal finish"
		add_current_state()
		return True

	def out_of_scope ():
		print "abnormal finish"


def get_global_variables():
	current_frame = gdb.newest_frame()
	
	if current_frame and current_frame.is_valid:
		current_block = current_frame.block()
		if current_block:
			if current_block.is_global:
				global_block = current_block
			else:
				global_block = current_block.global_block
	return get_frame_variables(current_frame, global_block)


"""Get all the frames currently active"""
def get_current_frames():
	frames = []
	current_frame = gdb.newest_frame()
	while current_frame:
		if current_frame.name():
			frames.append( Frame( name=current_frame.name(), \
				variables=get_frame_variables(current_frame, current_frame.block() ) ) )
		current_frame = current_frame.older()

	#Set breakpoint on all functions called in main and not main
	#because an exception is thrown if I set finish breakpoint on main.. I think
	#Investigate further.
	newest_frame = gdb.newest_frame()
	if newest_frame.name() != "main" and CustomFinishBreakpoint.frame_has_finish_bp(newest_frame):
			CustomFinishBreakpoint(current_frame) #set breakpoint on current frame
	return frames

""" Gets all the variables ( I believe all the global variables ) in a frame """
def get_frame_variables(frame, block):
	all_frame_variables = []
	if block and block.is_valid():
		for symbol in block:
			if not symbol.is_function and symbol.is_valid() and symbol.print_name != "__dso_handle":
				#ONly consider variabled defined in the source file (so ignore external libraries)
				if symbol.symtab.filename == SOURCE_FILE_NAME:
					variable_value = frame.read_var(symbol, block)
					variable = Variable(type=symbol.type, name=symbol.print_name, \
						value=variable_value)
					all_frame_variables.append(variable)
	return all_frame_variables


def get_current_line(frame):
	return frame.find_sal().line

def add_current_state():
	current_frame = gdb.newest_frame()
	if current_frame and current_frame.is_valid() :
		"""If the current line is 0, then continue to run the program until it exits.
		Note that this is the way I currently check if my program has exited from main 
		if not I will get an error in the next line. """
		if get_current_line(current_frame) == 0:
			gdb.execute("continue")
		else:
			print current_frame.name() 
			current_state = State(line_num=get_current_line(current_frame), globals=get_global_variables(), \
				frames=get_current_frames())

			""" Get objects """ 
			for frame in current_state.frames:
				for variable in frame.variables:
					print variable.name
					#print variable.is_uninitialized()
					print variable.raw_address()
					print variable.is_reference_type
					if variable.is_reference_type and variable.reference:
						current_state.objects.append( variable.reference )

			states.append(current_state)

	
def exit_gdb(event):
	print json.dumps(states, cls=DataEncoder)
	pickle.dump(states, open(STATES_OUTPUT_FILE, "wb"))
	gdb.execute("quit")



gdb.events.exited.connect(exit_gdb)

gdb.execute("file "+ EXECUTABLE_FILE_NAME)

#Don't break at the first line. 
#It won't work if you define anothe function other than main at the beginning
gdb.execute("break main") 
gdb.execute("run")

while True:
	add_current_state()
	gdb.execute("step")













