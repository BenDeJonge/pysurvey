from dataclasses import field
from typing import Optional
from .survey import Survey
from .json_serializable import JsonSerializable


class Respondee(JsonSerializable):
    name: Optional[str] = None
    age: Optional[int] = None
    adress: Optional[str] = None
    email: Optional[str] = None
    telephone: Optional[str] = None


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


def save_repondee_answers(path: str, respondee_survey: RespondeeSurvey) -> None:
    respondee_survey.write_json(path=path)
