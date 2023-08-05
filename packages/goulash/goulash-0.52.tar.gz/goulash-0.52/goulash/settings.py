""" goulash.settings

    Standard configuration parser suitable to inherit
    for all kinds of applications.  This parses ini files
    and command line options, then combines the information.
    As a result of having all the information it is convenient
    (if not exactly correct) to treat the settings object
    as an "entry point".
"""
import os
import configparser

class SettingsError(Exception):
    pass

class GoulashConfigParser(configparser.ConfigParser):
    pass

class Settings(object):

    default_file = None
    environ_key = None
    #__getitem__ = Dictionaryish.__getitem__

    @classmethod
    def get_parser(kls):
        """ build the default parser """
        from optparse import OptionParser
        parser = OptionParser()
        parser.set_conflict_handler("resolve")
        parser.add_option(
            "-c", default='',dest='cmd',
            help=("like python -c: \"a program passed in"
                  " as string (terminates option list)\""))
        parser.add_option(
            "-v", '--version', default=False, dest='version',
            action='store_true',
            help=("show version information"))
        parser.add_option("--shell", dest="shell",
                          default=False, help="application shell",
                          action='store_true')
        parser.add_option("--config", dest='config',
                          default="",
                          help="use config file")
        return parser

    @property
    def settings_file(self):
        if self.options.config:
            _file = self.options.config
        else:
            _file = self._init_filename or \
                    os.environ.get(self.environ_key) or \
                    self.default_file
        _file = os.path.expanduser(_file)
        return _file

    def pre_run(self):
        """ hook for subclassers.. """
        pass

    def load(self, file, config={}):
        """ returns a dictionary with key's of the form
            <section>.<option> and the values
        """
        if not os.path.exists(file):
            err = 'ERROR: config file at "{f}" does not exist'.format(f=file)
            raise SettingsError(err)
        config = config.copy()
        cp = GoulashConfigParser()
        cp.read(file)
        return cp

    def shell_namespace(self):
        """ when --shell is used, the dictionary
            returned by this function populates
            all the shell variables """
        return {}

    def show_version(self):
        """ subclassers should call super
            and then print their own junk """
        from goulash import __version__
        print 'goulash=={0}'.format(__version__)

    def run(self, *args, **kargs):
        """ this is a thing that probably does not belong in a
            settings abstraction, but it is very useful..
        """
        self.pre_run()

        if self.options.cmd:
            ns = globals()
            ns.update(settings=self)
            exec self.options.cmd in self.shell_namespace()
            return True

        if self.options.version:
            return self.show_version()

        if self['user']['shell']:
            try:
                from smashlib import embed;
            except ImportError:
                raise SettingsError("You need smashlib installed "
                                    "if you want to use the shell.")
            else:
                embed(user_ns=self.shell_namespace())
            return True

    def __init__(self, filename=None):
        """ first load the default config so that overrides don't need
            to mention everything.  update default with the config
            specified by the command line optionparser, then
            update that with any other overrides delivered to the parser.
        """
        self._init_filename = filename
        #super(Settings, self).__init__({})
        self.options, self.args = self.get_parser().parse_args()
        self._wrapped = self.load(file=self.settings_file)
        # build a special dynamic section for things the user wants,
        # ie, things that have been passed into the option
        # parser but are not useful in the .ini
        if 'user' not in self:
            self['user'] = {}
        self['user']['shell'] = self.options.shell and 'true' or ''

    def __contains__(self, other):
        """ dictionary compatability """
        return other in self._wrapped

    def __getitem__(self,k):
        """ dictionary compatability """
        return self._wrapped[k]

    def keys(self):
        return self._wrapped.keys()

    def update(self, *args, **kargs):
        return self._wrapped.update(*args, **kargs)

    def __setitem__(self, *args, **kargs):
        return self._wrapped.__setitem__(*args, **kargs)
