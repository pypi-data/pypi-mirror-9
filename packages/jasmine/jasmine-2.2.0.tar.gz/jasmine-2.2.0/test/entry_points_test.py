from six.moves import builtins

import os
import errno
import sys

from mockfs import replace_builtins, restore_builtins
from mock import MagicMock
import pytest

from yaml import load

from jasmine.entry_points import continuous_integration, _query, standalone, mkdir_p, install
from jasmine.ci import CIRunner
from jasmine.standalone import app as App


@pytest.fixture
def mockfs(request):
    mfs = replace_builtins()
    request.addfinalizer(lambda: restore_builtins())
    return mfs


@pytest.fixture
def mockfs_with_config(request):
    mfs = replace_builtins()
    mfs.add_entries({
        "/spec/javascripts/support/jasmine.yml": """
        src_dir: src
        spec_dir: spec
        """
    })
    request.addfinalizer(lambda: restore_builtins())
    return mfs


@pytest.fixture
def mock_CI_run(request):
    CIRunner.run = MagicMock(name='run')

def test_ci_config_check(mockfs, monkeypatch, mock_CI_run):
    monkeypatch.setattr(sys, 'argv', ['test.py'])

    continuous_integration()
    assert not CIRunner.run.called

def test_continuous_integration__set_browser(monkeypatch, mockfs_with_config, mock_CI_run):
    monkeypatch.setattr(sys, 'argv', ["test.py", "--browser", "firefox"])

    continuous_integration()

    CIRunner.run.assert_called_once_with(browser='firefox', logs=False)


def test_continuous_integration__show_logs(monkeypatch, mockfs_with_config, mock_CI_run):
    monkeypatch.setattr(sys, 'argv', ["test.py", "--logs"])

    continuous_integration()

    CIRunner.run.assert_called_once_with(logs=True, browser=None)


def test_continuous_integration__browser_default(monkeypatch, mockfs_with_config, mock_CI_run):
    monkeypatch.setattr(sys, 'argv', ["test.py"])

    continuous_integration()

    CIRunner.run.assert_called_once_with(browser=None, logs=False)


@pytest.fixture
def mock_App_run(request):
    App.run = MagicMock(name='run')


def test_standalone__set_host(monkeypatch, mock_App_run, mockfs_with_config):
    monkeypatch.setattr(sys, 'argv', ["test.py", "-o", "127.0.0.2"])
    App.run = MagicMock(name='run')

    standalone()

    App.run.assert_called_once_with(host="127.0.0.2", port=8888, debug=True)


def test_standalone__set_port(monkeypatch, mock_App_run, mockfs_with_config):
    monkeypatch.setattr(sys, 'argv', ["test.py", "-p", "1337"])

    standalone()

    App.run.assert_called_once_with(host="127.0.0.1", port=1337, debug=True)


def test_standalone__port_default(monkeypatch, mock_App_run, mockfs_with_config):
    monkeypatch.setattr(sys, 'argv', ["test.py"])

    standalone()

    App.run.assert_called_once_with(host="127.0.0.1", port=8888, debug=True)


def test_standalone__port_invalid(monkeypatch, mock_App_run, mockfs_with_config):
    monkeypatch.setattr(sys, 'argv', ["test.py", "-p", "pants"])

    with pytest.raises(SystemExit) as exception:
       standalone()

    assert "invalid int value: 'pants'"
    assert not App.run.called


def test_standalone__missing_config(monkeypatch, mock_App_run, mockfs):
    monkeypatch.setattr(sys, 'argv', ["test.py"])

    standalone()

    assert not App.run.called


def test__query__yes(capsys, monkeypatch):
    input_string(monkeypatch, "Y")

    choice = _query("Would you like to play a game?")

    out, err = capsys.readouterr()

    assert out == "Would you like to play a game? [Y/n] "
    assert True == choice


def test__query__no(capsys, monkeypatch):
    input_string(monkeypatch, "N")

    choice = _query("Would you like to hear some cat facts?")

    out, err = capsys.readouterr()

    assert out == "Would you like to hear some cat facts? [Y/n] "
    assert False == choice


def test__query__default(capsys, monkeypatch):
    input_string(monkeypatch, "")

    choice = _query("Would you like to blindly accept my defaults?")

    out, err = capsys.readouterr()

    assert out == "Would you like to blindly accept my defaults? [Y/n] "
    assert True == choice


def test__mkdir_p(mockfs):
    mkdir_p("/pants/a/b/c")

    assert os.path.isdir("/pants")
    assert os.path.isdir("/pants/a")
    assert os.path.isdir("/pants/a/b")
    assert os.path.isdir("/pants/a/b/c")


def test__mkdir_p(mockfs, monkeypatch):
    def raise_error(path):
        o = OSError()
        o.errno = errno.EEXIST
        raise o

    monkeypatch.setattr(os, 'makedirs', raise_error)
    mockfs.add_entries({
        '/pants/a/b/c': {}
    })

    mkdir_p("/pants/a/b/c")


def input_string(monkeypatch, string=""):
    try:
        monkeypatch.setattr(builtins, 'raw_input', lambda: string)
    except AttributeError:
        monkeypatch.setattr(builtins, 'input', lambda: string)


def test_install__yes(mockfs, monkeypatch):
    # Should create spec/javascripts/support
    # Should create a spec/javascripts/support/jasmine.yml
    spec_dir = "spec/javascripts/support"
    yaml_file = os.path.join(spec_dir, "jasmine.yml")

    input_string(monkeypatch, "Y")

    install()

    assert os.path.isdir(spec_dir)
    assert os.path.isfile(yaml_file)

    yaml = load(open(yaml_file))

    assert yaml['spec_files'] == ["**/*[Ss]pec.js"]


def test_install__yes__existing_yaml(mockfs, monkeypatch):
    # Should create spec/javascripts/support
    # Should NOT overwrite spec/javascripts/support/jasmine.yml
    spec_dir = "spec/javascripts/support"
    yaml_file = os.path.join(spec_dir, "jasmine.yml")

    mockfs.add_entries({
        '/spec/javascripts/support/jasmine.yml': """
        spec_files:
            - "**/pants.*"
        """
    })

    input_string(monkeypatch, "Y")

    install()

    assert os.path.isdir(spec_dir)
    assert os.path.isfile(yaml_file)

    yaml = load(open(yaml_file))

    assert yaml['spec_files'] == ["**/pants.*"]


def test_install__no(mockfs, monkeypatch):
    # Should NOT create spec/javascripts/support
    # Should NOT create a spec/javascripts/support/jasmine.yml
    spec_dir = "spec/javascripts/support"
    yaml_file = os.path.join(spec_dir, "jasmine.yml")

    input_string(monkeypatch, "N")

    install()

    assert not os.path.isdir(spec_dir)
    assert not os.path.isfile(yaml_file)
