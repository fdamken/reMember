"use strict";

if (!window.reMember) {
    window.reMember = {};
}

class _Flashcard {
    constructor(front, back) {
        this.front = front;
        this.back = back;
        this.id = reMember.util.random_string(100);
    }

    switch() {
        [this.front, this.back] = [this.back, this.front];
    }

    get guid() {
        return ankiHash([this.id]);
    }

    get front_file_name() {
        return `${this.id}-front.png`;
    }

    get back_file_name() {
        return `${this.id}-back.png`;
    }
}

const _model = new Model({
    id: "1893893968",  // hardcoded model ID, do not change
    name: "reMember Model",
    flds: [
        {name: "QuestionMedia"},
        {name: "AnswerMedia"},
    ],
    req: [[0, "all", [0]]],
    tmpls: [{
        name: "Card 1",
        qfmt: "{{QuestionMedia}}",
        afmt: '{{QuestionMedia}}<hr id="answer">{{AnswerMedia}}',
    }]
});

window.reMember.anki = {
    Flashcard: _Flashcard,
    async write_to_package(config, flashcards) {
        const deck = new Deck(config.deck_id, config.deck_name);
        const images = []
        for (const card of flashcards) {
            deck.addNote(
                _model.note(
                    [
                        `<img src="${card.front_file_name}" alt="">`,
                        `<img src="${card.back_file_name}" alt="">`,
                    ],
                    [],
                    card.guid,
                )
            );
            images.push([card.front, card.front_file_name]);
            images.push([card.back, card.back_file_name]);
        }
        const anki_package = new Package();
        anki_package.addDeck(deck);
        for (const [image, name] of images) {
            const blob = await image.to_png_blob();
            anki_package.addMedia(blob, name);
        }
        await anki_package.writeToFile(config.package_name);
    },
}
