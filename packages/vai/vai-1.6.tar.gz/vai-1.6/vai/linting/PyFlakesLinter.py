from .LinterResult import LinterResult
import pyflakes.api

class PyFlakesLinter:
    """Fast, less accurate linter."""
    def __init__(self, document):
        self._document = document

    def runOnce(self):
        reporter = Reporter()
        pyflakes.api.check(self._document.documentText(),
                           self._document.filename(),
                           reporter=reporter)
        return reporter.errors()

class Reporter:
    """Wrap class to get events delivered for our consumption"""
    def __init__(self):
        self._errors = []

    def unexpectedError(self, *args):
        pass

    def syntaxError(self, filename, msg, lineno, offset, text):
        self._errors.append( LinterResult(filename = filename,
                                          line = lineno,
                                          column = offset,
                                          level = "error",
                                          message = msg)
                            )

    def flake(self, msg):
        self._errors.append( LinterResult(filename = msg.filename,
                                          line = msg.lineno,
                                          column = msg.col,
                                          level = "warning",
                                          message = str(msg))
                            )

    def errors(self):
        return self._errors

