from tbfo.parser.fa import VariableChecker
import os
from pathlib import Path

class Symbol:
  def __init__(self, name, symbol):
    self.name = name
    self.symbol = symbol

  def __str__(self):
    return self.name

class Lexer:
  def __init__(self, filepath=None):
    self.symbols = []
    self.keywords = []
    self.whitespace = []
    if filepath is None:
      filepath = Path(
        Path(__file__).parent,
        "examples",
        "tokens.txt"
      )
    with open(filepath) as f:
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
    while i < len(res):
      if self.comment_flag:
        if (type(res[i]) == Symbol):
          if ("TRIPLEQUOTE" in str(res[i])):
            if self.comment_flag == res[i]:
              self.comment_flag = None
        res.pop(i)
      else:
        if (type(res[i]) == Symbol):
          check = [x for x in res if str(x) != "SPACE"]
          if ((check and "TRIPLEQUOTE" in str(check[0]) and "TRIPLEQUOTE" in str(res[i])) or str(res[i]) == "HASHTAG"):
            self.comment_flag = res[i]
            res.pop(i)
          else:
            i += 1
        else:
          i += 1
    # Parse Strings
    string_flag = None
    for i in range(len(res) - 1, -1, -1):
      if (string_flag):
        if (string_flag == res[i]):
          res[i] = self.sym_STRING
          string_flag = None
        else:
          res.pop(i)
      else:
        if type(res[i]) == Symbol:
          if (str(res[i]) == "QUOTE1" or str(res[i]) == "QUOTE2"):
            string_flag = res[i]
            res.pop(i)
    if string_flag:
      string_flag = None
      raise SyntaxError("Unterminated String")

    # Parse Number
    number_flag = False
    isFloat = False
    for i in range(len(res) - 1, -1, -1):
      if number_flag:
        if (type(res[i]) == Symbol):
          if (str(res[i]) == "DOT" and not isFloat):
            res.pop(i)
            isFloat = True
          else:
            res.insert(i+1, self.sym_NUMBER)
            number_flag = False
        else:
          if (res[i].isnumeric()):
            res.pop(i)
          else:
            res.insert(i+1, self.sym_NUMBER)
            number_flag = False
      else:
        if (type(res[i]) == str):
          if (res[i].isnumeric()):
            res.pop(i)
            number_flag = True
    if number_flag:
      number_flag = False
      res.insert(0, self.sym_NUMBER)

    # Evaluasi Variable
    for i in range(len(res)):
      if (type(res[i]) == str and self.varCheck.check(res[i])):
        res[i] = self.sym_NAME
    return res

  def lex_lines(self,lines, check_indent=True):
    res = []
    indentation = [0] # indentasi yang valid
    if_flag = [] # indentasi dimana ada if
    loop_flag = [] #indentasi dimana ada loop
    function_flag = [] #indentasi dimana ada fungsi
    indent_flag = 0
    lines.append("\n")
    try:
      for i in range(len(lines)):
        temp = self.lex(lines[i])
        if not [x for x in temp if str(x) not in ["SPACE", "NL"]]:
          res.append([Symbol("NL", "\n")])
          continue
        check = [x for x in temp if type(x) != Symbol]
        if (check):
          raise SyntaxError(f"Invalid variable : {','.join(check)}.")
        
        # Check Indentation
        if check_indent:
          indent = 0
          while (indent < len(temp) and type(temp[indent]) == Symbol and str(temp[indent]) == "SPACE"):
            indent += 1
          if indent_flag: 
            if (indent > max(indentation)): # Indentation must increase
              indentation.append(indent) 
              indent_flag -= 1
            else:
              raise SyntaxError(f"Indentation Error")
          else:
            if indent not in indentation: # Indentation Tidak
              raise SyntaxError(f"Indentation Error")
          if (indent < len(temp) and str(temp[indent]) in self.keyword_INDENT): # Indentation flag raised
            indent_flag += 1

          if indent < len(temp):
            # Check keyword that need flags
            if (str(temp[indent]) == "ELIF"):
              if (indent not in if_flag):
                raise SyntaxError(f"Invalid Syntax")
            elif (str(temp[indent]) == "ELSE"):
              if (indent not in if_flag + loop_flag):
                raise SyntaxError(f"Invalid Syntax")
            elif (str(temp[indent]) == "RETURN"):
              if not function_flag or indent < min(function_flag):
                raise SyntaxError(f"Invalid Syntax")
            elif (str(temp[indent]) in ["BREAK", "CONTINUE"]):
              if not loop_flag or indent < min(loop_flag):
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
          

        res.append(temp)

      # Clean all spaces
      for line in res:
        for j in range(len(line) - 1, -1, -1):
          if (type(line[j]) == Symbol and str(line[j]) == "SPACE"):
            line.pop(j)

      if res:
        for k in range(len(res)):
          if str(res[k][-1]) != "NL":
            res[k].append(Symbol("NL", "\n"))

      # If multiline comments arent terminated
      if (self.comment_flag):
          raise SyntaxError(f"Unterminated multiline comments.")
    except SyntaxError as e:
      print(f'Syntax Error in line: {i+1}')
      print(e)
      print(f'"{lines[i].strip()}"')
      return None
    return res

if __name__ == '__main__':
  with open("test.py") as f:
    lines = f.readlines()
  lexer = Lexer()
  res = lexer.lex_lines(lines)
  for line in lines:
    print(line, end='')
  print()
  for line in res:
    print('[')
    for a in line:
      print(str(a), end=' ')
      if (str(a) == "NL"):
        print()
    print(']')