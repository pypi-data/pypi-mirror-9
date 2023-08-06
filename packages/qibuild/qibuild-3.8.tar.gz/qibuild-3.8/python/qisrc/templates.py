import os
import re

from qisys import ui
import qisys.sh
import qisrc.git

def process(input_dir, output_dir, **kwargs):
    ui.info(ui.green, "Generating code in", output_dir)
    for root, directories, filenames in os.walk(input_dir):
        rel_root = os.path.relpath(root, input_dir)
        if rel_root == ".":
            rel_root = ""
        for directory in directories:
            input_name = os.path.join(rel_root, directory)
            output_name = process_string(input_name, **kwargs)
            to_make = os.path.join(output_dir, output_name)
            qisys.sh.mkdir(to_make, recursive=True)
        for filename in filenames:
            input_name = os.path.join(rel_root, filename)
            output_name = process_string(input_name, **kwargs)
            output_path = os.path.join(output_dir, output_name)
            input_path = os.path.join(input_dir, input_name)
            qisys.sh.install(input_path, output_path, quiet=True)
            process_file(output_path, **kwargs)
            ui.info("*", output_name)

def process_file(file_path, **kwargs):
    with open(file_path, "r") as fp:
        contents = fp.read()
    to_write = process_string(contents, **kwargs)
    with open(file_path, "w") as fp:
        fp.write(to_write)

def process_string(string, **kwargs):
    res = string
    for key, value in kwargs.iteritems():
        old = key
        new = value
        res = magic_replace(res, old, new)
    return res

def magic_replace(string, old, new):
    res = string
    for func in snake_case, camel_case, upper_case, mixed_case, attached_lower, attached_upper:
        sub_old = "@%s@" % func(old)
        sub_new = func(new)
        res = res.replace(sub_old, sub_new)
    return res

def snake_case(string):
    """
    >>> snake_case("FooBar")
    'foo_bar'

    """
    splitted = split_chunks(string)
    res = "_".join(x.lower() for x in splitted)
    return res

def camel_case(string):
    """
    >>> camel_case("FooBar")
    'fooBar'

    """
    res = mixed_case(string)
    res = res[0].lower() + res[1:]
    return res

def upper_case(string):
    """
    >>> upper_case("FooBar")
    'FOO_BAR'

    """
    splitted = split_chunks(string)
    return "_".join(x.upper() for x in splitted)

def mixed_case(string):
    """
    >>> mixed_case("FooBar")
    'FooBar'
    >>> mixed_case("foo_bar")
    'FooBar'

    """
    splitted = split_chunks(string)
    return "".join(x.title() for x in splitted)


def attached_lower(string):
    """
    >>> attached_lower("FooBar")
    'foobar'
    """
    splitted = split_chunks(string)
    return "".join(x.lower() for x in splitted)

def attached_upper(string):
    """
    >>> attached_upper("FooBar")
    'FOOBAR'
    """
    splitted = split_chunks(string)
    return "".join(x.upper() for x in splitted)

def split_chunks(string):
    """
    >>> split_chunks("FooBar")
    ['Foo', 'Bar']
    >>> split_chunks("fooBar")
    ['foo', 'Bar']
    >>> split_chunks("foo_bar")
    ['foo', 'bar']

    """
    if "_" in string:
        return string.split("_")
    res = list()
    chunk = ""
    for c in string:
        if c.isupper():
            if chunk:
                res.append(chunk)
            chunk = c
        else:
            chunk += c
    if chunk:
        res.append(chunk)
    return res
