"""`qanda`: q&a, question and answer"""

from dataclasses import dataclass
from math import inf
from typing import Any, Generic, Protocol, Self, Sequence, TypeVar

from .json_serializable import JsonSerializable


Numeric = TypeVar("Numeric", bound=int | float)


class QuestionError(Exception): ...


class HasMessage(Protocol):
    msg: str


@dataclass
class OpenRange(JsonSerializable, Generic[Numeric]):
    """
    Behaves like a `range`: inclusive at lower end, exclusive at higher end.

    Can let `lower` or `higher` to `-inf` or `inf` for open-ended ranges.
    """

    msg: str
    lower: Numeric
    higher: Numeric

    # def __init__(self, msg: str, lower: Numeric, higher: Numeric):
    #     self.msg = msg
    #     self.lower = lower
    #     self.higher = higher

    def __contains__(self, item: Numeric) -> bool:
        return self.lower <= item < self.higher

    @classmethod
    def from_json(cls, json: dict[str, Any]) -> Self:
        """
        Parse a `dict` in `JSON` format to a class instance.
        """
        return OpenRange(
            msg=json["msg"],
            lower=json["lower"],
            higher=json["higher"],
        )


@dataclass
class Response(JsonSerializable, Generic[Numeric]):
    msg: str
    score: Numeric

    # def __init__(self, msg: str, score: Numeric):
    #     self.msg = msg
    #     self.score = score

    def __lt__(self, other: Self) -> bool:
        return self.score < other.score

    def __gt__(self, other: Self) -> bool:
        return other < self

    def __eq__(self, other: Self) -> bool:
        return self.score == other.score

    @classmethod
    def from_json(cls, json: dict[str, Any]) -> Self:
        """
        Parse a `dict` in `JSON` format to a class instance.
        """
        return Response(
            msg=json["msg"],
            score=json["score"],
        )


@dataclass
class Question(JsonSerializable):
    msg: str
    responses: Sequence[Response]
    # def __init__(self, msg: str, responses: Sequence[Response]):
    #     self.msg = msg
    #     self.responses = responses

    def __post_init__(self):
        if len(self.responses) == 0:
            raise QuestionError("supply at least 1 response")

    def _get_response_range(self) -> OpenRange:
        lower = inf
        higher = -inf
        for response in self.responses:
            lower = min(response.score, lower)
            higher = max(response.score, higher)
        return OpenRange(msg="", lower=lower, higher=higher)

    @classmethod
    def from_json(cls, json: dict[str, Any]) -> Self:
        """
        Parse a `dict` in `JSON` format to a class instance.
        """
        return Question(
            msg=json["msg"],
            responses=[
                Response.from_json(response) for response in json["responses"]
            ],
        )
