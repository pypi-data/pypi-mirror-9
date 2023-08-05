import unittest

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
from Products.CMFCore.utils import getToolByName

ptc.setupPloneSite()

import c2.splitter.twocharacters

class TestCase(ptc.PloneTestCase):
    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            zcml.load_config('configure.zcml',
                             c2.splitter.twocharacters)
            fiveconfigure.debug_mode = False

        @classmethod
        def tearDown(cls):
            pass


class TestCanUseSpritter(TestCase):
    """Can Replace the catalog """
    def afterSetUp(self):
        pass

    def testWordSplitter(self):
        from Products.ZCTextIndex.PipelineFactory import element_factory
        group = 'Word Splitter'
        names = element_factory.getFactoryNames(group)
        self.failUnless('C2TwoCharaSplitter' in names)

        group = 'Case Normalizer'
        names = element_factory.getFactoryNames(group)
        self.failUnless('C2TwoChara Case Normalizer' in names)


    def testNounSearchableText(self):
        cat = getToolByName(self.portal, 'portal_catalog')
        # Create index
        from Products.ZCTextIndex.OkapiIndex import OkapiIndex
        from Products.ZCTextIndex.ZCTextIndex import PLexicon
        from Products.ZCTextIndex.ZCTextIndex import ZCTextIndex
        lexicon = PLexicon('c2chara_lexicon', '', c2.splitter.twocharacters.twochara.C2TwoCharaNormalizer())
        cat._setObject('c2chara_lexicon', lexicon)
        i = ZCTextIndex('NounSearchableText', caller=cat,
                index_factory=OkapiIndex,
                lexicon_id=lexicon.id)
        cat.addIndex('NounSearchableText', i)

        self.failUnless('NounSearchableText' in cat.indexes())
        self.failUnless('c2chara_lexicon' in
                        [ix.getLexicon().id for ix in cat.index_objects()
                         if ix.id == 'NounSearchableText'])

class TestTwoCharaFunctions(unittest.TestCase):
    """Test for Functions"""
    def afterSetUp(self):
        pass

    def test_process_str(self):
        process_str = c2.splitter.twocharacters.twochara.process_str
        txt = "This is a Plone symposium Tokyo site."
        result = ["Th", "hi" , "is", "s", "is", "s", "a", "Pl", "lo", "on"]
        self.assertEqual(process_str(txt, 'utf-8')[:10], result)


def test_suite():
    return unittest.TestSuite([

        unittest.makeSuite(TestCanUseSpritter),
        unittest.makeSuite(TestTwoCharaFunctions),

        # Unit tests
        #doctestunit.DocFileSuite(
        #    'README.txt', package='c2.splitter.twocharacters',
        #    setUp=testing.setUp, tearDown=testing.tearDown),

        #doctestunit.DocTestSuite(
        #    module='c2.splitter.twocharacters.mymodule',
        #    setUp=testing.setUp, tearDown=testing.tearDown),


        # Integration tests that use PloneTestCase
        #ztc.ZopeDocFileSuite(
        #    'README.txt', package='c2.splitter.twocharacters',
        #    test_class=TestCase),

        #ztc.FunctionalDocFileSuite(
        #    'browser.txt', package='c2.splitter.twocharacters',
        #    test_class=TestCase),

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
