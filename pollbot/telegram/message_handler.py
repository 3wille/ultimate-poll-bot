"""Handle messages."""

from pollbot.i18n import i18n
from pollbot.helper.session import session_wrapper
from pollbot.helper.enums import ExpectedInput, PollType
from pollbot.helper.display import get_settings_text
from pollbot.helper.update import update_poll_messages
from pollbot.telegram.callback_handler.creation import create_poll

from pollbot.helper.creation import (
    next_option,
    add_options,
)
from pollbot.telegram.keyboard import (
    get_settings_keyboard,
    get_open_datepicker_keyboard,
    get_skip_description_keyboard,
)

from pollbot.models import Reference


@session_wrapper()
def handle_private_text(bot, update, session, user):
    """Read all private messages and the creation of polls."""
    text = update.message.text.strip()
    poll = user.current_poll
    chat = update.message.chat

    if user.expected_input is None:
        return

    expected_input = ExpectedInput[user.expected_input]
    ignored_expected_inputs = [ExpectedInput.date, ExpectedInput.due_date]
    # The user is currently not expecting input or no poll is set
    if user.current_poll is None or user.expected_input is None:
        return
    elif expected_input in ignored_expected_inputs:
        return
    else:
        actions = {
            ExpectedInput.name: handle_set_name,
            ExpectedInput.description: handle_set_description,
            ExpectedInput.options: handle_create_options,
            ExpectedInput.vote_count: handle_set_vote_count,
            ExpectedInput.new_option: handle_new_option,
            ExpectedInput.new_user_option: handle_user_option_addition,
        }
        if '*' in text or '_' in text or '[' in text:
            chat.send_message(i18n.t('creation.error.markdown', locale=user.locale),
                              parse_mode='Markdown')
            return

        return actions[expected_input](bot, update, session, user, text, poll, chat)


def handle_set_name(bot, update, session, user, text, poll, chat):
    """Set the name of the poll."""
    poll.name = text
    user.expected_input = ExpectedInput.description.name
    keyboard = get_skip_description_keyboard(poll)
    chat.send_message(
        i18n.t('creation.description', locale=user.locale),
        reply_markup=keyboard,
    )


def handle_set_description(bot, update, session, user, text, poll, chat):
    """Set the description of the poll."""
    poll.description = text
    user.expected_input = ExpectedInput.options.name
    chat.send_message(
        i18n.t('creation.option.first', locale=user.locale),
        reply_markup=get_open_datepicker_keyboard(poll),
        parse_mode='markdown'
    )


def handle_create_options(bot, update, session, user, text, poll, chat):
    """Add options to the poll."""
    # Multiple options can be sent at once separated by newline
    # Strip them and ignore empty lines
    added_options = add_options(poll, text)

    if len(added_options) == 0:
        return i18n.t('creation.option.no_new', locale=user.locale)

    next_option(chat, poll, added_options)


def handle_set_vote_count(bot, update, session, user, text, poll, chat):
    """Set the amount of possible votes for this poll."""
    if poll.poll_type == PollType.limited_vote.name:
        error_message = i18n.t('creation.error.limit_between', locale=user.locale, limit=len(poll.options))
    elif poll.poll_type == PollType.cumulative_vote.name:
        error_message = i18n.t('creation.error.limit_bigger_zero', locale=user.locale)

    try:
        amount = int(text)
    except BaseException:
        return error_message

    # Check for valid count
    if amount < 1 or (poll.poll_type == PollType.limited_vote.name and amount > len(poll.options)):
        return error_message

    poll.number_of_votes = amount

    create_poll(session, poll, user, chat)


def handle_new_option(bot, update, session, user, text, poll, chat):
    """Add a new option after poll creation."""
    added_options = add_options(poll, text)

    if len(added_options) > 0:
        text = i18n.t('creation.option.multiple_added', locale=user.locale) + '\n'
        for option in added_options:
            text += f'\n*{option}*'
        chat.send_message(text, parse_mode='markdown')
    else:
        chat.send_message(i18n.t('creation.option.no_new', locale=user.locale))

    # Reset expected input
    user.current_poll = None
    user.expected_input = None

    text = get_settings_text(poll)
    keyboard = get_settings_keyboard(poll)
    message = chat.send_message(
        text,
        parse_mode='markdown',
        reply_markup=keyboard,
    )

    # Delete old references
    references = session.query(Reference) \
        .filter(Reference.poll == poll) \
        .filter(Reference.admin_chat_id == chat.id) \
        .all()
    for reference in references:
        try:
            bot.delete_message(chat.id, reference.admin_message_id)
        except:
            pass
        session.delete(reference)

    # Create new reference
    reference = Reference(
        poll,
        admin_chat_id=chat.id,
        admin_message_id=message.message_id
    )
    session.add(reference)
    session.commit()

    update_poll_messages(session, bot, poll)


def handle_user_option_addition(bot, update, session, user, text, poll, chat):
    """Handle the addition of options from and arbitrary user."""
    if not poll.allow_new_options:
        user.current_poll = None
        user.expected_input = None
        chat.send_message(i18n.t('creation.not_allowed', locale=user.locale))

    added_options = add_options(poll, text)

    if len(added_options) > 0:
        # Reset user
        user.current_poll = None
        user.expected_input = None

        # Send message
        text = i18n.t('creation.option.multiple_added', locale=user.locale) + '\n'
        for option in added_options:
            text += f'\n*{option}*'
        chat.send_message(text, parse_mode='markdown')

        # Upate all polls
        update_poll_messages(session, bot, poll)
    else:
        chat.send_message(i18n.t('creation.option.no_new', locale=user.locale))
