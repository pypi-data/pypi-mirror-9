""" goulash.ansi
"""

from ansi2html.style import get_styles
from ansi2html import Ansi2HTMLConverter as _Ansi2HTMLConverter

class Ansi2HTMLConverter(_Ansi2HTMLConverter):
    """ Subclassed from ansi2html.Ans2HTMLConverter to prevent
        every convert() call redundantly rendering the style
    """
    def get_style(self):
        return '<style>' + \
               "\n".join(map(str, get_styles(self.dark_bg, self.scheme))) + \
               '</style>'

    def convert(self, *args, **kargs):
        kargs.update(full=False)
        return super(Ansi2HTMLConverter, self).convert(*args, **kargs)
Ansi2HtmlConverter=Ansi2HTMLConverter
