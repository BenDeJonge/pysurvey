import unittest
import os
from pysurvey import OpenRange, Question, Response, Survey


# TODO:
# - msgspec.ValidationError: invalid json file with totally different data
# - SurveyError: survey json that is invalid because of questions or ranges
class TestDataSerialization(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.path = os.path.splitext(__file__)[0] + ".json"

        cls.survey = Survey(
            questions=[
                Question(
                    msg="How are you doing?",
                    responses=[
                        Response(msg="Good", score=5),
                        Response(msg="Ok", score=3),
                        Response(msg="Bad", score=1),
                    ],
                ),
                Question(
                    msg="Have you slept more than 7 hours?",
                    responses=[
                        Response(msg="Yes", score=5),
                        Response(msg="No", score=1),
                    ],
                ),
            ],
            ranges=[
                OpenRange(
                    msg="Unhealthy",
                    lower=2,
                    higher=4,
                ),
                OpenRange(
                    msg="Medium healthy",
                    lower=4,
                    higher=8,
                ),
                OpenRange(msg="Very healthy", lower=8, higher=11),
            ],
        )

    def test_to_and_from_json(self):
        self.survey.write_json(path=self.path)
        read = Survey.read_json(path=self.path)
        self.assertEqual(self.survey, read)

    @classmethod
    def tearDownClass(cls) -> None:
        os.remove(path=cls.path)


if __name__ == "__main__":
    unittest.main()
