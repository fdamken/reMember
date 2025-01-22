# reMember

This is a proof-of-concept to take images, cut them into flashcards, and export
them into an Anki deck. The idea is first-class support for notes taken on a
reMarkable tablet since writing notes by hand greatly improves retention.
However, Anki is a such a great tool for learning things, and I wanted to have
both without doubling the work of creating flashcards.

This tool takes in a PNG import from the reMarkable and detects manually placed
lines in the document for separating flashcards. Subsequently, the document is
cut accordingly and an Anki package is exported. See, e.g., [test.png] for an
example document that can be processed along with the Anki package [test.apkg]
for the Anki package resulting from running `python remember -mt 0 test.png`.
The `-mt 0` configures reMember to not assume a margin at the top of the page.
By default, it assumes a margin to support documents such as [page1.png].

**Note that this software is proof-of-concept and not yet ready for everyday
use. In particular, it is tricky to get it running etc. I plan to increase
usability in the future, but for now, I have to actually use it for studying.**
