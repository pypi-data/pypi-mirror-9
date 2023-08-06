"""
Provide all the default access to R (via rpy2)
"""

import os
import sys
import tempfile

from glob import glob
from django.utils.text import slugify as _sl
slugify = lambda t: _sl(unicode(t))

from .settings import *

__all__ = ('get_R', 'Packages', 'Library', 'ScriptRunner')

try:
    from rpy2.robjects import r, rinterface, conversion
    
    def get_r_command():
        return r
except:
    # This code has been copied in without much testing if you
    # need pyRserve, please text, fix and submit a patch.
    import pyRserve
    conn = None
    rServeHost = 'localhost'
    rServePort = 6311

    def get_r_command():
        global conn
        if conn and type(conn) is pyRserve.rconn.RConnector and not conn.isClosed:
            return conn.r
        conn = pyRserve.connect(host=rServeHost, port=6311)
        conn.r.__call__ = conn.eval
        return conn.r

R = None

def write_out(self, name):
    def _inner(msg):
        setattr(self, name, getattr(self, name, '') + msg)
    return _inner

def no_input(msg):
    raise IOError("R is asking for something on the command line. Intervention required!")

def r_set(name, value):
    robj = conversion.py2ri(value)
    rinterface.globalenv.__setitem__(name, robj)

def get_R(libs=LIB_PATH, mirror=CRAN_MIRROR):
    global R
    if R is None:
        R = get_r_command()

        R.out, R.err = ('', '')
        R.output = write_out(R, 'out')
        rinterface.set_writeconsole(R.output)
        rinterface.set_readconsole(no_input)
        R.set_value = r_set

        if not os.path.isdir(libs):
            os.makedirs(libs)

        # RPY2 can popup GUI menus, disable this.
        R('options(menu.graphics=FALSE)')

        # Install library destination (and location for imports)
        R('.libPaths( c( "%s", .libPaths()) )' % (libs.rstrip('/')+"/"))

        # Setup install source repository using RPY_CRAN_MIRROR
        R("""local({r <- getOption("repos");
           r["CRAN"] <- "%s"; 
           options(repos=r)})""" % mirror)
    return R

class Packages(list):
    def __iter__(self):
        if not len(self):
            self.generate()
        return super(Packages, self).__iter__()

    def generate(self):
        """Return a list of available packages"""
        r = get_R()
        packages = r('available.packages()[,"Package"]')
        versions = r('available.packages()[,"Version"]')
        for x, name in enumerate(packages):
            self.append( (name, "%s (%s)" % (name, versions[x])) )

    def installed(self):
        packages = r('installed.packages()[,1]')
        versions = r('installed.packages()[,3]')
        for x, name in enumerate(packages):
            yield (name, versions[x])

# Note: rpy2 provides package management code, but it provides
# very little benefit over doing it ourselves.
class Library(list):
    def append(self, lib):
        cmd = 'require(%s)' % lib
        if not list(get_R()(cmd))[0]:
            raise ImportError("Can't import required R module: '%s'" % lib)
        super(Library, self).append(cmd)

    def install(self, lib):
        """Attempts to install a library using R's"""
        r = get_R()
        r.out = ''
        r("install.packages(\"%s\")" % lib)
        # There is no way to know for sure if this worked, rpy2 has
        # a certain limit in what it will get back from R and this
        # Stops us known /for sure/ what's going on.
        return 'downloaded' in r.out.strip()


class ScriptRunner(list):
    """
    Run an R script with start-up and wrap-up sections.
    """
    DB_ENGINE_TO_R_DB = {
       'mysql': ('RMySQL', """
library("RMySQL")
%(DB)s <- dbConnect(MySQL(), user="%(USER)s", password="%(PASSWORD)s", dbname="%(NAME)s", host="%(HOST)s", port="%(PORT)s")
"""),
       'sqlite3': ('RSQLite', """
library(DBI)
%(DB)s <- dbConnect(RSQLite::SQLite(), "%(NAME)s", flags=SQLITE_RO)
"""),
       'postgresql_psycopg2': ('RPostgreSQL', """
library(RPostgreSQL)
%(DB)s <- dbConnect(dbDriver("PostgreSQL"), user="%(USER)s", password="%(PASSWORD)s", dbname="%(NAME)s", host="%(HOST)s", port="%(PORT)s")
""")}

    def __init__(self, script=None, libs=None):
        self.r = get_R()
        self.libs = libs or Library()
        self.close = [ ]
        self.script = [ script or '' ]
        self.filename = None

    def use_output(self, name, filename):
        if name == 'filename':
            self.filename = filename
        if not os.path.isdir(os.path.dirname(filename)):
            raise IOError("Directory for file doesn't exist: %s" % filename)
        if os.path.isfile(filename):
            raise IOError("Refusing to overwrite file: %s" % filename)
        self.append( "%s = \"%s\"" % (slugify(name), filename))

    def use_csvfile(self, name, filename):
        if not os.path.isfile(filename):
            raise IOError("Can't load csv file: %s" % filename)
        self.append( "%s = read.csv(\"%s\")" % (slugify(name), filename))

    def use_database(self, name):
        try:
            db = DATABASES[name]
        except KeyError:
            raise KeyError("Database '%s' not found." % name)

        engine = db['ENGINE'].split('.')[-1]
        r_db = self.DB_ENGINE_TO_R_DB.get(engine, None)
        if not r_db:
            raise KeyError("Database type '%s' not supported." % engine)

        # Add the required package
        self.libs.append(r_db[0])
        args = db.copy()
        args['DB'] = slugify(name)

        self.append( self.DB_ENGINE_TO_R_DB[engine][-1] % args )
        self.close.append( "dbDisconnect(%s)" % args['DB'] )

    def __str__(self):
        return "\n\n".join( self + self.libs + self.script + self.close )

    def run(self, script=None, **variables):
        if not self.filename:
            self.use_output('filename', tempfile.mktemp())

        if script:
            self.script = [ script ]

        for (name, value) in variables.items():
            self.r.set_value(name, value)

        self.r.out = ''
        ret = self.r(str(self))

        if not os.path.isfile(self.filename):
            self.filename = (glob(self.filename + '.*') + [self.filename])[0]

        return ret
