
""" ``mixin`` module.
"""


class ErrorsMixin(object):
    """ Used primary by service layer to validate business rules.

        Requirements:
        - self.errors

        Example::

            class MyService(ValidationMixin):

                def __init__(self, repository, errors, locale):
                    # ...

                def authenticate(self, credential):
                    if not self.factory.membership.authenticate(credentials):
                        self.error('The username or password provided '
                                   'is incorrect.')
                        return False
                    # ...
                    return True
    """

    def error(self, message, name='__ERROR__'):
        """ Add `message` to errors.
        """
        self.errors.setdefault(name, []).append(message)


class ValidationMixin(object):
    """ Used primary by service layer to validate domain model.

        Requirements:
        - self.errors
        - self.translations

        Example::

            class MyService(ValidationMixin):

                def __init__(self, repository, errors, translations, locale):
                    # ...

                def authenticate(self, credential):
                    if not self.validate(credential, credential_validator):
                        return False
                    # ...
                    return True
    """

    def error(self, message, name='__ERROR__'):
        """ Add `message` to errors.
        """
        self.errors.setdefault(name, []).append(message)

    def validate(self, model, validator):
        """ Validate given `model` using `validator`.
        """
        return validator.validate(
            model,
            self.errors,
            translations=self.translations['validation'])
