class EyesError(Exception):
    """
    Applitools Eyes Exception.
    """
    pass


class OutOfBoundsError(EyesError):
    """
    Indicates that an element is outside a specific boundary (e.g, region outside a frame,
    or point outside an image).
    """
    pass


class TestFailedError(Exception):
    """
    Indicates that a test did not pass (i.e., test either failed or is a new test).
    """
    def __init__(self, message, test_results=None,):
        self.message = message
        self.test_results = test_results

    def __str__(self):
        return "%s , %s" % (self.message, self.test_results)


class NewTestError(TestFailedError):
    """
    Indicates that a test is a new test.
    """
    def __init__(self, message, test_results=None):
        super(NewTestError, self).__init__(message, test_results)
