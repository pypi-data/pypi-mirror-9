""" goulash.heuristics

    Heuristics typically return answers of some kind, but if the heuristics
    themselves are complex or cascading, simply returning booleans or integers
    or whatever can be confusing.  The objects in this file provide tools
    for wrapping results in such a way that they function as expected but
    can optionally include explanations.  More detailed descriptions of available
    wrappers follow.

    Answer(obj):
      has a truth value depending on the object itself.

    ExplainedAnswer(obj, optional_explanation):
      Couples an answer with an explanation.
      The explanation may be any object, but
      whatever it is will be converted to a string.

    NotApplicable(optional_explanation):
      Heuristic was not applicable.
      This always tests as False.

    Affirmative(explanation):
      An ExplainedAnswer that always tests as true.
      Again any object may be used as the explanation,
      but it will always be converted to a string.

    Negative(explanation):
      An ExplainedAnswer that always tests as false.
      Again any object may be used as the explanation,
      but it will always be converted to a string.

"""

from goulash.wrappers import DumbWrapper

class Answer(DumbWrapper):
    def __str__(self):
        return "({0}: {1})".format(
            self.__class__.__name__,
            str(self.obj))

    def __nonzero__(self):
        return bool(self.obj)

    __repr__ = __str__

class ExplainedAnswer(Answer):
    def __init__(self, obj, explanation="No explanation given."):
        super(ExplainedAnswer, self).__init__(obj)
        self.explanation = str(explanation)

    def __str__(self):
        return "({0}: {1})".format(
            self.__class__.__name__,
            str(self.explanation))

class NotApplicable(DumbWrapper):
    def __init__(self, obj=None):
        super(NotApplicable, self).__init__(obj)

    def __nonzero__(self):
        return False

    def __str__(self):
        return "(NotApplicable: {0})".format(str(self.obj))
    __repr__=__str__

class Affirmative(ExplainedAnswer):
    def __init__(self, explanation="no reason given"):
        self.obj = True
        self.explanation = str(explanation)

    def __nonzero__(self):
        return True

class NegativeAnswer(ExplainedAnswer):
    def __init__(self, explanation="no reason given"):
        self.obj = False
        self.explanation = str(explanation)
Negative = NegativeAnswer
