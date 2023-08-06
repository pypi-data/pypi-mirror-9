# -*- coding: utf-8 -*-

import logging

from noseapp.suite.mediator import TestCaseMediator


logger = logging.getLogger(__name__)


class Suite(object):
    """
    Base Suite class for group or one TestCase.

    Usage DEFAULT_REQUIRE property for default extensions require.
    """

    mediator_class = TestCaseMediator

    def __init__(self, name, require=None):
        """
        :param name: suite name
        :type name: str
        :param require: extension names list
        :type require: list
        """
        self._name = name

        if hasattr(self, 'DEFAULT_REQUIRE'):
            _require = self.DEFAULT_REQUIRE + (require or [])
        else:
            _require = require

        self._mediator = self.mediator_class(require=_require)

    @property
    def name(self):
        return self._name

    @property
    def require(self):
        """
        List names of extensions require
        """
        return self._mediator.require

    @property
    def handlers(self):
        """
        Handlers list
        """
        return self._mediator.handlers

    def add_handler(self, f):
        """
        Set run test handler
        """
        return self._mediator.add_handler(f)

    def register(self, cls):
        """
        Add test case class

        :type cls: noseapp.case.TestCase
        """
        logger.debug('Registering test case "{}" in {} '.format(cls.__name__, repr(self)))

        self._mediator.add_test_case(cls)
        return cls

    def get_map(self):
        """
        Get map of test classes

        :return: dict
        """
        return self._mediator.create_map()

    def init_extensions(self):
        """
        Init extensions for test cases. Without building suite.
        """
        for case in self._mediator.test_cases:
            case.with_require(self.require)

    def __call__(self, nose_config, test_loader, class_factory):
        """
        Build suite
        """
        return self._mediator.create_suite(
            nose_config, test_loader, class_factory,
        )

    def __repr__(self):
        return '<Suite {}>'.format(self._name)
