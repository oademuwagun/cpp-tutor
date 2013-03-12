#!/usr/bin/gdb -x
import gdb
import sys
import pickle
from data_structures import Variable, Object, Frame, State

states = []
EXECUTABLE_FILE_NAME = "code"
SOURCE_FILE_NAME = EXECUTABLE_FILE_NAME +".cpp"
STATES_OUTPUT_FILE = "result"

class CustomFinishBreakpoint(gdb.FinishBreakpoint):
	def stop (self):
		print "normal finish"
		get_current_state()
		states[len(states)-1]["type"] = "return"
		states[len(states)-1]["return"] = self.return_value
		return True

	def out_of_scope ():
		print "abnormal finish"


def is_new_frame(frame):
	if frame != None and frame.name != None:
		#If this is the first state or the frame was not in previous state 
		if len(states) == 0 or frame.name() not in states[len(states)-1]["frames"]:	
			return True

def get_global_variables():
	current_frame = gdb.newest_frame()
	
	if current_frame and current_frame.is_valid:
		current_block = current_frame.block()
	if current_block:
		if current_block.is_global:
			global_block = current_block
		else:
			global_block = current_block.global_block
	return get_data(current_frame, global_block)

def get_current_frames():
	frames = []
	current_frame = gdb.newest_frame()
	while current_frame:
		if current_frame.name():
			frames.append( current_frame )
		current_frame = current_frame.older()
	#Set breakpoint on all functions called in main and not main
	#because an exception is thrown if I set finish breakpoint on main.. I think
	#Investigate further.
	if is_new_frame(current_frame) and len(frames) > 1:
		CustomFinishBreakpoint(current_frame) #set breakpoint on current frame
	return frames

def get_data(frame, block):
	data = {}
	if block and block.is_valid():
		for symbol in block:
			if not symbol.is_function and symbol.is_valid():
				#Ignore symbols not defined in the source file. All external
				#library symbols will be ignored.
				if symbol.symtab.filename == SOURCE_FILE_NAME:
					print symbol.name
					print symbol.type
					data[symbol.print_name] = str(frame.read_var(symbol, block))
	return data

def get_current_state():
	current_frame = gdb.newest_frame()
	if current_frame and current_frame.is_valid() :
		"""If the current line is 0, then continue to run the program until it exits.
		Note that this is the way I currently check if my program has exited from main 
		if not I will get an error in the next line. """
		if current_frame.find_sal().line == 0:
			gdb.execute("continue")
		print current_frame.name() 

		current_frames = get_current_frames()
		current_state = {}
		current_state["frames"] = [frame.name() for frame in current_frames if frame.name()]
		current_state["data"] = {}
		for frame in current_frames:
			if frame.name():
				current_state["data"][frame.name()] = get_data(frame, frame.block() )
		current_state["global"] = get_global_variables()
		states.append(current_state)
		#print states
	
def exit_gdb(event):
	print states
	pickle.dump(states, open(STATES_OUTPUT_FILE, "wb"))
	gdb.execute("quit")



gdb.events.exited.connect(exit_gdb)

gdb.execute("file "+ EXECUTABLE_FILE_NAME)
gdb.execute("break main") #Break at first line
gdb.execute("run")

while True:
	get_current_state()
	gdb.execute("step")













