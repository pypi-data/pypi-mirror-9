""" Driver for core gameplay """
from helga.db import db
from helga_quest.core import Action, Being
from helga_quest.util import encode, decode, random_cursor, current_state
import json, random

def status():
    """ Return the current status of the game as string """
    hero, enemy, in_encounter = current_state()
    next_xp = Being.xp_to_level(hero.level + 1)
    response = '{} XP: {}/{}'.format(str(hero), hero.xp, next_xp)
    if not in_encounter:
        response += u", you are not actively fighting."
    else:
        response += ' vs %s.' % str(enemy)
    template = ' There are {} mobs and {} actions in database'
    response += template.format(db.quest.enemies.count(),
                                db.quest.actions.count())
    return response

def action(mod, statsstr):
    """ Add/remove actions for NPCs """
    stats = json.loads(statsstr)
    action = Action(**stats)
    if mod == 'add':
        db.quest.actions.insert(encode(action))
        response = 'Action added'
    elif mod == 'remove':
        db.quest.actions.remove({'name':action.name,
                                 'description':action.description})
        response = 'Action removed'
    else:
        response = 'I do not understand %s' % mod
    return response

def adventure(mob=''):
    """ Begin new encounter """
    hero, enemy, in_encounter = current_state()
    if hero.hp_current <= 0:
        response = 'You must rest before adventuring!'
    elif in_encounter:
        response = "You can't abandon your valiant journey!"
    elif db.quest.enemies.count() == 0:
        response = "There are no enemies populated against which to quest!"
    else:
        if mob:
            query = db.quest.enemies.find({'name':mob})
        else:
            query = db.quest.enemies.find()
        enemy = decode(random_cursor(query))
        target_level = int(max(1, hero.level * (1 + random.gauss(0, .05))))
        enemy.scale_level(target_level)
        db.quest.encounter.insert(encode(enemy))
        template = "You've encountered a {} level {}!"
        response = template.format(enemy.name, enemy.level)
    return response

def rest():
    """ Direct player to rest if possible """
    hero, enemy, in_encounter = current_state()
    if in_encounter:
        response = "You can't rest whilst in combat!"
    else:
        hero.hp_current = hero.hp
        db.quest.heroes.remove({'name':hero.name})
        db.quest.heroes.insert(encode(hero))
        response = 'You feel refreshed and ready for combat'
    return response

def mob(mod, statsstr):
    """ Manage mobs in database """
    stats = json.loads(statsstr)
    being = Being(**stats)
    if mod == 'add':
        db.quest.enemies.insert(encode(being))
        response = 'Mob added'
    elif mod == 'remove':
        db.quest.enemies.remove({'name':being.name})
        response = 'Mob removed'
    return response

def execute_attack_enemy(hero, enemy, enemy_action):
    """ Execute enemy attack """
    received_dmg = enemy.do_attack(hero, attack_bonus=enemy_action.attack)
    hero.hp_current -= received_dmg
    db.quest.heroes.remove({'name':hero.name})
    db.quest.heroes.insert(encode(hero))
    response = enemy_action.create_response(hero, received_dmg) + ' '
    if hero.hp_current <= 0:
        db.quest.encounter.drop()
        response += '\nYou have been slain!'
    else:
        db.quest.encounter.remove({'name':enemy.name})
        db.quest.encounter.insert(encode(enemy))
    return response

def execute_attack_hero(hero, enemy, enemy_action):
    """ Execute hero attack """
    dmg = hero.do_attack(enemy, defense_bonus=enemy_action.defense)
    enemy.hp_current -= dmg
    db.quest.encounter.remove({'name':enemy.name})
    db.quest.encounter.insert(encode(enemy))
    response = 'You strike for %d damage. ' % dmg
    if enemy.hp_current <= 0:
        hero.xp += enemy.xp
        while hero.can_levelup():
            hero.levelup()
        db.quest.heroes.remove({'name':hero.name})
        db.quest.heroes.insert(encode(hero))
        db.quest.encounter.remove({'name':enemy.name})
        template = "You've slain the {}, and earned {} xp!"
        response += template.format(enemy.name, enemy.xp)
    return response

def attack():
    """ Execute attack on current encounter mob(s) """
    hero, enemy, in_encounter = current_state()
    if hero.hp_current <= 0:
        response = 'You must rest before exerting oneself!'
    elif not in_encounter:
        response = "There is no enemy to attack!"
    else:
        response = ''
        # grab enemy action to have defense bonus on hand
        query = db.quest.actions.find({'name':enemy.name})
        if query.count() > 0:
            action = decode(random_cursor(query))
        else:
            action = Action(name=enemy.name)
        if hero.initiative_roll(enemy.speed + action.speed):
            response += execute_attack_hero(hero, enemy, action)
            if enemy.hp_current > 0:
                response += execute_attack_enemy(hero, enemy, action)
        else:
            response += execute_attack_enemy(hero, enemy, action)
            if hero.hp_current > 0:
                response += execute_attack_hero(hero, enemy, action)

    return response

def drop(mod=''):
    """ Drop items from database """
    if not mod:
        db.quest.drop()
        db.quest.heroes.insert(encode(Being()))
        response = "Quest database dropped, so sad"
    elif mod == 'heroes':
        db.quest.heroes.drop()
        response = "Heroes dropped"
    elif mod == 'encounter':
        db.quest.encounter.drop()
        response = "Encounter dropped"
    elif mod == "enemies":
        db.quest.enemies.drop()
        response = "Enemies dropped"
    else:
        response = "I don't understand %s" % mod
    return response
