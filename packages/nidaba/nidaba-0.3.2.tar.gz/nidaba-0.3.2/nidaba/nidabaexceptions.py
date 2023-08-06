# -*- coding: utf-8 -*-
"""
nidaba.nidabaexceptions
~~~~~~~~~~~~~~~~~~~~~~~

All custom exceptions raised by various nidaba modules and packages. Packages
should always define their exceptions here.
"""


class NidabaUnibarrierException(Exception):

    def __init__(self, message=None):
        Exception.__init__(self, message)


class NidabaAlgorithmException(Exception):

    def __init__(self, message=None):
        Exception.__init__(self, message)


class NidabaTaskException(Exception):

    def __init__(self, status_code):
        self.status_code = status_code
        Exception.__init__(self, status_code)


class NidabaTickException(Exception):

    def __init__(self, status_code):
        self.status_code = status_code
        Exception.__init__(self, status_code)


class NidabaStepException(Exception):

    def __init__(self, status_code):
        self.status_code = status_code
        Exception.__init__(self, status_code)


class NidabaInputException(Exception):

    def __init__(self, status_code):
        self.status_code = status_code
        Exception.__init__(self, status_code)


class NidabaNoSuchAlgorithmException(Exception):

    def __init__(self, status_code):
        self.status_code = status_code
        Exception.__init__(self, status_code)


class NidabaInvalidParameterException(Exception):

    def __init__(self, status_code):
        self.status_code = status_code
        Exception.__init__(self, status_code)


class NidabaTesseractException(Exception):

    def __init__(self, status_code):
        self.status_code = status_code
        Exception.__init__(self, status_code)


class NidabaOcropusException(Exception):

    def __init__(self, status_code):
        self.status_code = status_code
        Exception.__init__(self, status_code)


class NidabaStorageViolationException(Exception):

    def __init__(self, status_code):
        self.status_code = status_code
        Exception.__init__(self, status_code)


class NidabaNoSuchStorageBin(Exception):

    def __init__(self, status_code):
        self.status_code = status_code
        Exception.__init__(self, status_code)
