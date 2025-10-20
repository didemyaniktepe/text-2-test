class TestError(Exception):
    """Base exception for test related errors"""
    pass


class TestGenerationError(TestError):
    """Raised when test generation fails"""
    pass


class TestExecutionError(TestError):
    """Raised when test execution fails"""
    pass

class TestNotFoundError(TestError):
    """Raised when a test is not found"""
    pass
