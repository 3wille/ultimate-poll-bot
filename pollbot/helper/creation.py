"""Poll creation helper."""
from pollbot.i18n import i18n
from pollbot.helper.enums import ExpectedInput
from pollbot.helper.display import get_poll_management_text
from pollbot.telegram.keyboard import (
    get_options_entered_keyboard,
    get_management_keyboard,
)
from pollbot.models import PollOption, Reference


def next_option(tg_chat, poll, options):
    """Send the options message during the creation ."""
    locale = poll.user.locale
    poll.user.expected_input = ExpectedInput.options.name
    keyboard = get_options_entered_keyboard(poll)

    if len(options) == 1:
        text = i18n.t('creation.option.single_added', locale=locale, option=options[0])
    else:
        text = i18n.t('creation.option.multiple_added', locale=locale)
        for option in options:
            text += f'\n*{option}*'
        text += '\n\n' + i18n.t('creation.option.next', locale=locale)

    tg_chat.send_message(text, reply_markup=keyboard, parse_mode='Markdown')


def create_poll(session, poll, user, chat, message=None):
    """Finish the poll creation."""
    poll.created = True
    user.expected_input = None
    user.current_poll = None

    if message:
        message = message.edit_text(
            get_poll_management_text(session, poll),
            parse_mode='markdown',
            reply_markup=get_management_keyboard(poll)
        )
    else:
        message = chat.send_message(
            get_poll_management_text(session, poll),
            parse_mode='markdown',
            reply_markup=get_management_keyboard(poll)
        )

    reference = Reference(
        poll,
        admin_chat_id=chat.id,
        admin_message_id=message.message_id
    )
    session.add(reference)
    session.commit()


def add_options(poll, text, is_date=False):
    """Add a new option to the poll."""
    options_to_add = [x.strip() for x in text.split('\n') if x.strip() != '']
    added_options = []

    for option_to_add in options_to_add:
        description = None
        # Extract the description if existing
        if not is_date and '-' in option_to_add:
            # Extract and strip the description
            splitted = option_to_add.split('-')
            option_to_add = splitted[0].strip()
            description = splitted[1].strip()
            if description == '':
                description = None

        if option_is_duplicate(poll, option_to_add) or option_to_add in added_options:
            continue

        poll_option = PollOption(poll, option_to_add)
        poll_option.description = description
        poll_option.is_date = is_date
        poll.options.append(poll_option)

        added_options.append(option_to_add)

    return added_options


def option_is_duplicate(poll, option_to_add):
    """Check whether this option already exists on this poll."""
    for existing_option in poll.options:
        if existing_option.name == option_to_add:
            return True

    return False
