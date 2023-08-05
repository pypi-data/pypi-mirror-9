.. role:: bash(code)
   :language: bash

I needed a way to generate random text strings for a variety of things. This module was
created to fit the bill. You might find it useful as well.

Installation
------------
Install this module with the standard :bash:`pip install randomthings`.

Usage
-----
This module is a stand python module. Here are some examples of random things you can
generate with it.

import random_things

.. code:: python 

  >>> random_things.random_course()
  'Hepatology'
  >>> random_things.random_job_title()
  'King of Town'
  >>> random_things.random_animal()
  'Rapid yellow snake'
  >>> random_things.random_name()
  ('Carl','Banks')
  >>> random_things.random_flower()
  {'common_name': 'love-in-a-mist', 'botonical_name': 'nigella', 'meaning': ''}

There are others. Here is the full list as of 1.2.1.3:
 - random_animal             
 - random_capital            
 - random_course             
 - random_flower             
 - random_highschool_musical 
 - random_job_title          
 - random_name               
 - random_president
 - random_sources 
 - random_state              
 - random_state_and_capital  



