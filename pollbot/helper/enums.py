"""Helper enums to properly map several properties of Polls and alike."""
from enum import Enum, unique


@unique
class ExpectedInput(Enum):
    """Helper class to map the creation steps of a Poll."""

    name = 1
    description = 2
    options = 3
    votes = 4
    vote_count = 5
    date = 6
    due_date = 7

    new_option = 10
    new_user_option = 11


@unique
class PollType(Enum):
    """Helper class to specify the different types of Polls."""

    single_vote = 0
    doodle = 10
    block_vote = 20
    limited_vote = 30
    cumulative_vote = 40
    count_vote = 50


@unique
class VoteResultType(Enum):
    """Helper enum to specify the different types of possible votes."""

    yes = 1
    no = 2
    maybe = 3


@unique
class CallbackType(Enum):
    """A class representing callback types."""

    # Poll creation
    show_poll_type_keyboard = 0
    change_poll_type = 1
    toggle_anonymity = 2
    skip_description = 3
    all_options_entered = 4
    toggle_results_visible = 5
    cancel_creation = 6

    # Poll voting
    vote = 20

    # Poll management menu
    menu_back = 30
    menu_vote = 31
    menu_option = 32
    menu_delete = 34
    menu_show = 35
    menu_update = 36
    menu_close = 37

    # Poll management
    delete = 50
    close = 51
    reopen = 52
    clone = 53
    reset = 54

    # Settings
    settings_anonymization_confirmation = 70
    settings_anonymization = 71
    settings_show_sorting = 72
    settings_user_sorting = 73
    settings_option_sorting = 74
    settings_new_option = 75
    settings_show_remove_option_menu = 76
    settings_remove_option = 77
    settings_toggle_percentage = 78
    settings_toggle_allow_new_options = 79
    settings_toggle_date_format = 80
    settings_open_add_option_datepicker = 81
    settings_open_due_date_datepicker = 82
    settings_pick_due_date = 83
    settings_open_language_picker = 84
    settings_change_poll_language = 85

    # Misc
    ignore = 100
    activate_notification = 101
    external_open_datepicker = 102
    external_open_menu = 103
    external_cancel = 104

    # User
    user_change_language = 200

    # Date picker
    open_creation_datepicker = 501
    close_creation_datepicker = 502
    pick_date_option = 503
    set_date = 504
    next_month = 505
    previous_month = 506


@unique
class CallbackResult(Enum):
    """A class representing callback results."""

    empty = 0
    true = 1
    false = 2

    # Poll voting
    vote = 20
    yes = 21
    no = 22
    maybe = 23

    # Menu navigation
    main_menu = 40
    settings = 41


@unique
class UserSorting(Enum):
    """Save several possible sorting options."""

    user_chrono = 0
    user_name = 1


@unique
class OptionSorting(Enum):
    """Save several possible sorting options."""

    option_chrono = 10
    option_percentage = 11
    option_name = 12
