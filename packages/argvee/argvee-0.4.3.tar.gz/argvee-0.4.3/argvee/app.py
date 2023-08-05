#!/usr/bin/env python
import argparse
import inspect

class Application(object):
    ''' Contains all registered functions '''

    def __init__(self):
        ''' Create initial application empty state '''
        self.subs = {}
        self.funcs = {}
        self.parser = argparse.ArgumentParser()

    def cmd(self, *args, **kwargs):
        ''' Return a decorator which reads func args and kwargs '''
        if args and callable(args[0]) and hasattr(args[0], 'func_name'):
            return self.cmd(name=args[0].func_name)(args[0])
        elif args and isinstance(args[0], basestring):
            funcname = args[0]
        else:
            funcname = kwargs.get('name')
        def open_func(func):
            name = funcname or func.func_name
            sub = {}
            sub['help'] = inspect.getdoc(func)
            argspec = inspect.getargspec(func)
            len_args = 0 if argspec.args is None else len(argspec.args)
            len_kwargs = 0 if argspec.defaults is None else len(argspec.defaults)
            split = len_args - len_kwargs
            sub['args'] = argspec.args[:split]
            sub['kwargs'] = {}
            sub['varargs'] = argspec.varargs
            kwargs = argspec.args[split:]
            for i, arg in enumerate(kwargs):
                sub['kwargs'][arg] = argspec.defaults[i]
            if kwargs and sub['varargs'] is not None:
                raise NotImplementedError(
                    "Function %s: Invalid function arguments\n"
                    "varargs %s combined with kwargs won't work.\n"
                    "Instead, please fix function definition like so:\n"
                    "\n"
                    "    def %s(%s,%s=[],%s):\n        ...\n"
                    % (name, sub['varargs'], name, ','.join(sub['args']),
                        sub['varargs'], ','.join(
                        ['%s=%s' % pair for pair in sub['kwargs'].items()]
                )))
            sub['func'] = func
            self.subs[name] = sub
            return func
        return open_func

    def parse_args(self):
        ''' Parse arguments and run desired command '''
        args = self.parser.parse_args()
        if len(self.subs) == 1 and 'main' in self.subs:
            cmd = 'main'
        else:
            cmd = args.cmd
        sub = self.subs[cmd]
        func = sub['func']
        fargs = [getattr(args, attr) for attr in sub['args']]
        if sub['varargs'] is not None:
            fargs += getattr(args, sub['varargs'])
        # Removed dict comprehension for 2.6 compatibility.
        fkwargs = {}
        for kwarg in sub['kwargs']:
            fkwargs[kwarg] = getattr(args, kwarg)
        return func(*fargs, **fkwargs)

    def __create_parsers(self):
        ''' Create subparsers for commands '''
        # Maps name of command to metadata
        parsers = {}
        if len(self.subs) == 1 and 'main' in self.subs:
            # add arguments to ArgumentParser for main function
            parsers['main'] = self.parser
        else:
            subparsers = self.parser.add_subparsers(dest='cmd')
            # create sub parsers
            for sub in self.subs:
                parsers[sub] = subparsers.add_parser(
                    sub, help=self.subs[sub]['help'])
        return parsers

    def __add_kwarg(self, parser, kwargs, default):
        if default is True:
            parser.add_argument(*kwargs, action='store_false')
        elif default is False:
            parser.add_argument(*kwargs, action='store_true')
        elif isinstance(default, int):
            parser.add_argument(*kwargs, default=default,
                type=int)
        elif isinstance(default, float):
            parser.add_argument(*kwargs, default=default,
                type=float)
        elif isinstance(default, list):
            parser.add_argument(*kwargs, default=default,
                nargs='*')
        else:
            parser.add_argument(*kwargs, default=default)

    def __load_arguments(self, parsers):
        ''' Load arguments into subparsers '''
        # Build subparser arguments
        for parser_name, parser in parsers.items():
            sub = self.subs[parser_name]
            for arg in sub['args']:
                parser.add_argument(arg)
            if sub['varargs'] is not None:
                parser.add_argument(sub['varargs'], nargs='+')
            shortnames = set()
            for kwarg, default in sub['kwargs'].items():
                kwarg_name = '--%s' % kwarg.replace('_', '-')
                short = '-%s' % kwarg[0]
                if short in shortnames:
                    short = short.swapcase()
                if short in shortnames:
                    kwargs = [kwarg_name]
                else:
                    kwargs = [kwarg_name, short]
                    shortnames.add(short)
                self.__add_kwarg(parser, kwargs, default)

    def run(self):
        ''' Build parsers and get args '''
        if len(self.subs) == 0:
            return
        parsers = self.__create_parsers()
        self.__load_arguments(parsers)
        return self.parse_args()

