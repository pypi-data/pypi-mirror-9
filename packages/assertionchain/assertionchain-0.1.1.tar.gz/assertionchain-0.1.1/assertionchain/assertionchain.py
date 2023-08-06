"""
AssertionChain is a utility for chaining together a series of related actions and checking their return values without
having to make a separate assertion each time.

>>> AssertionChain()\
    .do(lambda: 1 + 1, 'Add 1 and 1 together').expect(0, operator='>')\
    .do(lambda: 'my' + 'string', 'Concatenate strings').expect('mystring')\
    .perform()

Using this pattern encourages a developer to describe what each line is doing and what the expected result should be.

An example use case is in functional testing, where each step should provide a detailed debugging message if it fails.
AssertionChains allow the user to specify what the result of that function call should have been without adding a
verbose assertion after each line.
"""
from Queue import Queue


class ChainItem(object):
    """Represents an action to perform in the chain. The chain should store a queue of these items, which provide
    history and instructions for executing this step"""

    def __init__(self, item, flag, message, operator=None, *args, **kwargs):
        """
        :param item: The primary "item" of the event. For actions, this will be a function. For assertions, this
        will be a value
        :param flag: Flag is the identifier that signals what to do with this item. This will use the function object
        as a key (i.e. AssertionChain.expect or AssertionChain.do)
        :param message: The user-provided message to include with this step in the chain
        :param operator: Optional operator to use for assertion steps, such as '==', '!=', '<', etc.
        """
        self.item = item
        self.flag = flag
        self.message = message
        self.operator = operator
        self.args = args
        self.kwargs = kwargs


class AssertionChain(object):

    valid_operators = ('==', '!=', '>', '<', '>=', '<=', 'in', 'not in', 'is', 'is not')

    def __init__(self):
        self.items = Queue()

    def do(self, fn, message=None, *args, **kwargs):
        """Add a 'do' action to the steps. This is a function to execute

        :param fn: A function
        :param message: Message indicating what this function does (used for debugging if assertions fail)
        """
        self.items.put(ChainItem(fn, self.do, message, *args, **kwargs))
        return self

    def expect(self, value, message='Failed: "{actual} {operator} {expected}" after step "{step}"', operator='=='):
        """Add an 'assertion' action to the steps. This will evaluate the return value of the last 'do' step and
        compare it to the value passed here using the specified operator.

        Checks that the first function will return 2
        >>> AssertionChain().do(lambda: 1 + 1, 'add 1 + 1').expect(2)

        This will check that your function does not return None
        >>> AssertionChain().do(lambda: myfunction(), 'call my function').expect(None, operator='is not')

        :param value: The expected value
        :param message: The error message to raise if the assertion fails. You can access the variables:

            {actual} -- The actual value
            {expected} -- The expected value
            {step} -- The step just performed, which did not meet the expectation
            {operator} -- The operator used to make the comparison

        """
        if operator not in self.valid_operators:
            raise ValueError('Illegal operator specified for ')
        self.items.put(ChainItem(value, self.expect, message, operator=operator))
        return self

    def perform(self):
        """Runs through all of the steps in the chain and runs each of them in sequence.

        :return: The value from the lat "do" step performed
        """
        last_value = None
        last_step = None

        while self.items.qsize():

            item = self.items.get()

            if item.flag == self.do:
                last_value = item.item(*item.args, **item.kwargs)
                last_step = item.message
            elif item.flag == self.expect:
                message = item.message
                local = {'value': last_value, 'expectation': item.item}
                expression = 'value {operator} expectation'.format(operator=item.operator)
                result = eval(expression, local)

                # Format the error message
                format_vars = {
                    'actual': last_value,
                    'expected': item.item,
                    'step': last_step,
                    'operator': item.operator
                }

                for var, val in format_vars.iteritems():
                    message = message.replace('{' + str(var) + '}', str(val))

                assert result, message

        return last_value
