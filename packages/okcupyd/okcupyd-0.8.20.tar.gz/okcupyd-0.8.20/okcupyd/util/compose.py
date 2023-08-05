import collections
import functools

from .currying import curry

def _compose2(f, g):
    return lambda *args, **kwargs: f(g(*args, **kwargs))


@curry(evaluation_checker=curry.count_evaluation_checker(2))
def compose_with_joiner(joiner, *functions):
    return functools.reduce(joiner, functions)


compose_one_arg = compose_with_joiner(_compose2)


compose = compose_with_joiner(lambda f, g: _compose2(make_single_arity(f),
                                                force_args_return(g)))

def make_single_arity(function):
    @functools.wraps(function)
    def wrapped(args):
        return function(*args)
    return wrapped


def force_args_return(function):
    @functools.wraps(function)
    def wrapped(*args, **kwargs):
        value = function(*args, **kwargs)
        if not isinstance(value, collections.Iterable):
            value = (value,)
        return value
    return wrapped


def tee(*functions):
    def wrapped(*args, **kwargs):
        return tuple(function(*args, **kwargs) for function in functions)
    return wrapped
