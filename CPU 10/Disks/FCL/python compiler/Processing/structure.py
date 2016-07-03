def processBlock(parseTree,scope,result):
	if len(parseTree.children) == 2:
		return (processLine(parseTree.children[0],scope,processLine(parseTree.children[1],scope,result)[1]),Type('primitive','unit'))
	else:
		return processLine(parseTree.children[0],result)

def processLine(parseTree,scope,result):
 	extendedTable = {
		"FunDec": processFunDec,
		"TypeDec": processTypeDec,
		"Ifstatement": processIfstatement,
		"WhileLoop": processWhileLoop,
		"ForLoop": processForLoop,
		"Scope": processScope
	 	'"{"':processBlock
	}

	simpleTable = {
			"PureFunDec": processPureFunDec,
			"FunCall": processFunCall,
			"break":processBreak,
			"continue":processContinue,
			"Statement": processStatement,
			"VarDec": processVarDec,
			'"return"':processReturn,
	}

	if parseTree.type == "Simple":
		
		processFunction = simpleTable[parseTree.children[0].type]
		if parseTree.children[0].type != '"return"':
			return processFunction(parseTree.children[0],scope,result)
		else:
			return processFunction(parseTree.children[1],scope,result)

	elif parseTree.type == "Extended":
		processFunction = extendedTable[parseTree.children[0].type]
		if parseTree.children[0].type != '"{"':
			return processFunction(parseTree.children[0],scope,result)
		else:
			return processFunction(parseTree.children[1],scope,result)
	else:
		raise NodeErrorException(parseTree)





def processScope(parseTree,scope,result):
	return processLine(parseTree.children[2],ScopeList(getScope(parseTree.children[1]),scope),result)

def processStatement(parseTree,scope,result):
	raise incompleteError()

def processIfstatement(parseTree,scope,result):
	if len(parseTree.children) == 5:
		# if...end
		test = parseTree.children[2]
		trueCode = parseTree.children[4]

		result = processLine(trueCode,scope,"endif;\n"+result)
		(result,exprType,pure) = processExpression(test,scope,"gp0, if;\n"+result,registerNames.regNames,"gp0,")
		if not (Type.compareType(exprType,Type('primitive','"bool"'))):
			raise typeErrorException("The type of the condition expression in an if statement's definition must be boolean.")
		return result
	elif len(parseTree.children) == 7:
		# if ... else .. end
		test = parseTree.children[2]
		trueCode = parseTree.children[4]
		falseCode = parseTree.children[6]
		result = processLine(falseCode,scope,"endif;\n"+result)
		result = processLine(trueCode,scope,"else;\n"+result)
		(result,exprType,pure) = processExpression(test,scope,"gp0, if;\n"+result,registerNames.regNames,"gp0,")
		if not (Type.compareType(exprType,Type('primitive','"bool"'))):
			raise typeErrorException("The type of the condition expression in an if statement's definition must be boolean.")
		return result
	else:
		raise NodeErrorException()

def processWhileLoop(parseTree,scope,result):
	test = parseTree.children[2]
	loopedCode = parseTree.children[4]

	result = processLine(loopedCode,scope,'next;\nloop;\n'+result)
	(result,exprType,pure) = processExpression(test,scope,"gp0, do;\n"+result,registerNames.regNames,"gp0,")
	if not (Type.compareType(exprType,Type('primitive','"bool"'))):
		raise typeErrorException("The type of the condition expression in a while loop's definition must be boolean.")
	result = "while;\n" + result
	return result

def processForLoop(parseTree,scope,result):
	instantiation = parseTree.children[2]
	test = parseTree.children[4]
	nextValue = parseTree.children[6]
	loopedCode = parseTree.children[8]

	result = processStatement(nextValue,scope,'loop;\n'+result)
	result = processLine(loopedCode,scope,"next;\n"+result)
	(result,exprType, pure) = processExpression(test,scope,"gp0, do;\n"+result,registerNames.regNames,"gp0,")

	if not (Type.compareType(exprType,Type('primitive','"bool"'))):
		raise typeErrorException("The type of the condition expression in a for loop's definition must be boolean.")
	if instantiation.children[0].type == 'Statement':
		result = processStatement(instantiation.children[0],scope,"while;\n"+result)

	elif instantiation.children[0].type == 'VarDec':
		varDec = instantiation.children[0]
		if len(varDec.children) == 2:
			raise Errors.semanticError("Error: the variable declaration in a for loop instantiation must be of the statement type")
		else:
			result =  processStatementVarDec(varDec,scope,"while;\n"+result)
	else:
		raise NodeErrorException()
	return result

def processContinue(parseTree,scope,result):
	return "contin;\n" + result

def processBreak(parseTree,scope,result):
	return "break;\n" + result