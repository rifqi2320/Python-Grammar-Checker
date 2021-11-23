from pathlib import Path

class CFG(object):
    def __init__(self, filename=None):
        self.is_cnf = False
        if filename is None:
            filename = Path(Path(__file__).parent, "examples", "python.cfg")

        with open(filename) as f:
            lines = CFG.sanitize(f.readlines())

        (
            _,
            self._terminals,
            self.productions,
            self.start_variable,
        ) = CFG.parse(lines)
    
    def __str__(self) -> str:
        return '\n'.join([
            "{key} -> {prods}"
            .format(
                key=k,
                prods=' | '.join([
                    (' '.join(p))
                    for p in prods
                ])
            )
            for k, prods in self.productions.items()
        ])

    def __len__(self) -> int:
        return len(self.productions)

    @staticmethod
    def sanitize(lines):
        """Sanitize grammar lines from a text file.

        Args:
            lines (list): List of grammars in readlines() file.

        Returns:
            list: Sanitized and ignored lines in grammar.
        """
        return [
            line.replace("\r", "").replace("\n", "")
            for line in lines
            if line[0] != "#" and line[0] not in ["\n", "\r\n"]
        ]

    @staticmethod
    def parse(prod_lines: "list[str]"):
        """Parse a production lines in array to a properly grammar format.

        Production lines should be sanitized first, i.e. no comments
        or empty line or any trailing line breaks exist.
        First line should be the start variable.
        Return is a 4 tuple (V, T, P, S) where:
            V = set of variables
            T = set of terminals
            P = dict of productions
            S = start variable

        Args:
            grammar_lines (list): Sanitized array of grammar lines.

        Raises:
            KeyError: Duplicated key or terminal does not exist.

        Returns:
            V,T,P,S (set, set, dict, str): Formal CFG tuple.
        """
        terminals = set()
        prods = {}
        start_var = prod_lines[0].split(" -> ")[0].strip()
        for line in prod_lines:
            it = line.split(" -> ")
            # Make sure there's no multiple productions defined.
            it[0] = it[0].strip()
            if it[0] in prods:
                raise KeyError("Duplicate key: " + it[0])
            # Ignore empty, might caused by unnecessary spaces.
            prods[it[0]] = [
                [
                    prod.strip()
                    for prod in prods.split(" ")
                    if prod.strip() != ""
                ]
                for prods in it[1].split(" | ")
            ]
            for production in prods[it[0]]:
                for symbol in production:
                    if symbol.isupper(): # Symbol is a terminal
                        terminals.add(symbol)
        return (set(prods.keys()), terminals, prods, start_var)
    
    @property
    def variables(self):
        return list(self.productions.keys())

    @property
    def terminals(self):
        return self._terminals

    @property
    def get_cyk_form(self):
        prod_vars = []
        prod_terms = []
        for k, prods in self.productions.items():
            for prod in prods:
                if len(prod) == 1 and prod[0].isupper():
                    prod_terms.append([k, prod[0]])
                else:
                    if len(prod) == 2 and not prod[0].isupper() and not prod[1].isupper():
                        prod_vars.append([k, prod[0], prod[1]])
                    else:
                        raise SyntaxError(
                            f"Grammar has invalid productions (not in CNF): {prod}"
                        )
        return prod_vars, prod_terms

    def to_cnf(self):
        grammar = self.productions
        keys = self.variables
        def getVarKey(idx):
            return f'Var{idx}'
        
        def getVarIdx(idx):
            nonlocal grammar
            while getVarKey(idx) in grammar:
                idx += 1
            return idx

        def addNewGen(key, new_gen):
            nonlocal grammar
            for i in range(len(grammar[key])):
                if new_gen == grammar[key][i]:
                    return
            grammar[key].append(new_gen)

        def removeEpsilonProductions():
            nonlocal grammar, keys
            def removeEpsilon(term):
                nonlocal grammar, keys
                for i in range(len(keys)):
                    for j in range(len(grammar[keys[i]])):
                        if (
                            grammar[keys[i]][j].index(term)
                            if term in grammar[keys[i]][j]
                            else -1
                        ) >= 0:
                            new_gen = [[]]
                            for k in range(len(grammar[keys[i]][j])):
                                if grammar[keys[i]][j][k] != term:
                                    for l in range(len(new_gen)):
                                        new_gen[l].append(grammar[keys[i]][j][k])
                                else:
                                    cur_len = len(new_gen)
                                    for l in range(cur_len):
                                        new_gen.append(list(new_gen[l]))
                                        new_gen[l].append(grammar[keys[i]][j][k])
                            for k in range(len(new_gen)):
                                if len(new_gen[k]) == 0:
                                    new_gen[k] = ["e"]
                                addNewGen(keys[i], new_gen[k])
            hasEmpty = True
            while hasEmpty:
                hasEmpty = False
                for i in range(1, len(keys)):
                    j = 0
                    while j < len(grammar[keys[i]]):
                        if len(grammar[keys[i]][j]) == 1 and grammar[keys[i]][j][0] == "e":
                            grammar[keys[i]].pop(j)
                            j -= 1
                            removeEpsilon(keys[i])
                            hasEmpty = True
                        j += 1
        
        def removeSingleProduction():
            nonlocal grammar, keys
            hasSingle = True
            while hasSingle:
                hasSingle = False
                for i in range(len(keys)):
                    j = 0
                    while j < len(grammar[keys[i]]):
                        if len(grammar[keys[i]][j]) == 1 and grammar[keys[i]][j][0] in grammar:
                            key = grammar[keys[i]][j][0]
                            grammar[keys[i]].pop(j)
                            j -= 1
                            k = 0
                            while k < len(grammar[key]):
                                addNewGen(keys[i], grammar[key][k])
                                k += 1
                            hasSingle = True
                        j += 1

        removeEpsilonProductions()
        removeSingleProduction()

        # Convert grammar
        helper_idx = 0
        singles = {}
        multis = {}
        for i in range(len(keys)):
            if len(grammar[keys[i]]) == 1:
                if len(grammar[keys[i]][0]) == 1:
                    term = grammar[keys[i]][0][0]
                    if term != 'e' and term not in grammar:
                        singles[term] = keys[i]

        for i in range(len(keys)):
            if len(grammar[keys[i]]) == 1:
                multis[' '.join(grammar[keys[i]][0])] = keys[i]
        
        i = 0
        while i < len(keys):
            j = 0
            while j < len(grammar[keys[i]]):
                if len(grammar[keys[i]][j]) == 2:
                    for k in range(2):
                        if grammar[keys[i]][j][k] not in grammar:
                            if grammar[keys[i]][j][k] not in singles:
                                helper_idx = getVarIdx(helper_idx)
                                key = getVarKey(helper_idx)
                                keys.append(key)
                                grammar[key] = [[grammar[keys[i]][j][k]]]
                                singles[grammar[keys[i]][j][k]] = key
                            grammar[keys[i]][j][k] = singles[grammar[keys[i]][j][k]]
                elif len(grammar[keys[i]][j]) > 2:
                    last = len(grammar[keys[i]][j]) - 1
                    if grammar[keys[i]][j][last] not in grammar:
                        if grammar[keys[i]][j][last] not in singles:
                            helper_idx = getVarIdx(helper_idx)
                            key = getVarKey(helper_idx)
                            keys.append(key)
                            grammar[key] = [[grammar[keys[i]][j][last]]]
                            singles[grammar[keys[i]][j][last]] = key
                        grammar[keys[i]][j][last] = singles[grammar[keys[i]][j][last]]
                    term = ' '.join(grammar[keys[i]][j][:last])
                    if term not in multis:
                        helper_idx = getVarIdx(helper_idx)
                        key = getVarKey(helper_idx)
                        keys.append(key)
                        grammar[key] = [grammar[keys[i]][j][:last]]
                        multis[term] = key
                    grammar[keys[i]][j] = [multis[term], grammar[keys[i]][j][last]]
                j += 1
            i += 1

        # Delete useless/unreachable prod
        # 1. Traverse through unvisited prods
        front = 0
        queue = [keys[0]]
        reachable = set()
        reachable.add(keys[0])
        while front < len(queue):
            for i in range(len(grammar[queue[front]])):
                for j in range(len(grammar[queue[front]][i])):
                    var = grammar[queue[front]][i][j]
                    if var in grammar and var not in reachable:
                        queue.append(var)
                        reachable.add(var)
            front += 1
        # 2. Delete unreachable and useless prods
        # Delete useless and empty production first
        # Because prod can be unreachable after empty prod check
        i = 0
        while i < len(keys):
            # Useless productions
            j = 0
            while j < len(grammar[keys[i]]):
                for prod in grammar[keys[i]][j]:
                    if prod not in grammar and not prod.isupper():
                        del grammar[keys[i]][j]
                        j -= 1
                        break
                j += 1
            # Remove empty productions if has no prod
            if len(grammar[keys[i]]) == 0:
                del grammar[keys[i]]
                keys.pop(i)
                reachable.remove(keys[i])
                i -= 1
            i += 1
        i = 0
        while i < len(keys):
            if keys[i] not in reachable:
                del grammar[keys[i]]
                keys.pop(i)
                i -= 1
            i += 1

        self.is_cnf = True

if __name__ == "__main__":
    grammarcnf = CFG()
    parent = Path(Path(__file__).parent, "grammar")
    with open(Path(parent, "python-clean.txt"), "w+") as f:
        f.write(str(grammarcnf))
    grammarcnf.to_cnf()
    with open(Path(parent, "python-res.txt"), "w+") as f:
        f.write(str(grammarcnf))
