from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Generic, Self, Sequence
from .qanda import Numeric, Question, OpenRange, Response

from .json_serializable import JsonSerializable


class RangeBound(Enum):
    Lower = auto()
    Higher = auto()


class RangeError(Exception): ...


class SurveyError(Exception): ...


@dataclass
class Survey(JsonSerializable, Generic[Numeric]):
    questions: Sequence[Question]
    ranges: Sequence[OpenRange]

    def __post_init__(self) -> None:
        if len(self.questions) == 0:
            raise SurveyError("supply at least 1 question")
        if len(self.ranges) == 0:
            raise SurveyError("supply at least 1 range")
        self.ranges = sorted(self.ranges, key=lambda range_: range_.lower)
        self._check_ranges()

    def get_range(self, score: int) -> OpenRange:
        for range_ in self.ranges:
            if score in range_:
                return range_
        raise RangeError(
            "score falls out of question range",
            score,
        )

    def _check_ranges(self) -> bool:
        """
        Assumes that the ranges are sorted increasingly.

        Check that:
        1. the ranges cover the entire spectrum of the answers.
        2. the ranges are non-overlapping.
        """
        question_range = self._calculate_question_span(questions=self.questions)

        # First range should map to the lowest answers ...
        self._check_ranges_helper(
            range_=self.ranges[0],
            value=question_range.lower,
            range_bound=RangeBound.Lower,
        )
        # ... and the last range should map to the highest.
        # An OpenRange is exclusive at the higher end, making the higher bound
        # 1 larger than the actual largest value in the questions.
        self._check_ranges_helper(
            range_=self.ranges[-1],
            value=question_range.higher - 1,
            range_bound=RangeBound.Higher,
        )
        # For exactly 1 range no comparisons are needed (or possible, indexing wise).
        if len(self.ranges) > 1:
            previous = self.ranges[0]
            for i, range_ in enumerate(self.ranges[1:]):
                # TODO: should use one-based indexes?
                if range_.lower != previous.higher:
                    raise RangeError(f"Range {i} and {i + 1} are disconnected")
                previous = range_
        return True

    @classmethod
    def _check_ranges_helper(
        cls, range_: OpenRange, value: Numeric, range_bound: RangeBound
    ) -> None:
        """Raises a `RangeError` if `value` is not included in `range_`."""
        if not value in range_:
            match range_bound:
                case RangeBound.Lower:
                    k1, k2, attr = "Lowest", "low", "lower"
                case RangeBound.Higher:
                    k1, k2, attr = "Highest", "high", "higher"
                case _:
                    raise NotImplementedError(
                        "range_bound should be a RangeBound", range_bound
                    )
            raise RangeError(
                f"{k1} answer is {value} but the ranges only go as {k2} as {getattr(range_, attr)}"
            )

    @classmethod
    def _calculate_question_span(
        cls, questions: Sequence[Question]
    ) -> OpenRange:
        lower = 0
        # For a total maximal score of s, the loop will only add up to s.
        # We need to add a 1 because OpenRange is exclusive at the higher end.
        higher = 1
        for question in questions:
            range_ = question._get_response_range()
            lower += range_.lower
            higher += range_.higher
        return OpenRange(msg="", lower=lower, higher=higher)

    @classmethod
    def from_json(cls, json: dict[str, Any]) -> Self:
        """
        Parse a `dict` in `JSON` format to a class instance.
        """
        return Survey(
            questions=[
                Question.from_json(question) for question in json["questions"]
            ],
            ranges=[OpenRange.from_json(range_) for range_ in json["ranges"]],
        )


def make_dummy_survey() -> Survey:
    return Survey(
        questions=[
            Question(
                msg="question0",
                responses=[
                    Response(msg="response0", score=0),
                    Response(msg="response1", score=1),
                ],
            ),
            Question(
                msg="question1",
                responses=[
                    Response(msg="response2", score=2),
                    Response(msg="response3", score=3),
                ],
            ),
            Question(
                msg="question2",
                responses=[
                    Response(msg="response4", score=4),
                    Response(msg="response5", score=5),
                ],
            ),
        ],
        ranges=[
            OpenRange(msg="low", lower=0, higher=7),
            OpenRange(msg="medium", lower=7, higher=9),
            OpenRange(msg="high", lower=9, higher=10),
        ],
    )
