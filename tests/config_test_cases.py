"""
Boolean indicating whether to overwrite the test cases.
"""
from typing import Final


TEST_CASES_CONFIG_REWRITE_EXPECTED_OUTPUT: Final[bool] = False
"""
Used during development to overwrite the expected test case responses.
True if the tests should overwrite the responses. False, read the existing
expected test case response. See the unit tests for more information.
"""
