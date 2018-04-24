from typing import Iterable


class Definition:
    def __init__(self, word: str, definition: str):
        self.word = word
        self.definition = definition
        self.alternatives = []
        self.is_linked = None

    def add_alternative_definition(self, alternative: str):
        self.alternatives.append(alternative)

    def add_alternative_definitions(self, alternatives: Iterable[str]):
        self.alternatives.extend(alternatives)

    def __str__(self):
        return 'Word: {}, definition: {}, alternatives: {}'.format(self.word, self.definition, self.alternatives)

    def __repr__(self):
        return str(self)