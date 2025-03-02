import random
import tempfile
from pathlib import Path

import genanki

from remember.config import Config
from remember.model import Flashcard

_model = genanki.Model(
    model_id=1893893968,  # hardcoded model ID, do not change
    name="reMember Model",
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


def write_package(config: Config, flashcards: list[Flashcard]) -> None:
    if config.deck_id is None:
        deck_id = random.randrange(1 << 30, 1 << 31)
        print(
            f"No deck ID supplied! Generated a new one: ‘{deck_id}’. "
            f"Ensure to save and supply it via ‘-i {deck_id}’ when altering this deck!"
        )
    else:
        deck_id = config.deck_id
    with tempfile.TemporaryDirectory() as tmp_dir_name:
        tmp_dir = Path(tmp_dir_name)
        media_files = []
        deck = genanki.Deck(deck_id, config.deck_name)
        for card in flashcards:
            front_file_path = tmp_dir / card.front_file_name
            back_file_path = tmp_dir / card.back_file_name
            card.front.save(front_file_path)
            card.back.save(back_file_path)
            media_files += [front_file_path.as_posix(), back_file_path.as_posix()]
            deck.add_note(
                genanki.Note(
                    model=_model,
                    fields=[
                        f'<img src="{card.front_file_name}">',
                        f'<img src="{card.back_file_name}">',
                    ],
                    guid=card.anki_guid,
                )
            )
        genanki.Package(deck, media_files).write_to_file(config.output_file)
