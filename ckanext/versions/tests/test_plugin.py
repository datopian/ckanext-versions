"""Tests for plugin.py."""
import ckanext.versions.plugin as plugin


def test_plugin():
    """This is here just as a sanity test
    """
    p = plugin.VersionsPlugin()
    assert p
