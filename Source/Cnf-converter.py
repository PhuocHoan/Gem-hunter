# Reduces the operators, if "and" is present inside "and" or "or" inside "or"
# Example : ["and", "A", ["and", "B", "C"]] should be ["and", "A", "B", "C"]
def reduceOperators(formula) :
    if (isinstance(formula, str)) :
        return formula
    operator = formula[0]
    literals = []
    propositions = []
    for index, item in enumerate(formula) :
        if (index > 0) :
            if (isinstance(item, str)) :
                literals.append(item)
            elif (isinstance(item, list)) :
                propositions.append(reduceOperators(item))
    newFormula = literals
    for item in propositions :
        if (isinstance(item, list) and item[0] == operator) :
            for i,clause in enumerate(item) :
                if (i > 0) :
                    newFormula.append(clause)
        else :
            newFormula.append(item)
    newFormula.insert(0, operator)
    return newFormula

# Removes duplicate elements from "and" and "or"
# Example : ["and", "A", "A"] should be "A"
def removeDuplicates(formula) :
    if (isinstance(formula, str) or (isinstance(formula, list) and formula[0] == "not" and isinstance(formula[1], str))) :
        return formula
    formula_tmp = []
    for item in formula:
        if isinstance(item, list):
            item = removeDuplicates(item)
        if item not in formula_tmp:
            formula_tmp.append(item)
    formula = formula_tmp
    if (isinstance(formula_tmp, list) and formula_tmp[0] != "not" and len(formula_tmp) < 3) :
        return formula_tmp[1]
    return formula_tmp

# Sorts the literals and lists in the formula (will be used for removing duplicate items in list)
# The literals like {A, B, C, D, ...} are in the beginning followed by lists. And the "and" list is present in the end
def sort(formula) :
    if (isinstance(formula, str)) :
        return formula
    operator = formula[0]
    if (operator == "implies") :
        return formula
    literals = []
    propositions = []
    for index, item in enumerate(formula) :
        if (index > 0) :
            if (isinstance(item, list)) :
                if item[0] == "not" and isinstance(item[1], str):
                    literals.append(item)
                    continue
                propositions.append(sort(item))
            else:
                literals.append(item)
    if (len(literals) > 1) :
        literals = sorted(literals, key=lambda i: i if not isinstance(i, list) else i[1])
    if (len(propositions) > 1) :
        propositions = sorted(propositions, key=lambda proposition: proposition[0], reverse=True)
    newFormula = literals + propositions
    newFormula.insert(0, operator)
    return newFormula

# Converts to CNF by taking different cases separately
def convert(formula) :
    if (isinstance(formula, str)):
        return formula
    elif(isinstance(formula,list)) :
        # A => B    --->    ~A | B
        if (formula[0] == "implies") :
            return convert(["or", convert(["not",convert(formula[1])]), convert(formula[2])])
        # A <=> B   --->    (~A | B) & (A | ~B)
        elif (formula[0] == "iff") :
            return convert("and", convert(["or", convert(["not", formula[1]]), formula[2]]), convert(["or", formula[1], convert(["not", formula[2]])]))
        elif (formula[0] == "not") :
            # ~p
            if (isinstance(formula[1], str)) :
                return formula
            # ~~p   --->    p
            elif (isinstance(formula[1], list) and (formula[1])[0] == "not") :
                return convert((formula[1])[1])
            # ~(A & B & C & ...)  --->    ~A | ~B | ~C | ....
            elif (isinstance(formula[1], list) and (formula[1])[0] == "and") :
                disjuncts = []
                for index, item in enumerate(formula[1]) :
                    if (index > 0) :
                        disjuncts.append(convert(["not", item]))
                disjuncts.insert(0, "or")
                return convert(disjuncts)
            # ~(A | B | C | ...)  --->    ~A & ~B & ~C & ....
            elif (isinstance(formula[1], list) and (formula[1])[0] == "or") :
                conjuncts = []
                for index, item in enumerate(formula[1]) :
                    if (index > 0) :
                        conjuncts.append(convert(["not", item]))
                conjuncts.insert(0, "and")
                return convert(conjuncts)
            # ~(A => B)	--->	A & ~B
            elif (isinstance(formula[1], list) and ((formula[1])[0] == "implies")) :
                return convert(["and", convert((formula[1])[1]), ["not", convert((formula[1][2]))]])
            # ~(A <=> B)	--->	(A | B) & (~A | ~B)
            elif (isinstance(formula[1], list) and (formula[1])[0] == "iff") :
                return convert(["and", ["or", convert((formula[1])[1]), convert((formula[1])[2])], ["not", ["and", convert((formula[1])[1]), convert((formula[1])[2])]]])
        elif (formula[0] == "or") :
            # A | A  --->    A
            # formula = sort(formula)
            # Handling the case ["or", "A", ["or", "B", "C"]]
            formula = reduceOperators(formula)
            formula = removeDuplicates(formula)
            # The order will be messed up when the redundant operators are removed
            # Handling the case when the formula is reduced.
            # For instance A or A is reduced to A
            formula = sort(formula)
            if (len(formula) == 1) :
                return formula
            # case 0 | A = A
            if formula[1] == '0':
                formula.remove(formula[1])
            # case 1 | A = 1 or case A | -A = 1
            if formula[1] == '1' or (formula[2][0] == "not" and formula[1] == formula[2][1]):
                formula = "1"
                return formula
            if len(formula) == 2:
                return formula[1]
            if ((isinstance(formula[-1], list) and (formula[-1])[0] == "and")) :
                # A | (B & C & D & ...)  --->  (A | B) & (A | C) & (A | D) & ...
                conjuncts = []
                for i, item in enumerate(formula[-1]) :
                    if (i > 0) :
                        conjuncts.append(["or", formula[-2], item])
                conjuncts.insert(0, "and")
                # If only 2 items, then remove them and also remove OR
                if (len(formula) < 4) :
                    return convert(conjuncts)
                else :
                    # delete 2 last items
                    del formula[-2:]
                formula.append(conjuncts)
                return convert(formula)
            # # Case A OR B, 
            # elif ((isinstance(formula[1], str) and isinstance(formula[2], str)) or (isinstance(formula[1], str) and isinstance(formula[2], list) and (formula[2])[0] == "not" and isinstance((formula[2])[1], str)) or (isinstance(formula[2], str) and isinstance(formula[1], list) and (formula[1])[0] == "not" and isinstance((formula[1])[1], str))) :
            #     formula.append(["or", formula[1], formula[2]])
            #     del formula[1:3]
                
            #     formula = reduceOperators(formula)
            #     formula = sort(formula)
            #     return formula

            # Case A OR B, !A OR !B, A OR -B, B OR -A
            elif ((isinstance(formula[1], str) and isinstance(formula[2], str)) or (isinstance(formula[1], str) and isinstance(formula[2], list) and (formula[2])[0] == "not" and isinstance((formula[2])[1], str)) or (isinstance(formula[2], str) and isinstance(formula[1], list) and (formula[1])[0] == "not" and isinstance((formula[1])[1], str)) or (isinstance(formula[1], list) and (formula[1])[0] == "not" and isinstance((formula[1])[1], str) and isinstance(formula[2], list) and (formula[2])[0] == "not" and isinstance((formula[2])[1], str))) :
                return formula
            # For any other operator compute the inner operator after or
            else :
                disjuncts = []
                for i, item in enumerate(formula) :
                    if (i > 0) :
                        disjuncts.append(convert(item))
                disjuncts.insert(0, "or")
                while "0" in disjuncts:
                    disjuncts.remove("0")
                disjuncts = reduceOperators(disjuncts)
                return convert(disjuncts)
                # return disjuncts
            # disjuncts = []
            # for i, item in enumerate(formula) :
            #     if (i > 0) :
            #         disjuncts.append(convert(item))
            # disjuncts.insert(0, "or")
            # while "0" in disjuncts:
            #     disjuncts.remove("0")
            # disjuncts = reduceOperators(disjuncts)
            # # return convert(disjuncts)
            # return disjuncts
            
        elif (formula[0] == "and") :
            # Handling the case ["and", "A", ["or", "C", "D"], ["or", "D", "C"]]
            # formula = sort(formula)
            # Handling the case ["and", "A", ["and", "B", "C"]]
            formula = reduceOperators(formula)
            formula = removeDuplicates(formula)
            # The order will be messed up when the redundant operators are removed
            formula = sort(formula)
            if (len(formula) == 1) :
                return formula
            # case 1 & A = A
            if formula[1] == '1':
                formula.remove(formula[1])
            # case 0 & A = 0 and case A & -A = 0
            if formula[1] == '0' or (formula[2][0] == "not" and formula[1] == formula[2][1]):
                formula = "0"
                return formula
            if len(formula) == 2:
                return formula[1]
            disjuncts = []
            for i, item in enumerate(formula) :
                if (i > 0) :
                    disjuncts.append(convert(item))
            disjuncts.insert(0, "and")
            while "1" in disjuncts:
                disjuncts.remove("1")
            disjuncts = reduceOperators(disjuncts)
            return disjuncts
            
# Read the input file
inputFile = open("sentences.txt")
numSentences = -1
sentences = []

for line in inputFile:
    if (numSentences > 0):
        sentences.append(eval(line.strip()))
    else:
        numSentences = int(line.strip())
outputFile = open('sentences_CNF.txt', 'w+')
# For each sentence convert it to CNF
for sentence in sentences:
    formula = convert(sentence)
    # formula = removeDuplicates(formula)
    # formula = reduceOperators(formula)
    formula = sort(formula)
    
    outputFile.write (str(formula) + '\n')
inputFile.close()