import unittest
from assertionchain.assertionchain import AssertionChain


# Some helper functions
def return_true():  return True
def return_false(): return False
def return_one():  return 1


class TestAssertionChain(unittest.TestCase):

    def test_case_assert_all_valid_operators(self):
        """Tests all valid operators"""

        # All cases listed here. Key is the operator, value is tuple of (function to call, pass case, failure case)
        cases = {
            '==': (return_one, 1, 0),
            '!=': (return_one, 0, 1),
            '>': (return_one, 0, 2),
            '>=': (return_one, 0, 2),
            '<': (return_one, 2, 0),
            '<=': (return_one, 2, 0),
            'is': (return_true, True, False),
            'is not': (return_true, False, True),
            'in': (lambda: 'A', 'ABC', 'XYZ'),
            'not in': (lambda: 'X', 'ABC', 'XYZ'),

        }

        for operator, value in cases.iteritems():
            function = value[0]
            pass_value = value[1]
            fail_value = value[2]

            # Pass case
            AssertionChain().do(function).expect(pass_value, operator=operator).perform()

            # Failure case
            try:
                AssertionChain().do(function).expect(fail_value, operator=operator).perform()
            except AssertionError:
                pass
            else:
                assert False, 'No exception raised for failure case on operator: {}'.format(operator)

    def test_case_invalid_operators(self):
        """Tests that passing an invalid operator throws a usage error"""
        try:
            AssertionChain().do(return_one).expect(1, operator='=-')
        except ValueError:
            pass
        else:
            assert False, 'No exception raised using invalid operator in an assertion step'

    def test_case_assertion_message_replace(self):
        """Tests building the assertion failure message variables replaces the correct variables"""
        try:
            AssertionChain()\
                .do(lambda: False, 'step')\
                .expect(True, operator='is', message='{actual}-{expected}-{step}-{operator}')
        except AssertionError, e:
            expected_message = 'False-True-step-is'
            assert e.message == expected_message, \
                'Error {e} did not have the expected error message {message}'.format(
                    e=e,
                    message=expected_message
                )

    def test_case_function_call_with_args(self):
        """Tests that you can call a "do" function with args"""
        value = AssertionChain().do(lambda x, y: x + y, 'no message', x=1, y=2).perform()
        assert value == 3

    def test_case_no_items_in_chain(self):
        """Tests the AssertionChain does not fail if it has no items"""
        val = AssertionChain().perform()
        assert val is None

    def test_case_reuse_instance(self):
        """Tests that an instance of assertion chain can be reused (empties the queue after it is performed)"""
        chain = AssertionChain()

        chain.do(lambda: 1+1).expect(2)
        chain.perform()

        assert chain.items.qsize() == 0, 'Chain did not empty the queue after perform step'

        chain.do(lambda: 1+1).expect(2)
        chain.perform()