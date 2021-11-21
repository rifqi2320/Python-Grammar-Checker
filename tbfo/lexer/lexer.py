from tbfo.parser.fa import VariableChecker
import os

class Symbol:
  def __init__(self, name, symbol):
    self.name = name
    self.symbol = symbol

  def __str__(self):
    return self.name


class Lexer:
  def __init__(self):
    self.symbols = []
    with open(os.path.dirname(os.path.realpath(__file__)) + "\\keyword.txt") as f:
      lines = f.readlines()
      flag = False
      for line in lines:
        if (line.strip() == "NON-SPACE"):
          flag = True
        temp = line.strip().split()
        if len(temp) == 2:
          if flag:
            self.symbols.append(Symbol(temp[0], temp[1]))
          else:
            self.symbols.append(Symbol(temp[0], temp[1] + " "))
    self.symbols.append(Symbol("SPACE", " "))
    self.symbols.append(Symbol("NL", "\n"))

    # Helper (Finite Automata)
    self.varCheck = VariableChecker()

    # Flags
    self.comment_flag = None
    self.string_flag = None
    self.number_flag = False

    # Constants
    self.sym_STRING = Symbol("STRING", '""')
    self.sym_NUMBER = Symbol("NUMBER", "0-9")
    self.sym_NAME = Symbol("NAME", "var")

  def lex(self, line):
    res = [line]
    # Tokenize symbol
    for sym in self.symbols:
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

    # Clean empty element
    res = [x for x in res if x]

    # Clean all spaces
    for i in range(len(res) - 1, -1, -1):
      if (type(res[i]) == Symbol and str(res[i]) == "SPACE"):
        res.pop(i)

    # Parse Comment (remove comments)
    i = 0
    self.comment_flag = None
    while i < len(res):
      if self.comment_flag:
        if (type(res[i]) == Symbol):
          if ("TRIPLEQUOTE" in str(res[i])):
            if self.comment_flag == res[i]:
              self.comment_flag = None
        res.pop(i)
      else:
        if (type(res[i]) == Symbol):
          if (("TRIPLEQUOTE" in str(res[i]) and i == 0) or str(res[i]) == "HASHTAG"):
            self.comment_flag = res[i]
            res.pop(i)
          else:
            i += 1
        else:
          i += 1

    # Parse Strings
    self.string_flag = None
    for i in range(len(res) - 1, -1, -1):
      if (self.string_flag):
        if (self.string_flag == res[i]):
          res[i] = self.sym_STRING
          self.string_flag = None
        else:
          res.pop(i)
      else:
        if type(res[i]) == Symbol:
          if (str(res[i]) == "QUOTE1" or str(res[i]) == "QUOTE2"):
            self.string_flag = res[i]
            res.pop(i)
    if self.string_flag:
      self.string_flag = None
      raise SyntaxError("Unterminated String")

    # Parse Number
    self.number_flag = False
    for i in range(len(res) - 1, -1, -1):
      if self.number_flag:
        if (type(res[i]) == Symbol):
          if (str(res[i]) == "DOT"):
            res.pop(i)
          else:
            res.insert(i+1, self.sym_NUMBER)
            self.number_flag = False
        else:
          if (res[i].isnumeric()):
            res.pop(i)
          else:
            res.insert(i+1, self.sym_NUMBER)
            self.number_flag = False
      else:
        if (type(res[i]) == str):
          if (res[i].isnumeric()):
            res.pop(i)
            self.number_flag = True
    if self.number_flag:
      self.number_flag = False
      res.insert(0, self.sym_NUMBER)

    
    for i in range(len(res)):
      if (type(res[i]) == str and self.varCheck.check(res[i])):
        res[i] = self.sym_NAME
    return res

  def lex_lines(self,lines):
    res = []
    try:
      for i in range(len(lines)):
        temp = self.lex(lines[i])
        check = [x for x in temp if type(x) != Symbol]
        if (check):
          raise SyntaxError(f"Invalid variable : {','.join(check)}.")
        if (self.comment_flag):
          raise SyntaxError(f"Unterminated multiline comments.")
        res += temp
    except SyntaxError as e:
      print(f'Error in line: {i+1}')
      print(e)
    return res