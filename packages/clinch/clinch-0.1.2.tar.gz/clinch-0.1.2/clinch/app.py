import argparse
import inspect

from .arg import Argument

class Application(object):
    def __init__(self, name=None, usage=None, description=None):
        self.name = name

        self._parser = argparse.ArgumentParser(prog=name,
                                               usage=usage,
                                               description=description)
        self._subparsers = self._parser.add_subparsers(dest='_command')

    def command(self, description=None):
        def register(fn):
            argspec = inspect.getfullargspec(fn)
            parser = self._subparsers.add_parser(fn.__name__)
            parser.set_defaults(_impl=fn)

            for arg_name, arg_annotation in read_annotations(fn):
                if arg_annotation.is_option:
                    arg_kwargs = dict(arg_annotation.kwargs, dest=arg_name)
                else:
                    assert arg_name == arg_annotation.names[0]
                    arg_kwargs = arg_annotation.kwargs

                parser.add_argument(*arg_annotation.names, **arg_kwargs)

            return fn

        return register

    def parse(self, argv=None):
        return self._parser.parse_args(argv)

    def run(self, argv=None):
        args = self.parse(argv)
        fn = args._impl

        kwargs = {arg_name: getattr(args, arg_name)
                  for arg_name, _ in read_annotations(fn)}

        return fn(**kwargs)

    def __repr__(self):
        return '<%s%s>' % (type(self).__name__,
                           ' %s' % self.name if self.name else '')

def read_annotations(fn):
    argspec = inspect.getfullargspec(fn)
    args = []

    for arg in argspec.args:
        ann = argspec.annotations.get(arg)

        if isinstance(ann, Argument):
            args.append((arg, ann))

    return args
