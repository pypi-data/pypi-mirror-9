# -*- coding: utf-8 -*-

from unittest import TestCase

from nose.suite import ContextSuite

from noseapp.suite import Suite
from noseapp.core import TestProgram
from noseapp.core import CollectSuite
from noseapp import NoseApp as _NoseApp
from noseapp.suite import TestCaseMediator
from noseapp import TestCase as NoseAppTestCase
from noseapp.plugins.configure import AppConfigurePlugin


class NoseApp(_NoseApp):

    def initialize(self):
        pass


class FakeTestCase(NoseAppTestCase):

    def test(self):
        pass


class TestSuiteClass(TestCase):
    """
    Test case for noseapp.suite.base.Suite
    """

    def test_default_mediator_class(self):
        self.assertEqual(Suite.mediator_class, TestCaseMediator)

    def test_set_require(self):
        require = ['one', 'two']
        suite = Suite(__name__, require=require)

        self.assertEqual(suite.require, require)

    def test_default_require(self):

        class TestSuite(Suite):

            DEFAULT_REQUIRE = ['one']

        suite = TestSuite(__name__, require=['two'])

        self.assertEqual(suite.require, ['one', 'two'])

    def test_set_name(self):
        suite = Suite(__name__)

        self.assertEqual(suite.name, __name__)

    def test_register_test_case(self):
        suite = Suite(__name__)
        suite.register(NoseAppTestCase)

        self.assertEqual(len(suite.get_map()), 1)

    def test_build_suite(self):
        from nose.case import Test
        import noseapp.suite.mediator
        from noseapp.suite.bases.simple import BaseSuite

        mock_get_suite_class = lambda o: BaseSuite
        noseapp.suite.mediator.get_suite_class = mock_get_suite_class

        suite = Suite(__name__)
        suite.register(FakeTestCase)

        program = TestProgram(NoseApp(), ['test'])
        test = suite(program.config, program.testLoader)

        self.assertIsInstance(test, BaseSuite)

        test = [t for t in test]

        self.assertEqual(len(test), 1)
        self.assertIsInstance(test[0], Test)


class TestMediatorClass(TestCase):
    """
    Test case for noseapp.suite.mediator.TestCaseMediator
    """

    def test_set_require(self):
        require = ['one', 'two']
        instance = TestCaseMediator(require)

        self.assertEqual(instance._require, require)
        self.assertEqual(instance._test_cases, [])

    def test_add_test_case(self):
        mediator = TestCaseMediator(None)
        mediator.add_test_case(NoseAppTestCase)

        self.assertIn(NoseAppTestCase, mediator.test_cases)

    def test_create_map(self):
        mediator = TestCaseMediator(None)
        mediator.add_test_case(FakeTestCase)

        mp = mediator.create_map()

        self.assertIn('FakeTestCase', mp)
        self.assertEqual(mp['FakeTestCase']['cls'], FakeTestCase)
        self.assertIn('test', mp['FakeTestCase']['tests'])
        self.assertEqual(mp['FakeTestCase']['tests']['test'], FakeTestCase.test)


class TestCollectorClass(TestCase):
    """
    Test noseapp.suite.collector.CollectSuites class
    TODO: unification algorithm
    """

    def test_collect_suites(self):
        argv = ['test', '--with-app-configure']

        program = TestProgram(
            NoseApp(),
            argv,
            plugins=[AppConfigurePlugin()],
        )
        suites = [Suite(__name__) for _ in xrange(10)]

        for suite in suites:
            suite.register(NoseAppTestCase)

        collector = CollectSuite(
            argv,
            suites,
            program.testLoader,
            program.config,
        )
        result = collector.make_result()

        self.assertIsInstance(result, ContextSuite)

        result = [s for s in result]

        self.assertEqual(len(result), 10)

        for suite in result:
            self.assertIsInstance(suite, ContextSuite)

    def test_collect_one_suite(self):
        expect_suite_name = 'test.test_suite_name'
        expect_suite = Suite(expect_suite_name)
        argv = ['test', expect_suite_name, '--with-app-configure']

        suites = [Suite(__name__) for _ in xrange(9)] + [expect_suite]

        program = TestProgram(
            NoseApp(),
            argv,
            plugins=[AppConfigurePlugin()],
        )

        collector = CollectSuite(
            argv,
            suites,
            program.testLoader,
            program.config,
        )
        result = collector.make_result()

        self.assertIsInstance(result, ContextSuite)

        result = [s for s in result]

        self.assertEqual(len(result), 1)

        for suite in result:
            self.assertIsInstance(suite, ContextSuite)

    def test_collect_one_case(self):
        expect_case_name = FakeTestCase.__name__
        expect_suite_name = 'test_suite_name'

        argv = [
            'test',
            '{}:{}'.format(expect_suite_name, expect_case_name),
            '--with-app-configure'
        ]

        expect_suite = Suite(expect_suite_name)
        expect_suite.register(FakeTestCase)
        expect_suite.register(NoseAppTestCase)

        suites = [Suite(__name__) for _ in xrange(9)] + [expect_suite]

        program = TestProgram(
            NoseApp(),
            argv,
            plugins=[AppConfigurePlugin()],
        )

        collector = CollectSuite(
            argv,
            suites,
            program.testLoader,
            program.config,
        )
        result = collector.make_result()

        self.assertIsInstance(result, ContextSuite)

        result = [s for s in result]

        self.assertEqual(len(result), 1)

        for suite in result:
            self.assertIsInstance(suite, ContextSuite)

            for test in suite:
                self.assertIsInstance(test.test, FakeTestCase)

    def test_collect_one_case_method(self):

        class NewFakeTestCase(FakeTestCase):

            def test_(self):
                pass

        expect_case_name = NewFakeTestCase.__name__
        expect_suite_name = 'test_suite_name.test'

        argv = [
            'test',
            '{}:{}'.format(expect_suite_name, expect_case_name),
            '--with-app-configure'
        ]

        expect_suite = Suite(expect_suite_name)
        expect_suite.register(NewFakeTestCase)
        expect_suite.register(NoseAppTestCase)

        suites = [Suite(__name__) for _ in xrange(9)] + [expect_suite]

        program = TestProgram(
            NoseApp(),
            argv,
            plugins=[AppConfigurePlugin()],
        )

        collector = CollectSuite(
            argv,
            suites,
            program.testLoader,
            program.config,
        )
        result = collector.make_result()

        self.assertIsInstance(result, ContextSuite)

        result = [s for s in result]

        self.assertEqual(len(result), 1)

        for suite in result:
            self.assertIsInstance(suite, ContextSuite)

            for test in suite:
                self.assertIsInstance(test.test, FakeTestCase)
