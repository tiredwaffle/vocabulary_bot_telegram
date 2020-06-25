# vocabulary_bot_telegram
Small bot for searching for translation of words. (English, French, German, Spanish, Russian, Dutch supported)

## Libraries:
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) This library provides a pure Python interface for the Telegram Bot API. In addition to the pure API implementation, this library features a number of high-level classes to make the development of bots easy and straightforward. These classes are contained in the telegram.ext submodule.

## API for translation
[SYSTRAN.io](https://platform.systran.net/index) - Translation and NLP API Documentation

SYSTRAN.io platform is a collection of APIs for Translation, Multilingual Dictionary lookups, Natural Language Processing (Entity recognition, Morphological analysis, Part of Speech tagging, Language Identification…) and Text Extraction (from documents, audio files or images).

## Commands:
- <b>/start</b> - to initiate the session;
- <b>/change</b> - to change the language;
- <b>/more</b> - to return additional data about the last word translated (transcription, expressions);
- <b>Add new word</b> - to translate new words and add them to the temorary database;
- <b>Show all words</b> - show all words (with translarions) that were saved during this session;
- <b>Train me!</b> - returning random word from current language with translation to train the user;
While adding any other word the bot will try to return the translation.

