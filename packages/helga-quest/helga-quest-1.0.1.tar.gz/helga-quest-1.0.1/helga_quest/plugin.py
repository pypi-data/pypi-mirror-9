from helga.plugins import command
from helga_quest import driver

_help_text = """Collaboratively play an RPG from user driven content \
Usage: !quest (action|adventure|attack|mob|rest)\
!quest mob add '{"name":"Assault Shaker", "hp":1, "level":1, "xp":60}'\
!quest action add '{"name":"Assault Shaker", "description":"{name} peppers {target} for {dmg} damage", "attack":5}'\
!quest adventure\
helga> You've encountered a Assault Shaker!\
!quest attack\
helga> You strike for 1 damage, Assault Shaker peppers Hero for 5.9 damage\
!quest rest\
helga> You feel refreshed..."""


@command('quest', help=_help_text, shlex=True)
def quest(client, channel, nick, message, cmd, args):
    """ Parse commands and execute via driver """
    response = ''
    if len(args) == 0 or args[0] == 'status':
        response = driver.status()
    elif args[0] == 'action' or args[0] == 'actions':
        mod = args[2] if len(args) > 2 else ''
        response = driver.action(args[1], mod)
    elif args[0] == 'adventure':
        mob = args[1] if len(args) > 1 else ''
        response = driver.adventure(mob)
    elif args[0] == 'rest' or args[0] == 'sleep':
        response = driver.rest()
    elif args[0] == 'mob' or args[0] == 'mobs':
        response = driver.mob(args[1], args[2])
    elif args[0] == 'attack' or args[0] == 'fight':
        response = driver.attack()
    elif args[0] == 'drop':
        mod = args[1] if len(args) > 1 else ''
        response = driver.drop(mod)
    else:
        response = "I don't understand %s" % args[0]
    return response
