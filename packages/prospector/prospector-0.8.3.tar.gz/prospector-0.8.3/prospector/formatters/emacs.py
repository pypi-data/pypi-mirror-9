from prospector.formatters.text import TextFormatter


__all__ = (
    'EmacsFormatter',
)


class EmacsFormatter(TextFormatter):
    def render_message(self, message):
        output = []

        output.append('%s:%s :' % (
            message.location.path,
            message.location.line,
        ))

        output.append(
            '    L%s:%s %s: %s - %s' % (
                message.location.line or '-',
                message.location.character if message.location.line else '-',
                message.location.function,
                message.source,
                message.code,
            )
        )

        output.append('    %s' % message.message)

        return '\n'.join(output)
