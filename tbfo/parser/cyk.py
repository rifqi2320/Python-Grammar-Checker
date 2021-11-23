from tbfo.grammar import CFG

class CYK:
    def __init__(self, grammar: CFG, verbose=False) -> None:
        self.grammar = grammar
        (
            variables,
            self.terminals
        ) = self.grammar.get_cyk_form
        variables_cache = {}
        for prod in variables:
            h = ' '.join(prod[1:])
            if h not in variables_cache:
                variables_cache[h] = []
            variables_cache[h].append(prod[0])
        self.variables_cache = variables_cache
        self.verbose = verbose
    
    # ALGORITMA PERKALIAN SILANG, MISALNYA NON
    # TERMINAL A B*C D JADINYA AC AD BC BD.
    # Digunakan untuk mengisi / mengecek kotak pada tabel CYK
    @staticmethod
    def kali_silang(kiri, kanan):
        return [
            [l, r]
            for l in kiri
            for r in kanan
        ]

    def parse(self, tokens):
        # INISIALISASI TABEL UNTUK CYK, ISINYA BERUPA LIST
        tabel = [
            [ [] for _ in range(len(tokens)-i) ]
            for i in range(len(tokens))
        ]

        # INI UNTUK MENGISI LEVEL PERTAMA DARI TABEL
        for i in range(len(tokens)):
            for term in self.terminals:
                # Kalau tokens ke-i ketemu di terminal,
                # langsung gas isi pada tabel level pertama
                if (
                    tokens[i] == term[1]
                    and term[0] not in tabel[0][i]
                ):
                    tabel[0][i].append(term[0])

        # INI UNTUK MENGISI LEVEL SISANYA DARI TABEL
        # i adalah iterasi untuk tiap level pada tabel
        for i in range(1,len(tokens)):
            # j adalah iterasi untuk tiap kolom pada tabel
            for j in range(len(tokens) - i):
                # k adalah iterasi untuk banyaknya pengecekan/kali
                # silang untuk tiap pengisian kotak pada tabel
                for k in range(i):
                    hasil = self.kali_silang(
                        tabel[k][j],
                        tabel[i-k-1][j+k+1],
                    )
                    for h in hasil: # h adalah iterasi untuk tiap hasil kali silang
                        h = ' '.join(h)
                        if h in self.variables_cache:
                            if self.variables_cache[h] not in tabel[i][j]:
                                # Kalau hasil kali silang ada di variables,
                                # langsung gas isi pada tabel
                                tabel[i][j] = [
                                    *tabel[i][j],
                                    *self.variables_cache[h]
                                ]
        # APABILA INGIN DICETAK
        if self.verbose: 
            for t in tokens:
                # UNTUK MENCETAK TIAP TOKEN
                print("\t" + str(t), end="\t")
            print()
            for i in range(len(tokens)): # ITERASI UNTUK TIAP BARIS PADA TABEL
                print(i + 1, end="")
                for j in range(len(tabel[i])): # ITERASI UNTUK TIAP KOLOM PADA TABEL
                    print("\t" + str(tabel[i][j]), end="\t")
                print()

        # Mengembalikan apakah start terkandung di paling bawah
        # (kotak full sequence) / accepted atau tidak / rejected
        return self.grammar.start_variable in tabel[len(tokens)-1][0]
