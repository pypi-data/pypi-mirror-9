from __future__ import unicode_literals

from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.contrib.completers import PathCompleter
from prompt_toolkit.contrib.regular_languages.compiler import compile as compile_grammar
from prompt_toolkit.contrib.regular_languages.completion import GrammarCompleter

from ptpython.utils import get_jedi_script_from_document

import re

__all__ = (
    'PythonCompleter',
)


class PythonCompleter(Completer):
    """
    Completer for Python code.
    """
    def __init__(self, get_globals, get_locals):
        super(PythonCompleter, self).__init__()

        self.get_globals = get_globals
        self.get_locals = get_locals

        self._path_completer_grammar, self._path_completer = self._create_path_completer()

    def _create_path_completer(self):
        def unwrapper(text):
            return re.sub(r'\\(.)', r'\1', text)

        def single_quoted_wrapper(text):
            return text.replace('\\', '\\\\').replace("'", "\\'")

        def double_quoted_wrapper(text):
            return text.replace('\\', '\\\\').replace('"', '\\"')

        grammar = r"""
                # Text before the current string.
                (
                    [^'"#]            |  # Not quoted characters.
                    '''.*'''          |  # Inside single quoted triple strings
                    "" ".*"" "        |  # Inside double quoted triple strings
                    \#[^\n]*          |  # Comment.
                    "([^"\\]|\\.)*"   |  # Inside double quoted strings.
                    '([^'\\]|\\.)*'      # Inside single quoted strings.
                )*
                # The current string that we're completing.
                (
                    ' (?P<var1>([^\n'\\]|\\.)*) |  # Inside a single quoted string.
                    " (?P<var2>([^\n"\\]|\\.)*)    # Inside a double quoted string.
                )
        """

        g = compile_grammar(
            grammar,
            escape_funcs={
                'var1': single_quoted_wrapper,
                'var2': double_quoted_wrapper,
            },
            unescape_funcs={
                'var1': unwrapper,
                'var2': unwrapper,
            })
        return g, GrammarCompleter(g, {
            'var1': PathCompleter(),
            'var2': PathCompleter(),
        })

    def _complete_path_while_typing(self, document):
        char_before_cursor = document.char_before_cursor
        return document.text and (
            char_before_cursor.isalnum() or char_before_cursor in '/.~')

    def _complete_python_while_typing(self, document):
        char_before_cursor = document.char_before_cursor
        return document.text and (
            char_before_cursor.isalnum() or char_before_cursor in '_.')

    def get_completions(self, document, complete_event):
        """
        Get Python completions.
        """
        # Do Path completions
        if complete_event.completion_requested or self._complete_path_while_typing(document):
            for c in self._path_completer.get_completions(document, complete_event):
                yield c

        # If we are inside a string, Don't do Jedi completion.
        if self._path_completer_grammar.match(document.text):
            return

        # Do Jedi Python completions.
        if complete_event.completion_requested or self._complete_python_while_typing(document):
            script = get_jedi_script_from_document(document, self.get_locals(), self.get_globals())

            if script:
                try:
                    completions = script.completions()
                except TypeError:
                    # Issue #9: bad syntax causes completions() to fail in jedi.
                    # https://github.com/jonathanslenders/python-prompt-toolkit/issues/9
                    pass
                except UnicodeDecodeError:
                    # Issue #43: UnicodeDecodeError on OpenBSD
                    # https://github.com/jonathanslenders/python-prompt-toolkit/issues/43
                    pass
                except AttributeError:
                    # Jedi issue #513: https://github.com/davidhalter/jedi/issues/513
                    pass
                except ValueError:
                    # Jedi issue: "ValueError: invalid \x escape"
                    pass
                else:
                    for c in completions:
                        yield Completion(c.name_with_symbols, len(c.complete) - len(c.name_with_symbols),
                                         display=c.name_with_symbols)
