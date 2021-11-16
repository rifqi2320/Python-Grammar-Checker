class Symbol:
  def __init__(self, name, symbol):
    self.name = name
    self.symbol = symbol

  def __str__(self):
    return self.name

symbols = []
with open("keyword.txt") as f:
  lines = f.readlines()
  flag = False
  for line in lines:
    if (line.strip() == "SYMBOL"):
      flag = True
    temp = line.strip().split()
    
    if len(temp) == 2:
      if flag:
        symbols.append(Symbol(temp[0], temp[1]))
      else:
        symbols.append(Symbol(temp[0], temp[1] + " "))


class VariableChecker:
  def __init__(self):
    # inisialisasi quintuple
    self.startState = ["q1"]
    self.finalState = ["q2"]
    self.state = ["q1", "q2"]
    self.sym = {
      "upperCase" : "A B C D E F G H I J K L M N O P Q R S T U V W X Y Z".split(),
      "lowerCase" : "a b c d e f g h i j k l m n o p q r s t u v w x y z".split(),
      "number" : "1 2 3 4 5 6 7 8 9 0".split(),
      "underscore" : ["_"]
    }
    self.delta = [
      ["q1", self.sym["upperCase"] + self.sym["lowerCase"] + self.sym["underscore"], "q2"],
      ["q2", self.sym["upperCase"] + self.sym["lowerCase"] + self.sym["underscore"] + self.sym["number"], "q2"]    ]
  
  def check(self, inp):
    state = self.startState
    for c in inp:
      transition = [x for x in self.delta if ((c in x[1]) and (x[0] in state))]
      if transition:
        state = list(set([x[2] for x in transition]))
      else:
        return False
    if set(state) & set(self.finalState):
      return True
    else:
      return False


def lex(line):
  res = [line]
  global symbols
  for sym in symbols:
    n = len(sym.symbol)
    for i in range(len(res) -1 , -1, -1):
      if (type(res[i]) == str):
        while sym.symbol in res[i]:
          find = res[i].rfind(sym.symbol)
          if find >= 0:
            text = res.pop(i)
            res.insert(i, text[find + n:])
            res.insert(i, sym)
            res.insert(i, text[:(find)])
  return [x for x in res if x]

with open("test.py") as f:
  lines = f.readlines()
for line in lines:
  res = lex(line.strip())
  print("[",end='')
  for a in res:
    print(a,end=',')
  print("]")