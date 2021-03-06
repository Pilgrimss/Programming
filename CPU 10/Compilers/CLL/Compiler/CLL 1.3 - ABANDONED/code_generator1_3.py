# To do:
#	- reorganise getting hold of variables
#	- calculate struct offsets
#	- get hold of values from structs
#	- write floating point library
#		- basic operations
#		- comparisons
#		- converting floats to ints and vice versa
#	- write casting operations - woop woop -Assembly!
#	- Reoranise snippets - also eed to rorganise code generator for multiple snippet files 
# 	- conditional import snippet files - such as floating point
#	- rewrite signed snippets
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#	+ Addition
# 	- deletion
#	~ change
#__________________________________ changes 03/03 _________________________________________________
# + type indexing snippet
# + starting float comparison snippets
# + started snippets index


#__________________________________ 04/03 ________________________________
# + float comparison snippets complete
# + started float conversion functions


#__________________________________ 08/03 ____________________________
# + completed float conversions to and from unsigned and fromsigned


#__________________________________ 09/03 ____________________________
# + Completed all float conversions 


#__________________________________ 11/03 ____________________________
# ~ Fixed Float comparison subroutine
# + signed comparison subroutines
# + worked on snippets index
# + added much of the Runtime snippets to the index

#_________________________________ 12/03 _____________________________
# + finished adding run time snippets to snippet index

#_________________________________ 14/03 _____________________________
# + adding arithmetic snippets

#__________________________ 29/03 ____________________________________
# + fixed up signed arithmetic snippets
# + tested and debugged fist pass of the compiler 

#__________________________ 31/03 ____________________________________
# + put in framework for new variables

#__________________________ 1/04 _____________________________________
# + Planning for new variable system - framework probably redundant - requires reworking on pushing and pulling
# + The type checking in the main compiler file now stores a variable's type in its parse tree node, and trivial vars get a local? signifier ==> makes life easier
# + code to generate floats from value parse tree nodes
# + added new framework again

#__________________________to do: _________________________

# + unify typing in code generator
# + new indexing - can index multiple times so needs to get the first variable then act on it
# + all getting variables needs overhauling to be able to get at non trivial variables (use check typing maybe)
# + create algorithm to partition structs to be placed on hte stack and to recover a struct
# + snippets/code generation for passing structs to functions (push and pop entire structs onto and off the stack)
# ~ update signed multiplication and division
# + retrieving from structs
# + retrieving through  multiple layers of pointers
# + continue snippets index
# ~ test first pass of compiler

# ~ sizeof operator


import sys
import optimiser1_3 as optimiser
def process_snippets(filename):
	'''generates a list of snippets objects'''
	snippet_text = open(filename,"r").read()
	snippets_dict = parse_snippets(snippet_text)
#	print snippets_dict
	snippets_dict = {name:snippet(name,snippets_dict[name]) for name in snippets_dict}
	#print [name for name in snippets_dict]
	return snippets_dict

def parse_snippets(text):
	#simple splitting up job
	snippets = {}
	state = "begin" 				#state machine which builds up name and text before addign entry to dictionary
	previous_state = ''
	current_snippet = ''
	current_snippet_name = ''
	for character in text: 		    #makes single pass over text
		if state == "begin":        #begin state is before the machine has seen the start of a snippet
			if character == "<":  
				previous_state = state
				state = "found <"
		elif state == "found <": 	#the machine can find a < either at the start of a new snippet, the use of a name in the snippet, or general use
			if character == "<":  	# two < indicates the name of a new snippet
				if previous_state == "in snippet": 		#if had already found a snippet
					snippets[current_snippet_name] = current_snippet
					current_snippet = ''
					current_snippet_name = ''
				previous_state = "found <"
				state = "snippet name"
			else: 										#for other uses of <
				state = previous_state
				if previous_state  == "in snippet":
					current_snippet += '<'
					current_snippet += character

		elif state == "snippet name": 					#in the name of a snippet
			if character == ">":
				previous_state = state
				state = "found >"
			else:
				current_snippet_name += character


		elif state == "found >": 						#at the and of a name of a snippet
			if character == ">":
				state = "in snippet"
			else:
				state = previous_state
				current_snippet_name += character

		elif state == "in snippet": 				   #in the body of a snippet
			if character == "<":
				previous_state = state
				state = "found <"
			else:
				current_snippet += character
	if current_snippet_name and current_snippet:
		snippets[current_snippet_name] = current_snippet
	return snippets


class snippet: 										   #class to do main snippet processing
	def __init__(self,name,snippet_text):
		self.name = name
		self.snippet_text = snippet_text
		self.blocks,self.labels = self.split_snippet() 	#gets lists of plain text and labels to substituted in

	def split_snippet(self):
		''' simple state machine to find the permanent and non permanent parts of the code'''
		blocks = []
		labels = []
		label_name = ''
		block = ''
		state = 'body'
		for character in self.snippet_text: 		#single pass through text, with state machine splitting up text
			if state == 'body': 					#if between gaps
				if character == "<":
					blocks.append(block)
					block = ''
					state = 'name'
				else:
					block += character
			elif state == 'name': 					#if in a gap
				if character == '>':
					labels.append(label_name)
					label_name = ''
					state = 'body'
				else:
					label_name += character 
		if state == 'body': 						#cleaning up
			blocks.append(block)
		elif state == "name":
			labels.append(label_name)
		return blocks,labels

	def generate_code(self,substitution_dictionary):
		'''takes in a dictionary of substitutions and generates code from it'''
		substituted = []
		#print self.name
		#print self.labels
		#print substitution_dictionary
		for label in self.labels:
			substituted.append(str(substitution_dictionary[label])) #gets labels in order as needed by generator
		new_code = []
		for i in xrange(len(self.blocks)): 	#builds new list
			new_code.append(self.blocks[i])
			try:
				new_code.append(substituted[i])
			except IndexError:
				pass
		try:	
			new_code += substituted[len(self.blocks):] #adds substituted to the end if any is left
		except IndexError:
			pass
		#print ''.join(new_code)
		#a = raw_input('')
		return ''.join(new_code)

class code_generator:
	def __init__(self,function_object,global_variable_address_dictionary,global_variable_type_dict):
		self.snippets = snippets
		self.IF_COUNT = 0 							#initialises if and loop counts
		self.LOOP_COUNT = 0 

		self.global_variable_address_dict = global_variable_address_dictionary #gets globals
		self.global_variable_type_dict = global_variable_type_dict
#		print self.global_variable_address_dict
		self.function_name = function_object.name
		self.variable_address_dict,self.stack_frame_size = self.get_var_addresses(function_object.variable_sizes)
		self.variable_types = function_object.variables
		self.simplified_variable_types = {var_name:("char" if self.variable_types[var_name] == "char" else "int") for var_name in self.variable_types} #simplified types means @int and @chars are ints
		self.input_variables = self.get_input_variables(function_object)


		#does the generation
		self.in_loop = 0
		self.assembly = self.generate_function_code(function_object.parse_tree,self.input_variables,self.simplified_variable_types,self.stack_frame_size)
		self.assembly = optimiser.assembly_optimise(self.assembly)

	

	def get_var_addresses(self,var_sizes):
		#generates a dictionary of the addresses of variables used b a function
		address_dict = {}
		current_address = 8 #2 ints are alreadying in stack frame: Return address, and previous top of stack
		for var in var_sizes:
			address_dict[var] = current_address
			current_address += var_sizes[var]
		return address_dict,current_address #current address is stack frame size

	def get_input_variables(self,function):
		# extracts a list of the names of input variables from the function
		return [pair[1] for pair in function.input_parameters]



	# _________________________________ functions  _________________________________
	def generate_function_code(self,function_parse_tree,input_variables,var_types,stack_frame_size):
		'''generates code fo a function,
		input variables is a dict matching variables to a stack frame index
		'''
		#var types is overall type - ie @int and @char are ints
		#pop_to_gp0_code = self.snippets["Popgp0"].generate_code({})
		code_to_get_parameters = ''
		for var in input_variables:
			if var_types[var] == "int":
				pop_code = self.snippets[" store "].generate_code({"absolute_address":self.variable_address_dict[var],"Popgp0":self.snippets["Popgp0"].generate_code({})})
			elif var_types[var] == "char":
 				pop_code = self.snippets[" store char "].generate_code({"absolute_address":self.variable_address_dict[var],"Popgp0":self.snippets["Popgp0"].generate_code({})})
			else:
				 print "ERROR(9): incorrect type passed to code generator: ", var_types[var]
				 quit()
			code_to_get_parameters = pop_code +"\n" + code_to_get_parameters #inverts code to match stack
		assembly_code = self.snippets[" function startup routine "].generate_code(
			{
			"function_name":self.function_name,
			"new_length":str(stack_frame_size),
			"get_parameters":code_to_get_parameters
			})
		assembly_code += self.generate_block_code(function_parse_tree)
		return assembly_code
		#last line should be a return command
	
	def generate_function_call(self,call_parse_tree):
		'''Generates the code to call a function'''
		function_name = call_parse_tree.children[0].string
		args_parse_tree = call_parse_tree.children[2]
		if len(call_parse_tree.children) == 4:
			function_call_code = self.snippets[" function call routine "].generate_code(
				{
				"Push args":self.generate_push_args(args_parse_tree),
				"Call_address":function_name
				}
			)
		else:
			function_call_code = self.snippets[" function call routine "].generate_code(
				{
				"Push args":'',
				"Call_address":function_name
				}
			)
		return function_call_code
	
	def generate_push_args(self,args_parse_tree):
		'''generates code to push arguments onto the stack for the start of a function'''
		if len(args_parse_tree.children)>1: 	#if not at end, add the code, and update the parse tree
			return self.generate_push_args(args_parse_tree.children[0]) + self.generate_expression_code(args_parse_tree.children[2])
			
		else: 	#gets to the end of the the arguments 
			return self.generate_expression_code(args_parse_tree.children[0])
	
	def generate_block_code(self,block):
		return "\n".join([self.generate_line(line) for line in block.children])

	def generate_line(self,line):
		if line.type == "<assignment>": #line tree is simplified by semantic checking
			return self.generate_assignment_code(line)
		elif line.type == "<cntrl_flow>":
			if line.children[0].type == "<if_stmnt>":
				return self.generate_if_code(line.children[0])
			elif line.children[0].type == "<while_loop>":
				return self.generate_while_code(line.children[0])
			elif line.children[0].type == "<for_loop>":
				return self.generate_for_loop(line.children[0])
			else:
				print "ERROR(10): did not expect tree of type "+line.children[0].type + " as control flow"
		elif line.type == "<other>":
			if len(line.children) == 1:
				if line.children[0].type == '"return"': #nothing to return
					return self.snippets[" return routine "].generate_code({"generate value to return":''})
				elif line.children[0].type == "<fun_call>":
					return self.generate_function_call(line.children[0])
				elif line.children[0].type == '"break"':
					return self.generate_break_code()
				elif line.children[0].type == '"continue"':
					return self.generate_continue_code()
				elif line.children[0].type == '"pass"':
					return '' #placeholder
				else:
					print "ERROR(11): not expecting tree of type: "+line.children[0].type+" as an \"<other>\" line"
					quit()
			elif len(line.children) == 2:
				if line.children[0].type == '"return"':
					#print line.children[1].type 
					#raw_input('')
					return self.snippets[" return routine "].generate_code({"generate value to return":self.generate_expression_code(line.children[1])})
				else:
					print "ERROR(12): not expecting type: "+line.children[0].type+" in other tree"	
					quit()
			else:
				print "ERROR(13): line too long to be an \"<other>\""
				quit()

		else:
			print "ERROR(14): invalid line: ",line
			quit()
	#__________________________________________________ control flow _____________________________________
	
	def generate_if_code(self,if_parse_tree):
		if len(if_parse_tree.children)>2: 		#two kinds of if
			return self.generate_if_else_code(if_parse_tree)
		else:
			return self.generate_only_if_code(if_parse_tree)
	
	def generate_only_if_code(self,if_parse_tree):
		condition_code = self.generate_boolean_expression(if_parse_tree.children[0]) #generates the boolean condition	
		block_code = self.generate_block_code(if_parse_tree.children[1]) 			#gets block code to run if true
		pop_gp0 = self.snippets["Popgp0"].generate_code({}) 							#code to deal with a pop
		return_code =  self.snippets[" if statement code "].generate_code({ 			#generates if code using a snippet
			"Calculate_condition":condition_code,
			"Popgp0":pop_gp0,
			"number":self.function_name+"-"+str(self.IF_COUNT), 	#if count used to make labels distinct
			"conditional code":block_code,
			})
		self.IF_COUNT += 1 															#increments if count to make it distinct
		return return_code
	
	def generate_if_else_code(self,if_parse_tree):
		condition_code = self.generate_boolean_expression(if_parse_tree.children[0])  		#get boolean condition
		true_code = self.generate_block_code(if_parse_tree.children[1]) 						#gets truwe and false code
		false_code = self.generate_block_code(if_parse_tree.children[2])
		pop_gp0 = self.snippets["Popgp0"].generate_code({})
		return_code =  self.snippets[" if-else statement code "].generate_code({ 					#uses snippet
			"Calculate_condition":condition_code,
			"Popgp0":pop_gp0,
			"number":self.function_name+"-"+str(self.IF_COUNT),
			"true_code":true_code,
			"false_code":false_code
			})
		self.IF_COUNT += 1
		return return_code
	
	def generate_while_code(self,while_parse_tree):
		#similar to if code, using counter make labels distinct
		condition_code = self.generate_boolean_expression(while_parse_tree.children[0]) 		#condition and code to run fetched
		pop_gp0 = self.snippets["Popgp0"].generate_code({})
		previous_in_loop = self.in_loop
		self.in_loop = 1 #allows continue and break generating code to check whether code is in a loop or not
		looped_code = self.generate_block_code(while_parse_tree.children[1])
		self.in_loop = previous_in_loop
		return_code = self.snippets[" while loop code "].generate_code({ 					#snippet used to generate code
			"number":self.function_name+"-"+str(self.LOOP_COUNT),
			"Popgp0":pop_gp0,
			"Calculate_condition":condition_code,
			"looped_code":looped_code
			})
		self.LOOP_COUNT += 1
		return return_code
	
	def generate_for_loop(self,for_parse_tree): 
		assign_1 = self.generate_assignment_code(for_parse_tree.children[0]) 		#2 assignments are an initial assignment and a repeated assignment
		if for_parse_tree.children[1].children[0].type == "<bool_factor>":
			condition = self.generate_boolean_factor(for_parse_tree.children[1].children[0])
		else:
			condition = self.generate_comparison(for_parse_tree.children[1].children[0])
		pop_gp0 = self.snippets["Popgp0"].generate_code({})
		assign_2 = self.generate_assignment_code(for_parse_tree.children[2])

		previous_in_loop = self.in_loop
		self.in_loop = 1 #allows continue and break generating code to check whether code is in a loop or not	

		block = self.generate_block_code(for_parse_tree.children[3])
		self.in_loop = previous_in_loop


		return_code = self.snippets[" for loop code "].generate_code({
				"assignment1":assign_1,
				"Calculate_condition":condition,
				"Popgp0":pop_gp0,
				"assignment2":assign_2,
				"number": self.function_name+"-"+str(self.LOOP_COUNT),
				"looped_code":block
			})
		self.LOOP_COUNT += 1
		return return_code
	
	def generate_break_code(self):
		#goes to exit of the loop
		if self.in_loop:
			return "Load PC loop"+self.function_name+"-"+str(self.LOOP_COUNT)+"exit\n" #most recent loop generated
		else:
			print "ERROR(44): Break called outside of a loop"
			quit()

	def generate_continue_code(self):
		#skips to next iteration of the loop
		if self.in_loop:
			return "Load PC loop"+self.function_name+"-"+str(self.LOOP_COUNT)+"continue\n" #most recent loop generated
		else:
			print "ERROR(44): Continue called outside of a loop"
			quit()	
	
	#___________________________________________ getting and storing variables _______________________
	#How variables are going to be handled:
	#	- Parse and semantic checking:
	#		- Struct definitions will be singled out.
	# 			- Each struct type has an object generated for it stored in program.structs {struct_name:struct_object}
	# 				- contains variable types (Struct.var_types)
	# 				- the parse trees for declarations of values within the struct (Struct.declarations)
	#				- size of each variable 	(Struct.var_sizes)
	# 				- address offset for each variable (Struct.var_offsets)
	#				- starting value parse tree for each variable in the struct (Struct.var_starting_values)
	#		- in type checking
	#			- sets out the type of the variable in every variable parse tree node (VPTN.var_type)
	#			- if a struct's value is called, check that that the struct contains that variable
	#	- in Code Generator
	#			- simple variables ==> call by address
	#			- define trivial as having no pointer resolution higher up the chain
	#			- pointer resolution is generating a value by resolving a[x]
	#			- trivial pointers - old fashioned style
	#			- non trivial pointers - eg a[x][y] needs to load from a, apply index of x, load from new value and apply index of y to generate address
	#			- trivial structs: generate static address then add offsets as needed
	# 			- non trivial structs - generate address using pointer resolution then add offset
	#
	#	- introduce a "resolve_variable" function
	# 			- (parse_tree) ==> code for fetching the variable
	#
	#
	#
	#
	#
	def generate_push(self,type,address):
		#for default var types simple push
		#recurse for structs
	def generate_pop(self,type,address):

	
	def generate_get_value(self,value_parse_tree):
		#generates either loading a variable or a constant
		#print value_parse_tree.type
		if value_parse_tree.type == "<const>":
			return self.generate_get_constant(value_parse_tree)
		elif value_parse_tree.type  == "<variable>":
			return self.generate_get_variable(value_parse_tree)
		else:
			print "ERROR(15): incorrect value node type: ",
			print value_parse_tree.type
			quit()

	def generate_get_variable(self,variable_parse_tree):
		if len(variable_parse_tree.children) == 1: #trivial variables
			if variable_parse_tree.local: #locals 


			else: #globals
		elif len(variable_parse_tree.children) == 3: #struct member -gets address of the struct and adds offset
													 # 				-needs to check the chain for pointers
			struct_type = variable_parse_tree.children[0].var_type
			address_offset = program.structs[struct_type].var_offsets[variable_parse_tree.children[2].string]
			if self.is_struct_local(variable_parse_tree.children[0]):	

			else:
		elif len(variable_parse_tree.children == 4): #pointer resolution
			#pointers need to get the value of the variable in children[0], pop into gp0, evaluate the index and multiply by the width of the indexed type
			#then add the two and place in gp6 for indexing - simples
		else:
			#error

	def generate_store_variable(self,variable_parse_tree):


	def resolve_value(self,variable_parse_tree):
		#places value of variable onto the stack


	def generate_get_variable(self,variable_parse_tree):
		variable_name = variable_parse_tree.children[0].string
		if variable_name in self.variable_address_dict: #checks local namespace first
			#print "local variable"
			return self.generate_get_local_variable(variable_parse_tree)
		elif variable_name in self.global_variable_address_dict: #then global
			#print "global variable"
			return self.generate_get_global_variable(variable_parse_tree)
		else:
			print "ERROR(16): unrecognised variable: ", variable_name
			quit()

	def generate_get_constant(self,constant_parse_tree):
		if len(constant_parse_tree.children) == 1 and constant_parse_tree.children[0].type == "num":
			#if a numerical constant
			return "Load gp0 @"+constant_parse_tree.children[0].string+"\n"+self.snippets["Pushgp0"].generate_code({})
		elif len(constant_parse_tree.children) == 3 and constant_parse_tree.children[0].type == ".":
			#if a float
			return "Load gp0 @"+generate_float_value(constant_parse_tree.children[0].string+"."+constant_parse_tree.children[0].string) +"\n"+self.snippets["Pushgp0"].generate_code({})
		elif len(constant_parse_tree.children) == 2 and constant_parse_tree.children[1].type == "id":
			#if a pointer
			variable_name = constant_parse_tree.children[1].string
			push_gp0 = self.snippets["Pushgp0"].generate_code({})
			if variable_name in self.variable_address_dict: #if a local variable
				return self.snippets[" get ptr "].generate_code({"absolute_address":self.variable_address_dict[variable_name],"Push gp0":push_gp0})
			elif variable_name in self.global_variable_address_dict: #if a global variable
				return self.snippets[" get ptr global "].generate_code({"absolute_address":self.global_variable_address_dict[variable_name],"Push gp0":push_gp0})
			else:
				print "ERROR(17): unrecognised variable name: ",constant_parse_tree.children[1].string
				quit()
		else:
			print "ERROR(18): incorrect constant: ",
			print constant_parse_tree.children
			quit()
	def generate_store_value(self,variable_parse_tree):
		variable_name = variable_parse_tree.children[0].string
		if variable_name in self.variable_address_dict:
			return self.generate_store_local_variable(variable_parse_tree)
		elif variable_name in self.global_variable_address_dict:
			return self.generate_store_global_variable(variable_parse_tree)
		else:
			print "ERROR(19): does not recognise variable name: "+variable_name

	def generate_get_local_variable(self,variable_parse_tree):
		#gets a variable's value onto the stack
		variable_name = variable_parse_tree.children[0].string
		variable_type = self.variable_types[variable_name]
		variable_address = str(self.variable_address_dict[variable_name])
		#######################################################
		# bit above needs overhall, massively 				  #
		#######################################################
		if len(variable_parse_tree.children) == 1:  							#raw variables
			if variable_type in ("int","float","signedInt") or variable_type[0] == "@": 					#integer sized
				return self.snippets[" load "].generate_code({"absolute_address":variable_address,"Pushgp0":self.snippets["Pushgp0"].generate_code({})})
			elif variable_type in ("char",signedChar): 							#char sized things
				return self.snippets[" load char "].generate_code({"absolute_address":variable_address,"Pushgp0":self.snippets["Pushgp0"].generate_code({})})		
			elif variable_type in program.structs: 								#programmer defined structures
				###################################################
				# run routine to get the struct onto the stack 	  #
				###################################################
			print "ERROR(20): uncrecognised type: "+variable_type
			quit()
		elif len(variable_parse_tree.children) == 4: 																	#indexed variables
			if variable_type[1:] in ("int","float","signedInt") or variable_type[1] == "@":
				index_expr = self.generate_expression_code(variable_parse_tree.children[2])
				pop_index = self.snippets["Popindex"].generate_code({})
				get_index = self.snippets[" get index integer "].generate_code({"index expr":index_expr,"pop index":pop_index})
				return self.snippets[" load relative "].generate_code({"get_index":get_index,"absolute_address":variable_address,"Pushgp0":self.snippets["Pushgp0"].generate_code({})})
			elif variable_type[1:] in ("char","signedChar"):
				index_expr = self.generate_expression_code(variable_parse_tree.children[2])
				pop_index = self.snippets["Popindex"].generate_code({})
				get_index = self.snippets[" get index char "].generate_code({"index expr":index_expr,"pop index":pop_index})
				return self.snippets[" load relative char "].generate_code({"get_index":get_index,"absolute_address":variable_address,"Pushgp0":self.snippets["Pushgp0"].generate_code({})})
			elif variable_type[1:] in program.structs:
				###################################################
				# routine to index the struct 					  #
				###################################################
			else:
				print "ERROR(21): unexpected variable type for relative addressing: "+variable_type
				quit()
		elif len(variable_parse_tree.children) == 3:
			##############################################
			# - code to get members of a struct  		 #
			# - essentially needs to get address of the  # 
			#	struct then add the offset 				 # 
			#	(precalculated before code generation)	 #
			##############################################

		else:
			print "ERROR(50): unrecognised variable parse tree"
			print_parse_tree(variable_parse_tree)
			quit()
	
	
	def generate_store_local_variable(self,variable_parse_tree):
		variable_name = variable_parse_tree.children[0].string
		variable_type = self.variable_types[variable_name]
		variable_address = str(self.variable_address_dict[variable_name])
		if len(variable_parse_tree.children) == 1: 										#raw variables (unindexed)
			if variable_type in ("int","signedInt","float") or variable_type[0] == "@": #integer sized things
				return self.snippets[" store "].generate_code({"absolute_address":variable_address,"Popgp0":self.snippets["Popgp0"].generate_code({})}) 
			elif variable_type in ("char","signedChar"): 								#char sized things
				return self.snippets[" store char "].generate_code({"absolute_address":variable_address,"Popgp0":self.snippets["Popgp0"].generate_code({})}) 			
			elif variable_type in program.structs: 										#user defined variables
				######################################################
				# code to recover a struct from teh stack and store  #
				######################################################
			else:
				print "ERROR(22): unexpected variable type for relative addressing: "+variable_type
				quit()	
	
		elif len(variable_parse_tree.children) == 4: 				#indexed variables
			if variable_type[1:]  in ("int","signedInt","float") or variable_type[1] == "@":  #integer sized things
				index_expr = self.generate_expression_code(variable_parse_tree.children[2])
				pop_index = self.snippets["Popindex"].generate_code({})
				get_index = self.snippets[" get index integer "].generate_code({"index expr":index_expr,"pop index":pop_index})
				return self.snippets[" store relative "].generate_code({"get_index":get_index,"absolute_address":variable_address,"Popgp0":self.snippets["Popgp0"].generate_code({})})
			elif variable_type[1:]  in ("char","signedChar"): 						#byte sized things
				index_expr = self.generate_expression_code(variable_parse_tree.children[2])
				pop_index = self.snippets["Popindex"].generate_code({})
				get_index = self.snippets[" get index char "].generate_code({"index expr":index_expr,"pop index":pop_index})
				return self.snippets[" store relative char "].generate_code({"get_index":get_index,"absolute_address":variable_address,"Popgp0":self.snippets["Popgp0"].generate_code({})})
			elif variable_type[1:] in program.structs:
				#########################################################
				# code to store structs to an index 					#
				#########################################################
			else:
				print "ERROR(23): unexpected variable type for relative addressing: "+variable_type
				quit()
		elif len(variable_parse_tree.children) == 3:
			##############################################
			# - code to get members of a struct  		 #
			# - essentially needs to get address of the  # 
			#	struct then add the offset 				 # 
			#	(precalculated before code generation)	 #
			##############################################

		else:
			print "ERROR(50): unrecognised variable parse tree"
			print_parse_tree(variable_parse_tree)
			quit()

	def generate_get_global_variable(self,variable_parse_tree):
		#gets a variable's value onto the stack
		variable_name = variable_parse_tree.children[0].string
		variable_type = self.global_variable_type_dict[variable_name]
		variable_address = str(self.global_variable_address_dict[variable_name])
		if len(variable_parse_tree.children) == 1: 											#raw variables
			if variable_type in ("int","signedInt","float") or variable_type[0] == "@": 		#int sized values
				return self.snippets[" load global "].generate_code({"absolute_address":variable_address,"Pushgp0":self.snippets["Pushgp0"].generate_code({})})
			elif variable_type in ("char","signedChar"): 										#byte sized values
				return self.snippets[" load char global "].generate_code({"absolute_address":variable_address,"Pushgp0":self.snippets["Pushgp0"].generate_code({})})			
			elif variable_type in program.structs: 												#user defined
				#####################################
				# code to get and push a struct 	#
				#####################################
			else:
				print "ERROR(24): unexpected variable type for relative addressing: "+variable_type
				quit()	
		
		elif len(variable_parse_tree.children) == 4: 																				#indexed variables
			if variable_type[1:] in ("int","signedInt","float") or variable_type[1] == "@": 		#int sized 
				index_expr = self.generate_expression_code(variable_parse_tree.children[2])
				pop_index = self.snippets["Popindex"].generate_code({})
				get_index = self.snippets[" get index integer "].generate_code({"index expr":index_expr,"pop index":pop_index})
				return self.snippets[" load relative global "].generate_code({"get_index":get_index,"absolute_address":variable_address,"Pushgp0":self.snippets["Pushgp0"].generate_code({})})
			elif variable_type[1:] in ("char","signedChar"): 											#byte sized
				index_expr = self.generate_expression_code(variable_parse_tree.children[2])
				pop_index = self.snippets["Popindex"].generate_code({})
				get_index = self.snippets[" get index char "].generate_code({"index expr":index_expr,"pop index":pop_index})
				return self.snippets[" load relative char global "].generate_code({"get_index":get_index,"absolute_address":variable_address,"Pushgp0":self.snippets["Pushgp0"].generate_code({})})
			elif variable_type[1:] in program.structs: 													#user defined
				#########################
				# code to index structs #
				#########################

			else:
				print "ERROR(25): unexpected variable type for relative addressing: "+variable_type
				quit()
		elif len(variable_parse_tree.children) == 3:
			##############################################
			# - code to get members of a struct  		 #
			# - essentially needs to get address of the  # 
			#	struct then add the offset 				 # 
			#	(precalculated before code generation)	 #
			##############################################

		else:
			print "ERROR(50): unrecognised variable parse tree"
			print_parse_tree(variable_parse_tree)
			quit()
	
	def generate_store_global_variable(self,variable_parse_tree):
		variable_name = variable_parse_tree.children[0].string
		variable_type = self.global_variable_type_dict[variable_name]
		variable_address = str(self.global_variable_address_dict[variable_name])
		if len(variable_parse_tree.children) == 1: #not indexed
			if variable_type in ("int","signedInt","float") or variable_type[0] == "@": #int sized
				return self.snippets[" store global "].generate_code({"absolute_address":variable_address,"Popgp0":self.snippets["Popgp0"].generate_code({})})
			elif variable_type in ("char","signedChar"): 								#byte sized
				return self.snippets[" store char global "].generate_code({"absolute_address":variable_address,"Popgp0":self.snippets["Popgp0"].generate_code({})})			
			elif variable_type in program.structs: 										#user defined
				#########################
				# code to store structs #
				#########################
			else:
				print "ERROR(26): unexpected variable type: "+variable_type
				quit()
		elif len(variable_parse_tree.children) == 4: 												#indexed variables
			if variable_type[1:]  in ("int","signedInt","float") or variable_type[0] == "@":
				index_expr = self.generate_expression_code(variable_parse_tree.children[2])
				pop_index = self.snippets["Popindex"].generate_code({})
				get_index = self.snippets[" get index integer "].generate_code({"index expr":index_expr,"pop index":pop_index})
				return self.snippets[" store relative global "].generate_code({"get_index":get_index,"absolute_address":variable_address,"Popgp0":self.snippets["Popgp0"].generate_code({})})
			elif variable_type[1:] in ("char","signedChar"):
				index_expr = self.generate_expression_code(variable_parse_tree.children[2])
				pop_index = self.snippets["Popindex"].generate_code({})
				get_index = self.snippets[" get index char "].generate_code({"index expr":index_expr,"pop index":pop_index})
				return self.snippets[" store relative char global "].generate_code({"get_index":get_index,"absolute_address":variable_address,"Popgp0":self.snippets["Popgp0"].generate_code({})})
			elif variable_type[1:] in program.structs: 
				#####################################
				# obligatory code to store structs  #
				#####################################
			else:
				print "ERROR(27): unexpected variable type for relative addressing: "+variable_type
				quit()
		elif len(variable_parse_tree.children) == 3:
			##############################################
			# - code to get members of a struct  		 #
			# - essentially needs to get address of the  # 
			#	struct then add the offset 				 # 
			#	(precalculated before code generation)	 #
			##############################################

		else:
			print "ERROR(50): unrecognised variable parse tree"
			print_parse_tree(variable_parse_tree)
			quit()
	

	#______________________________________________ Line types _________________________________
	def generate_assignment_code(self,assignment_parse_tree):
		lhs = assignment_parse_tree.children[0]
		rhs = assignment_parse_tree.children[1]
		expression_code = self.generate_expression_code(rhs)
		assignment_code = self.generate_store_value(lhs)
		return expression_code + assignment_code

	def generate_expression_code(self,expression_parse_tree):
		#needs to deal with typing etc
		#print expression_parse_tree.type
		if len(expression_parse_tree.children) == 1:
			#term, factor, variable, const, fun_call
			child = expression_parse_tree.children[0]
			if child.type in ["<term>","<factor>","<cast>","<ternary_op>"]: #simple to do, just pass on to another recursion level
				#print "simple pass on"
				return_code = self.generate_expression_code(child)
				return return_code
			elif child.type in ["<fun_call>"]:  			#handled by another function
				#print "function call"
				return self.generate_function_call(child)
			elif child.type in ["<variable>","<const>"]: 	#handled by generate_get_value
				#print "value"
				return_code = self.generate_get_value(child)
				#print return_code
				return return_code
			else:
				print "ERROR(28): code generator cannot handle expressions of type: "+expression_parse_tree.type+" with length 1"
				print_parse_tree(expression_parse_tree)
				quit()

		elif len(expression_parse_tree.children) == 2: #unary ops only: handled by unary ops generator
			#print "unary"
			return self.generate_expression_code(expression_parse_tree.children[1])+self.generate_unary_op(expression_parse_tree.children[0])

		elif len(expression_parse_tree.children) == 3:
			#[expr addop term]
			#[term mulop factor]
			#[( expr )]
			#[expr  type type] -cast
			if expression_parse_tree.children[1].type in ["<addopchar>","<addopint>","<mulopchar>","<mulopint>"]: #handles externally mostly
				#binary operations
				#print "binary"
				expr1_code = self.generate_expression_code(expression_parse_tree.children[0])
				expr2_code = self.generate_expression_code(expression_parse_tree.children[2])
				operation_code = self.generate_binary_op(expression_parse_tree.children[1])
				return expr1_code + expr2_code+operation_code
			elif expression_parse_tree.children[0].type in ['"("']: #if ( expr ), simply return the code from expr
				#print "bracketed"
				return self.generate_expression_code(expression_parse_tree.children[1])
			elif expression_parse_tree.type == "<cast>": #does the casting
				#print "casting"
				start_type = expression_parse_tree.children[1].string
				destination_type = expression_parse_tree.children[2].string
				expression_code = self.generate_expression_code(expression_parse_tree.children[0])
				return expression_code + self.cast(start_type,destination_type)
			else:
				print "ERROR(29): cannot handle node of type: "+expression_parse_tree.type
				quit()
		elif expression_parse_tree.type == "<ternary_op>":
			true_code = self.generate_expression_code(expression_parse_tree.children[0])
			false_code = self.generate_expression_code(expression_parse_tree.children[4])


			if expression_parse_tree.children[2].children[0].type == "<bool_factor>":
				condition_code = self.generate_boolean_factor(expression_parse_tree.children[2].children[0])
			else:
				condition_code = self.generate_comparison(expression_parse_tree.children[2].children[0])
			pop_gp0 = self.snippets["Popgp0"].generate_code({})
			return_code =  self.snippets[" if-else statement code "].generate_code({ 					#uses snippet
				"Calculate_condition":condition_code,
				"Popgp0":pop_gp0,
				"number":self.function_name+"-"+str(self.IF_COUNT),
				"true_code":true_code,
				"false_code":false_code
				})
			self.IF_COUNT += 1
			return return_code

		print "ERROR(30): unrecognised tree handled by code generator: "+parse_tree.type
		quit()

#______________________________________________ Bolean code ________________________________________
	
	def generate_boolean_expression(self,bool_parse_tree):  			#set of mutually recursive functions
		#print_parse_tree(bool_parse_tree)
		#print_parse_tree(bool_parse_tree)
		if bool_parse_tree.children[1].type == "<bool_factor>":  	#follows grammar parse tree
			return self.generate_boolean_factor(bool_parse_tree.children[1])   
		elif bool_parse_tree.children[1].type == "<comparison>":
			return self.generate_comparison(bool_parse_tree.children[1])
		else:
			print "ERROR(31): incorrect type passed to boolean generator: "+bool_parse_tree.children[1].type
			quit()
	
	
	def generate_boolean_factor(self,bool_parse_tree):
		if len(bool_parse_tree.children) == 1: 			#can be simply a bool expr, a binary op or unary op
			return_code = self.generate_boolean_expression(bool_parse_tree.children[0])
		elif len(bool_parse_tree.children) == 2:
			return_code = self.generate_boolean_expression(bool_parse_tree.children[1]) + self.generate_bool_unary_op(bool_parse_tree.children[0])
		elif len(bool_parse_tree.children) == 3:
			return_code = self.generate_boolean_factor(bool_parse_tree.children[0])+self.generate_boolean_expression(bool_parse_tree.children[2])+self.generate_boolean_operation(bool_parse_tree.children[1])
		return return_code
		
	def generate_boolean_operation(self,bool_parse_tree):
		'''modular boolean operation generator'''
		pop_gp0 = self.snippets["Popgp0"].generate_code({})
		pop_gp1 = self.snippets["Popgp1"].generate_code({})
		push_gp0 = self.snippets["Pushgp0"].generate_code({})
		if  bool_parse_tree.children[0].string == "and":
			return '\n'.join([pop_gp0,pop_gp1,"AND gp0 gp1",push_gp0])
		elif bool_parse_tree.children[0].string == "or":
			return '\n'.join([pop_gp0,pop_gp1,"OR gp0 gp1",push_gp0])
		elif bool_parse_tree.children[0].string == "xor":
			return '\n'.join([pop_gp0,pop_gp1,"XOR gp0 gp1",push_gp0])
		else:
			print "ERROR(32): unexpected boolean operation: ",bool_parse_tree.string
			quit()
	
	def generate_bool_unary_op(self,bool_parse_tree):
		pop_gp0 = self.snippets["Popgp0"].generate_code({})
		push_gp0 = self.snippets["Pushgp0"].generate_code({})
		if bool_parse_tree.children[0].string == "not":
			return ''.join([pop_gp0,"NOT gp0",push_gp0])
		else:
			print "ERROR(33): incorrect boolean operation type: "+bool_parse_tree.children[0].type
	def generate_comparison(self,bool_parse_tree):
		if len(bool_parse_tree.children) == 1: #just an if true comparison
			pop_gp0 = self.snippets["Popgp0"].generate_code({})
			push_gp0 = self.snippets["Pushgp0"].generate_code({})
			return self.generate_expression_code(bool_parse_tree.children[0]) + self.snippets["is true"].generate_code({"getgp0":pop_gp0,"Push gp0":push_gp0})
		elif len(bool_parse_tree.children) == 3:
			pop_gp0 = self.snippets["Popgp0"].generate_code({}) #pop routines
			pop_gp1 = self.snippets["Popgp1"].generate_code({})
			expr0 = self.generate_expression_code(bool_parse_tree.children[0]) #gets code to calculate expressions
			expr1 = self.generate_expression_code(bool_parse_tree.children[2]) 
			push_gp0 = self.snippets["Pushgp0"].generate_code({})
			comparison_operation = bool_parse_tree.children[1]
			if len(comparison_operation.children) == 2: 						#is equal/not equal
				return expr0 + expr1 + self.snippets[("is equal" if comparison_operation.children[0].string == "=" else "not equal")].generate_code({"getgp0":pop_gp0,"getgp1":pop_gp1,"Push gp0":push_gp0})
			elif len(comparison_operation.children) == 1: 						#other operations
				if comparison_operation.children[0].terminal:  					#if a < or >
					if comparison_operation.children[0].string == "<":
						return expr0 + expr1 +self.snippets["is less"].generate_code({"getgp0":pop_gp0,"getgp1":pop_gp1,"Push gp0":push_gp0})
					elif comparison_operation.children[0].string == ">":
						return expr0 + expr1 +self.snippets["is greater"].generate_code({"getgp0":pop_gp0,"getgp1":pop_gp1,"Push gp0":push_gp0})
					else:
						print "ERROR(34): not expecting comparison operator: "+comparison_operation.children[0].string
						quit()
				else:
					if comparison_operation.children[0].type == "<not_less>": 			#deal with non terminals
						return expr0 + expr1 +self.snippets["not less"].generate_code({"getgp0":pop_gp0,"getgp1":pop_gp1,"Push gp0":push_gp0})
					elif comparison_operation.children[0].type == "<not_greater>":
						return expr0 + expr1 +self.snippets["not greater"].generate_code({"getgp0":pop_gp0,"getgp1":pop_gp1,"Push gp0":push_gp0})
					else:
						print "ERROR(35): not expecting comparison operator: "+comparison_operation.children[0].type
						quit()
	
	
	
	

	def generate_unary_op(self,unary_op_tree):
		get_gp0 = self.snippets["Popgp0"].generate_code({})
		store_gp0 = self.snippets["Pushgp0"].generate_code({})

		unop_int_dict = {
			"~":" NOT ",
			"-":" unary SUB "
		}
		unop_char_dict = {
			"~":" NOT char ",
			"-":" unary SUB char "
		}
		if unary_op_tree.type == "<unary_opint>":
			return self.snippets[unop_int_dict[unary_op_tree.children[0].string]].generate_code({"getgp0":get_gp0,"storegp0":store_gp0})
		elif unary_op_tree.type == "<unary_opchar>":
			return self.snippets[unop_char_dict[unary_op_tree.children[0].string]].generate_code({"getgp0":get_gp0,"storegp0":store_gp0})
		else:
			print "ERROR(36): unrecognised operation passed to code generator: "+unary_op_tree.type
			quit()

	def generate_binary_op(self,binary_op_tree):
		get_gp0 = self.snippets["Popgp0"].generate_code({})
		get_gp1 = self.snippets["Popgp1"].generate_code({})
		store_gp0 = self.snippets["Pushgp0"].generate_code({})
		
		#could speed up by pregenerating
		addop_int_dict = {
			"+": " ADD ",
			"-": " SUB ",
			"<": " SHL ",  #just looking at child 0, so only needs to look for < or >
			">": " SHR "
		}
		addop_char_dict = {			
			"+":" ADD char ",
			"-":" SUB char ",
			"<":" SHL char ",
			">":" SHR char "
		}
		mulop_int_dict = {
			"*":" MUL ",
			"/":" DIV ",
			"%":" MOD ",
			"^":" XOR ",
			"|":" OR ",
			"&":" AND "
		}
		mulop_char_dict = {
			"*":" MUL char ",
			"/":" DIV char ",
			"%":" MOD char ",
			"^":" XOR char ",
			"|":" OR char ",
			"&":" AND char "
		}

		if binary_op_tree.type == "<addopint>": #uses the correct dict for each type to generate code
			return self.snippets[addop_int_dict[binary_op_tree.children[0].string]].generate_code({"getgp0":get_gp0,"getgp1":get_gp1,"storegp0":store_gp0})
		elif binary_op_tree.type == "<addopchar>":
			return self.snippets[addop_char_dict[binary_op_tree.children[0].string]].generate_code({"getgp0":get_gp0,"getgp1":get_gp1,"storegp0":store_gp0})
		elif binary_op_tree.type == "<mulopint>":
			return self.snippets[mulop_int_dict[binary_op_tree.children[0].string]].generate_code({"getgp0":get_gp0,"getgp1":get_gp1,"storegp0":store_gp0})
		elif binary_op_tree.type == "<mulopchar>":
			return self.snippets[mulop_char_dict[binary_op_tree.children[0].string]].generate_code({"getgp0":get_gp0,"getgp1":get_gp1,"storegp0":store_gp0})
		else:
			print "ERROR(37): unrecognised operation passed to code generator: "+binary_op_tree.type
			quit()


	def cast(self,start_type,destination_type):
		if start_type == destination_type:
			return ''
		elif start_type == "int" and destination_type == "char":
			Popgp0 = self.snippets["Popgp0"].generate_code({})
			Pushgp0 = self.snippets["Pushgp0"].generate_code({})
			return self.snippets[" cast int to char "].generate_code({"Popgp0":Popgp0,"Push gp0":Pushgp0})
		elif start_type == "char" and destination_type == "int":
			return ''
		else:
			print "ERROR(38): unhandled type casting: "+start_type+" and "+destination_type
			quit()

def print_parse_tree(parse_tree_node,offset = ''):
	if parse_tree_node.terminal:
		print offset+parse_tree_node.type+"("+parse_tree_node.string+")"
		return
	else:
		print offset+parse_tree_node.type+"("
		for child in parse_tree_node.children:
			print_parse_tree(child,offset+"  ")
		print offset+")"


def generate_float_value(float_string):
	#convertsa string of a float into a 32bit CLL float value
	value = float(floatstring)
	if value == 0: return '0' #zero is the same in float and int forms
	sign = 0 if value>=0 else 1
	value = abs(value)  #gets the sign and sets value to its own magnitude
	mantissa = value
	exponent = 0
	while mantissa>=2: #while too ig increase size of exponent and decrease the size of the mantissa
		mantissa /= 2.0
		exponent += 1
		if exponent>128:
			return str(sign<<31 +(2**31 -1)) # too big== return infinity
	while mantissa <1:
		mantissa *=2.0
		exponent -= 1
		if exponent<127: return '0' #if too small return 0
	return str((sign<<31)+(int(mantissa*(2**23))&(2**23 - 1))+((exponent+127)<<24))


import os
CURRENT_DIR = os.path.dirname(__file__)
snippet_files = ["arithmetic_snippets.al","comparison and boolean.al","float_snippets.al","runtime.al"]
snippet_files = ["snippets\\"+file_name for file_name in snippet_files]
file_paths = [os.path.join(CURRENT_DIR, snippet_file) for snippet_file in snippet_files] 
snippets = {}
for path in file_paths:
	snippets.update(process_snippets(path))
