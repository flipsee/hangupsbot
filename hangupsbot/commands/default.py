import json, random, asyncio

import hangups
from hangups.ui.utils import get_conv_name

from hangupsbot.utils import text_to_segments
from hangupsbot.commands import command


@command.register_unknown
def unknown_command(bot, event, *args):
    """Unknown command handler"""
    bot.send_message(event.conv,
                     _('{}: Unknown command!').format(event.user.full_name))


@command.register
def help(bot, event, cmd=None, *args):
    """Help me, Obi-Wan Kenobi. You're my only hope.
       Usage: /bot help [command]"""
    if not cmd:
        segments = [hangups.ChatMessageSegment(_('Supported commands:'), is_bold=True),
                    hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK),
                    hangups.ChatMessageSegment(', '.join(sorted(command.commands.keys())))]
    else:
        try:
            command_fn = command.commands[cmd]
            segments = [hangups.ChatMessageSegment('{}:'.format(cmd), is_bold=True),
                        hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK)]
            segments.extend(text_to_segments(_(command_fn.__doc__)))
        except KeyError:
            yield from command.unknown_command(bot, event)
            return

    bot.send_message_segments(event.conv, segments)


@command.register
def ping(bot, event, *args):
    """Let's play ping pong!"""
    bot.send_message(event.conv, 'pong')


@command.register
def echo(bot, event, *args):
    """Monkey see, monkey do!
       Usage: /bot echo text"""
    bot.send_message(event.conv, '{}'.format(' '.join(args)))


@command.register
def users(bot, event, *args):
    """List all participants in current conversation (including G+ accounts and emails)"""
    segments = [hangups.ChatMessageSegment(_('List of participants ({} total):').format(len(event.conv.users)),
                                           is_bold=True),
                hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK)]
    for u in sorted(event.conv.users, key=lambda x: x.full_name.split()[-1]):
        link = 'https://plus.google.com/u/0/{}/about'.format(u.id_.chat_id)
        segments.append(hangups.ChatMessageSegment(u.full_name, hangups.SegmentType.LINK,
                                                   link_target=link))
        if u.emails:
            segments.append(hangups.ChatMessageSegment(' ('))
            segments.append(hangups.ChatMessageSegment(u.emails[0], hangups.SegmentType.LINK,
                                                       link_target='mailto:{}'.format(u.emails[0])))
            segments.append(hangups.ChatMessageSegment(')'))
        segments.append(hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK))
    bot.send_message_segments(event.conv, segments)


@command.register
def user(bot, event, username, *args):
    """Find user by name
       Usage: /bot user user_name"""
    username_lower = username.strip().lower()
    segments = [hangups.ChatMessageSegment(_('Search results for user name "{}":').format(username),
                                           is_bold=True),
                hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK)]
    for u in sorted(bot._user_list._user_dict.values(), key=lambda x: x.full_name.split()[-1]):
        if username_lower not in u.full_name.lower():
            continue

        link = 'https://plus.google.com/u/0/{}/about'.format(u.id_.chat_id)
        segments.append(hangups.ChatMessageSegment(u.full_name, hangups.SegmentType.LINK,
                                                   link_target=link))
        if u.emails:
            segments.append(hangups.ChatMessageSegment(' ('))
            segments.append(hangups.ChatMessageSegment(u.emails[0], hangups.SegmentType.LINK,
                                                       link_target='mailto:{}'.format(u.emails[0])))
            segments.append(hangups.ChatMessageSegment(')'))
        segments.append(hangups.ChatMessageSegment(' ... {}'.format(u.id_.chat_id)))
        segments.append(hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK))
    bot.send_message_segments(event.conv, segments)


@command.register
def hangouts(bot, event, *args):
    """List all conversations where bot is wreaking havoc
       Legend: c ... commands, f ... forwarding, a ... autoreplies"""
    segments = [hangups.ChatMessageSegment(_('Active conversations:'), is_bold=True),
                hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK)]
    for c in bot.list_conversations():
        s = '{} [c: {:d}, f: {:d}, a: {:d}]'.format(get_conv_name(c, truncate=True),
                                                    bot.get_config_suboption(c.id_, 'commands_enabled'),
                                                    bot.get_config_suboption(c.id_, 'forwarding_enabled'),
                                                    bot.get_config_suboption(c.id_, 'autoreplies_enabled'))
        segments.append(hangups.ChatMessageSegment(s))
        segments.append(hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK))

    bot.send_message_segments(event.conv, segments)


@command.register
def rename(bot, event, *args):
    """Rename current conversation
       Usage: /bot rename new_conversation_name"""
    yield from bot._client.setchatname(event.conv_id, ' '.join(args))


@command.register
def leave(bot, event, conversation=None, *args):
    """Leave current (or specified) conversation
       Usage: /bot leave [conversation_name]"""
    convs = []
    if not conversation:
        convs.append(event.conv)
    else:
        conversation = conversation.strip().lower()
        for c in bot.list_conversations():
            if conversation in get_conv_name(c, truncate=True).lower():
                convs.append(c)

    for c in convs:
        yield from c.send_message([
            hangups.ChatMessageSegment(_('I\'ll be back!'))
        ])
        yield from bot._conv_list.leave_conversation(c.id_)


@command.register
def easteregg(bot, event, easteregg, eggcount=1, period=0.5, *args):
    """Annoy people with easter egg combo!
       Usage: /bot easteregg easter_egg_type [count] [period]
       Supported easter eggs: ponies, pitchforks, bikeshed, shydino"""
    for i in range(int(eggcount)):
        yield from bot._client.sendeasteregg(event.conv_id, easteregg)
        if int(eggcount) > 1:
            yield from asyncio.sleep(float(period) + random.uniform(-0.1, 0.1))


@command.register
def spoof(bot, event, *args):
    """Spoof IngressBot on specified GPS coordinates
       Usage: /bot spoof latitude,longitude [hack|fire|deploy|mod] [level] [count]"""
    segments = [hangups.ChatMessageSegment(_('!!! WARNING !!!'), is_bold=True),
                hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK)]
    segments.append(hangups.ChatMessageSegment(_('Agent {} (').format(event.user.full_name)))
    link = 'https://plus.google.com/u/0/{}/about'.format(event.user.id_.chat_id)
    segments.append(hangups.ChatMessageSegment(link, hangups.SegmentType.LINK,
                                               link_target=link))
    segments.append(hangups.ChatMessageSegment(_(') has been reported to Niantic for attempted spoofing!')))
    bot.send_message_segments(event.conv, segments)


@command.register
def reload(bot, event, *args):
    """Reload bot configuration from file"""
    bot.config.load()


@command.register
def quit(bot, event, *args):
    """Oh my God! They killed Kenny! You bastards!"""
    print(_('HangupsBot killed by user {} from conversation {}').format(event.user.full_name,
                                                                        get_conv_name(event.conv, truncate=True)))
    yield from bot._client.disconnect()


@command.register
def config(bot, event, cmd=None, *args):
    """Show or change bot configuration
       Usage: /bot config [get|set] [key] [subkey] [...] [value]"""

    if cmd == 'get' or cmd is None:
        config_args = list(args)
        value = bot.config.get_by_path(config_args) if config_args else dict(bot.config)
    elif cmd == 'set':
        config_args = list(args[:-1])
        if len(args) >= 2:
            bot.config.set_by_path(config_args, json.loads(args[-1]))
            bot.config.save()
            value = bot.config.get_by_path(config_args)
        else:
            yield from command.unknown_command(bot, event)
            return
    else:
        yield from command.unknown_command(bot, event)
        return

    if value is None:
        value = _('Key not found!')

    config_path = ' '.join(k for k in ['config'] + config_args)
    segments = [hangups.ChatMessageSegment('{}:'.format(config_path),
                                           is_bold=True),
                hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK)]
    segments.extend(text_to_segments(json.dumps(value, indent=2, sort_keys=True)))
    bot.send_message_segments(event.conv, segments)