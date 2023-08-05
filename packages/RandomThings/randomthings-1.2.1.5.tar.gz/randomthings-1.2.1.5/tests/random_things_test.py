#!/usr/bin/env python

import os.path
import random_things

from unittest import TestCase

class TestRandomCalls(TestCase):

    
  def test_gets_course(self):
    course = random_things.random_course()
    self.assertIsInstance(course,dict)
    course_keys = ('name','dept','short_name')
    self.assertEqual(sorted(course.keys()),sorted(course_keys))

  def test_get_random_title(self):
    title = random_things.random_job_title()
    self.assertIsInstance(title,str)

  def test_random_animal(self):
    self.assertIsInstance(random_things.random_animal(),str)

  def test_random_name(self):
    name = random_things.random_name()
    self.assertIsInstance(name,tuple)
    self.assertNotEqual('',name[0])
    self.assertNotEqual('',name[1])


  def test_random_flower(self):
    flower = random_things.random_flower()
    flower_keys = ("common_name", "botonical_name", "meaning")
    self.assertEqual(sorted(flower.keys()),sorted(flower_keys))


  def test_random_highschool_musical(self):
    musical = random_things.random_highschool_musical()
    self.assertNotEqual('',musical)

  def test_random_president(self):
    pres = random_things.random_president()
    pres_keys = ('# of electoral votes','% electoral', ' National total votes ', 'Age at inauguration', 'Years in office', 'Rating points', '% popular', 'Year first inaugurated', 'Total electoral votes', ' # of popular votes ', 'College', 'President', 'Political Party', 'State elected from', 'Occupation')
    self.assertEqual(sorted(pres.keys()),sorted(pres_keys))

  def test_random_capital(self):
    capital = random_things.random_capital()
    self.assertIsInstance(capital,str)

  def test_random_state(self):
    state = random_things.random_state()
    self.assertIsInstance(state,str)

  def test_random_state_and_capital(self):
    state_and_capital = random_things.random_state_and_capital()
    self.assertIsInstance(state_and_capital,tuple)
    self.assertNotEqual('',state_and_capital[0])
    self.assertNotEqual('',state_and_capital[1])

root_dir = os.path.dirname(os.path.realpath(__file__))
class TestClientDB(TestCase):
  def test_load_bad_db(self):
    db = dict(
      raw_source = os.path.join(root_dir,'bad_db.txt'),
    )
    self.assertRaises(Exception,random_things.Randomer(db))

    self.assertRaises(Exception,random_things.Randomer('justastring'))
