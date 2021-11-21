class CFG(object):
    def __init__(self, filename):
        self.is_cnf = False
        with open(filename) as f:
            self.lines = f.readlines()

    def to_cnf(self):
        RULE_DICT = {}
        # MENGHAPUS SEMUA RULES YANG TIDAK SESUAI DENGAN BENTUK CHOMSKY NORMAL FORM
        unit_productions, result = [], []
        res_append = result.append
        index = 0 # UNTUK MENAMAI VARIABEL / NONTERMINAL BARU
        grammar = [x.replace("->", "").split() for x in self.lines if x[0] != "#"]
        for rule in grammar:
            new_rules = []
            if len(rule) < 2:
                continue
            elif len(rule) == 2 and rule[1][0] != "'":
                # RULE MEMILIKI FORMAT A -> B, MASIH TIDAK SESUAI SEHINGGA DICATAT DI TAHAP UNIT PRODUCTIONS
                unit_productions.append(rule)
                if rule[0] not in RULE_DICT:
                    RULE_DICT[rule[0]] = []
                RULE_DICT[rule[0]].append(rule[1:])
                continue
            elif len(rule) > 2:
                # RULE MASIH TIDAK SESUAI KARENA PADA SISI KANAN MEMILIKI LEBIH DARI DUA VARIABEL, ATAU GABUNGAN DARI TERMINAL DAN NONTERMINAL
                terminals = [(item, i) for i, item in enumerate(rule) if item[0] == "'"]
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
                    if len(new_rule) > 2 or new_rule[1][0] == "'":
                        result.insert(0, new_rule)
                    else:
                        unit_productions.append(new_rule)
                    if rule[0] not in RULE_DICT:
                        RULE_DICT[rule[0]] = []
                    RULE_DICT[rule[0]].append(rule[1:])
        self.is_cnf = True
        self.lines = result

if __name__ == "__main__":
    from pathlib import Path
    g = CFG(Path(Path(__file__).parent, "examples", "python.txt"))
    g.to_cnf()
    for i in range (len(g.lines)):
        print(g.lines[i])
    print(len(g.lines))
