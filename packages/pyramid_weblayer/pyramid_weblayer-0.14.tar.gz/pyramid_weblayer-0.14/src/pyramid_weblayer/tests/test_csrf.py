#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Unit tests for `pyramid_weblayer.csrf`."""

import unittest

try: # pragma: no cover
    from mock import Mock
except: # pragma: no cover
    pass

class TestCSRFValidator(unittest.TestCase):
    """Test the logic of py:class:`~pyramid_weblayer.csrf.CSRFValidator`."""
    
    def makeOne(self, session_token, **kwargs):
        from ..csrf import CSRFValidator
        return CSRFValidator(session_token, **kwargs)
    
    def test_validates_with_correct_request_param(self):
        """Requests validate OK when they have the correct ``_csrf``."""
        
        from ..csrf import CSRFError
        
        mock_request = Mock()
        mock_request.method = 'a'
        mock_request.params = {'_csrf': 'token'}
        
        validator = self.makeOne('token', target_methods=['a'])
        retval = validator.validate(mock_request)
        self.assertTrue(retval is None)
    
    def test_raises_csrf_error_with_no_request_param(self):
        """Requests must have ``_csrf``."""
        
        from ..csrf import CSRFError
        
        mock_request = Mock()
        mock_request.method = 'a'
        mock_request.params = {}
        
        validator = self.makeOne('token', target_methods=['a'])
        self.assertRaises(
            CSRFError,
            validator.validate,
            mock_request
        )
    
    def test_raises_csrf_error_with_wrong_request_param(self):
        """Requests must have the right ``_csrf``."""
        
        from ..csrf import CSRFError
        
        mock_request = Mock()
        mock_request.method = 'a'
        mock_request.params = {'_csrf': 'wrong'}
        
        validator = self.makeOne('token', target_methods=['a'])
        self.assertRaises(
            CSRFError,
            validator.validate,
            mock_request
        )
    
    def test_method_must_have_side_effects(self):
        """Method must have side effects."""
        
        from ..csrf import CSRFError
        
        mock_request = Mock()
        mock_request.method = 'b'
        
        validator = self.makeOne('token', target_methods=['a'])
        retval = validator.validate(mock_request)
        
        self.assertTrue(retval is None)
        self.assertRaises(
            AssertionError,
            mock_request.headers.get.assert_called_with,
            'X-Requested-With'
        )
        
        mock_request = Mock()
        mock_request.method = 'a'
        self.assertRaises(
            CSRFError,
            validator.validate,
            mock_request
        )
    
    def test_force_to_lowercase(self):
        """Method name is forced to lower case."""
        
        from ..csrf import CSRFError
        
        mock_request = Mock()
        mock_request.method = 'A'
        
        validator = self.makeOne('token', target_methods=['a'])
        self.assertRaises(
            CSRFError,
            validator.validate,
            mock_request
        )
    
    def test_xmlhttprequests(self):
        """Also validates ``XMLHttpRequest``s."""
        
        from ..csrf import CSRFError
        
        mock_request = Mock()
        mock_request.method = 'A'
        
        validator = self.makeOne('token', target_methods=['a'])
        self.assertRaises(
            CSRFError,
            validator.validate,
            mock_request
        )
        
        mock_request.headers = {'X-Requested-With': 'XMLHttpRequest'}
        self.assertRaises(
            CSRFError,
            validator.validate,
            mock_request
        )
    
    def test_xmlhttprequests_headers(self):
        """Looks for token in ``X-CSRFToken`` of ``XMLHttpRequest``s."""
        
        from ..csrf import CSRFError
        
        mock_request = Mock()
        mock_request.method = 'A'
        mock_request.headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': 'token'
        }
        validator = self.makeOne('token', target_methods=['a'])
        retval = validator.validate(mock_request)
        self.assertTrue(retval is None)
    
    def test_xmlhttprequests_headers(self):
        """``X-CSRFToken`` will be overriden by ``_csrf``."""
        
        from ..csrf import CSRFError
        
        mock_request = Mock()
        mock_request.method = 'A'
        mock_request.headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': 'wrong'
        }
        validator = self.makeOne('token', target_methods=['a'])
        self.assertRaises(
            CSRFError,
            validator.validate,
            mock_request
        )
        
        mock_request.params = {'_csrf': 'token'}
        validator = self.makeOne('token', target_methods=['a'])
        retval = validator.validate(mock_request)
        self.assertTrue(retval is None)
    


class TestCSRFSubscriber(unittest.TestCase):
    """Test the logic of ``pyramid_weblayer.csrf.validate_against_csrf``."""
    
    def test_validates_the_request(self):
        """Validates the request against CSRF attacks."""
        
        from ..csrf import validate_against_csrf
        
        mock_request = Mock()
        mock_request.registry.settings = {}
        mock_validator = Mock()
        mock_validator_factory = Mock()
        mock_validator_factory.return_value = mock_validator
        mock_event = Mock()
        mock_event.request = mock_request
        
        validate_against_csrf(mock_event, Validator=mock_validator_factory)
        mock_validator.validate.assert_called_with(mock_request)
    
    def test_doesnt_validate_the_request(self):
        """Only validates the request against CSRF attacks if settings['csrf_validate']
          isn't false.
        """
        
        from ..csrf import validate_against_csrf
        
        mock_request = Mock()
        mock_request.registry.settings = {'csrf.validate': False}
        mock_validator = Mock()
        mock_validator_factory = Mock()
        mock_validator_factory.return_value = mock_validator
        mock_event = Mock()
        mock_event.request = mock_request
        
        validate_against_csrf(mock_event, Validator=mock_validator_factory)
        self.assertRaises(
            AssertionError,
            mock_validator.validate.assert_called_with,
            mock_request
        )
    
    def test_raises_httpunauthorized(self):
        """Raises ``HTTPUnauthorized`` if CSRF doesn't validate."""
        
        from pyramid.httpexceptions import HTTPUnauthorized
        from ..csrf import validate_against_csrf, CSRFError
        
        def raise_exc(*args):
            raise CSRFError
        
        mock_request = Mock()
        mock_request.registry.settings = {}
        mock_validator = Mock()
        mock_validator_factory = Mock()
        mock_validator_factory.return_value = mock_validator
        mock_validator.validate = raise_exc
        mock_event = Mock()
        mock_event.request = mock_request
        
        self.assertRaises(
            HTTPUnauthorized,
            validate_against_csrf,
            mock_event, 
            Validator=mock_validator_factory
        )
    

