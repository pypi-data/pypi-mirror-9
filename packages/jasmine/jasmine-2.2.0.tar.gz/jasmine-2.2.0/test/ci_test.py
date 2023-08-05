import datetime
import time
import sys
try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO

from mock import MagicMock, Mock
import pytest

from jasmine.ci import CIRunner, TestServerThread

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict


def test_possible_ports():
    ports = TestServerThread().possible_ports("localhost:80,8000-8002")
    assert ports == [80, 8000, 8001, 8002]

@pytest.fixture
def sysexit(monkeypatch):
    mock_exit = MagicMock()
    monkeypatch.setattr(sys, 'exit', mock_exit)
    return mock_exit

@pytest.fixture
def test_server(monkeypatch):
    import jasmine.ci
    server = MagicMock()
    server.port = 80
    monkeypatch.setattr(jasmine.ci, 'TestServerThread', server)
    return server

@pytest.fixture
def firefox_driver(monkeypatch):
    import selenium.webdriver.firefox.webdriver
    driver = MagicMock()
    driver_class = lambda: driver
    monkeypatch.setattr(selenium.webdriver.firefox.webdriver, 'WebDriver', driver_class)
    return driver

@pytest.fixture
def suites():
    return [
        {
            "id": 0,
            "name": "datepicker",
            "type": "suite",
            "children": [
                {
                    "id": 0,
                    "name": "calls the datepicker constructor",
                    "type": "spec",
                    "children": []
                },
                {
                    "id": 1,
                    "name": "icon triggers the datepicker",
                    "type": "spec",
                    "children": []
                }
            ]
        }
    ]


@pytest.fixture
def results():
    return [
        {
            "id": "spec0",
            "description": "",
            "fullName": "",
            "status": "failed",
            'failedExpectations': [
                {
                    "matcherName": "toHaveBeenCalledWith",
                    "expected": {
                        "format": "yyy-mm-dd"
                    },
                    "actual": {},
                    "message": "Expected spy datepicker to have been called with [ { format : 'yyy-mm-dd' } ] but actual calls were [ { format : 'yyyy-mm-dd' } ]",
                    "stack": "Totally the one you want",
                    "passed": False
                }

            ]
        },
        {
            "id": "spec1",
            "description": "",
            "fullName": "",
            "status": "passed",
            "failedExpectations": []
        }
    ]

@pytest.fixture
def suite_results():
    return [
            {
                "id": "suite0",
                "status": "failed",
                "failedExpectations": [
                    { "message": "something went wrong"}
                 ]
            },
            {
                "id": "suite1",
                "status": "finished"
            }
           ]

def test_run_exits_with_zero_on_success(suites, results, capsys, sysexit, firefox_driver, test_server):
    results[0] = results[1]
    del results[1]

    def execute_script(js):
        if 'jsApiReporter.finished' in js:
            return True
        if 'jsApiReporter.specResults' in js:
            return results
        if 'jsApiReporter.suiteResults' in js:
            return []
        return None

    def get_log(type):
        return [dict(timestamp=0, level='INFO', message='hello')]

    firefox_driver.execute_script = execute_script
    firefox_driver.get_log = get_log

    CIRunner().run(logs=True)
    stdout, _stderr = capsys.readouterr()

    assert not sysexit.called
    stdout, _stderr = capsys.readouterr()

    dt = datetime.datetime.fromtimestamp(0)
    assert '[{0} - INFO] hello\n'.format(dt) not in stdout


def test_run_exits_with_nonzero_on_failure(suites, results, capsys, sysexit, firefox_driver, test_server):
    def execute_script(js):
        if 'jsApiReporter.finished' in js:
            return True
        if 'jsApiReporter.specResults' in js:
            return results
        if 'jsApiReporter.suiteResults' in js:
            return []
        return None

    timestamp = time.time() * 1000

    def get_log(type):
        assert type == 'browser'
        return [
            dict(timestamp=timestamp, level='INFO', message='hello'),
            dict(timestamp=timestamp + 1, level='WARNING', message='world'),
        ]

    firefox_driver.execute_script = execute_script
    firefox_driver.get_log = get_log

    CIRunner().run()

    sysexit.assert_called_with(1)
    stdout, _stderr = capsys.readouterr()

    assert "Browser Session Logs" not in stdout
    assert "hello" not in stdout
    assert "world" not in stdout


def test_run_with_browser_logs(suites, results, capsys, sysexit, firefox_driver, test_server):
    def execute_script(js):
        if 'jsApiReporter.finished' in js:
            return True
        if 'jsApiReporter.specResults' in js:
            return results
        if 'jsApiReporter.suiteResults' in js:
            return []
        return None

    timestamp = time.time() * 1000

    def get_log(type):
        assert type == 'browser'
        return [
            dict(timestamp=timestamp, level='INFO', message='hello'),
            dict(timestamp=timestamp + 1, level='WARNING', message='world'),
        ]

    firefox_driver.execute_script = execute_script
    firefox_driver.get_log = get_log

    CIRunner().run(logs=True)

    stdout, _stderr = capsys.readouterr()

    dt = datetime.datetime.fromtimestamp(timestamp / 1000.0)
    assert '[{0} - INFO] hello\n'.format(dt) in stdout

    dt = datetime.datetime.fromtimestamp((timestamp + 1) / 1000.0)
    assert '[{0} - WARNING] world\n'.format(dt) in stdout


def test_displays_afterall_errors(suite_results, suites, results, capsys, sysexit, firefox_driver, test_server):
    results[0] = results[1]
    del results[1]

    def execute_script(js):
        if 'jsApiReporter.finished' in js:
            return True
        if 'jsApiReporter.specResults' in js:
            return results
        if 'jsApiReporter.suiteResults' in js:
            return suite_results
        return None

    firefox_driver.execute_script = execute_script

    CIRunner().run()
    stdout, _stderr = capsys.readouterr()

    assert 'After All something went wrong' in stdout
    sysexit.assert_called_with(1)

