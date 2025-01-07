import unittest
from itertools import chain
from math import inf
from typing import TypeVar

from pysurvey import OpenRange

_RangeBoundClosed = TypeVar("_RangeBoundClosed", bound=tuple[int, int])
_RangeBoundOpen = TypeVar(
    "_RangeBoundOpen", bound=tuple[int | float, int | float]
)


class TestOpenRange(unittest.TestCase):
    BEYOND_LOWER = 0
    LOWER = 5
    HIGHER = 10
    BEYOND_HIGHER = 15

    def _test_contains_helper(
        self,
        result_bound: _RangeBoundOpen,  # type: ignore
        too_low_bound: _RangeBoundClosed,
        correct_bound: _RangeBoundClosed,
        too_high_bound: _RangeBoundClosed,
    ):
        range_ = OpenRange(
            msg="", lower=result_bound[0], higher=result_bound[1]
        )
        too_low = range(*too_low_bound)
        correct = range(*correct_bound)
        too_high = range(*too_high_bound)
        for value in chain(too_low, too_high):
            self.assertFalse(
                value in range_, msg=f"value {value} should be out"
            )
        for value in correct:
            self.assertTrue(value in range_, msg=f"value {value} should be in")

    def test_contains_closed(self) -> None:
        """
        ```
        <----------------|================|---------------->
        BEYOND_LOWER     LOWER       HIGHER    BEYOND_HIGHER

        -: False
        =: True
        ```
        """
        self._test_contains_helper(
            result_bound=(self.LOWER, self.HIGHER),
            too_low_bound=(self.BEYOND_LOWER, self.LOWER),
            correct_bound=(self.LOWER, self.HIGHER),
            too_high_bound=(self.HIGHER, self.BEYOND_HIGHER),
        )

    def test_contains_open_lower(self) -> None:
        """
        ```
        <================|================|---------------->
        BEYOND_LOWER     LOWER       HIGHER    BEYOND_HIGHER

        -: False
        =: True
        ```
        """
        self._test_contains_helper(
            result_bound=(-inf, self.HIGHER),
            too_low_bound=(0, 0),
            correct_bound=(self.BEYOND_LOWER, self.HIGHER),
            too_high_bound=(self.HIGHER, self.BEYOND_HIGHER),
        )

    def test_contains_open_higher(self) -> None:
        """
        ```
        <----------------|================|================>
        BEYOND_LOWER     LOWER       HIGHER    BEYOND_HIGHER

        --: False
        ==: True
        ```
        """
        self._test_contains_helper(
            result_bound=(self.LOWER, inf),
            too_low_bound=(self.BEYOND_LOWER, self.LOWER),
            correct_bound=(self.LOWER, self.BEYOND_HIGHER),
            too_high_bound=(0, 0),
        )

    def test_contains_open_lower_higher(self) -> None:
        """
        ```
        <================|================|================>
        BEYOND_LOWER     LOWER       HIGHER    BEYOND_HIGHER

        -: False
        =: True
        ```
        """
        self._test_contains_helper(
            result_bound=(-inf, inf),
            too_low_bound=(0, 0),
            correct_bound=(self.BEYOND_LOWER, self.BEYOND_HIGHER),
            too_high_bound=(0, 0),
        )


if __name__ == "__main__":
    unittest.main()
