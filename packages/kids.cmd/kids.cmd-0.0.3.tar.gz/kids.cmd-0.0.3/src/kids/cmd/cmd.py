# -*- coding: utf-8 -*-
"""

"""

from __future__ import print_function

import os
import os.path
import sys
import types
import glob
import importlib
import inspect
import re
from collections import OrderedDict

from docopt import docopt, DocoptExit, DocoptLanguageError

from . import msg

from kids.cache import cache
import kids.cfg
import kids.data as data
import kids.txt as txt
import kids.file as kf
from kids.common.exc import format_last_exception
from kids.ansi import aformat

PY3 = sys.version_info >= (3, 0)


def cmd(f):
    """Decorator to declare class method as a command"""
    f.__command__ = True
    return f


def is_cmd(obj):
    return getattr(obj, '__command__', False)


@cmd
class BaseCommand(object):

    __version__ = "0.0.1"

    @property
    @cache
    def local_path(self):
        return False

    @cache
    @property
    def cfg(self):  ## shortcut
        if self.local_path:
            return kids.cfg.load(local_path=self.local_path)
        else:
            return kids.cfg.load()

    def __call__(self, arguments):
        return run(self, arguments)


def get_obj_subcmds(obj):
    """Fetch action in callable attributes which and commands

    Callable must have their attribute 'command' set to True to
    be recognised by this lookup.

    Please consider using the decorator ``@cmd`` to declare your
    subcommands in classes for instance.

    """
    subcmds = []
    for label in dir(obj.__class__):
        if label.startswith("_"):
            continue
        if isinstance(getattr(obj.__class__, label, False), property):
            continue
        rvalue = getattr(obj, label)
        if not callable(rvalue) or not is_cmd(rvalue):
            continue
        if isinstance(obj, types.MethodType) and \
               label in ("im_func", "im_self", "im_class"):
            continue
        ## potential command
        command_name = getattr(rvalue, "command_name",
                               label[:-1] if label.endswith("_") else
                               label)
        subcmds.append((command_name, rvalue))
    return OrderedDict(subcmds)


def get_mod_subcmds(mod):
    """Fetch action in same directory in python module

    python module loaded are of this form: '%s_*.py' % prefix

    """

    ## Look in modules attributes

    subcmds = get_obj_subcmds(mod)

    ##

    path = os.path.dirname(os.path.realpath(mod.__file__))
    prefix = kf.basename(mod.__file__, (".py", ".pyc"))

    if mod.__package__ is None:
        sys.path.insert(0, os.path.dirname(path))
        mod.__package__ = kf.basename(path)

    for f in glob.glob(os.path.join(path, '%s_*.py' % prefix)):
        module_name, _ext = os.path.splitext(kf.basename(f))
        try:
            mod = importlib.import_module(".%s" % module_name, mod.__package__)
        except ImportError as e:
            msg.warn("%r could not be loaded: %s"
                     % (module_name, e.message))
            continue
        except IOError as e:
            print("%s" % module_name)
            raise
        if hasattr(mod, "Command") and is_cmd(mod.Command):
            obj = mod.Command
            if obj.__doc__ is None:
                msg.warn("Missing doc string for command from "
                         "module %s" % module_name)
                continue
            if isinstance(obj, type):
                obj = obj()  ## instanciate it.
            name = module_name.split("_", 1)[1]
            if name in subcmds:
                raise ValueError(
                    "Module command %r conflicts with already defined object "
                    "command."
                    % name)
            subcmds[name] = obj

    return subcmds


@cache
def get_subcmds(obj):
    if isinstance(obj, types.ModuleType):
        return get_mod_subcmds(obj)
    return get_obj_subcmds(obj)


def get_action_help(exname, actions):
    return "" if not actions else (
        "ACTION could be one of:\n\n"
        "%(actions)s\n\n"
        "See '%(surcmd)s help ACTION' for more information "
        "on a specific command."
        % actions)


def _find_prefix(template, pattern):
    line = data.lib.first(template.split('\n'),
                          lambda line: pattern in line)
    idx = line.index(pattern)
    return line[:idx]


def subcmd_env(env, name, only_sub=False):
    subcmd_env = env.copy()
    if only_sub:
        subcmd_env["surcmd"] = name
    else:
        subcmd_env["surcmd"] = "%s %s" % (env["surcmd"], name) \
                               if env.get("surcmd") else name
    subcmd_env["cmd"] = name
    return subcmd_env


def get_help(obj, env, subcmds):
    """Interpolate complete help doc of given object

    Assumption that given object as a specific interface:

    obj.__doc__ is the basic help object.
    obj.get_actions_titles() returns the subcommand if any.


    """
    doc = txt.dedent(obj.__doc__ or "")
    env = env.copy()  ## get a local copy

    doc = doc.strip()
    if not re.search(r"^usage:\s*$", doc, flags=re.IGNORECASE | re.MULTILINE):
        doc += txt.dedent("""

            Usage:
              %(std_usage)s

            Options:
              %(std_options)s""")

    help_line = ("  %%-%ds  %%s"
                 % (max([5] + [len(a) for a in subcmds]), ))
    env["actions"] = "\n".join(
        help_line % (
            name,
            get_help(subcmd, subcmd_env(env, name), {}).split("\n")[0])
        for name, subcmd in subcmds.items())
    env["actions_help"] = "" if not env["actions"] else (
        "ACTION could be one of:\n\n"
        "%(actions)s\n\n"
        "See '%(surcmd)s help ACTION' for more information "
        "on a specific command."
        % env)
    if "%(std_usage)s" in doc:
        env["std_usage"] = txt.indent(
            ("%(surcmd)s --help\n"
             "%(surcmd)s --version" +
             (("\n%(surcmd)s help [COMMAND]"
               "\n%(surcmd)s ACTION [ARGS...]") if subcmds else ""))
            % env,
            _find_prefix(doc, "%(std_usage)s"),
            first="")
    if "%(std_options)s" in doc:
        env["std_options"] = txt.indent(
            "--help          Show this screen.\n"
            "--version       Show version.",
            _find_prefix(doc, "%(std_options)s"),
            first="")

    if subcmds and "%(actions_help)s" not in doc:
        doc += "\n\n%(actions_help)s"
    try:
        output = doc % env
    except KeyError as e:
        msg.err("Doc interpolation of %s needed missing key %r"
                % (aformat(env["surcmd"], attrs=["bold", ]),
                   e.args[0]))
        exit(1)
    except Exception as e:
        msg.err(
            "Documentation of %s is not valid. Please check it:\n%s"
            % (aformat(env["surcmd"], attrs=["bold", ]),
               doc))
        import traceback
        import pdb; pdb.set_trace()
        exit(1)
    return output


def get_help_subcmd(name, subcmd, env, only_sub=False):
    return get_help(
        subcmd,
        subcmd_env(env, name, only_sub=only_sub),
        get_subcmds(subcmd))


## Removing traceback when failing to encode unicode string in
## console's locale.
import locale
from codecs import getwriter, StreamWriter, lookup
Writer = getwriter(locale.getpreferredencoding())
writer = Writer(sys.stdout)

sys.stdout = writer   ## Breaks pdb readline capabilities on python 2
sys.stdout.errors = "replace"


def is_bound(method):
    """Return if method is bound or not.

        >>> class A(object):
        ...     def m1(self, a, b, c=None): pass
        >>> is_bound(A.m1)
        False
        >>> is_bound(A().m1)
        True

    Note that it should work with python callable and return
    False also:

        >>> is_bound(lambda: None)
        False

    """
    if PY3:
        return hasattr(method, '__self__')
    return getattr(method, "im_self", None) is not None


def get_calling_prototype(acallable):
    """Returns actual working calling prototype

    This means that the prototype given can be used directly
    in the same way by bound method, method, function, lambda::

        >>> def f1(a, b, c=1): pass
        >>> get_calling_prototype(f1)
        (['a', 'b', 'c'], (1,))
        >>> get_calling_prototype(lambda a, b: None)
        (['a', 'b'], ())
        >>> get_calling_prototype(lambda a=None: None)
        (['a'], (None,))
        >>> get_calling_prototype(lambda : None)
        ([], ())
        >>> class A(object):
        ...     def m1(self, a, b, c=None): pass
        ...     @classmethod
        ...     def cm(cls, a, b, c=None): pass
        ...     @staticmethod
        ...     def st(a, b, c=None): pass
        ...     def __call__(self, a, b, c=None): pass

        >>> get_calling_prototype(A.m1)
        (['self', 'a', 'b', 'c'], (None,))
        >>> A.m1(A(), 1, 2, 3)
        >>> get_calling_prototype(A().m1)
        (['a', 'b', 'c'], (None,))
        >>> get_calling_prototype(A.cm)
        (['a', 'b', 'c'], (None,))
        >>> get_calling_prototype(A().cm)
        (['a', 'b', 'c'], (None,))
        >>> get_calling_prototype(A.st)
        (['a', 'b', 'c'], (None,))
        >>> get_calling_prototype(A().st)
        (['a', 'b', 'c'], (None,))
        >>> get_calling_prototype(A())
        (['a', 'b', 'c'], (None,))



    """
    assert callable(acallable)
    if inspect.ismethod(acallable) or inspect.isfunction(acallable):
        args, vargs, vkwargs, defaults = inspect.getargspec(acallable)
    elif not inspect.isfunction(acallable) and hasattr(acallable, "__call__"):
        ## a class instance ? which is callable...
        args, vargs, vkwargs, defaults = inspect.getargspec(acallable.__call__)
        ## remove the 'self' argument
        args = args[1:]
    else:
        raise ValueError("Hum, %r is a callable, but not a function/method, "
                         "nor a instance with __call__ arg..."
                         % acallable)

    if vargs or vkwargs:
        raise SyntaxError("variable *arg or **kwarg are not supported.")

    if is_bound(acallable):
        args = args[1:]

    if defaults is None:
        defaults = ()  ## be coherent

    return args, defaults


def match_prototype(acallable, arguments):
    """Return tuple (pos args, kwargs) to call given callable

    Let's define a callable that will printout

    >>> arguments = {'alphonse': 1, 'bertrand': 2, 'charlie': 3}

    >>> match_prototype(lambda arguments: None, arguments)
    ([{'bertrand': 2, 'charlie': 3, 'alphonse': 1}], {})
    >>> match_prototype(lambda args: None, arguments)
    ([{'bertrand': 2, 'charlie': 3, 'alphonse': 1}], {})


    >>> match_prototype(lambda bertrand, arguments: None, arguments)
    ([2, {'charlie': 3, 'alphonse': 1}], {})

    >>> match_prototype(lambda bertrand, arguments, foo=None: None, arguments)
    ([2, {'charlie': 3, 'alphonse': 1}], {})

    >>> match_prototype(lambda bertrand, arguments, charlie=None: None,
    ...                 arguments)
    ([2, {'alphonse': 1}], {'charlie': 3})

    """

    args, defaults = get_calling_prototype(acallable)
    arguments = arguments.copy()
    defaults = [] if defaults is None else defaults
    p = []
    kw = {}

    pos_args = len(args) - len(defaults)
    has_args = any(k in ('args', 'arguments')
                   for k in args)
    args_label_pos = None
    for i, arg in enumerate(args):
        is_pos = i < pos_args
        val = None
        if not args_label_pos and arg in ('arguments', 'args'):
            val = arguments  ## copy by reference here is important
        else:
            k = None
            for k in arguments:
                norm = k
                if norm.startswith("--"):
                    if is_pos:
                        continue
                    norm = norm[2:]
                elif k.startswith("-"):
                    if is_pos:
                        continue
                    norm = norm[1:]
                norm = norm.lower()
                norm = norm.replace('-', '_')
                if norm == arg:
                    break
            else:
                if not has_args:
                    raise SyntaxError(
                        "Can't match your function argument %r with "
                        "command line keys (%s)."
                        % (arg, ", ".join(arguments.keys())))
                else:
                    k = None
            if k is not None:
                ## inplace removal is important here
                val = arguments.pop(k)
        if is_pos:
            p.append(val)
        else:
            if val is not None:
                ## we should only have strings if it was set.
                kw[arg] = val
    return p, kw


def manage_std_options(arguments, doc, version=None):

    if any(k == '--help' and v for k, v in arguments.items()):
        print(doc)
        exit(0)

    if any(k == '--version' and v for k, v in arguments.items()):
        print(doc)
        exit(0)
    if '--help' in arguments:
        arguments.pop('--help')
    if '--version' in arguments:
        arguments.pop('--version')


def register():
    try:
        ## Get callers module
        frm = inspect.stack()[1]
        frame, _, _, _, _, _ = frm
        obj = inspect.getmodule(frame)
    except:
        raise SyntaxError(
            "Couldn't infer caller's module. "
            "Please provide a compatible object as command.")
    if obj.__name__ == "__main__":
        exit(run(obj))
    else:
        obj.run = lambda: exit(run(obj))


def is_debug_mode(args):
    return args.get("--debug", False) or \
           os.environ.get("%s_DEBUG" % args["__env__"]["name"].upper(), False)


def run(obj=None, arguments=None):
    if obj is None:
        try:
            ## Get callers module
            frm = inspect.stack()[1]
            frame, _, _, _, _, _ = frm
            obj = inspect.getmodule(frame)
        except:
            raise SyntaxError(
                "Couldn't infer caller's module. "
                "Please provide a compatible object as command.")
    subcmds = get_subcmds(obj)
    if arguments is None:
        exname = kf.basename(sys.argv[0])
        name = kf.basename(exname, ['.py', '.pyc'])
        env = {"exname": exname, "name": name, "surcmd": exname}
    else:
        env = arguments["__env__"]

    doc = get_help(obj, env=env, subcmds=subcmds)

    if arguments is None:
        try:
            arguments = docopt(
                doc, version=getattr(obj, '__version__', False),
                options_first=True, help=False)
        except DocoptExit as e:
            msg.err("Invalid command line for %r" % env["surcmd"])
            raise e

    manage_std_options(arguments, doc)

    if arguments["help"]:
        command = arguments["COMMAND"]
        if command is None:
            print(doc)
        else:
            if command not in subcmds:
                print("Action %r not found." % command)
                exit(1)
            print(get_help_subcmd(command, subcmds[command], env))
        exit(0)

    assert "ACTION" in arguments
    action = arguments["ACTION"]

    if action not in subcmds:
        msg.err("Action '%s' does not exists." % action)
        print("Use `%(surcmd)s --help` to get full help." % env)
        exit(1)

    subcmd = subcmds[action]
    ## XXXvlab: this would be nice if only one doc would have worked,
    ## it might be possible but didn't have much time to dig
    docopt_doc = get_help_subcmd(action, subcmd, env, only_sub=True)
    real_doc = get_help_subcmd(action, subcmd, env)

    options_first = True if get_subcmds(subcmd) else False
    try:
        args = docopt(docopt_doc, argv=arguments["ARGS"], help=False,
                      version=getattr(subcmd, '__version__', False),
                      options_first=options_first)
    except DocoptLanguageError as e:
        msg.die("Doc syntax error %s, please check:\n%s"
                % (e.message, real_doc))
        exit(1)
    except DocoptExit:
        ## XXXvlab: hum we can't give the correct doc and have to
        ## do bad things to make it work. So I have to substitute
        ## the help printing message.
        msg.err("Invalid command line for command '%s %s'"
                % (env["surcmd"], action))
        print(get_help_subcmd(action, subcmd, env))
        exit(1)

    manage_std_options(args, real_doc)

    env = subcmd_env(env, action)
    args["__env__"] = env
    p, kw = match_prototype(subcmd, args)
    try:
        ret = subcmd(*p, **kw)
    except KeyboardInterrupt:
        if is_debug_mode(args):
            msg.err("Keyboard interrupt received while running '%s':"
                    % (env["surcmd"], ))
            print(format_last_exception(
                prefix=aformat(" | ", fg="black", attrs=["bold", ])))
        else:
            print()
            msg.err("Keyboard Interrupt. Bailing out.")
        exit(254)
    except Exception as e:  ## pylint: disable=broad-except
        if is_debug_mode(args):
            msg.err("Exception while running '%s':"
                    % (env["surcmd"], ))
            print(format_last_exception(
                prefix=aformat(" | ", fg="black", attrs=["bold", ])))
        else:
            message = "%s" % e
            msg.err(message)
        exit(255)
    exit(ret)
