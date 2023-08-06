#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test suite for language_check."""

import unittest
import warnings
from collections import namedtuple

import language_check


class TestLanguageTool(unittest.TestCase):

    CheckTest = namedtuple('CheckTest', ('text', 'matches'))
    Match = namedtuple('Match', ('fromy', 'fromx', 'ruleId'))

    check_tests = {
        'en': [
            CheckTest(
                ('Paste your own text here... or check this text too see '
                 'a few of the problems that that LanguageTool can detect. '
                 'Did you notice that their is no spelcheckin included?'),
                [
                    Match(0, 47, 'TOO_TO'),
                    Match(0, 132, 'THEIR_IS'),
                ]
            ),
        ],
        'fr': [
            CheckTest(
                ('Se texte est un exemple pour pour vous montrer '
                 'le fonctionnement de LanguageTool. '
                 'notez que LanguageTool ne comporte pas '
                 'de correcteur orthographique.'),
                [
                    Match(0, 0, 'SE_CE'),
                    Match(0, 3, 'TE_NV'),
                    Match(0, 24, 'FRENCH_WORD_REPEAT_RULE'),
                    Match(0, 82, 'UPPERCASE_SENTENCE_START'),
                ]
            ),
            CheckTest(
                'je me rappelle de tout sans aucun soucis!',
                [
                    Match(0, 0, 'UPPERCASE_SENTENCE_START'),
                    Match(0, 6, 'RAPPELER_DE'),
                    Match(0, 28, 'ACCORD_NOMBRE'),
                    Match(0, 34, 'FRENCH_WHITESPACE'),
                ]
            ),
        ],
    }

    correct_tests = {
        'en-US': {
            'that would of been to impressive.':
            'That would have been too impressive.',
        },
        'fr': {
            'il monte en haut si il veut.':
            'Il monte s’il veut.',
        },
    }

    def setUp(self):
        self.lang_check = language_check.LanguageTool()

    def test_check(self):
        for language, tests in self.check_tests.items():
            try:
                self.lang_check.language = language
            except ValueError:
                version = language_check.get_version()
                warnings.warn(
                    'LanguageTool {} doesn’t support language {!r}'
                    .format(version, language)
                )
            for text, expected_matches in tests:
                matches = self.lang_check.check(text)
                for expected_match in expected_matches:
                    for match in matches:
                        if (
                            (match.fromy, match.fromx, match.ruleId) ==
                            (expected_match.fromy, expected_match.fromx,
                             expected_match.ruleId)
                        ):
                            break
                    else:
                        raise IndexError(
                            'can’t find {!r}'.format(expected_match))

    def test_correct(self):
        for language, tests in self.correct_tests.items():
            try:
                self.lang_check.language = language
            except ValueError:
                version = language_check.get_version()
                warnings.warn(
                    'LanguageTool {} doesn’t support language {!r}'
                    .format(version, language)
                )
            for text, result in tests.items():
                self.assertEqual(self.lang_check.correct(text), result)

    def test_languages(self):
        languages = language_check.get_languages()
        self.assertIn('en', languages)

    def test_version(self):
        version = language_check.get_version()
        self.assertTrue(version)


if __name__ == '__main__':
    unittest.main()
