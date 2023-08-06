import os
import gettext
import json
from collections import defaultdict

import jsonschema


class ValidationError(Exception):
    def display(self, error):
        """
        Find a translated error that can be displayed to the user.
        """
        validator = error.get('validator')
        if validator == 'minLength':
            return self._gettext.gettext('This field is too short')

        if validator == 'required':
            return self._gettext.gettext('This field is required')

        if validator == 'unique':
            return self._gettext.gettext('Already exists')

    @property
    def _gettext(self):
        """
        Load the relevant translations

        """
        if not hasattr(self, '_translations'):
            try:
                import babel
                from flask import current_app

                locales = current_app.babel_instance.list_translations()
                self._translations = babel.support.Translations.load(
                    os.path.join(os.path.dirname(__file__), 'locale'),
                    locales
                )
            except (AttributeError, RuntimeError, ImportError):
                self._translations = gettext

        return self._translations

    def __init__(self, errors):
        if isinstance(errors, dict):
            # Single error. Convert it to a list
            errors = [errors]

        self.errors = defaultdict(list)

        for error in errors:
            if isinstance(error, jsonschema.ValidationError):
                # jsonschema error, convert to dict
                error = {
                    'message': error.message,
                    'instance': error.instance,
                    'validator': error.validator,
                    'path': '/' + '/'.join(error.path)
                }

            display_message = self.display(error)
            if display_message:
                error['display_message'] = display_message

            self.errors[error.pop('path')].append(error)

        super(ValidationError, self).__init__(json.dumps(self.errors))


class ResourceNotFound(Exception):
    pass


class ResourceExists(Exception):
    pass


class Forbidden(Exception):
    pass


class UnAuthorized(Exception):
    pass


class ServiceUnavailable(Exception):
    pass

