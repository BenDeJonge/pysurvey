from dataclasses import dataclass, field
from typing import Any, Optional, Self
from .survey import Survey
from .json_serializable import JsonSerializable


@dataclass
class Respondee(JsonSerializable):
    name: Optional[str] = None
    age: Optional[int] = None
    adress: Optional[str] = None
    email: Optional[str] = None
    telephone: Optional[str] = None

    @classmethod
    def from_json(cls, json: dict[str, Any]) -> Self:
        """
        Parse a `dict` in `JSON` format to a class instance.
        """
        return Respondee(
            name=json["name"],
            age=json["age"],
            adress=json["address"],
            email=json["email"],
            telephone=json["telephone"],
        )


@dataclass
class RespondeeSurvey(JsonSerializable):
    respondee: Respondee
    survey: Survey
    responses: list[int]
    score: int = field(init=False)

    def __post_init__(self):
        score = 0
        for response, question in zip(
            self.responses, self.survey.questions, strict=True
        ):
            assert 0 <= response < len(question.responses)
            score += question.responses[response].score
        self.score = score

    @classmethod
    def from_json(cls, json: dict[str, Any]) -> Self:
        """
        Parse a `dict` in `JSON` format to a class instance.
        """
        return RespondeeSurvey(
            respondee=Respondee.from_json(json["respondee"]),
            survey=Survey.from_json(json["survey"]),
            responses=json["responses"],
        )


def save_repondee_answers(path: str, respondee_survey: RespondeeSurvey) -> None:
    respondee_survey.write_json(path=path)
