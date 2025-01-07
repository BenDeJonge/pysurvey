import unittest
from itertools import chain
from math import inf

from pysurvey import (
    OpenRange,
    Question,
    RangeError,
    Response,
    Survey,
    SurveyError,
)


class TestSurvey(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.n_questions = 5
        cls.n_answers_per_question = tuple(range(1, 1 + cls.n_questions))

        cls.questions = [
            Question(
                msg=f"question{i}",
                responses=[
                    Response(
                        msg=f"response{j}",
                        score=j,
                    )
                    for j in range(cls.n_answers_per_question[i])
                ],
            )
            for i in range(cls.n_questions)
        ]

        # There are n questions. The i-th questions has i + 1 answers, scoring 0 to i.
        # The mimimum score is 0, picking the 0-scored (first) answer for all questions.
        # The maximum score is 0 + 1 + 2 + ... + n - 1, which is sum(range(n)).
        # However, an OpenRange is exclusive at the higher end, so we add 1.
        cls.response_range = OpenRange(
            msg="",
            lower=0,
            higher=sum(range(cls.n_questions)) + 1,
        )
        cls.middle = (cls.response_range.lower + cls.response_range.higher) // 2
        cls.ranges = [
            OpenRange(
                msg="range0",
                lower=cls.response_range.lower,
                higher=cls.middle,
            ),
            OpenRange(
                msg="range1",
                lower=cls.middle,
                higher=cls.response_range.higher,
            ),
        ]

    # T E S T   L O G I C
    # -----------------------------------
    def test_private_calculate_question_span(self):
        self.assertEqual(
            self.response_range, Survey._calculate_question_span(self.questions)
        )

    def test_get_range_ok(self):
        survey = Survey(questions=self.questions, ranges=self.ranges)
        for i in range(self.response_range.lower, self.middle):
            self.subTest(self.assertEqual(self.ranges[0], survey.get_range(i)))
        for i in range(self.middle, self.response_range.higher - 1):
            self.subTest(self.assertEqual(self.ranges[1], survey.get_range(i)))

    def test_get_range_not_ok(self):
        survey = Survey(questions=self.questions, ranges=self.ranges)
        for i in chain(
            (-inf, -5, -1),
            (self.response_range.higher, self.response_range.higher + 3),
        ):
            self.subTest(self.assertRaises(RangeError, survey.get_range, i))

    # T E S T   I N S T A N T I A T I O N
    # -----------------------------------
    def test_ranges_match(self):
        try:
            Survey(questions=self.questions, ranges=self.ranges)
        except Exception as e:
            self.fail(e)

    def test_empty_inputs(self):
        self.assertRaises(
            SurveyError,
            lambda: Survey(questions=[], ranges=[self.response_range]),
        )
        self.assertRaises(
            SurveyError,
            lambda: Survey(questions=self.questions, ranges=[]),
        )

    def test_incomplete_coverage_single(self):
        # Higher end is too low.
        self.assertRaises(
            SurveyError,
            lambda: Survey(
                questions=[],
                ranges=[
                    OpenRange(
                        msg="",
                        lower=self.response_range.lower,
                        higher=self.response_range.higher - 1,
                    )
                ],
            ),
        )
        self.assertRaises(
            SurveyError,
            lambda: Survey(
                questions=[],
                ranges=[
                    OpenRange(
                        msg="",
                        lower=-inf,
                        higher=self.response_range.higher - 1,
                    )
                ],
            ),
        )
        # Lower end is too high.
        self.assertRaises(
            SurveyError,
            lambda: Survey(
                questions=[],
                ranges=[
                    OpenRange(
                        msg="",
                        lower=self.response_range.lower + 1,
                        higher=self.response_range.higher,
                    )
                ],
            ),
        )
        self.assertRaises(
            SurveyError,
            lambda: Survey(
                questions=[],
                ranges=[
                    OpenRange(
                        msg="",
                        lower=self.response_range.lower + 1,
                        higher=inf,
                    )
                ],
            ),
        )
        # Both ends are insufficient.
        self.assertRaises(
            SurveyError,
            lambda: Survey(
                questions=[],
                ranges=[
                    OpenRange(
                        msg="",
                        lower=self.response_range.lower + 1,
                        higher=self.response_range.higher - 1,
                    )
                ],
            ),
        )

    def test_incomplete_coverage_multiple(self):
        # Higher is too low.
        self.assertRaises(
            SurveyError,
            lambda: Survey(
                questions=[],
                ranges=[
                    OpenRange(
                        msg="",
                        lower=self.response_range.lower,
                        higher=self.middle,
                    ),
                    OpenRange(
                        msg="",
                        lower=self.middle,
                        higher=self.response_range.higher - 1,
                    ),
                ],
            ),
        )
        # Lower is too high.
        self.assertRaises(
            SurveyError,
            lambda: Survey(
                questions=[],
                ranges=[
                    OpenRange(
                        msg="",
                        lower=self.response_range.lower + 1,
                        higher=self.middle,
                    ),
                    OpenRange(
                        msg="",
                        lower=self.middle,
                        higher=self.response_range.higher,
                    ),
                ],
            ),
        )
        # Both are insufficient.
        self.assertRaises(
            SurveyError,
            lambda: Survey(
                questions=[],
                ranges=[
                    OpenRange(
                        msg="",
                        lower=self.response_range.lower + 1,
                        higher=self.middle,
                    ),
                    OpenRange(
                        msg="",
                        lower=self.middle,
                        higher=self.response_range.higher - 1,
                    ),
                ],
            ),
        )

    def test_incomplete_coverage_disconnected(self):
        self.assertRaises(
            SurveyError,
            lambda: Survey(
                questions=[],
                ranges=[
                    OpenRange(
                        msg="",
                        lower=self.response_range.lower,
                        higher=self.middle,
                    ),
                    OpenRange(
                        msg="",
                        lower=self.middle + 1,
                        higher=self.response_range.higher,
                    ),
                ],
            ),
        )


if __name__ == "__main__":
    unittest.main()
