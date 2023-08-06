from __future__ import absolute_import

import ast
import atexit
import inspect
import linecache
import os
import pdb
import re
import sys
import tokenize

from functools import partial
from itertools import chain

from colorama import AnsiToWin32
from colorama import Back
from colorama import Fore
from colorama import Style
from fields import Fields

__version__ = "0.5.0"
__all__ = 'Q', 'When', 'And', 'Or', 'CodePrinter', 'Debugger', 'VarsPrinter', 'trace', 'stop'

DEFAULT_MIN_FILENAME_ALIGNMENT = 30
NO_COLORS = {
    'reset': '',
    'filename': '',
    'colon': '',
    'lineno': '',
    'kind': '',
    'continuation': '',
    'return': '',
    'exception': '',
    'detail': '',
    'vars': '',
    'vars-name': '',
    'call': '',
    'line': '',
    'internal-failure': '',
    'internal-detail': '',
    'source-failure': '',
    'source-detail': '',
}
EVENT_COLORS = {
    'reset': Style.RESET_ALL,
    'filename': '',
    'colon': Fore.BLACK + Style.BRIGHT,
    'lineno': Style.RESET_ALL,
    'kind': Fore.CYAN,
    'continuation': Fore.BLUE,
    'return': Style.BRIGHT + Fore.GREEN,
    'exception': Style.BRIGHT + Fore.RED,
    'detail': Style.NORMAL,
    'vars': Style.RESET_ALL + Fore.MAGENTA,
    'vars-name': Style.BRIGHT,
    'internal-failure': Back.RED + Style.BRIGHT + Fore.RED,
    'internal-detail': Fore.WHITE,
    'source-failure': Style.BRIGHT + Back.YELLOW + Fore.YELLOW,
    'source-detail': Fore.WHITE,
}
CODE_COLORS = {
    'call': Fore.RESET + Style.BRIGHT,
    'line': Fore.RESET,
    'return': Fore.YELLOW,
    'exception': Fore.RED,
}


class Tracer(object):
    """
    Trace object.

    """
    def __init__(self):
        self._handler = None
        self._previous_tracer = None

    def __str__(self):
        return "Tracer(_handler={}, _previous_tracer={})".format(
            "<not started>" if self._handler is None else self._handler,
            self._previous_tracer,
        )

    def __call__(self, frame, kind, arg):
        """
        The settrace function.

        .. note::

            This always returns self (drills down) - as opposed to only drilling down when predicate(event) is True because it might
            match further inside.
        """
        if self._handler is None:
            raise RuntimeError("Tracer is not started.")

        self._handler(Event(frame, kind, arg))

        if self._previous_tracer:
            self._previous_tracer(frame, kind, arg)
        return self

    def trace(self, *predicates, **options):
        """
        Starts tracing. Can be used as a context manager (with slightly incorrect semantics - it starts tracing before ``__enter__`` is
        called).

        Args:
            predicates (:class:`hunter.Q` instances): Runs actions if any of the given predicates match.
            options: Keyword arguments that are passed to :class:`hunter.Q`, for convenience.
        """
        if "action" not in options and "actions" not in options:
            options["action"] = CodePrinter
        merge = options.pop("merge", True)
        predicate = Q(*predicates, **options)

        previous_tracer = sys.gettrace()
        if previous_tracer is self and merge:
            self._handler |= predicate
        else:
            self._previous_tracer = previous_tracer
            self._handler = predicate
            sys.settrace(self)
        return self

    def stop(self):
        """
        Stop tracing. Restores previous tracer (if any).
        """
        sys.settrace(self._previous_tracer)
        self._previous_tracer = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

_tracer = Tracer()
trace = _tracer.trace
stop = atexit.register(_tracer.stop)


class _CachedProperty(object):
    def __init__(self, func):
        self.func = func

    def __get__(self, obj, cls):
        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value


class Event(Fields.kind.function.module.filename):
    """
    Event wrapper for ``frame, kind, arg`` (the arguments the settrace function gets).

    Provides few convenience properties.
    """
    frame = None
    kind = None
    arg = None

    def __init__(self, frame, kind, arg):
        self.frame = frame
        self.kind = kind
        self.arg = arg

    @_CachedProperty
    def locals(self):
        return self.frame.f_locals

    @_CachedProperty
    def globals(self):
        return self.frame.f_locals

    @_CachedProperty
    def function(self):
        return self.code.co_name

    @_CachedProperty
    def module(self):
        return self.frame.f_globals.get('__name__', '')

    @_CachedProperty
    def filename(self):
        filename = self.frame.f_globals.get('__file__', '')

        if filename.endswith(('.pyc', '.pyo')):
            filename = filename[:-1]
        elif filename.endswith('$py.class'):  # Jython
            filename = filename[:-9] + ".py"

        return filename

    @_CachedProperty
    def lineno(self):
        return self.frame.f_lineno

    @_CachedProperty
    def code(self):
        return self.frame.f_code

    @_CachedProperty
    def fullsource(self, getlines=linecache.getlines):
        """
        Get a line from ``linecache``. Ignores failures somewhat.
        """
        try:
            return self._raw_fullsource
        except Exception as exc:
            return "??? NO SOURCE: {!r}".format(exc)

    @_CachedProperty
    def source(self, getline=linecache.getline):
        try:
            return getline(self.filename, self.lineno)
        except Exception as exc:
            return "??? NO SOURCE: {!r}".format(exc)

    @_CachedProperty
    def _raw_fullsource(self, getlines=linecache.getlines, getline=linecache.getline):
        if self.kind == 'call' and self.code.co_name != "<module>":
            lines = []
            try:
                for _, token, _, _, line in tokenize.generate_tokens(partial(
                    next,
                    yield_lines(self.filename, self.lineno - 1, lines.append)
                )):
                    if token in ("def", "class", "lambda"):
                        return ''.join(lines)
            except tokenize.TokenError:
                pass

        return getline(self.filename, self.lineno)

    __getitem__ = object.__getattribute__


def yield_lines(filename, start, collector,
                limit=10,
                getlines=linecache.getlines,
                leading_whitespace_re=re.compile('(^[ \t]*)(?:[^ \t\n])', re.MULTILINE)):
    dedent = None
    amount = 0
    for line in getlines(filename)[start:start + limit]:
        if dedent is None:
            dedent = leading_whitespace_re.findall(line)
            dedent = dedent[0] if dedent else ""
            amount = len(dedent)
        elif not line.startswith(dedent):
            break
        collector(line)
        yield line[amount:]


def Q(*predicates, **query):
    """
    Handles situations where :class:`hunter.Query` objects (or other callables) are passed in as positional arguments.
    Conveniently converts that to an :class:`hunter.Or` predicate.
    """
    optional_actions = query.pop("actions", [])
    if "action" in query:
        optional_actions.append(query.pop("action"))

    if predicates:
        predicates = tuple(
            p() if inspect.isclass(p) and issubclass(p, Action) else p
            for p in predicates
        )
        if any(isinstance(p, CodePrinter) for p in predicates):
            if CodePrinter in optional_actions:
                optional_actions.remove(CodePrinter)
        if query:
            predicates += Query(**query),

        result = Or(*predicates)
    else:
        result = Query(**query)

    if optional_actions:
        result = When(result, *optional_actions)

    return result


class Query(Fields.query):
    """
    A query class.
    """
    query = ()
    allowed = tuple(i for i in Event.__dict__.keys() if not i.startswith('_'))

    def __init__(self, **query):
        """
        Args:
            query: criteria to match on. Currently only 'function', 'module' or 'filename' are accepted.
        """
        for key in query:
            if key not in self.allowed:
                raise TypeError("Unexpected argument {!r}. Must be one of {}.".format(key, self.allowed))
        self.query = query

    def __repr__(self):
        return "Query({})".format(
            ', '.join("{}={!r}".format(*item) for item in self.query.items()),
        )

    def __call__(self, event):
        """
        Handles event. Returns True if all criteria matched.
        """
        for key, value in self.query.items():
            if event[key] != value:
                return

        return True

    def __or__(self, other):
        """
        Convenience API so you can do ``Q() | Q()``. It converts that to ``Or(Q(), Q())``.
        """
        return Or(self, other)

    def __and__(self, other):
        """
        Convenience API so you can do ``Q() & Q()``. It converts that to ``And(Q(), Q())``.
        """
        return And(self, other)


class When(Fields.condition.actions):
    """
    Runs ``actions`` when ``condition(event)`` is ``True``.

    Actions take a single ``event`` argument.
    """
    def __init__(self, condition, *actions):
        if not actions:
            raise TypeError("Must give at least one action.")
        super(When, self).__init__(condition, [
            action() if inspect.isclass(action) and issubclass(action, Action) else action
            for action in actions
        ])

    def __call__(self, event):
        """
        Handles the event.
        """
        if self.condition(event):
            for action in self.actions:
                action(event)

            return True

    def __or__(self, other):
        return Or(self, other)

    def __and__(self, other):
        return And(self, other)


def _with_metaclass(meta, *bases):
    """Create a base class with a metaclass."""
    # This requires a bit of explanation: the basic idea is to make a dummy
    # metaclass for one level of class instantiation that replaces itself with
    # the actual metaclass.
    class metaclass(meta):

        def __new__(cls, name, this_bases, d):
            return meta(name, bases, d)
    return type.__new__(metaclass, 'temporary_class', (), {})


class _UnwrapSingleArgumentMetaclass(type):
    def __call__(cls, predicate, *predicates):
        if not predicates:
            return predicate
        else:
            all_predicates = []

            for p in chain((predicate,), predicates):
                if isinstance(p, cls):
                    all_predicates.extend(p.predicates)
                else:
                    all_predicates.append(p)
            return super(_UnwrapSingleArgumentMetaclass, cls).__call__(*all_predicates)


class And(_with_metaclass(_UnwrapSingleArgumentMetaclass, ~Fields.predicates)):
    """
    `And` predicate. Exits at the first sub-predicate that returns ``False``.
    """
    def __init__(self, *predicates):
        self.predicates = predicates

    def __str__(self):
        return "And({})".format(', '.join(str(p) for p in self.predicates))

    def __call__(self, event):
        """
        Handles the event.
        """
        for predicate in self.predicates:
            if not predicate(event):
                return
        return True

    def __or__(self, other):
        return Or(self, other)

    def __and__(self, other):
        return And(*chain(self.predicates, other.predicates if isinstance(other, And) else (other,)))


class Or(_with_metaclass(_UnwrapSingleArgumentMetaclass, ~Fields.predicates)):
    """
    `Or` predicate. Exits at first sub-predicate that returns ``True``.
    """
    def __init__(self, *predicates):
        self.predicates = predicates

    def __call__(self, event):
        """
        Handles the event.
        """
        for predicate in self.predicates:
            if predicate(event):
                return True

    def __or__(self, other):
        return Or(*chain(self.predicates, other.predicates if isinstance(other, Or) else (other,)))

    def __and__(self, other):
        return And(self, other)


class Action(object):
    def __call__(self, event):
        raise NotImplementedError()


class Debugger(Fields.klass.kwargs, Action):
    """
    An action that starts ``pdb``.
    """
    def __init__(self, klass=pdb.Pdb, **kwargs):
        self.klass = klass
        self.kwargs = kwargs

    def __call__(self, event):
        """
        Runs a ``pdb.set_trace`` at the matching frame.
        """
        self.klass(**self.kwargs).set_trace(event.frame)


class ColorStreamAction(Action):
    _stream = None
    _tty = None

    @property
    def stream(self):
        return self._stream

    @stream.setter
    def stream(self, value):
        isatty = getattr(value, 'isatty', None)
        if isatty and isatty() and os.name != 'java':
            self._stream = AnsiToWin32(value)
            self._tty = True
            self.event_colors = EVENT_COLORS
            self.code_colors = CODE_COLORS
        else:
            self._tty = False
            self._stream = value
            self.event_colors = NO_COLORS
            self.code_colors = NO_COLORS

    def _safe_repr(self, obj):
        try:
            return repr(obj)
        except Exception as exc:
            return "{internal-failure}!!! FAILED REPR: {internal-detail}{!r}".format(exc, **self.event_colors)


class CodePrinter(Fields.stream.filename_alignment, ColorStreamAction):
    """
    An action that just prints the code being executed.

    Args:
        stream (file-like): Stream to write to. Default: ``sys.stderr``.
        filename_alignment (int): Default size for the filaname column (files are right-aligned). Default: ``15``.
    """
    def __init__(self, stream=sys.stderr, filename_alignment=DEFAULT_MIN_FILENAME_ALIGNMENT):
        self.stream = stream
        self.filename_alignment = filename_alignment

    def _safe_source(self, event):
        try:
            lines = event._raw_fullsource.rstrip().splitlines()
            if not lines:
                raise RuntimeError("Source code string is empty.")
            return lines
        except Exception as exc:
            return "{source-failure}??? NO SOURCE: {source-detail}{!r}".format(exc, **self.event_colors),

    def __call__(self, event, sep=os.path.sep, join=os.path.join):
        """
        Handle event and print filename, line number and source code. If event.kind is a `return` or `exception` also prints values.
        """
        filename = event.filename or "<???>"
        # TODO: support auto-alignment, need a context object for this, eg:
        # alignment = context.filename_alignment = max(getattr(context, 'filename_alignment', self.filename_alignment), len(filename))
        lines = self._safe_source(event)
        self.stream.write("{filename}{:>{align}}{colon}:{lineno}{:<5} {kind}{:9} {code}{}{reset}\n".format(
            join(*filename.split(sep)[-2:]),
            event.lineno,
            event.kind,
            lines[0],
            align=self.filename_alignment,
            code=self.code_colors[event.kind],
            **self.event_colors
        ))
        for line in lines[1:]:
            self.stream.write("{:>{align}}       {kind}{:9} {code}{}{reset}\n".format(
                "",
                r"   |",
                line,
                align=self.filename_alignment,
                code=self.code_colors[event.kind],
                **self.event_colors
            ))

        if event.kind in ('return', 'exception'):
            self.stream.write("{:>{align}}       {continuation}{:9} {color}{} value: {detail}{}{reset}\n".format(
                "",
                "...",
                event.kind,
                self._safe_repr(event.arg),
                align=self.filename_alignment,
                color=self.event_colors[event.kind],
                **self.event_colors
            ))


class VarsPrinter(Fields.names.globals.stream.filename_alignment, ColorStreamAction):
    """
    An action that prints local variables and optionally global variables visible from the current executing frame.

    Args:
        *names (strings):
            Names to evaluate. Expressions can be used (will only try to evaluate if all the variables are present on the frame.
        stream (file-like): Stream to write to. Default: ``sys.stderr``.
        filename_alignment (int): Default size for the filaneme column (files are right-aligned). Default: ``15``.
        globals (bool): Allow access to globals. Default: ``False`` (only looks at locals).
    """
    default_stream = sys.stderr

    def __init__(self, *names, **options):
        if not names:
            raise TypeError("Must give at least one name/expression.")
        self.stream = options.pop('stream', self.default_stream)
        self.filename_alignment = options.pop('filename_alignment', DEFAULT_MIN_FILENAME_ALIGNMENT)
        self.names = {
            name: set(self._iter_symbols(name))
            for name in names
        }
        self.globals = options.pop('globals', False)

    @staticmethod
    def _iter_symbols(code):
        """
        Iterate all the variable names in the given expression.

        Example:

        * ``self.foobar`` yields ``self``
        * ``self[foobar]`` yields `self`` and ``foobar``
        """
        for node in ast.walk(ast.parse(code)):
            if isinstance(node, ast.Name):
                yield node.id

    def _safe_eval(self, code, event):
        """
        Try to evaluate the given code on the given frame. If failure occurs, returns some ugly string with exception.
        """
        try:
            return eval(code, event.globals if self.globals else {}, event.locals)
        except Exception as exc:
            return "{internal-failure}FAILED EVAL: {internal-detail}{!r}".format(exc, **self.event_colors)

    def __call__(self, event):
        """
        Handle event and print the specified variables.
        """
        first = True
        frame_symbols = set(event.locals)
        if self.globals:
            frame_symbols |= set(event.globals)

        for code, symbols in self.names.items():
            if frame_symbols >= symbols:
                self.stream.write("{:>{align}}       {vars}{:9} {vars-name}{} {vars}=> {reset}{}{reset}\n".format(
                    "",
                    "vars" if first else "...",
                    code,
                    self._safe_repr(self._safe_eval(code, event)),
                    align=self.filename_alignment,
                    **self.event_colors
                ))
                first = False
