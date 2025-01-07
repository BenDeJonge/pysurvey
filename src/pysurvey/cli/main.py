from typing import Any, Sequence
import pysurvey


class ParsingError(Exception): ...


def validate(input: str, expected: Sequence[Any]):
    try:
        type_ = type(expected[0])
        typed = type_(input)
    except ValueError:
        raise ParsingError("could not convert input to type", input, type_)
    if any(val == typed for val in expected):
        return typed
    raise ParsingError("input differs from expected", input, expected)


def format_message(
    message: pysurvey.HasMessage, i: int, one_based_index: bool, sep: str
):
    print(i + one_based_index, sep, message.msg)


def display_messages(
    messages: Sequence[pysurvey.HasMessage],
    one_based_index: bool = True,
    sep: str = " - ",
) -> None:
    for i, message in enumerate(messages):
        format_message(
            message=message, i=i, one_based_index=one_based_index, sep=sep
        )


def display_question(
    question: pysurvey.Question,
    i: int,
    one_based_index: bool = True,
    sep: str = " - ",
):
    format_message(
        message=question, i=i, one_based_index=one_based_index, sep=sep
    )
    display_messages(
        messages=question.responses, one_based_index=one_based_index, sep=sep
    )


def survey(survey: pysurvey.Survey, one_based_index: bool = True, sep="-"):
    score = 0
    for i, question in enumerate(survey.questions):
        input_ = None
        while input_ is None:
            display_question(
                question=question, i=i, one_based_index=one_based_index, sep=sep
            )
            try:
                input_ = validate(
                    input=input("> "),
                    expected=[
                        i + one_based_index
                        for i in range(len(question.responses))
                    ],
                )
            except ParsingError:
                continue
        score += question.responses[input_ - one_based_index].score
    print("Your result:", survey.get_range(score=score).msg)


def main():
    survey_ = pysurvey.Survey.read_json("./resources/quiz_01.json")
    survey(survey=survey_)


if __name__ == "__main__":
    main()
