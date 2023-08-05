# -*- coding: utf-8 -*-

__author__ = 'Ben Lopatin'
__email__ = 'ben@wellfire.co'
__version__ = '0.1.0'


import importlib
from unittest.mock import patch


def mock_decorator(*a, **k):
    """
    An 'empty' decorator that returns the underlying function.

    """
    # This is a decorator without parameters, e.g.
    #
    # @login_required
    # def some_view(request):
    #     ...
    #
    if a:
        if callable(a[0]):
            def wrapper(*args, **kwargs):
                return a[0](*args, **kwargs)
            return wrapper

    # This is a decorator with parameters, e.g.
    #
    # @render_template("index.html")
    # def some_view(request):
    #     ...
    #
    def real_decorator(function):
        def wrapper(*args, **kwargs):
            return function(*args, **kwargs)
        return wrapper
    return real_decorator


def tinsel(to_patch, module_name):
    """
    Decorator for simple in-place decorator mocking for tests

    :param to_patch: string path of the function to patch
    :param module_name: complete string path of the module to reload
    :return:
    """
    def decorator(function):
        def wrapper(*args, **kwargs):
            with patch(to_patch, mock_decorator):
                m = importlib.import_module(module_name)
                importlib.reload(m)
                function(*args, **kwargs)

            importlib.reload(m)
        return wrapper
    return decorator

