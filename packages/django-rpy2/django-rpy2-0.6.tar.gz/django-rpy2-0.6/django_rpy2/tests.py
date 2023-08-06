import datetime
import tempfile
import shutil

from django.utils import timezone
from django.test import TestCase

from .core import *
from .models import *
from .settings import *

TEST_DOWNLOADS = False

class CoreTests(TestCase):
    def _pre_setup(self):
        if TEST_DOWNLOADS:
            self.libs = tempfile.mktemp('-test-libs')
        else:
            self.libs = '/tmp/rpy2-tests'
        self.r = get_R(libs=self.libs)

    def _post_teardown(self):
        if os.path.isdir(self.libs):
            shutil.rmtree(self.libs)

    def test_get_r(self):
        """Get R"""
        pass

    def test_directory(self):
        """Lib directory is added"""
        self.assertEqual(self.r('.libPaths()')[0], self.libs)

    def test_mirror(self):
        """CRAN mirror is set"""
        ret = str(self.r('getOption("repos")'))
        self.assertEqual(ret.strip().split()[-1].strip('"'), CRAN_MIRROR)

    def test_run(self):
        """Running a script"""
        ret = ScriptRunner("'1'").run()
        self.assertEqual(ret[0], '1')
        runner = ScriptRunner()
        self.assertEqual(runner.run("'2'")[0], '2')

    def test_require(self):
        """Import an R library"""
        runner = ScriptRunner('my - unrun - script')
        with self.assertRaises(ImportError):
            runner.libs.append('doesnotexist')
        self.assertNotIn('doesnotexist', str(runner))
        runner.libs.append('class')
        self.assertIn('require(class)\n', str(runner))

    def test_install(self):
        """Installing library"""
        libs = Library()
        if TEST_DOWNLOADS:
            self.assertFalse(libs.install('four-candles'))
            self.assertTrue(libs.install('ref'))

    def test_output(self):
        """Adding output filename"""
        runner = ScriptRunner('my - unrun - script')
        runner.use_output('fn_two', '/tmp/test')
        self.assertIn('/tmp/test', str(runner))

    def test_output_extension(self):
        """Getting output file with extension"""
        runner = ScriptRunner()
        runner.run("""
           x <- matrix(1:10, ncol = 5)
           write(x, paste(filename,'.txt',sep=""), sep="\t")
        """)
        self.assertTrue(os.path.isfile(runner.filename))
        with open(runner.filename, 'r') as fhl:
            self.assertEqual(fhl.read(), '1\t2\t3\t4\t5\n6\t7\t8\t9\t10\n')

        os.unlink(runner.filename)

    def test_csv_file(self):
        """Using CSV files"""
        filename = tempfile.mktemp('.csv')
        with open(filename, 'w') as fhl:
            fhl.write("""A,B,C\n1,2,3\n4,5,6\n""")
        runner = ScriptRunner()
        runner.use_csvfile('csv', filename)
        ret = runner.run("csv")
        self.assertEqual(ret[0][1], 4)
        os.unlink(filename)

    def test_varialbles(self):
        """Variables"""
        runner = ScriptRunner()
        ret = runner.run('foo', foo='bar\'"}]+=-')
        self.assertEqual(ret[0], 'bar\'"}]+=-')

    def test_database(self):
        runner = ScriptRunner()
        if TEST_DOWNLOADS:
            with self.assertRaises(ImportError):
                runner.use_database('default')
        else:
            try:
                runner.use_database('default')
            except ImportError:
                runner.libs.install('RSQLite')
                runner.use_database('default')
        self.assertIn('dbConnect', str(runner))
        ret = runner.run("dbListTables(default)")
        # TODO: In future we want to try and connect to the testcase test database
        # We can't do that here because django has made the database 'in-memory'
        # and when we connect, R created a new 'in-memory' database instead of seeing
        # django's in-memory database.
        #self.assertIn('auth_user', tables)

    

