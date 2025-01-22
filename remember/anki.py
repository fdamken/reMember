import genanki

from remember.model import Flashcard

_model = genanki.Model(
    model_id=2125390554,
    name="reAnki Model",
    fields=[
        {"name": "QuestionMedia"},
        {"name": "AnswerMedia"},
    ],
    templates=[
        {
            "name": "Card 1",
            "qfmt": "{{QuestionMedia}}",
            "afmt": '{{QuestionMedia}}<hr id="answer">{{AnswerMedia}}',
        },
    ],
)


def to_note(card: Flashcard) -> genanki.Note:
    return genanki.Note(
        model=_model,
        fields=[
            f'<img src="{card.front_guid}-questions.png">',
            f'<img src="{card.front_guid}-answer.png">',
        ],
    )
