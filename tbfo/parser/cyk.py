
# LOAD GRAMMAR DARI FILE TXT. Format dari grammarnya harus one liner, kalau ada | Maka harus ditulis dibawahnya.
def readgrammar(filename):
    nonterminals, terminals = [], [] # INI ITU LIST OF LIST, ISINYA ADALAH [VARIABEL,NONTERM,NONTERM] ATAU [VARIABEL,TERM] UNTUK MEMPERMUDAH PROSES SEARCHING NANTI
    with open(filename) as f:
        lines = f.readlines()
    for line in lines :
        if line[0] != '|' : # INI KASUS START DARI SEBUAH VARIABEL, MISALNYA A -> B
            sementara = line.replace("->", "").split()
            nonterminal = sementara[0]
            if len(sementara) == 2 :
                terminals.append(sementara)
            elif len(sementara) == 3:
                nonterminals.append(sementara)
        else : # INI KASUS KALAU AWALNYA |
            buangawal = line[2:]
            tambahan = buangawal.split()
            if len(tambahan) == 1:
                terminals.append([nonterminal, tambahan[0]])
            elif len(tambahan) == 2:
                nonterminals.append([nonterminal, tambahan[0], tambahan[1]])
    return nonterminals, terminals

# ALGORITMA PERKALIAN SILANG, MISALNYA NON TERMINAL A B*C D JADINYA AC AD BC BD. digunakan untuk mengisi / mengecek kotak pada tabel CYK
def kaliSilang(kiri , kanan):
    hasil = []
    for i in range (len(kiri)):
        for j in range(len(kanan)):
            hasil.append([kiri[i],kanan[j]])
    return hasil

# ALGORITMA YANG DIGUNAKAN PERSIS SESUAI DENGAN PSEUDOCODE PADA WIKIPEDIA
def cyk(variables,terminals, lexer): 
    tabel = [[[] for j in range(len(lexer)-i)] for i in range(len(lexer))] # INISIALISASI TABEL UNTUK CYK, ISINYA BERUPA LIST

    # INI UNTUK MENGISI LEVEL PERTAMA DARI TABEL
    for i in range(len(lexer)):
        for j in range (len(terminals)):
            if lexer[i] == terminals[j][1]: # Kalau lexer ke-i ketemu di terminal, langsung gas isi pada tabel level pertama
                tabel[0][i].append(terminals[j][0])
                
    # INI UNTUK MENGISI LEVEL SISANYA DARI TABEL
    for i in range(1,len(lexer)): # i adalah iterasi untuk tiap level pada tabel
        for j in range(len(lexer) - i): # j adalah iterasi untuk tiap kolom pada tabel
            for k in range(i): # k adalah iterasi untuk banyaknya pengecekan/kali silang untuk tiap pengisian kotak pada tabel
                hasil = kaliSilang(tabel[k][j], tabel[i-k-1][j+k+1])
                for l in range(len(hasil)): # l adalah iterasi untuk tiap hasil kali silang
                    for m in range (len(variables)): #m adalah iterasi untuk mencari di variables apakah ada
                        if variables[m][1:] == hasil[l] :
                            tabel[i][j].append(variables[m][0]) # Kalau hasil kali silang ada di variables, langsung gas isi pada tabel
    return tabel

def show_result(tab, inp): # DA REAL MVP FOR DEBUGGING!
    for c in inp:
        print("\t{}".format(c), end="\t")
    print()
    for i in range(len(inp)):
        print(i+1, end="")
        for c in tab[i]:
            if c == []:
                print("\t{}".format("_"), end="\t")
            else:
                print("\t{}".format(c), end=" ")
        print()

    if 'Start' in tab[len(inp)-1][0]:
        print("CONGRATS MOM YOU DID IT!")
    else:
        print("Rejected")

if __name__ == "__main__":
    variables, terminals = readgrammar("./tbfo/examples/python-cnf.txt")
    lexer = "FROM NAME DOT NAME DOT NAME IMPORT NAME NL ENDMARK".split()
    tabel = cyk(variables, terminals, lexer)
    show_result(tabel, lexer)