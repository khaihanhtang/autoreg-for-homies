from auto_registration_system.command import Command


class Term:
    DATE_VENUE = "[dv]"
    DATE_VENUE_SHORTENED = "dv"
    NUM_PLAYERS = "#players:"
    RESERVATION = "reserve"
    PENDING = "(pending)"
    INDENT_SPACE = "   "
    HELP_TEXT = f"""
    Please use the following syntaxes:
    1. To register a slot, use
        /{Command.COMMAND_RG} [name 1], ..., [name n] [slot]
    2. To reserve a slot, use
        /{Command.COMMAND_RS} [name 1], ..., [name n] [slot]
    3. To deregister from a slot (main players/reserves), use
        /{Command.COMMAND_DRG} [name 1], ..., [name n] [slot]
    4. To show the full list, use
        /{Command.COMMAND_ALL}
    5. To show available slots, use
        /{Command.COMMAND_AV}
    6. To set your alias, use
        /{Command.COMMAND_AKA} [your new alias]
    7. To view your alias, use
        /{Command.COMMAND_AKA}
    8. To check the lock, active list and release schedule, use
        /{Command.COMMAND_STATE}

    Admin release commands use Singapore time.
        /{Command.COMMAND_NOTITIME} HH:MM:SS DD/MM/YYYY
        /{Command.COMMAND_WEEKLYNOTITIME} HH:MM:SS DD/MM/YYYY
    The weekly command sets the first release and repeats every 7 days.
    Setting a release time switches to that command's mode. Send the active command without a time to turn it off.
        
    See detailed guide from the below link. 
    https://hackmd.io/@1UKfawZER96uwy_xohcquQ/B1fyW-c4R
    
    The source code is in the below link.
    https://github.com/khaihanhtang/autoreg-for-homies
    
    ---------------
    For /{Command.COMMAND_RG}, if the list is full, the corresponding player(s) will be put into the reserve list WITH the tag (pending). This means that the corresponding player(s) WILL be automatically inserted into the main player list, if some other player deregisters, by respecting the first-come, first-served basis.
    
    For /{Command.COMMAND_RS}, the corresponding player(s) will be put into reserve list WITHOUT the tag (pending). This means that the corresponding player(s) WILL NOT be automatically inserted into the main player list. Only admins can move them to the main player list if necessary.
    
    Command /{Command.COMMAND_DRG} applies to both main and reserve players.
    """
