AssertionChain
=============

[![Build Status](https://travis-ci.org/justiniso/AssertionChain.svg)](https://travis-ci.org/justiniso/AssertionChain) [![Coverage Status](https://coveralls.io/repos/justiniso/AssertionChain/badge.svg?branch=master)](https://coveralls.io/r/justiniso/AssertionChain?branch=master)

An AssertionChain is a wrapper for a group of commands that must happen in sequence.

Installation:

    pip install assertionchain

Features:

- Control order of execution of a group of functions
- Terminate execution of the rest of the chain if certain conditions are not met

Simple example:

    AssertionChain()\
        .do(lambda: 1 + 1, 'Add two numbers together') \
        .expect(3, message='Step "{step}" did not result in expected value {expected}, value was: {actual}') \
        .perform()

This is roughly equivalent to:

    val = 1 + 1
    assert val == 3

The above example is certainly more readable, so why use an AssertionChain at all? For starters, the chain
encourages the user to provide line-by-line detail about each step being executed. So if you want to understand
why the above assertion failed, you would have to construct a detailed error message indicating the actual and
expected value along with the step that produced the actual value. That's not particularly hard:

    expected = 3
    val = 1 + 1
    message = 'Adding 1 + 1 did not result in expected value {expected}, value was: {actual}'.format(
        expected=expected,
        actual=val
    )
    assert val == expected, message

But having to repeat this every time you run a command can become very, very tedious. AssertionChain provides this
API for performing incremental checks on each operation being executed in the chain, reducing the overhead of having
to type all of this out.

It is a simple utility for grouping related actions and ensuring each step succeeds. For instance, assume we have a
suite of functions that interact with files (get_contents, write_contents, delete_file). Their contract stipulates
that each function will return True, False, or a value depending on whether or not they were successful. We can use an
AssertionChain to make sure each step was successful:

    filename = '/tmp/sd9x0c2'
    new_contents = 'myfile'

    # Write the file, retrieve the contents
    contents = AssertionChain()\
        .do(lambda: get_contents(filename), 'Retrieve file contents').expect(False, operator='is not')\
        .do(lambda: write_contents(filename, new_contents), 'Write file content').expect(True, operator='is')\
        .do(lambda: write_contents(filename, ''), 'Write empty file content').expect(True, operator='is')\
        .perform()

    # Delete the file
    AssertionChain().do(lambda: delete_file(filename), 'Delete file').expect(True, operator='is').perform()
