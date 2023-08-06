from os import symlink
from os.path import join, realpath
from functools import wraps
from textwrap import dedent
from pprint import PrettyPrinter
from operator import itemgetter

from mock import Mock
from git import Repo

from jig.tests.testcase import JigTestCase
from jig.diffconvert import describe_diff, DiffType, GitDiffIndex
from jig.tools import cwd_bounce


def assertDiff(func):
    """
    Decorator used to test diffs.

    Uses ``yield`` in the following way:

        @assertDiff
        def test_my_diff(self):
            yield 'one'

            yield 'two'

            yield [(1, '-', 'one'), (1, '+', 'two')]

    The order of the yields are:

        1. Original value (a)
        2. After it's edited (b)
        3. The expected difference
    """
    pp = PrettyPrinter().pformat

    @wraps(func)
    def wrapper(self, **kwargs):
        queue = func(self, **kwargs)

        a = queue.next()
        b = queue.next()
        expected = queue.next()

        a = dedent(a).strip()
        b = dedent(b).strip()

        actual = [i for i in describe_diff(a, b)]
        if not expected == actual:   # pragma: no cover
            self.fail('Diff does not match:\nexpected\n{}\nactual\n{}'.format(
                pp(expected),
                pp(actual)))

    return wrapper


class TestDescribeDiff(JigTestCase):

    """
    Test our diff description method.

    """
    @assertDiff
    def test_all_addition(self):
        """
        All lines are being added.
        """
        yield ''

        yield '''
            one
            two
            three'''

        yield [
            (1, '+', 'one'),
            (2, '+', 'two'),
            (3, '+', 'three')]

    @assertDiff
    def test_add_blank_lines(self):
        """
        Lines added are just blank lines.
        """
        yield '''
            one
            two
            three'''

        yield '''
            one


            two
            three'''

        # This is a bit counter-intuitive, but correct
        yield [
            (1, ' ', 'one'),
            (2, '+', ''),
            (3, '+', ''),
            (4, ' ', 'two'),
            (5, ' ', 'three')]

    @assertDiff
    def test_all_same(self):
        """
        No changes.
        """
        yield '''
            one
            two
            three'''

        yield '''
            one
            two
            three'''

        yield [
            (1, ' ', 'one'),
            (2, ' ', 'two'),
            (3, ' ', 'three')]

    @assertDiff
    def test_one_insert(self):
        """
        Just one line inserted.
        """
        yield '''
            one
            two
            three'''

        yield '''
            one
            two
            2.5
            three'''

        yield [
            (1, ' ', 'one'),
            (2, ' ', 'two'),
            (3, '+', '2.5'),
            (4, ' ', 'three')]

    @assertDiff
    def test_one_delete(self):
        """
        Just one deleted.
        """
        yield '''
            one
            two
            three
            four'''

        yield '''
            one
            two
            four'''

        yield [
            (1, ' ', 'one'),
            (2, ' ', 'two'),
            (3, '-', 'three'),
            (3, ' ', 'four')]

    @assertDiff
    def test_one_insert_delete(self):
        """
        One insert, one delete.
        """
        yield '''
            one
            two
            three
            four'''

        yield '''
            one
            two
            3
            four'''

        yield [
            (1, ' ', 'one'),
            (2, ' ', 'two'),
            (3, '-', 'three'),
            (3, '+', '3'),
            (4, ' ', 'four')]

    @assertDiff
    def test_one_character_change(self):
        """
        A single character changed.
        """
        yield '''
            one
            two
            three
            four'''

        yield '''
            one
            two
            thr3e
            four'''

        yield [
            (1, ' ', 'one'),
            (2, ' ', 'two'),
            (3, '-', 'three'),
            (3, '+', 'thr3e'),
            (4, ' ', 'four')]

    @assertDiff
    def test_complex_01(self):
        """
        Complex example with several changes.
        """
        yield '''
            one
            two
            three
            three-and-a-smidge
            four'''

        yield '''
            one
            1.5
            two
            three

            four'''

        yield [
            (1, ' ', 'one'),
            (2, '+', '1.5'),
            (3, ' ', 'two'),
            (4, ' ', 'three'),
            (4, '-', 'three-and-a-smidge'),
            (5, '+', ''),
            (6, ' ', 'four')]


class TestDiffType(JigTestCase):

    """
    Detect diff type from :py:class:`Git.Diff` objects.

    """
    def test_add(self):
        """
        Add type.
        """
        diff = Mock()
        diff.new_file = True

        self.assertEqual(DiffType.A, DiffType.for_diff(diff))

    def test_deleted(self):
        """
        Deleted type.
        """
        diff = Mock()
        diff.new_file = False
        diff.deleted_file = True

        self.assertEqual(DiffType.D, DiffType.for_diff(diff))

    def test_renamed(self):
        """
        Renamed type.
        """
        diff = Mock()
        diff.new_file = False
        diff.deleted_file = False
        diff.renamed = True

        self.assertEqual(DiffType.R, DiffType.for_diff(diff))

    def test_modified(self):
        """
        Modified type.
        """
        diff = Mock()
        diff.new_file = False
        diff.deleted_file = False
        diff.renamed = False
        diff.a_blob = 'blob a'
        diff.b_blob = 'blob b'

        self.assertEqual(DiffType.M, DiffType.for_diff(diff))

    def test_unknown(self):
        """
        Unknown type.
        """
        diff = Mock()
        diff.new_file = False
        diff.deleted_file = False
        diff.renamed = False
        diff.a_blob = False
        diff.b_blob = False

        self.assertEqual(DiffType.U, DiffType.for_diff(diff))


class TestGitDiffIndex(JigTestCase):

    """
    Test converting Git changes to JSON.

    """
    def setUp(self):
        super(TestGitDiffIndex, self).setUp()

        repo, working_dir, diffs = self.repo_from_fixture('repo01')

        self.testrepo = repo
        self.testrepodir = working_dir
        self.testdiffs = diffs

    def test_new_file(self):
        """
        Handles new files.
        """
        gdi = self.git_diff_index(self.testrepo, self.testdiffs[0])

        self.assertEqual(1, len(list(gdi.files())))

        file1 = gdi.files().next()

        # This one is relative to the Git repo
        self.assertEqual('argument.txt', file1['name'])
        # It should be added because this is a new file
        self.assertEqual('added', file1['type'])
        # This one is the full path to the file
        self.assertEqual(
            realpath(join(self.testrepodir, 'argument.txt')),
            realpath(file1['filename']))

    def test_modified(self):
        """
        Handles modified files.
        """
        gdi = self.git_diff_index(self.testrepo, self.testdiffs[1])

        self.assertEqual(1, len(list(gdi.files())))

        file1 = gdi.files().next()
        diff = [i for i in file1['diff']]
        difftypes = set([i[1] for i in diff])

        # File was changed
        self.assertEqual('modified', file1['type'])

        # We should have every kind of modification
        # Same lines, additions, and subtractions
        self.assertEqual(
            set([' ', '+', '-']),
            difftypes)

        # And we have a list of differences as expected
        self.assertEqual(47, len(diff))

    def test_deleted_file(self):
        """
        Handles deleted files.
        """
        gdi = self.git_diff_index(self.testrepo, self.testdiffs[2])

        self.assertEqual(1, len(list(gdi.files())))

        file1 = gdi.files().next()
        diff = [i for i in file1['diff']]
        difftypes = set([i[1] for i in diff])

        # File was deleted
        self.assertEqual('deleted', file1['type'])

        # Each line should be a removal
        self.assertEqual(
            set(['-']),
            difftypes)

        self.assertEqual(35, len(diff))

    def test_multiple_changes(self):
        """
        Handles multiple files changed.
        """
        gdi = self.git_diff_index(self.testrepo, self.testdiffs[3])

        self.assertEqual(2, len(list(gdi.files())))

        files = sorted(
            [i for i in gdi.files()],
            key=itemgetter('name'))

        self.assertEqual(
            'famous-deaths.txt',
            files[0]['name'])

        self.assertEqual(
            'italian-lesson.txt',
            files[1]['name'])

    def test_name_contains_subdirectories(self):
        """
        If sub-directories are involved, those are included properly.
        """
        gdi = self.git_diff_index(self.testrepo, self.testdiffs[4])

        # Since we've moved the file Git will see this as a deletion of 2 files
        # plus the addition of 2 files, so it makes our count 4.
        self.assertEqual(4, len(list(gdi.files())))

        files = sorted(
            [i for i in gdi.files()],
            key=itemgetter('name'))

        # Make sure that the name contains our sub-directory.
        self.assertEqual(
            'scripts/famous-deaths.txt',
            files[2]['name'])

        self.assertEqual(
            'scripts/italian-lesson.txt',
            files[3]['name'])

    def test_binary_diff(self):
        """
        Binary files are ignored.
        """
        gdi = self.git_diff_index(self.testrepo, self.testdiffs[5])

        # We should see our file
        self.assertEqual(1, len(list(gdi.files())))

        # But we don't include the diff since it's binary data
        self.assertEqual([], gdi.files().next()['diff'])

    def test_ignores_jig_directory(self):
        """
        Does not include anything in the .jig directory.
        """
        gdi = self.git_diff_index(self.testrepo, self.testdiffs[6])

        # We should see our file
        self.assertEqual(0, len(list(gdi.files())))

    def test_symlinks(self):
        """
        Symlinks are ignored because they are not real files.
        """
        self.commit(self.gitrepodir, 'text/a.txt', 'a')
        self.commit(self.gitrepodir, 'text/b.txt', 'b')
        self.commit(self.gitrepodir, 'text/c.txt', 'c')

        # Create the symlink that should be ignored by GitDiffIndex
        with cwd_bounce(self.gitrepodir):
            symlink('text', 'also_text')

        # We have to do this without our testcase since it's a special
        # situation.
        repo = Repo(self.gitrepodir)
        repo.git.add('also_text')

        # The symlink is staged, time to convert the diff
        gdi = GitDiffIndex(self.gitrepodir, repo.head.commit.diff())

        # If we ignored the symlink, which we should, there should be no files
        self.assertEqual(0, len(list(gdi.files())))
