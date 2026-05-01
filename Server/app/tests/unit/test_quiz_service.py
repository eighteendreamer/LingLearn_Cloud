from dataclasses import dataclass

from app.modules.quiz.service import QuizService


@dataclass
class OptionStub:
    id: int
    option_text: str
    vote_count: int
    is_correct: bool


def test_quiz_options_hide_correct_answer_before_submission() -> None:
    options = [
        OptionStub(id=1, option_text="A", vote_count=3, is_correct=True),
        OptionStub(id=2, option_text="B", vote_count=1, is_correct=False),
    ]

    response = QuizService._build_options(options, total_votes=4, reveal_correct=False)

    assert response[0].percent == 75.0
    assert response[0].is_correct is None


def test_quiz_options_reveal_correct_answer_after_submission() -> None:
    options = [
        OptionStub(id=1, option_text="A", vote_count=0, is_correct=True),
        OptionStub(id=2, option_text="B", vote_count=0, is_correct=False),
    ]

    response = QuizService._build_options(options, total_votes=0, reveal_correct=True)

    assert response[0].percent == 0.0
    assert response[0].is_correct is True
    assert response[1].is_correct is False
