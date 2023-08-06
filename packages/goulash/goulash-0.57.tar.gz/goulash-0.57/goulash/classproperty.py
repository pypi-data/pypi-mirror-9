""" goulash.classproperty

    SOURCE:
      http://stackoverflow.com/questions/128573/using-property-on-classmethods
"""
class classproperty(property):
    """
        USAGE:
          class constants:
              @classproperty
              def lazy(kls):
                  return "whatevs"
    """
    def __init__(self, func):
        return super(classproperty, self).__init__(classmethod(func))

    def __get__(self, obj, type_):
        return self.fget.__get__(None, type_)()

    def __set__(self, obj, value):
        cls = type(obj)
        return self.fset.__get__(None, cls)(value)
