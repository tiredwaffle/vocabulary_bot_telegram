import requests
import random
import time

import telegram
from telegram import ReplyKeyboardMarkup
from telegram import ChatAction, ReplyKeyboardRemove
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, PicklePersistence)

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TYPING_CHOICE, LANGUAGE= range(2)


#for translation API
url = "https://systran-systran-platform-for-language-processing-v1.p.rapidapi.com/resources/dictionary/lookup"
headers = {
    'x-rapidapi-host': "systran-systran-platform-for-language-processing-v1.p.rapidapi.com",
    'x-rapidapi-key': "###Key###"
    }
#for flag function
OFFSET = 127462 - ord('A')

lang_keyboard = [['English', 'French'], ['German', 'Spanish'], ['Russian', 'Dutch']]
action_keyboard = [['Add new word'], ['Change language'], ['Show all words'], ['Train me!'], ['Help!']]

langs = ['english', 'french','german', 'spanish','russian','dutch']
langs_code = {'english':'en', 'french':'fr','german':'de', 'spanish':'es','russian':'ru','dutch':'nl'}

markup = ReplyKeyboardMarkup(lang_keyboard, one_time_keyboard=True)
def flags(code):
    code = code.upper()
    return chr(ord(code[0]) + OFFSET) + chr(ord(code[1]) + OFFSET)
def change_lang(update, context):
    update.message.reply_text('Alright, choose a new language!', reply_markup = markup)
    return LANGUAGE
def facts_to_str(user_data):
    facts = list()
    for key, value in user_data.items():
        facts.append('{} - {}'.format(key, value))

    return "\n".join(facts).join(['\n', '\n'])
def keep_typing(last, chat, action):
    now = time.time()
    if (now - last) > 1:
        chat.send_action(action)
    return now

def searching(response, input, current_lang, mode):
    text1 = eval(response.text.replace('false', '0').replace('true', '1'))['outputs'][0]['output']['matches'] 
    output = ''
    if mode == 0:
        for el in text1:
            output += ", ".join([smth['lemma'] for smth  in el['targets']]) + ', '
        output = output[:-2]
        output += ' '  
    elif mode == 1:
        for el in text1:
            output += '\n\n' + el['source']['pos'] + ':\n'
            output += ", ".join([smth['lemma'] for smth  in el['targets']])
        output += ' '   
    
    elif mode==2:
        if current_lang == 'english':
            transcription = str(text1[0]['source']['phonetic'])
            output = '\n' + transcription + '\n'
        else:
            output = ''
        for l1 in text1:
            output += '\n<b>' + l1['source']['pos'] + '</b> :\n- '
            output += ", ".join([smth['lemma'] for smth  in l1['targets']]) +'\n'
            output += ("-- Expressions --\n<i>")
            for l3 in ([l2['expressions'] for l2  in l1['targets']]):
                if not l3 == []:
                    output += ("\n".join([( l4['source']+ ' - ' + l4['target'] + ';') for l4  in l3]))
                    output += '\n'
            output += '</i> '   
    return output

def start(update, context):
    update.message.reply_text("Hi! I'm going to collect and translate all words you wanna save.")
    update.message.reply_text("Default language for transaltion is english. For translating english words - russian")
    if context.user_data:
        reply_text = "You already told me some words. Why don't you tell me something more?"
    else:
        reply_text = "First of all choose the language you are learning!\nDon't worry, you can change it anytime ;)"
    update.message.reply_text(reply_text, reply_markup=markup)
    for lan in langs:
        if lan not in context.user_data:
            context.user_data[lan] = {}
    return LANGUAGE

def regular_choice_lang(update, context):
    text = update.message.text.lower()
    context.user_data['current_lang'] = text
    reply_text = 'Nice! Your language is {} now. To change it use /change. Now add some words!'.format(text)
    markup = ReplyKeyboardMarkup(action_keyboard, one_time_keyboard=True)
    update.message.reply_text(reply_text, reply_markup = markup)
    return TYPING_CHOICE

def no_lang(update, context):
    reply_text = 'Sorry, your language is {} not in our list yet. You have to choose language before you start working!'.format(text)
    update.message.reply_text(reply_text, reply_markup = markup)
    return LANGUAGE

def regular_choice(update, context):
    last = 0
    text = update.message.text.lower()
    context.user_data['choice'] = text
    current_lang = context.user_data['current_lang'] 
    if current_lang == 'english':
        target = 'ru'
        flag = flags('gb')
    else:
        target = 'en'
        flag = flags(langs_code[current_lang])
    last = keep_typing(last, update.effective_chat, ChatAction.TYPING)
    if context.user_data[current_lang].get(text):
        reply_text = 'You know this one already! \n' +  flag + ' <b>'+ text +'</b> - ' + context.user_data[current_lang][text] + '\n /more - to know more'
    else:
        querystring = {"source":langs_code[current_lang],"target":target,"input":text}
        response = requests.request("GET", url, headers=headers, params=querystring)
        if response.text == "{\"outputs\":[{\"output\":{}}]}":
            reply_text = 'Hmmm... Can\'t find \'{}\'. Are you sure it\'s spelled right? Try again!'.format(text)
        else:
            context.user_data[current_lang][text] = searching(response, text,current_lang, 0)
            reply_text = flag + ' <b>'+ text +'</b> - ' + searching(response, text, current_lang, 0) + '\n /more - to know more'

    update.message.reply_text(reply_text, quote = True, parse_mode=telegram.ParseMode.HTML)

    return TYPING_CHOICE

def more(update, context):
    text = context.user_data['choice'] 
    current_lang = context.user_data['current_lang'] 
    if current_lang == 'english':
        target = 'ru'
    else:
        target = 'en'
    querystring = {"source":langs_code[current_lang],"target":target,"input":text}
    response = requests.request("GET", url, headers=headers, params=querystring)
    reply_text = searching(response, text, current_lang, 2)
    update.message.reply_text(reply_text, quote = True, parse_mode=telegram.ParseMode.HTML)

    return TYPING_CHOICE

def adding(update, context):
    update.message.reply_text("Just type them here! It's that simple")
    return TYPING_CHOICE

def show_data(update, context):
    if context.user_data[context.user_data['current_lang']]=={}:
        update.message.reply_text("You don't have words for this language yet\n")
    else:
        update.message.reply_text("This is what you already told me from {} language:\n"
                                "{}"
                              "\nYou can tell me more, or change the language /change".format(context.user_data['current_lang'], facts_to_str(context.user_data[context.user_data['current_lang']])))
    return TYPING_CHOICE

def show_random_word(update, context):
    if context.user_data[context.user_data['current_lang']]=={}:
        update.message.reply_text("You don't have words for this language yet\n")
    else:
        rand_word = str(random.sample(list(context.user_data[context.user_data['current_lang']]), 1)[0])
        update.message.reply_text("The word you should remind today from {} language is:\n"
                              "{} - {}" .format(context.user_data['current_lang'], rand_word, str(context.user_data[context.user_data['current_lang']][rand_word])))
    return TYPING_CHOICE

def help_m(update, context):
    update.message.reply_text('This is bot for storing and translating words!\n'
                              '\n/change - to change the language'
                              '\n/show_all - to show all words of a current language'
                              '\n/more - to find out more about your words'
                              '\n/remind_me - to get random word of a current language')
    return TYPING_CHOICE

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    # Create the Updater and pass it your bot's token.
    pp = PicklePersistence(filename='conversationbot')
    updater = Updater("###Token###", persistence=pp, use_context=True)
    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            TYPING_CHOICE: [CommandHandler('change', change_lang),
                            CommandHandler('more', more),
                            CommandHandler('show_all', show_data),
                            CommandHandler('remind_me', show_random_word),
                            CommandHandler('help', help_m),
                            CommandHandler('cancel', change_lang),
                            MessageHandler(Filters.regex('^(Change language)$'), change_lang),
                            MessageHandler(Filters.regex('^(Show all words)$'), show_data),
                            MessageHandler(Filters.regex('^(Train me!)$'), show_random_word),
                            MessageHandler(Filters.regex('^(Help!)$'), help_m),
                            MessageHandler(Filters.regex('^(Add new word)$'), adding),
                            MessageHandler(Filters.text, regular_choice),  
                            ],
            LANGUAGE: [MessageHandler(Filters.regex('^(English|French|German|Spanish|Russian|Ukrainian|Dutch)$'), regular_choice_lang),
                       MessageHandler(Filters.text, no_lang) ],
        },
        fallbacks=[CommandHandler('cancel', change_lang)],
        name="my_conversation",
        persistent=True
    )
    dp.add_handler(conv_handler)
    show_data_handler = CommandHandler('show_data', show_data)
    dp.add_handler(show_data_handler)
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
