import os
import glob

import mockfs
import pkg_resources
import pytest


@pytest.fixture
def fs(request):
    mfs = mockfs.replace_builtins()

    os.path.lexists = mfs.exists
    glob.iglob = mfs.glob

    mfs.add_entries({
        "jasmine.yml": """
            src_files:
              - src/player.js
              - src/**/*.js
              - http://cdn.jquery.com/jquery.js
              - vendor/test.js
              - vendor/**/*.{js,coffee}
            """,
        "/spec/javascripts/helpers/spec_helper.js": '',
        "/lib/jams/jam_spec.js": '',
        "/src/player.js": '',
        "/src/mixer/mixer.js": '',
        "/src/tuner/fm/fm_tuner.js": '',
        "/spec/javascripts/player_spec.js": '',
        "/spec/javascripts/mixer/mixer_spec.js": '',
        "/spec/javascripts/tuner/fm/fm_tuner_spec.js": '',
        "/spec/javascripts/tuner/am/AMSpec.js": '',
        "/vendor/test.js": '',
        "/vendor/pants.coffee": '',
        "/vendor_spec/pantsSpec.js": '',
        "/main.css": '',
    })

    request.addfinalizer(lambda: mockfs.restore_builtins())

    return mfs


@pytest.fixture
@pytest.mark.usefixtures("fs")
def config():
    from jasmine.config import Config

    return Config("jasmine.yml", project_path="/")


@pytest.mark.usefixtures("fs")
def test_src_files(config):
    src_files = config.src_files()

    assert src_files[0] == "src/player.js"
    assert src_files.index("vendor/test.js") < src_files.index("vendor/pants.coffee")

    assert 'http://cdn.jquery.com/jquery.js' in src_files
    assert 'src/mixer/mixer.js' in src_files
    assert 'src/tuner/fm/fm_tuner.js' in src_files
    assert 'vendor/pants.coffee' in src_files


@pytest.mark.usefixtures("fs")
def test_stylesheets_default(config):
    assert config.stylesheets() == []


@pytest.mark.usefixtures("fs")
def test_helpers_default(config):
    assert config.helpers() == ['helpers/spec_helper.js']


@pytest.mark.usefixtures("fs")
def test_spec_files_default(config):
    # sort because all of the specified paths are globs, order does not matter
    assert sorted(config.spec_files()) == [
        'mixer/mixer_spec.js',
        'player_spec.js',
        'tuner/am/AMSpec.js',
        'tuner/fm/fm_tuner_spec.js',
    ]


@pytest.mark.usefixtures("fs")
def test_src_dir_spec_dir(config):
    config.yaml['src_dir'] = 'src'
    config.yaml['spec_dir'] = 'spec'
    config.yaml['src_files'] = ['**/*.js', 'player.js', 'vendor/test.js', 'vendor/**/*.{js,coffee}']

    src_files = config.src_files()

    assert 'player.js' in src_files
    assert 'mixer/mixer.js' in src_files
    assert 'tuner/fm/fm_tuner.js' in src_files

    # noinspection PySetFunctionToLiteral
    assert set(config.spec_files()) == set([
        "javascripts/player_spec.js",
        "javascripts/mixer/mixer_spec.js",
        "javascripts/tuner/am/AMSpec.js",
        "javascripts/tuner/fm/fm_tuner_spec.js",
    ])

@pytest.mark.usefixtures("fs")
def test_script_urls(config, monkeypatch):
    monkeypatch.setattr(pkg_resources, 'resource_listdir',
                        lambda package, directory: ['json2.js', 'jasmine.js', 'boot.js', 'node_boot.js', 'jasmine-html.js', 'jasmine.css'])

    script_urls = config.script_urls()

    assert script_urls[:5] == [
        "__jasmine__/jasmine.js",
        "__jasmine__/jasmine-html.js",
        "__jasmine__/json2.js",
        "__jasmine__/boot.js",
        "__src__/src/player.js"
    ]
    
    assert 'http://cdn.jquery.com/jquery.js' in script_urls
    assert '__src__/src/mixer/mixer.js' in script_urls
    assert '__src__/src/tuner/fm/fm_tuner.js' in script_urls
    assert '__src__/vendor/pants.coffee' in script_urls


def test_stylesheet_urls(fs, config, monkeypatch):
    monkeypatch.setattr(pkg_resources, 'resource_listdir',
                        lambda package, directory: ['json2.js', 'jasmine.js', 'jasmine-html.js', 'boot.js', 'node_boot.js', 'jasmine.css'])

    config.yaml['stylesheets'] = ['**/*.css']

    fs.add_entries({
        'main.css': """ body { color: blue; } """
    })

    stylesheet_urls = config.stylesheet_urls()

    assert stylesheet_urls == [
        "__jasmine__/jasmine.css",
        "__src__/main.css"
    ]


def test_reload(fs, config):
    fs.add_entries({
        "jasmine.yml": """
            src_files:
              - pants
            """
     })

    config.reload()

    assert config.yaml['src_files'] == ['pants']
