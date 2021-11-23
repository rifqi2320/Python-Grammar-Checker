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
    self.keywords = []
    self.whitespace = []
    with open(os.path.dirname(os.path.realpath(__file__)) + "\\keyword.txt") as f:
      lines = f.readlines()
    flag = False
    for line in lines:
      if line[0] == '#':
        continue
      if (line.strip() == "SYMBOL"):
        flag = True
        self.whitespace.append(Symbol("SPACE", " "))
        self.whitespace.append(Symbol("NL", "\r\n"))
        self.whitespace.append(Symbol("NL", "\n"))

      temp = line.strip().split()
      if len(temp) == 2:
        if flag:
          self.symbols.append(Symbol(temp[0], temp[1]))
        else:
          self.keywords.append(Symbol(temp[0], temp[1]))
    
          


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

    self.keyword_INDENT = ["IF", "ELIF", "ELSE", "FOR", "WHILE", "DEF", "CLASS", "WITH"]

  def lex(self, line):
    res = [line]
    # Tokenize symbol and whitespace
    for sym in self.symbols + self.whitespace:
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

    # Tokenize keyword
    for keyword in self.keywords:
      for i in range(len(res) -1, -1, -1):
        if res[i] == keyword.symbol:
          res[i] = keyword

    # Clean empty element
    res = [x for x in res if x]

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
          if (("TRIPLEQUOTE" in str([x for x in res if str(x) != "SPACE"][0])) or str(res[i]) == "HASHTAG"):
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
    indentation = [0] # indentasi yang valid
    if_flag = [] # indentasi dimana ada if
    loop_flag = [] #indentasi dimana ada loop
    function_flag = [] #indentasi dimana ada fungsi
    indent_flag = False
    try:
      for i in range(len(lines)):
        temp = self.lex(lines[i])
        if not temp:
          continue
        check = [x for x in temp if type(x) != Symbol]
        if (check):
          raise SyntaxError(f"Invalid variable : {','.join(check)}.")
        
        # Check Indentation
        indent = 0
        while (indent < len(temp) and type(temp[indent]) == Symbol and str(temp[indent]) == "SPACE"):
          indent += 1
        if indent_flag: # Indentation flag raised
          if (indent > max(indentation)):
            indentation.append(indent)
            indent_flag = False
          else:
            raise SyntaxError(f"Indentation Error")
        else:
          if indent in indentation: # Indentation Valid
            if (str(temp[indent]) in self.keyword_INDENT):
              indent_flag = True
          else:
            raise SyntaxError(f"Indentation Error")

        
        if indent < len(temp):
          # Check keyword that need flags
          if (str(temp[indent]) == "ELIF"):
            if (indent not in if_flag):
              raise SyntaxError(f"Invalid Syntax")
          elif (str(temp[indent]) == "ELSE"):
            if (indent not in if_flag + loop_flag):
              raise SyntaxError(f"Invalid Syntax")
          elif (str(temp[indent]) == "RETURN"):
            if indent < min(function_flag):
              raise SyntaxError(f"Invalid Syntax")

          # Update Indentation
          if_flag = [x for x in if_flag if x < indent]  
          loop_flag = [x for x in loop_flag if x < indent]
          function_flag = [x for x in function_flag if x < indent]
          indentation = [x for x in indentation if x <= indent]

          # Check flag raiser
          if (str(temp[indent]) in ["IF", "ELIF"]):
            if_flag.append(indent)
          elif (str(temp[indent]) in ["FOR", "WHILE"]):
            loop_flag.append(indent)
          elif (str(temp[indent]) == "DEF"):
            function_flag.append(indent)
        

        res += temp

      # Clean all spaces
      for i in range(len(res) - 1, -1, -1):
        if (type(res[i]) == Symbol and str(res[i]) == "SPACE"):
          res.pop(i)
      
      # If multiline comments arent terminated
      if (self.comment_flag):
          raise SyntaxError(f"Unterminated multiline comments.")
    except SyntaxError as e:
      print(f'Error in line: {i+1}')
      print(e)
      print(f'"{lines[i].strip()}"')
      return None
    res.append(Symbol("ENDMARK", ""))
    return res

if __name__ == '__main__':
  with open("test.py") as f:
    lines = f.readlines()
  lexer = Lexer()
  res = lexer.lex_lines(lines)
  for line in lines:
    print(line, end='')
  print()
  for a in res:
    print(a,end=' ')
    if (str(a) == "NL"):
      print()