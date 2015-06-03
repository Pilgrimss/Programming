import re
import json
import random

def pretokenise(source_text,path):
	#deals with import and define directives

	lines = source_text.split("\n")
	replace_dict = {}
	i = 0
	while i < len(lines):
		line = lines[i]
		split_line = split([" ","\t"],line)
		if len(split_line)  and split_line[0][0] == "#":
			if split_line[0] == "#include":  #replaces this line with the code of the specified file
				#print line
				if split_line[1][:4] == "STD:":
					file_path = os.path.join(CURRENT_DIR,"standard library\\"+split_line[1][4:])
					included = pretokenise(open(file_path,"r").read(),file_path[-1])
				else:
					file_path = path+[split_line[1]]
					included = pretokenise(open("\\".join(file_path),"r").read(),file_path[-1])
				lines[i] = included[0]
				replace_dict.update(included[1])
			elif split_line[0] == "#define": #defines token to be changed for another
				try:
					replace_dict[split_line[1]] = split_line[2]
					lines = lines[:i]+lines[i+1:] #removes line 
					i -=1 							#accounts for removal of line
				except IndexError:
					print "ERROR(43): not enough tokens for a #define in line "+str(i)
					quit()
			elif split_line[0] == "#random": #defines a token to be replaced by a random integer
				try:

					replace_dict[split_line[1]] = str(random.randrange(2**23))
					lines = lines[:i]+lines[i+1:] #removes line 
					i -=1 							#accounts for removal of line	
				except IndexError:
					print "ERROR(44): not enough tokens for a #random in line "+str(i)
					
			elif split_line[0] == "#enum":
				#ENUM followed by an identifier and a set in [], which represents the name of the class of defined values and individual macros within it
				#numbers of the form 0x5555550000 - 0x555555ffff are used - so the enum values do not intefere with instructions etc
				if len(split_line>2):
					enum_name = split_line[1]
					if split_line[2] == "[" and split_line[-1][-1] == "]":
						rest_of_string = ''.join(split_line[2:])


					lines = lines[:i]+lines[i+1:] #removes line 
					i -=1 							#accounts for removal of line
				else:

					print "ERROR: not enough tokens for an enum statment"
					quit()
		i += 1
	return "\n".join(lines),replace_dict


def tokenis_enum_set(string):
	state = "start"
	tokens = []
	seperators = (' ','\t',',')
	for character in string:
		if state == "start":
			if character in seperators:
				pass
			elif character == ']':
				pass
			pass

def split(delimiters, string, maxsplit=0):
    regexPattern = '|'.join(map(re.escape, delimiters))
    return [string for string in re.split(regexPattern, string, maxsplit) if string != '' ]