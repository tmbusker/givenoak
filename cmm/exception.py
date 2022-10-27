class RecursiveParenthoodError(Exception):
    """
    Raised when race condition was detected.
    """
    def __str__(self):
        return 'Recursive parenthood was detected.'
