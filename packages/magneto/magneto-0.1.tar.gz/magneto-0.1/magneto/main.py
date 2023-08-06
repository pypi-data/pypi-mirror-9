#!/usr/bin/env python
import argparse
import logging
import os
import pytest

from .logger import Logger
from .base import BaseTestCase
from .magneto import Magneto
from .utils import ADB, wait_for_device, unlock_device


class MagnetoPlugin(object):
    def pytest_addoption(self, parser):
        parser.addoption('--app-package')
        parser.addoption('--app-activity')
        parser.addoption('--apk-path', help='APK to install on device before tests')
        parser.addoption('--clean-install', default=False, action='store_true',
                         help='Uninstalls apk before installation. Requires --apk-path.')
        parser.addoption('--device-id', help='Device id to run tests on')
        parser.addoption('--save-data-on-failure', default=False, action='store_true',
                         help='Save hierarchy.xml/screenshot.png/logcat.log if a test fails')
        parser.addoption('--include-video-on-failure', default=False, action='store_true',
                         help='Wether to record video or not')
        parser.addoption('--magneto-failed-data-dir', default='/tmp/magneto_test_data', help='')
        parser.addoption('--wait-for-element-timeout', default=5000, type='int',
                         help='wait_for_element() default timeout')

    def pytest_configure(self, config):
        apk_path = config.getoption('--apk-path')
        app_package = config.getoption('--app-package')
        app_activity = config.getoption('--app-activity')
        device_id = config.getoption('--device-id')
        clean_install = config.getoption('--clean-install')

        Magneto.configure(device_id)

        wait_for_device()
        unlock_device()

        if apk_path:
            if not apk_path.startswith('/'):
                apk_path = os.path.abspath(os.path.join(os.getcwd(), apk_path))

            if clean_install:
                ADB.uninstall(app_package)
            ADB.install(apk_path, '-r')

        # launch app
        ADB.exec_cmd('shell am start {0}/{1}'.format(app_package, app_activity)).wait()

    def pytest_unconfigure(self, config):
        BaseTestCase.unconfigure(config)

    def pytest_runtest_makereport(self, item, call, __multicall__):
        """
        Skip remaining tests if current_test (item) is blocker and it has failed.
        """
        # get current report status from _pytest.runner.pytest_runtest_makereport
        report = __multicall__.execute()
        getattr(BaseTestCase, 'pytest_runtest_' + report.when)(item, report)
        return report


def main():
    parser = argparse.ArgumentParser(description='.')
    parser.add_argument('tests_path', type=str, help='ui test directory')
    parser.add_argument('--log', type=str, default='INFO', help='logging level. default:INFO')

    args, other = parser.parse_known_args()

    numeric_level = getattr(logging, args.log.upper(), None)
    Logger.setLevel(numeric_level)

    pytest.main(['-sv', args.tests_path] + other, plugins=[MagnetoPlugin()])


if __name__ == '__main__':
    main()
