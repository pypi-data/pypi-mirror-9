from helga.db import db
from random import random
import jaraco.modb, math

def encode(target):
    """ Encode as mongodb friendly object """
    return jaraco.modb.encode(target)

def decode(target):
    """ Decode from mongodb """
    return jaraco.modb.decode(target)

def random_cursor(cursor):
    """ Pull a random item from a cursor """
    index = int(math.floor(random()*cursor.count()))
    return cursor.limit(1).skip(index).next()

def current_state():
    """ Return tuple representing hero, enemy, and in_encounter """
    hero = decode(db.quest.heroes.find_one())
    enemy = None
    in_encounter = db.quest.encounter.count() > 0
    if in_encounter:
        enemy = decode(db.quest.encounter.find_one())
    return (hero, enemy, in_encounter)
