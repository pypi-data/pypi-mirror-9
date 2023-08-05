from __future__ import absolute_import

from pyflakes.api import checkPath
from pyflakes.reporter import Reporter

from prospector.message import Location, Message
from prospector.tools.base import ToolBase


__all__ = (
    'PyFlakesTool',
)


_MESSAGE_CODES = {
    'UnusedImport': 'FL0001',
    'RedefinedWhileUnused': 'FL0002',
    'RedefinedInListComp': 'FL0003',
    'ImportShadowedByLoopVar': 'FL0004',
    'ImportStarUsed': 'FL0005',
    'UndefinedName': 'FL0006',
    'DoctestSyntaxError': 'FL0007',
    'UndefinedExport': 'FL0008',
    'UndefinedLocal': 'FL0009',
    'DuplicateArgument': 'FL0010',
    'Redefined': 'FL0011',
    'LateFutureImport': 'FL0012',
    'UnusedVariable': 'FL0013',
}


class ProspectorReporter(Reporter):
    def __init__(self, ignore=None):
        super(ProspectorReporter, self).__init__(None, None)
        self._messages = []
        self.ignore = ignore or ()

    # pylint: disable=R0913
    def record_message(
            self,
            filename=None,
            line=None,
            character=None,
            code=None,
            message=None):

        code = code or 'FL0000'
        if code in self.ignore:
            return

        location = Location(
            path=filename,
            module=None,
            function=None,
            line=line,
            character=character,
        )
        message = Message(
            source='pyflakes',
            code=code,
            location=location,
            message=message,
        )
        self._messages.append(message)

    def unexpectedError(self, filename, msg):  # noqa
        self.record_message(
            filename=filename,
            code='FL9997',
            message=msg,
        )

    # pylint: disable=R0913
    def syntaxError(self, filename, msg, lineno, offset, text):  # noqa
        self.record_message(
            filename=filename,
            line=lineno,
            character=offset,
            code='FL9998',
            message=msg,
        )

    def flake(self, message):
        code = _MESSAGE_CODES.get(message.__class__.__name__, 'FL9999')

        self.record_message(
            filename=message.filename,
            line=message.lineno,
            character=(message.col + 1),
            code=code,
            message=message.message % message.message_args,
        )

    def get_messages(self):
        return self._messages


class PyFlakesTool(ToolBase):
    def __init__(self, *args, **kwargs):
        super(PyFlakesTool, self).__init__(*args, **kwargs)
        self.ignore_codes = ()

    def configure(self, prospector_config, _):
        self.ignore_codes = prospector_config.get_disabled_messages('pyflakes')
        return None

    def run(self, found_files):
        reporter = ProspectorReporter(ignore=self.ignore_codes)
        for filepath in found_files.iter_module_paths():
            checkPath(filepath, reporter)

        return reporter.get_messages()
