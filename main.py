

class Literal(object):
    """
    Defining a literal class to help check for compliments
    """
    def __init__(self, lit):
        self.lit = lit
        self.leng = len(self.lit)
        if not 1 <= self.leng <= 2:
            raise ValueError("Literal must be between 1 and 2 characgers")
        
    def __str__(self):
        return self.lit

    def __eq__(self, o):
        return self.lit == o.lit

    def getComp(self):
        if self.leng == 1:
            return Literal("~" + self.lit)
        else:
            return Literal(self.lit[1])

class Statement(object):
    """
    A class to help turn statements into CNF form
    """
    def __init__(self, statement):
        """
        Operators
        ~: Negation
        $: Conditional
        %: Biconditional
        &: AND
        |: OR
        """
        self.statement = statement.replace(" ", "")
        self.NNF = ""
        self.CNF = ""

    def getOpenIndex(self, s, index):
        # gets the starting parenthesis of a certain scope
        count = 0
        for i in range(index-1, -1, -1):
            if s[i] == "(" and count == 0:
                return i
            elif s[i] == "(":
                count -= 1
            elif s[i] == ")":
                count += 1

    def getCloseIndex(self, s, index):
        # gets the ending parenthesis of a certain scope
        count = 0
        for i in range(index, len(s)):
            if s[i] == ")" and count == 1:
                return i
            elif s[i] == ")":
                count -= 1
            elif s[i] == "(":
                count += 1

    def toNNF(self):
        # turn statement to Negation Normal Form
        self.NNF = self.statement
        i = 0
        # replace conditionals and biconditionals
        while i < len(self.NNF):
            # conditionals
            if self.NNF[i] == "$":
                pre = i - 1
                post = i + 1
                # find P and Q indexes
                if self.NNF[pre] == ")":
                    pre = self.getOpenIndex(self.NNF, pre)
                if self.NNF[post] == "(":
                    post = self.getCloseIndex(self.NNF, post)
                # P$Q <=> ~P|Q
                P = self.NNF[pre:i]
                Q = self.NNF[i+1:post+1]
                self.NNF = self.NNF[:pre] + "~" + P + "|" + Q + self.NNF[post+1:]
                i = 0
                continue
            # biconditionals
            if self.NNF[i] == "%":
                pre = i - 1
                post = i + 1
                if self.NNF[pre] == ")":
                    pre = self.getOpenIndex(self.NNF, pre)
                elif self.NNF[pre-1] == "~" and pre != 0:
                    pre -= 1
                if self.NNF[post] == "(" or self.NNF[post:post+2] == "~(":
                    post = self.getCloseIndex(self.NNF, post)
                elif self.NNF[post] == "~":
                    post += 1
                # P%Q <=> (P|~Q)&(~P|Q)
                P = self.NNF[pre:i]
                Q = self.NNF[i+1:post+1]
                self.NNF = self.NNF[:pre] + "(" + P + "|~" + Q + ")&(~" + P + "|" + Q + ")" + self.NNF[post+1:]
                i = 0
                continue
            i += 1
        # reduce double negatives and perform DeMorgan's
        i = 0
        while i < len(self.NNF):
            # double negatives
            if self.NNF[i:i+2] == "~~":
                self.NNF = self.NNF[:i] + self.NNF[i+2:]
                continue
            # DM
            elif self.NNF[i] == "~" and self.NNF[i+1] == "(":
                post = self.getCloseIndex(self.NNF, i+1)
                DM = "("
                count = 0
                j = i+2
                while j < post + 1:
                    if self.NNF[j] not in {"(", ")", "&", "|", "~"} and count == 0:
                        DM = DM + "~" + self.NNF[j]
                    elif self.NNF[j] == "(" and count == 0:
                        count += 1
                        DM += "~("
                    elif self.NNF[j] == ")":
                        count -= 1
                        DM += ")"
                    elif self.NNF[j] == "&" and count == 0:
                        DM += "|"
                    elif self.NNF[j] == "|" and count == 0:
                        DM += "&"
                    elif self.NNF[j] != "~" and count == 0:
                        DM += "~" + self.NNF[j]
                    else:
                        DM += self.NNF[j]
                    j += 1
                self.NNF = self.NNF[:i] + DM + self.NNF[post+1:]
            i += 1
        return self

    def clean(self):
        # Remove unnecessary parentheses from NNF formulation
        i = 0
        while i < len(self.NNF):
            count = 0
            L = None
            R = None
            if self.NNF[i] == "(" and count == 0:
                L = i
                for j in range(i+1, len(self.NNF)):
                    if self.NNF[j] == ")" and count == 0:
                        R = j
                        break
                    elif self.NNF[j] == ")":
                        count -= 1
                    elif self.NNF[j] == "(":
                        count += 1
                L_op = ""
                R_op = ""
                try:
                    for j in range(L-1, -1, -1):
                        if self.NNF[j] in {"|", "&"}:
                            L_op = self.NNF[j]
                            break
                        elif self.NNF[j] == "(":
                            break
                except:
                    L_op=None
                for j in range(R+1, len(self.NNF)):
                    if self.NNF[j] in {"|", "&"}:
                        R_op = self.NNF[j]
                        break
                    elif self.NNF[j] in {"(", ")"}:
                        break
                X = set()
                count2 = 0
                for j in range(L+1, R):
                    if self.NNF[j] in {"&", "|"} and count2 == 0:
                        X.add(self.NNF[j])
                    elif self.NNF[j] == "(":
                        count2 += 1
                    elif self.NNF[j] == ")":
                        count2 -= 1
                # end parenthesis
                if L_op == "" and R_op == "":
                    self.NNF = self.NNF[L+1:R]
                    i = 0
                    continue
                # if same operators, remove inner parenthesis
                else:
                    comp = X.union(L_op).union(set(R_op))
                    if (comp == {"|"} or comp == {"&"}) and len(comp) == 1:
                        self.NNF = self.NNF[:L] + self.NNF[L+1:R] + self.NNF[R+1:]
                        i = 0
                        continue
            i += 1
        return self
 
    def toCNF(self):
        # Turn statement into Conjunctive Normal Form
        self.CNF = self.NNF
        # distribute ORs
        i = 0
        while i < len(self.CNF):
            if self.CNF[i] == "|":
                # check for P1|...|Pn|(Q&R)
                if self.CNF[i+1] == "(" and self.CNF[i-1] != ")":
                    P = self.CNF[i-1]
                    k = i-2
                    if self.CNF[i-2] == "~":
                        P = "~" + P
                        k -= 1
                    while k > -1:
                        if self.CNF[k] == "|":
                            if self.CNF[k-1] == "~":
                                P = self.CNF[k:k+3]
                                k -= 2
                            else:
                                P = self.CNF[k:k+2]
                                k -= 1
                        else:
                            break
                    j = i
                    while self.CNF[j] != ")":
                        j += 1
                    parts = self.CNF[i+2:j].split("&")
                    build = self.CNF[:i-len(P)]
                    for part in parts:
                        build += "(" + P + "|" + part + ")&"
                    try:
                        self.CNF = build[:-1] + self.CNF[j+1:]
                    except:
                        self.CNF = build[:-1]
                    i = 0
                    continue
                # check for (Q&R)|P1|...|Pn
                elif self.CNF[i+1] != "(" and self.CNF[i-1] == ")":
                    P = self.CNF[i+1]
                    k= i+2
                    if P == "~":
                        P = P + self.CNF[i+2]
                        k += 1
                    # handle |...|Pn part
                    while k < len(self.CNF):
                        if self.CNF[k] == "|":
                            if self.CNF[k+1] == "~":
                                P = P + self.CNF[k:k+3]
                                k += 3
                            else:
                                P = P + self.CNF[k:k+2]
                                k += 2
                        else:
                            break
                    j = i
                    while self.CNF[j] != "(":
                        j-=1
                    parts = self.CNF[j+1:i-1].split("&")
                    build = self.CNF[:j]
                    for part in parts:
                        build += "(" + P + "|" + part + ")&"
                    try:
                        self.CNF = build[:-1] + self.CNF[i + 1 + len(P):]
                    except:
                        self.CNF = build[:-1]
                    i = 0
                # check for (P1&P2)|(Q1&Q2)
                elif self.CNF[i-1] == ")" and self.CNF[i+1] == "(":
                    Ps = []
                    j = i - 2
                    while self.CNF[j] != "(":
                        if self.CNF[j] != "&" and self.CNF[j-1] == "~":
                            Ps.append(self.CNF[j-1:j+1])
                            j -= 2
                        elif self.CNF[j] != "&":
                            Ps.append(self.CNF[j])
                            j -= 1
                        else:
                            j -= 1
                    pre = j
                    Qs = []
                    j = i + 2
                    while self.CNF[j] != ")":
                        if self.CNF[j] != "&" and self.CNF[j-1] == "~":
                            Qs.append(self.CNF[j-1:j+1])
                        elif self.CNF[j] != "&" and self.CNF[j] != "~":
                            Qs.append(self.CNF[j])
                        j += 1
                    post = j
                    build = self.CNF[:pre]
                    for P in Ps:
                        for Q in Qs:
                            build += "(" + P + "|" + Q + ")&"
                    self.CNF = build[:-1] + self.CNF[post+1:]
            i += 1
        return self.CNF

def generateClauses(statement):
    # generate clauses from CNF statements
    conjuncts = statement.split("&")
    clauses = []
    for conjunct in conjuncts:
        clause = []
        i=0
        while i < len(conjunct):
            if conjunct[i] in {"(", ")", "|"}:
                i += 1
            elif conjunct[i] == "~":
                clause.append(Literal(conjunct[i:i+2]))
                i += 2
            else:
                clause.append(Literal(conjunct[i]))
                i += 1
        clauses.append(clause)
    return clauses
        
            
def resolve(c):
    # perform resolution
    w.write("Begin Resolution\n")
    clause_list = []
    for i, clauses in enumerate(c):
        for clause in clauses:
            clause_list.append(clause)
    temp = clause_list.copy()
    i = 0
    for clause in clause_list:
        w.write(str(list(map(lambda c: str(c), clause))) + "\n")
    w.write("---------------\n")
    while i < len(clause_list):
        # if there is an empty set then return true
        if len(clause_list[i]) == 0:
            return True
        # if the clause is just one literal then it could be used to eliminate others
        elif len(clause_list[i]) == 1:
            lit_set = clause_list[i].copy()
            lit = lit_set.pop()
            for clause_set in clause_list:
                # check if the literal's compliment is in any other set
                if lit.getComp() in clause_set:
                    clause_set.remove(lit.getComp())
                    w.write("Removed: " + str(lit) + ", " + str(lit.getComp()) + "\n")
                    for clause in clause_list:
                        w.write(str(list(map(lambda c: str(c), clause))) + "\n")
                    w.write("---------------\n")
                    # if this creates an empty set then return true
                    if len(clause_set) == 0:
                        w.write("Empty set: {}\n")
                        return True
                    i = 0
        else:
            for l in clause_list[i]:
                # check for tautologous clauses
                if l.getComp() in clause_list[i]:
                    clause_list.remove(clause_list[i])
                    i = 0
                    break
                # check for repeat elements
                if clause_list[i].count(l) != 1:
                    for j in range(clause_list[i].count(l) - 1):
                        clause_list[i].remove(l)

        i += 1
    w.write("Finish\n")
    for clause in clause_list:
        w.write(str(list(map(lambda c: str(c), clause))) + "\n")
    return False

    
if __name__ == "__main__":
    # Settings
    file_input = "test_cases.txt"
    file_output = "output.txt"
    user = True
    user_output = "user_output.txt"
    # start up code
    test = 1
    choice = ""
    while choice not in {"user", "file"}:
        print('Would you like to read from file? Type "file"\nWould you like manual input? Type "user"')
        choice = input("---> ").lower().strip()
    if choice == "user":
        user = True
        user_output = input("Give user output filename ---> ")
        if user_output[-4:] != ".txt":
            user_output += ".txt"
    else:
        user = False
        file_input = input("Give input filename ---> ")
        file_output = input("Give output filename ---> ")
        if file_input[-4:] != ".txt":
            file_input += ".txt"
        if file_output[-4:] != ".txt":
            file_output += ".txt"
    
    """
    User code
    """
    if user:
        with open(user_output, 'w') as w:
            mode = "default"
            input_text = "\nEnter a mode\n\
                Validity: Determine validity of an argument\n\
                Tautology: Determine if a statement is a logical tautology\n\
                Exit: Exit the program"
            validity_text = 'Input premises and conclusion line by line.\nInput "Done" after conclusion has been input'
            taut_text = 'Input a statement to test if it is a logical tautology.'
            while mode != "exit":
                print(input_text)
                mode = input("---> ").lower().strip()
                if mode == "validity":
                    # collect premises
                    premises = []
                    premise = ''
                    print(validity_text)
                    while premise.lower() != 'done':
                        premise = input("---> ").strip()
                        premises.append(premise)
                    premises.pop(-1)
                    length = max(len(max(premises,key=lambda x: len(x))), 5)
                    # ouput argument to be tested
                    w.write("-"*4+"TEST " + str(test) + "-"*4 + "\n\n")
                    for premise in premises[:-1]:
                        w.write(premise + "\n")
                    w.write("-"*length+"\n")
                    w.write(premises[-1]+"\n\n")
                    # negate conclusion
                    premises[-1] = "~(" + premises[-1] + ")"
                    # begin process to turn premises into clauses for resolution
                    statements = list(map(lambda i: Statement(i), premises))
                    # turn statements into CNF form
                    statements = list(map(lambda s: s.toNNF().clean().toCNF(), statements))
                    # get clauses from CNF statements
                    clause_list = list(map(lambda s: generateClauses(s), statements))
                    # perform resolution
                    result = resolve(clause_list)
                    if result:
                        print("\n"+"-"*14+"\nVALID ARGUMENT\n"+"-"*14)
                        w.write("-"*14+"\nVALID ARGUMENT\n"+"-"*14+"\n\n")
                    else:
                        print("\n"+"-"*16+"\nINVALID ARGUMENT\n"+"-"*16)
                        w.write("-"*16+"\nINVALID ARGUMENT\n"+"-"*16+"\n\n")
                    test += 1

                elif mode == "tautology":
                    w.write("-"*4+"TEST " + str(test) + "-"*4 + "\n\n")
                    print(taut_text)
                    # collect statement
                    statement = input("---> ").strip()
                    w.write(statement+"\n\n")
                    # negate statement
                    statement = "~(" + statement + ")"
                    statements = [Statement(statement)]
                    # turn statements to CNF
                    statements = list(map(lambda s: s.toNNF().clean().toCNF(), statements))
                    # generate clauses
                    clause_list = list(map(lambda s: generateClauses(s), statements))
                    # perform resolution
                    result = resolve(clause_list)
                    if result:
                        print("\n"+"-"*9+"\nTAUTOLOGY\n"+"-"*9)
                        w.write("-"*9+"\nTAUTOLOGY\n"+"-"*9+"\n\n")
                    else:
                        print("\n"+"-"*15+"\nNOT A TAUTOLOGY\n"+"-"*15)
                        w.write("-"*15+"\nNOT A TAUTOLOGY\n"+"-"*15+"\n\n")
                    test += 1

    else:
        """
        Code to run from a file
        """
        with open(file_input) as f:
            with open(file_output, 'w') as w:
                for line in f:
                    parts = line.split("/")
                    if parts[0] == "VALIDITY":
                        # get premises from file
                        premises = parts[1].split(",")
                        length = len(max(premises,key=lambda x: len(x)))
                        # display premises and conlcusion
                        print("\n"+"-"*4+"TEST ", test,  "-"*4)
                        w.write("-"*4+"TEST " + str(test) + "-"*4 + "\n")
                        for p in premises[:-1]:
                            print(p)
                            w.write(p + "\n")
                        print("-"*length)
                        w.write("-"*length + "\n")
                        print(premises[-1] + "\n")
                        w.write(premises[-1] + "\n")
                        # collect statements
                        statements = list(map(lambda i: Statement(i.strip()), premises[:-1]))
                        # negate conclusion 
                        statements.append(Statement("~("+premises[-1].strip()+")"))
                        # turn statements into CNF 
                        statements = list(map(lambda s: s.toNNF().clean().toCNF(), statements))
                        # generate clauses
                        clause_list = list(map(lambda s: generateClauses(s), statements))
                        # resolve clauses
                        result = resolve(clause_list)
                        if result:
                            print("-"*14+"\nVALID ARGUMENT\n"+"-"*14)
                            w.write("-"*14+"\nVALID ARGUMENT\n"+"-"*14+"\n\n")
                        else:
                            print("-"*16+"\nINVALID ARGUMENT\n"+"-"*16)
                            w.write("-"*16+"\nINVALID ARGUMENT\n"+"-"*16+"\n\n")
                        test += 1
                    elif parts[0] == "TAUTOLOGY":
                        premises = [parts[1]]
                        # display statement
                        print("\n"+"-"*4+"TEST ", test,  "-"*4)
                        w.write("-"*4+"TEST " + str(test) + "-"*4 + "\n")
                        print(parts[1])
                        w.write(parts[1]+"\n")
                        # negate statement
                        statements = list(map(lambda i: Statement("~("+i.strip()+")"), premises))
                        # turn into CNF
                        statements = list(map(lambda s: s.toNNF().clean().toCNF(), statements))
                        # generate clauses
                        clause_list = list(map(lambda s: generateClauses(s), statements))
                        # resolve clauses
                        result = resolve(clause_list)
                        if result:
                            print("-"*9+"\nTAUTOLOGY\n"+"-"*9)
                            w.write("-"*9+"\nTAUTOLOGY\n"+"-"*9+"\n\n")
                        else:
                            print("-"*15+"\nNOT A TAUTOLOGY\n"+"-"*15)
                            w.write("-"*15+"\nNOT A TAUTOLOGY\n"+"-"*15+"\n\n")
                        test += 1
                    else:
                        print("Invalid Test Mode:", parts[1])
                        w.write("Invalid Test Mode" + parts[1])
            