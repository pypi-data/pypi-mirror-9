#!/usr/bin/env python
# -*- coding: utf-8 -*-

colors = [ 'amber', 'aquamarine', 'azure', 'beige', 'black', 'pitch-black',
'blue', 'bluegreen', 'brindled', 'bronze', 'brown', 'burgundy', 'carmine',
'carnation', 'carnelian', 'celadon', 'cerulean', 'champagne', 'charcoal',
'chartreuse', 'chestnut', 'chocolate', 'copper', 'crimson', 'cyan', 'ebony',
'emerald', 'gold', 'goldenrod', 'grey', 'gray', 'green', 'indigo', 'ivory',
'jade', 'khaki', 'lavender', 'lime', 'magenta', 'maroon', 'mauve', 'ochre',
'olive', 'orange', 'pearl', 'pink', 'plum', 'purple', 'blood-red', 'fire',
'engine-red', 'red', 'rose', 'rouge', 'rusty', 'saffron', 'scarlet', 'sepia',
'sienna', 'silver', 'tan', 'taupe', 'teal', 'turquoise', 'ultramarine',
'vermilion', 'vert', 'violet', 'white', 'yellow' ] 

color_additives = [
'hot','blood','sky','powder','sea','lime','forest','hunter','olive','emerald',
'pale','brownish','vivid','rosy','dull','pale','deep','rich','lime','bright','metalic','light','dark','reddish','yellowish','orangish','pinkish']

adjectives = [ 'adorable', 'adventurous', 'aggressive', 'alert', 'attractive',
'average', 'beautiful', 'blue-eyed ', 'bloody', 'blushing', 'bright', 'clean',
'clear', 'cloudy', 'colorful', 'crowded', 'cute', 'dark', 'drab', 'distinct',
'dull', 'elegant', 'excited', 'fancy', 'filthy', 'glamorous', 'gleaming',
'gorgeous', 'graceful', 'grotesque', 'handsome', 'homely', 'light', 'long',
'magnificent', 'misty', 'motionless', 'muddy', 'old-fashioned', 'plain',
'poised', 'precious', 'quaint', 'shiny', 'smoggy', 'sparkling', 'spotless',
'stormy', 'strange', 'ugly', 'ugliest', 'unsightly', 'unusual', 'wide-eyed',
'alive', 'annoying', 'bad', 'better', 'beautiful', 'brainy', 'breakable',
'busy', 'careful', 'cautious', 'clever', 'clumsy', 'concerned', 'crazy',
'curious', 'dead', 'different', 'difficult', 'doubtful', 'easy', 'expensive',
'famous', 'fragile', 'frail', 'gifted', 'helpful', 'helpless', 'horrible',
'important', 'impossible', 'inexpensive', 'innocent', 'inquisitive', 'modern',
'mushy', 'odd', 'open', 'outstanding', 'poor', 'powerful', 'prickly', 'puzzled',
'real', 'rich', 'shy', 'sleepy', 'stupid', 'super', 'talented', 'tame',
'tender', 'tough', 'uninterested', 'vast', 'wandering', 'wild', 'wrong',
'angry', 'annoyed', 'anxious', 'arrogant', 'ashamed', 'awful', 'bad',
'bewildered', 'black', 'blue', 'bored', 'clumsy', 'combative', 'condemned',
'confused', 'crazy', 'flipped-out', 'creepy', 'cruel', 'dangerous', 'defeated',
'defiant', 'depressed', 'disgusted', 'disturbed', 'dizzy', 'dull',
'embarrassed', 'envious', 'evil', 'fierce', 'foolish', 'frantic', 'frightened',
'grieving', 'grumpy', 'helpless', 'homeless', 'hungry', 'hurt', 'ill', 'itchy',
'jealous', 'jittery', 'lazy', 'lonely', 'mysterious', 'nasty', 'naughty',
'nervous', 'nutty', 'obnoxious', 'outrageous', 'panicky', 'repulsive', 'scary',
'selfish', 'sore', 'tense', 'terrible', 'testy', 'thoughtless', 'tired',
'troubled', 'upset', 'uptight', 'weary', 'wicked', 'worried', 'agreeable',
'amused', 'brave', 'calm', 'charming', 'cheerful', 'comfortable', 'cooperative',
'courageous', 'delightful', 'determined', 'eager', 'elated', 'enchanting',
'encouraging', 'energetic', 'enthusiastic', 'excited', 'exuberant', 'fair',
'faithful', 'fantastic', 'fine', 'friendly', 'funny', 'gentle', 'glorious',
'good', 'happy', 'healthy', 'helpful', 'hilarious', 'jolly', 'joyous', 'kind',
'lively', 'lovely', 'lucky', 'nice', 'obedient', 'perfect', 'pleasant', 'proud',
'relieved', 'silly', 'smiling', 'splendid', 'successful', 'thankful',
'thoughtful', 'victorious', 'vivacious', 'witty', 'wonderful', 'zealous',
'zany', 'broad', 'chubby', 'crooked', 'curved', 'deep', 'flat', 'high',
'hollow', 'low', 'narrow', 'round', 'shallow', 'skinny', 'square', 'steep',
'straight', 'wide', 'big', 'colossal', 'fat', 'gigantic', 'great', 'huge',
'immense', 'large', 'little', 'mammoth', 'massive', 'miniature', 'petite',
'puny', 'scrawny', 'short', 'small', 'tall', 'teeny', 'tiny', 'cooing',
'deafening', 'faint', 'harsh', 'high-pitched','hissing', 'hushed', 'husky',
'loud', 'melodic', 'moaning', 'mute', 'noisy', 'purring', 'quiet', 'raspy',
'resonant', 'screeching', 'shrill', 'silent', 'soft', 'squealing', 'thundering',
'voiceless', 'whispering', 'ancient', 'brief', 'Early', 'fast', 'late', 'long',
'modern', 'old', 'old-fashioned', 'quick', 'rapid', 'short', 'slow', 'swift',
'young', 'bitter', 'delicious', 'fresh', 'juicy', 'ripe', 'rotten', 'salty',
'sour', 'spicy', 'stale', 'sticky', 'strong', 'sweet', 'tart', 'tasteless',
'tasty', 'thirsty', 'fluttering', 'fuzzy', 'greasy', 'grubby', 'hard', 'hot',
'icy', 'loose', 'melted', 'nutritious', 'plastic', 'prickly', 'rainy', 'rough',
'scattered', 'shaggy', 'shaky', 'sharp', 'shivering', 'silky', 'slimy',
'slippery', 'smooth', 'soft', 'solid', 'steady', 'sticky', 'tender', 'tight',
'uneven', 'weak', 'wet', 'wooden', 'yummy', 'boiling', 'breezy', 'broken',
'bumpy', 'chilly', 'cold', 'cool', 'creepy', 'crooked', 'cuddly', 'curly',
'damaged', 'damp', 'dirty', 'dry', 'dusty', 'filthy', 'flaky', 'fluffy',
'freezing', 'hot', 'warm', 'wet', 'abundant', 'empty', 'few', 'heavy', 'light',
'many', 'numerous', 'substantial']

animals = [ 'Bison', 'Carabao', 'Cattle', 'Water Buffalo', 'Domesticated Yak',
'Llama', 'Camel', 'Dog', 'Poi dog', 'Nureongi', 'Xoloitzcuintle', 'Goat', 'Cat',
'Donkey', 'Horse', 'Rabbit', 'Kangaroo', 'sheep', 'Guinea pig', 'mouse', 'pig',
'warthog', 'Moose', 'Reindeer', 'deer', 'Elk', 'Chicken', 'duck', 'goose',
'turkey', 'Quail', 'Ostrich', 'Emu', 'Pigeon', 'Frog', 'Fish', 'Carp',
'Catfish', 'Salmon', 'Tilapia', 'worm', 'Silkworm', 'Crayfish', 'Lobster',
'Shrimp', 'Prawn', 'Oyster', 'Mussel', 'Snail', 'Alligator', 'Crocodile',
'Turtle' ]

from random import choice
import os
import csv
import json
from .random_sources.state_capitals import state_capitals
from .random_sources.presidents import presidents
from .random_sources.high_school_musicals import musicals
from .random_sources.flowers import flowers
from .random_sources.democoursedata import course_data
from .random_sources.job_titles import job_title_parts

from .randomer import Randomer

RANDOM_BASE_DIR = os.path.dirname(__file__)

NAMES = None
def load_names():
  global NAMES
  NAMES = {'male':[],'female':[],'last':[]}
  try:
    NAMES = json.load(os.path.join(RANDOM_BASE_DIR,'names_csv','all_names.json'))
  except Exception as err:

    names_loaded = csv.DictReader(open(os.path.join(RANDOM_BASE_DIR,'names_csv','all_names.csv'),'rU')) 
    for n in names_loaded:
      if n['gender']=='m':
        NAMES['male'].append(n['name'])
      if n['gender']=='f':
        NAMES['female'].append(n['name'])
      if n['gender'] =='na' and n['type'] =='last':
        NAMES['last'].append(n['name'])
    json.dumps(NAMES,os.path.join(RANDOM_BASE_DIR,'names_csv','all_names.json'))

def random_animal():
  return " ".join((choice(adjectives).capitalize(),choice(colors).capitalize(),choice(animals).capitalize()))


def random_name(gender="either"):
  if not NAMES:
    # load male names
    load_names()

  if gender !='either':
    first_name = choice(NAMES[gender])
  else:
    first_name = choice(NAMES[choice(('male','female'))])

  last_name = choice(NAMES['last'])

  return first_name,last_name

def random_course():
    return choice(course_data)

def random_flower():
  return choice(flowers)

def random_highschool_musical():
  return choice(musicals)

def random_president():
  return choice(presidents)

def random_capital():
  return choice(state_capitals)[1]

def random_state():
  return choice(state_capitals)[0]

def random_state_and_capital():
  return choice(state_capitals)

def random_job_title():
  return ' '.join((choice(job_title_parts[0]),choice(job_title_parts[1]),choice(job_title_parts[2])))
