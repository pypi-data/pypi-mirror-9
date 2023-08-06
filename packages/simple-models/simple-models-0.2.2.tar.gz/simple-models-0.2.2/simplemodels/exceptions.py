# -*- coding: utf-8 -*-
import six


class ValidationError(Exception):

    """ Custom exception class. Useful for validation methods """

    def __unicode__(self):
        return six.u(self.message)


class RequiredValidationError(ValidationError):

    """ Raised when required field is not found """

    pass


class ValidationTypeIsNotSupported(ValidationError):
    pass