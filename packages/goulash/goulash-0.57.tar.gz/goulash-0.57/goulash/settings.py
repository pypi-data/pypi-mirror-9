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
from argparse import ArgumentParser

class SettingsError(Exception):
    pass

class GoulashConfigParser(configparser.ConfigParser):
    pass

class Settings(object):

    default_file = None
    environ_key = None
    #__getitem__ = Dictionaryish.__getitem__

    def get_parser(self):
        """ build the default parser """
        #from optparse import OptionParser
        parser = ArgumentParser() #OptionParser()
        #parser.set_conflict_handler("resolve")
        parser.add_argument(
            "-c", default='',dest='cmd',
            help=("just like python -c or sh -c (pass in a command)"))
        parser.add_argument(
            "-e", "--exec", default='',dest='execfile',
            help='a filename to execute')
        parser.add_argument(
            "-v", '--version', default=False, dest='version',
            action='store_true',
            help=("show version information"))
        parser.add_argument("--shell", dest="shell",
                          default=False, help="application shell",
                          action='store_true')
        parser.add_argument("--config", dest='config',
                          default="",
                          help="use config file")
        return parser

    def get_section(self, k, insist=False):
        try:
            return dict(self._wrapped)[k]
        except KeyError:
            if insist:
                error = 'Fatal: You need to specify a "{0}" section in {1}'
                raise SettingsError(error.format(k, self.settings_file))
            else:
                return None

    def get_setting(self, k, insist=False, default=None):
        """ TODO: move into goulash
            this function returns True for 'true', False for
            `false` or 'no', any other strings are passed through
        """
        _type = 'val'
        section,var = k.split('.')
        section_obj = self.get_section(section, insist=insist)
        try:
            tmp = section_obj[var]
        except KeyError:
            if insist:
                error = ('Fatal: You need to specify a "{0}" section '
                             'with an entry like  "{1}=<{2}>" in {3}')
                raise SettingsError(error.format(
                    section, var, _type, self.settings_file))
            elif default:
                tmp = default
            else:
                return None
        if isinstance(tmp, basestring):
            test = tmp not in ['0', 'false', 'no', 0]
            if not test: return test
        return tmp

    @property
    def settings_file(self):
        if self.options is not None and self.options.config:
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
            err = 'ERROR: config file at "{f}" does not exist'
            err = err.format(f=file)
            raise SettingsError(err)
        config = config.copy()
        cp = GoulashConfigParser()
        from smashlib import embed; embed()
        cp.read(file)
        return cp._sections

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

        if self.options.execfile:
            ns = globals()
            ns.update(settings=self)
            execfile(self.options.execfile, self.shell_namespace())
            return True

        if self.options.version:
            return self.show_version()

        if self.get_setting('user.shell'):
            try:
                from smashlib import embed;
            except ImportError:
                raise SettingsError("You need smashlib installed "
                                    "if you want to use the shell.")
            else:
                embed(user_ns = self.shell_namespace())
            return True

    def __init__(self, filename=None, use_argv=True):
        """ first load the default config so that overrides don't need
            to mention everything.  update default with the config
            specified by the command line optionparser, then
            update that with any other overrides delivered to the parser.
        """
        self._init_filename = filename
        #super(Settings, self).__init__({})
        if use_argv:
            #self.options, self.args = self.get_parser().parse_args()
            self.options, self.args = [self.get_parser().parse_args()]*2
        else:
            self.options = self.args = None
        self._wrapped = self.load(file=self.settings_file)
        # build a special dynamic section for things the user wants,
        # ie, things that have been passed into the option
        # parser but are not useful in the .ini
        if not self.get_section('user'):
            self['user'] = {}
        if self.options is not None:
            self['user']['shell'] = self.options.shell and 'true' or ''
        else:
            self['user']['shell'] = ''

    def __contains__(self, other):
        """ dictionary compatability """
        return other in self._wrapped

    def __getitem__(self,k):
        """ dictionary compatability """
        return self._wrapped[k]

    def keys(self):
        return self._wrapped.keys()

    def __setitem__(self, *args, **kargs):
        return self._wrapped.__setitem__(*args, **kargs)
