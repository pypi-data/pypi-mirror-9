# -*- coding: utf-8 -*-
import os
import os.path
from unittest import main

from pypeline.markup import markup
from pypeline.tests import TestPairwise

class TestMarkup(TestPairwise):
    
    basedir = os.path.join(os.path.dirname(__file__), 'markups')
    
    """
    test_* methods are run like regular tests
    _test_* methods are run with the allpairs logic (e.g. once for each readme)
        and that is kicked off by test()
    """
    def __init__(self):
        super(TestMarkup, self).__init__()
        self.data = {}
        files = os.listdir(self.basedir)
        for f in files:
            format = os.path.splitext(f)[1].lstrip('.')
            if format == 'html':
                continue
            self.data[format] = f

    def setUp(self):
        pass

    def _test_rendering(self, format):
        readme = self.data[format]
        source_file = open(os.path.join(self.basedir, readme), 'r')
        source = source_file.read().decode('utf-8')
        expected_file = open(os.path.join(self.basedir, '%s.html' % readme),
                             'r')
        expected = expected_file.read().decode('utf-8')
        actual = markup.render(os.path.join(self.basedir, readme))
        #assert_true(isinstance(actual, unicode))
        if source != expected:
            self.assertTrue(source != actual, "Did not render anything.")
        self.assertEqual(expected, actual)

    def test_can_render(self):
        self.assertEqual('markdown', markup.can_render('README.markdown'))
        self.assertEqual('markdown', markup.can_render('README.md'))
        self.assertEqual(None, markup.can_render('README.cmd'))

    def test_unicode_utf8(self):
        chinese = markup.unicode(u'華語')
        self.assertEqual(chinese, u'華語')
        self.assertEqual(type(chinese), unicode)
    
    def test_unicode_ascii(self):
        ascii = markup.unicode('abc')
        self.assertEqual(ascii, u'abc')
        self.assertEqual(type(ascii), unicode)
        
    def test_unicode_latin1(self):
        latin1 = u'abcdé'.encode('latin_1')
        latin1 = markup.unicode(latin1)
        self.assertEqual(latin1, u'abcdé')
        self.assertEqual(type(latin1), unicode)

if __name__ == '__main__':
    main()