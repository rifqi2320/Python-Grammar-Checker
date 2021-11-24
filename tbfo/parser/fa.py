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
      ["q2", self.sym["upperCase"] + self.sym["lowerCase"] + self.sym["underscore"] + self.sym["number"], "q2"]]
  
  def check(self, inp):
    """Melakukan check terhadap input string
    
    """

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


