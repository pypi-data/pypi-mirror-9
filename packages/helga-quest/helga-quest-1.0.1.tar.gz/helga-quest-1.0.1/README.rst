helga-quest
===========

Collaborative RPG base on user driven content

Purpose
-------

Include light rpg mechanics in a user generated world. One may add mobs or
actions the mobs can take. Users can go serious/pure fantasy or more comical
in content.

Usage
-----
A high level view of commands below, quest allows users control over content including mobs and their actions:
```
!quest (action|adventure|attack|mob|rest)
```

```
!quest mob add '{"name":"Assault Shaker", "hp":1, "level":1, "xp":60}'
!quest mob remove '{"name":"Assault Shaker"}'
```
Helga adds/removes mobs with the specified stats/parameters

```
!quest action add '{"name":"Assault Shaker", "description":"{name} peppers {target} for {dmg} damage", "attack":5}'
```
Helga adds/removes actions (which maps to specific mobs with the 'name' attribute) to a pool of randomly selected behaviors each round

```
!quest adventure
helga> You've encountered a Assault Shaker!
```
Initiate the beginning of an adventure/encounter. Currently a single enemy is selected and scaled to around the power of the hero.

```
!quest attack
helga> You strike for 1 damage, Assault Shaker peppers Hero for 5.9 damage"
```
Execute an attack against the enemy! Eventually actions should be available to heroes, however right now it is lame and not supported.

```
!quest rest
```
Takes a short break to restore health outside of combat.

License
-------

Copyright (c) 2015 Jon Robison

See included LICENSE for licensing information
