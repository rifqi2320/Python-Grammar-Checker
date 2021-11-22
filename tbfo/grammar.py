class CFG(object):
    def __init__(self, filename):
        self.is_cnf = False
        with open(filename) as f:
            self.lines = f.readlines()

    def to_cnf(self):
        RULE_DICT = {}
        # MENGGANTI SEMUA RULES YANG TIDAK SESUAI DENGAN BENTUK CHOMSKY NORMAL FORM
        unit_productions, result = [], []
        res_append = result.append
        index = 0 # UNTUK MENAMAI VARIABEL / NONTERMINAL BARU
        grammar = [x.replace("->", "").split() for x in self.lines if (x[0] != "#" and x[0] != "\n")]
        for rule in grammar:
            new_rules = []
            if len(rule) < 2:
                continue
            elif len(rule) == 2 and (not rule[1].isupper()) :
                # RULE MEMILIKI FORMAT A -> B, MASIH TIDAK SESUAI SEHINGGA DICATAT DI TAHAP UNIT PRODUCTIONS
                unit_productions.append(rule)
                if rule[0] not in RULE_DICT:
                    RULE_DICT[rule[0]] = []
                RULE_DICT[rule[0]].append(rule[1:])
                continue
            elif len(rule) > 2:
                # RULE MASIH TIDAK SESUAI KARENA PADA SISI KANAN MEMILIKI LEBIH DARI DUA VARIABEL, ATAU GABUNGAN DARI TERMINAL DAN NONTERMINAL
                terminals = [(item, i) for i, item in enumerate(rule) if item.isupper()]
                if terminals:
                    for item in terminals:
                        # Create a new non terminal symbol and replace the terminal symbol with it.
                        # The non terminal symbol derives the replaced terminal symbol.
                        rule[item[1]] = f"{rule[0]}{str(index)}"
                        new_rules += [f"{rule[0]}{str(index)}", item[0]]
                    index += 1
                while len(rule) > 3:
                    new_rules.append([f"{rule[0]}{str(index)}", rule[1], rule[2]])
                    rule = [rule[0]] + [f"{rule[0]}{str(index)}"] + rule[3:]
                    index += 1
            # Adds the modified or unmodified (in case of A -> x i.e.) rules.
            if rule[0] not in RULE_DICT:
                RULE_DICT[rule[0]] = []
            RULE_DICT[rule[0]].append(rule[1:])
            res_append(rule)
            if new_rules:
                result.extend(new_rules)
        # MEMPROSES DAFTAR UNIT PRODUCTIONS YANG SUDAH DISIMPAN DI AWAL TADI
        while unit_productions:
            rule = unit_productions.pop()
            if rule[1] in RULE_DICT:
                for item in RULE_DICT[rule[1]]:
                    new_rule = [rule[0]] + item
                    if len(new_rule) > 2 or new_rule[1].isupper():
                        result.insert(0, new_rule)
                    else:
                        unit_productions.append(new_rule)
                    if rule[0] not in RULE_DICT:
                        RULE_DICT[rule[0]] = []
                    RULE_DICT[rule[0]].append(rule[1:])
        panjang = len(result)
        tes = 0
        while tes < panjang :
            if not isinstance(result[tes], list) :
                gabungan = [result[tes], result[tes+1]]
                result.pop(tes)
                result.pop(tes)
                result.insert(tes,gabungan)
                panjang -= 1
            tes += 1
        self.is_cnf = True
        self.lines = result
        
def cyk(line,grammarcnf):
    #convert the grammar cnf from a list of list format to a dictionary (hash table) format for cyk efficiency
    dictrules = {}
    for i in range(len(grammarcnf.lines)):
        if grammarcnf.lines[i][0] not in dictrules.keys(): # to add the keys
            dictrules[grammarcnf.lines[i][0]] = []
        if len(grammarcnf.lines[i]) == 2: # format is Nonterminal -> Terminal
            a = grammarcnf.lines[i][1] 
            dictrules[grammarcnf.lines[i][0]].append([a]) 
        elif len(grammarcnf.lines[i]) == 3: # format is Nonterminal -> Terminal
            a = grammarcnf.lines[i][1] 
            b = grammarcnf.lines[i][2] 
            dictrules[grammarcnf.lines[i][0]].append([a,b]) 
        n = len(line)
        
    print(dictrules) # TO TEST THE NEW DICT OF RULES
      
    # Initialize the table
    T = [[set([]) for j in range(n)] for i in range(n)]
  
    # Filling in the table
    for j in range(0, n):
  
        # Iterate over the rules
        for lhs, rule in dictrules.items():
            for rhs in rule:
                  
                # If a terminal is found
                if len(rhs) == 1 and \
                rhs[0] == line[j]:
                    T[j][j].add(lhs)

        for i in range(j, -1, -1):   
               
            # Iterate over the range i to j + 1   
            for k in range(i, j + 1):     
  
                # Iterate over the rules
                for lhs, rule in dictrules.items():
                    for rhs in rule:
                          
                        # If a terminal is found
                        if len(rhs) == 2 and \
                        rhs[0] in T[i][k] and \
                        rhs[1] in T[k + 1][j]:
                            T[i][j].add(lhs)
    # If word can be formed by rules 
    # of given grammar
    if len(T[0][n-1]) != 0:
        print("Accepted")
    else:
        print("Rejected")

if __name__ == "__main__":
    from pathlib import Path
    grammarcnf = CFG(Path(Path(__file__).parent, "examples", "python-cfgrevised.txt"))
    grammarcnf.to_cnf()
    for i in range (len(grammarcnf.lines)):
        print(grammarcnf.lines[i])
    print(len(grammarcnf.lines))
    w = "NAME ASSIGN NUMBER ENDMARK".split()
    cyk(w,grammarcnf) #gatau cara ngetesnya bener gini atau enggak, tapi hasilnya dapet rejected hiks
