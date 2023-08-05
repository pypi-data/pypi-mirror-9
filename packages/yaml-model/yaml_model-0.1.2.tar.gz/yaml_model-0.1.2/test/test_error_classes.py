"""
Test the Exception classes work as expected for things like string coersion,
operator overloading, etc
"""
import pytest

from yaml_model import NoValueError, ValidationError


class TestValidationError(object):
    """
    Test the ValidationError class
    """
    @pytest.mark.parametrize('messages,expected', [
        ('just 1 message', 'just 1 message'),
        (('now more', 'messages', 'tuple'), 'now more\nmessages\ntuple'),
        (['now other', 'messages', 'list'], 'now other\nmessages\nlist'),
    ])
    def test_to_string(self, messages, expected):
        """
        Test string coersion
        """
        ex = ValidationError(messages)
        assert str(ex) == expected


class TestNoValueError(object):
    """
    Test the NoValueError class
    """
    @pytest.mark.parametrize('var_name', [
        'some_var', 'other_var', 'Σ'
    ])
    def test_to_string(self, var_name):
        """
        Test string coersion
        """
        ex = NoValueError(None, var_name)
        assert var_name in str(ex)
