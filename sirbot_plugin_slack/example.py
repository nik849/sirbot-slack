import aiohttp
import logging
import re

from .hookimpl import hookimpl
from .message import Attachment, Field, Button

logger = logging.getLogger('sirbot.slack')


async def react(message, slack, _, facade):
    """
    Test reaction

    React to any message containing 'sirbot' with a robot face reaction
    """
    reaction = 'robot_face'
    await slack.add_reaction([message.incoming, reaction])


# Example quote of the day plugin
async def get_quote_of_the_day():
    url = 'http://api.theysaidso.com/qod.json'
    quote_r = {}
    async with aiohttp.get(url) as response:
        if response.status != 200:
            raise Exception('Error talking to quote api')
        quote_r = await response.json()

    quote = quote_r['contents']['quotes'][0]['quote']
    author = quote_r['contents']['quotes'][0]['author']
    image = quote_r['contents']['quotes'][0]['background']

    return quote, author, image


async def quote_of_the_day(message, slack, _, facade):
    """
    Quote of the day example.

    Query theysaidso.com API and create of message with an Attachment
    """
    message.text = 'Looking for it...'
    await slack.send(message)

    try:
        quote, author, image = await get_quote_of_the_day()
    except Exception:
        message.text = '''Sorry. I couldn't find it.'''
    else:
        message.text = ''
        google_url = 'http://www.google.com/search?q={}'
        attachment = Attachment(fallback='The quote of the day',
                                text='_{}_'.format(quote),
                                author_name=author,
                                author_link=google_url.format(author),
                                footer='theysaidso.com',
                                color='good',
                                thumb_url=image)
        message.attachments.append(attachment)
    finally:
        await slack.update(message)


async def test_message(message, slack, _, facade):
    """
    Test message

    Create a message with an attachments containing multiple fields, buttons
    and an image.
    Confirmation for the 'danger' button
    Change the username/avatar of the bot
    """

    message.text = 'A beautiful message'
    message.username = 'BOT'
    message.icon = ':tada:'
    att = Attachment(title='Carter',
                     fallback='A test attachment',
                     image_url='http://imgs.xkcd.com/comics/twitter_bot.png',
                     )

    f1 = Field(title='Field1', value='A short field', short=True)
    f2 = Field(title='Field2', value='A short field', short=True)
    f3_str = 'A long *long* ~long~ `long` _long_ long field\n'
    f3 = Field(title='Field3', value=f3_str * 3)
    att.fields += f1, f2, f3

    b1 = Button(name='b1', text='Bonjour', style='primary')
    b2 = Button(name='b2', text='Hello')
    confirm = {'title': 'Are you sure?',
               'text': 'DANGER DANGER DANGER !!!',
               'ok_text': 'Yes',
               'dismiss_text': 'No'}
    b3 = Button(name='b3', text='Danger', style='danger', confirm=confirm)

    att.actions += b1, b2, b3

    message.attachments.append(att)
    await slack.send(message)


async def hello_world(msg, *_):
    print('user typing')


async def test(msg, slack, *_):
    print('test')


async def parrot(message, slack, facades, *_):
    message.text = 'Send stop to stop the parrot'
    await slack.send(message)

    return {'func': parrot_next}


async def parrot_next(message, slack, facades, *_):
    if message.incoming.text != 'stop':
        message.text = 'Your previous message was: `{}`'.format(
            message.incoming.previous[0]['text'])
        await slack.send(message)

        return {'func': parrot_next}


@hookimpl
def register_slack_messages():
    commands = [
        {
            'match': 'test',
            'func': test
        },
        {
            'match': 'sirbot',
            'func': react,
        },
        {
            'match': '',
            'func': react,
            'mention': True
        },
        {
            'match': '(([Cc]an|[Mm]ay) I have the )?quote of the day\?$',
            'func': quote_of_the_day,
            'mention': True
        },
        {
            'match': 'test message',
            'func': test_message,
            'mention': True,
            'flags': re.IGNORECASE
        },
        {
            'match': 'parrot',
            'func': parrot,
            'mention': True,
        }
    ]

    return commands


@hookimpl
def register_slack_events():
    events = [
        {
            'func': hello_world,
            'name': 'user_typing'
        }
    ]

    return events
