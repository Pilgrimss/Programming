

############################################################################
# 						SET UP ROUTINE
############################################################################
def STACK_SIZE 65536   						#makes stack sizes easy to change

array Callstack	STACK_SIZE []  				#initialise runtime variables
array Expression_stack STACK_SIZE []
int stack_length STACK_SIZE 				
int Callstack_ptr Callstack 				

Load Stack_pointer Callstack_ptr 				
Load gp0 stack_length 						
MUL gp0 @4
SUB gp0 @12 
ADD Stack_pointer gp0							

Goto function:main 										
Halt
	
Out @'E'	%Stack_overflow_error 					#Define error handling 
Out @'R'
Out @'R'
Out @'O'
Out @'R'
Out @':'
Out @32
Out @'S'
Out @'T'
Out @'A'
Out @'C'
Out @'K'
Out @32
Out @'O'
Out @'V'
Out @'E'
Out @'R'
Out @'F'
Out @'L'
Out @'O'
Out @'W'
Halt
	
Out @'E' %Recursion_limit_reached 				#deal with a recursion error
Out @'R'
Out @'R'
Out @'O'
Out @'R'
Out @32
Out @'M'
Out @'A'
Out @'X'
Out @'I'
Out @'M'
Out @'U'
Out @'M'
Out @32
Out @'R'
Out @'E'
Out @'C'
Out @'U'
Out @'R'
Out @'S'
Out @'I'
Out @'O'
Out @'N'
Out @32
Out @'D'
Out @'E'
Out @'P'
Out @'T'
Out @'H'
Out @32
Out @'R'
Out @'E'
Out @'A'
Out @'C'
Out @'H'
Out @'E'
Out @'D'
Out @32
Outd Jump
Halt

Out @'E' %DIV_BY_ZERO
Out @'R'
Out @'R'
Out @'O'
Out @'R'
Out @':'
Out @32
Out @'D'
Out @'I'
Out @'V'
Out @'I'
Out @'S'
Out @'I'
Out @'O'
Out @'N'
Out @32
Out @'B'
Out @'Y'
Out @32
Out @'Z'
Out @'E'
Out @'R'
Out @'O'
Halt


Halt %function:quit

#################################### Built in function print_integer ####################################
SUB gp7 @4 		 		 %function:print_i										#Pops into gp0
Load gp0 Expression_stack [gp7]  				
Outd gp0
Move Jump PC  			
####################################################################################################


##################### built in function getc ###############################################
#returns a char
In gp0 %function:getc #gets a char without waiting (state of keyboard)
Store gp0 Expression_stack [gp7]
ADD gp7 @4
Compare gp7 stack_length
if Greater then Load PC Stack_overflow_error
Move Jump PC
##########################################################################

################## built in function char ##############################################

SUB gp7 @4 		 		 %function:char									#Pops into gp0
Load gp0 Expression_stack [gp7]  				
AND gp0 @255
Store gp0 Expression_stack [gp7] 
ADD gp7 @4
Move Jump PC 
#######################################################################################
################## built in function dRead ##############################################

SUB gp7 @4 		 		 %function:dRead									
								# disk addr, start, length ==> success?
Load gp3 Expression_stack [gp7] #len
SUB gp7 @4
Load gp2 Expression_stack [gp7] #start
SUB gp7 @4						
Load gp1 Expression_stack [gp7] #addr
HDScan gp1 						#scan to the right position
HDRead gp3 gp2 0 				# read l characters to memory at addr s
Move Zero gp0 		
if EOF then Move One gp0 			#test for EOF
Store gp0 Expression_stack [gp7]  #push flag
ADD gp7 @4
Move Jump PC 
#######################################################################################
########################## built in function putc ########################################
SUB gp7 @4 															%function:putc
Load gp0  Expression_stack [gp7]
Out gp0
Move Jump PC
################################################################################
############################################## Built in function printf ####################################################################

#heavily optimised printf loop, avoids call stack use entirely

SUB gp7 @4 		 		 %function:printf										#Pops into gp0
Load gp0 Expression_stack [gp7]
						
					
																#increments through addresses printing out until a null char is found (0x0)
LoadByte gp1 0 [gp0] %PrintfLoop
Compare gp1 Zero
if Equal then Move Jump PC							#null char found
Out gp1
ADD gp0 One
Load PC PrintfLoop
############################################################################################################################################
################## built in function dWrite ##############################################

SUB gp7 @4 		 		 %function:dWrite									
								# disk addr, start, length ==> success?
Load gp3 Expression_stack [gp7] #len
SUB gp7 @4
Load gp2 Expression_stack [gp7] #start
SUB gp7 @4						
Load gp1 Expression_stack [gp7] #addr
HDScan gp1 						#scan to the right position
HDWrite gp3 gp2 0 				# write l characters from memory at addr s
Move Zero gp0 		
if EOF then Move One gp0 			#test for EOF
Store gp0 Expression_stack [gp7]  #push flag
ADD gp7 @4
Move Jump PC 
################################################################################################################################################################################################################
																	Scope main
def expression_stack_ptr gp7
def ret_addr Jump
def previous_stack_ptr gp5
#__________ Defining offsets of local variables __________#
def Local.i 8
def @Local.i @8
#__________ End of local variable definitions __________#
Move Stack_pointer previous_stack_ptr								%function:main
SUB Stack_pointer @12 									#OVERHEAD FOR FUNCTION main
Compare Stack_pointer Callstack_ptr
if Less then Load PC Recursion_limit_reached
Store ret_addr 0 [Stack_pointer]
Store previous_stack_ptr 4 [Stack_pointer]							#GETTING PARAMETERS FOR FUNCTION main
Load gp0 @0
Store gp0 Local.i [Stack_pointer] 						#STORE GP0
Pass 										%loopmain-0entry
Load gp1 Local.i [Stack_pointer] 						#LOAD GP0
Load gp0 @100000000
Move Zero gp2 														#COMPARE (IS LESS)
Compare gp1 gp0
if Less then Load gp2 @4294967295
Move gp2 gp0
NOT gp0
if gp0 then Load PC loopmain-0exit 								#WHILE LOOP
Load gp1 Local.i [Stack_pointer] 						#LOAD GP0
Load gp0 @1
ADD gp0 gp1 														#ADD
Store gp0 Local.i [Stack_pointer] 						#STORE GP0
Load PC loopmain-0entry					%loopmain-0continue
Pass 										%loopmain-0exit
Load gp0 Local.i [Stack_pointer] 						#LOAD GP0
Store gp0 Expression_stack [gp7]									#PUSH GP0
ADD gp7 @4
Compare gp7 stack_length
if Greater then Load PC Stack_overflow_error
Goto function:print_i 												#CALLING print_i
Load ret_addr 0 [Stack_pointer]										#RETURNING
Load Stack_pointer 4 [Stack_pointer] 
Move ret_addr PC

############################## built in function getw ################################
#returns a char
In gp0 %function:getw 				#waits for a user to press a key
Compare gp0 Zero
if Equal then Load PC function:getw
Store gp0 Expression_stack [gp7]

ADD gp7 @4
Compare gp7 stack_length
if Greater then Load PC Stack_overflow_error
Move Jump PC
###################################################################
