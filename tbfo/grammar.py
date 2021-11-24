from pathlib import Path

EPSILON_TERM = "e"

class CFG(object):
    def __init__(self, file_path=None):
        """Create a new Context Free Grammar object from a file.

        If file_path is None then the object with python.cfg
        grammar located in examples folder.

        Args:
            file_path (str, optional): File path of the CFG. Defaults to None.
        """
        if file_path is None:
            file_path = Path(Path(__file__).parent, "examples", "python.cfg")

        with open(file_path) as f:
            lines = CFG.sanitize(f.readlines())

        (
            _,
            self._terminals,
            self.productions,
            self.start_variable,
        ) = CFG.parse(lines)
    
    def __str__(self) -> str:
        """Get string representation of this grammar.

        Returns:
            str: String representation of this grammar.
        """
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
        """Get variables of this grammar.

        Returns:
            list: List variables in this grammar.
        """
        return list(self.productions.keys())

    @property
    def terminals(self):
        """Get terminals of this grammar.

        Returns:
            list: List of terminals in this grammar.
        """
        return self._terminals

    def to_cyk(self):
        grammars = self.productions.items()
        prod_vars: dict[str, list[str]] = {}
        prod_terms: dict[str, list[str]] = {}
        for k, prods in grammars:
            for prod in prods:
                if len(prod) == 1 and prod[0].isupper():
                    if prod[0] not in prod_terms:
                        prod_terms[prod[0]] = []
                    prod_terms[prod[0]].append(k)
                elif len(prod) == 2 and not prod[0].isupper() and not prod[1].isupper():
                    h = ' '.join(prod)
                    if h not in prod_vars:
                        prod_vars[h] = []
                    prod_vars[h].append(k)
                else:
                    raise SyntaxError(
                        f"Grammar has invalid productions (not in CNF): {prod}"
                    )
        return prod_vars, prod_terms

    def to_cnf(self):
        """Convert this grammar to Chomsky Normal Form.
        """
        grammar: dict[str, list[list[str]]] = self.productions
        keys = self.variables
        def gen_var(idx):
            """Generate variable name for additional production.

            Prevent duplicate variable name if variable somehow
            present in grammar by adding number.

            Args:
                idx (int): Current variable index.

            Returns:
                int, str: Generated variable index and name.
            """
            nonlocal grammar
            var = 'Var{}'
            while var.format(idx) in grammar:
                idx += 1
            return idx, var.format(idx)

        def add_new_gen(var, new_prod):
            """Add new production in var if not exist.

            Args:
                var (str): Variable name to add new production.
                new_gen (str): New production to add.
            """
            nonlocal grammar
            for prod in grammar[var]:
                if new_prod == prod:
                    return
            grammar[var].append(new_prod)

        def remove_epsilon_productions():
            """Remove any epsilon production.

            Will also regenerate any production that uses that
            epsilon production.
            """
            nonlocal grammar, keys
            def remove_epsilon(var_eps):
                """Regenerate production if uses production `var_eps`.

                It will try to add new production in any production
                that uses `var_eps` which has an apsilon production.

                Args:
                    var_eps (str): Variable that has epsilon production.
                """
                nonlocal grammar, keys
                for var in keys:
                    for prod in grammar[var]:
                        if var_eps in prod:
                            new_gen = [[]]
                            for k in range(len(prod)):
                                if prod[k] != var_eps:
                                    for l in range(len(new_gen)):
                                        new_gen[l].append(prod[k])
                                else:
                                    cur_len = len(new_gen)
                                    for l in range(cur_len):
                                        new_gen.append(list(new_gen[l]))
                                        new_gen[l].append(prod[k])
                            for k in range(len(new_gen)):
                                if len(new_gen[k]) == 0:
                                    new_gen[k] = [EPSILON_TERM]
                                add_new_gen(var, new_gen[k])
            hasEmpty = True
            while hasEmpty:
                hasEmpty = False
                for i in range(1, len(keys)):
                    j = 0
                    while j < len(grammar[keys[i]]):
                        if len(grammar[keys[i]][j]) == 1 and grammar[keys[i]][j][0] == EPSILON_TERM:
                            grammar[keys[i]].pop(j)
                            j -= 1
                            remove_epsilon(keys[i])
                            hasEmpty = True
                        j += 1
        
        def remove_single_productions():
            nonlocal grammar, keys
            hasSingle = True
            while hasSingle:
                hasSingle = False
                for var in keys:
                    j = 0
                    while j < len(grammar[var]):
                        if len(grammar[var][j]) == 1 and grammar[var][j][0] in grammar:
                            key = grammar[var][j][0]
                            grammar[var].pop(j)
                            j -= 1
                            k = 0
                            while k < len(grammar[key]):
                                add_new_gen(var, grammar[key][k])
                                k += 1
                            hasSingle = True
                        j += 1

        remove_epsilon_productions()
        remove_single_productions()

        # Convert grammar
        helper_idx = 0
        singles = {}
        multis = {}
        for var in keys:
            prods = grammar[var]
            if len(prods) == 1:
                multis[' '.join(prods[0])] = var
                if len(prods[0]) == 1:
                    term = prods[0][0]
                    if term != EPSILON_TERM and term not in grammar:
                        singles[term] = var

        i = 0
        while i < len(keys):
            j = 0
            prod = grammar[keys[i]]
            while j < len(prod):
                if len(prod[j]) == 2:
                    for k in range(2):
                        if prod[j][k] not in grammar:
                            if prod[j][k] not in singles:
                                helper_idx, key = gen_var(helper_idx)
                                keys.append(key)
                                grammar[key] = [[prod[j][k]]]
                                singles[prod[j][k]] = key
                            prod[j][k] = singles[prod[j][k]]

                elif len(prod[j]) > 2:
                    last = len(prod[j]) - 1
                    if prod[j][last] not in grammar:
                        if prod[j][last] not in singles:
                            helper_idx, key = gen_var(helper_idx)
                            keys.append(key)
                            grammar[key] = [[prod[j][last]]]
                            singles[prod[j][last]] = key
                        prod[j][last] = singles[prod[j][last]]

                    term = ' '.join(prod[j][:last])
                    if term not in multis:
                        helper_idx, key = gen_var(helper_idx)
                        keys.append(key)
                        grammar[key] = [prod[j][:last]]
                        multis[term] = key
                    prod[j] = [multis[term], prod[j][last]]
                j += 1
            i += 1

        # Delete useless/unreachable prod
        # 1. Traverse through unvisited prods
        front = 0
        queue = [keys[0]]
        reachable = set()
        reachable.add(keys[0])
        while front < len(queue):
            for prod in grammar[queue[front]]:
                for sym in prod:
                    if sym in grammar and sym not in reachable:
                        queue.append(sym)
                        reachable.add(sym)
            front += 1
        # 2. Delete useless prods
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
        # 3. Delete unreachable prods
        while i < len(keys):
            if keys[i] not in reachable:
                del grammar[keys[i]]
                keys.pop(i)
                i -= 1
            i += 1

if __name__ == "__main__":
    grammarcnf = CFG()
    parent = Path(Path(__file__).parent, "grammar")
    with open(Path(parent, "python-clean.txt"), "w+") as f:
        f.write(str(grammarcnf))
    grammarcnf.to_cnf()
    with open(Path(parent, "python-res.txt"), "w+") as f:
        f.write(str(grammarcnf))
