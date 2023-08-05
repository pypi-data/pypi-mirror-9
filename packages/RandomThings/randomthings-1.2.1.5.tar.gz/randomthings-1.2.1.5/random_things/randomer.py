# -*- coding: utf-8 -*-
import csv,sqlite3
class Randomer(object):
  def __init__(self,db=None):
    self.db = db

  def validate_db(self):
    """A Database should have several attributes:
    - raw_source
      - A csv file with at least one column
    - selection order
      - list of columns to select from.  For example, ('first_name','last_name')
      - if no selection order is given, the randomer will select one value from each column
    - separator
      - default to a single space
    - Future possibilities:
      - Support uniqueness guarantees
      - Support DB as source
    """
    if not type(self.db) == dict:
      raise Exception('invalid database, not a dictionary')
    if not self.db.haskey('raw_source'):
      raise Exception('invalid database, no raw_source key')
    if not os.path.exists(self.db['raw_source']):
      raise Exception('invalid database, source file does not exist')

    # Initialize CSV file save iterator to self.db_values
    # self.db_values is a dictionary with a key for each column
    self.db_values = csv.DictReader(open(self.db['raw_source'],'rU'))

  def import_csv(self):

    persons= csv.reader(open("users.csv"))
    con = sqlite3.connect(":memory:")

    con.execute("create table person(firstname, lastname)")
    con.executemany("insert into person(firstname, lastname) values (?, ?)", persons)

    for row in con.execute("select firstname, lastname from person"):
        print(row)
