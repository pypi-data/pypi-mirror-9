from bs4 import BeautifulSoup
import requests
import re
import html5lib

class Laundry(object):
  """The client for Laundry. Used to make requests to the API.

    Usage::

      >>> from penn import Laundry
      >>> l = Laundry()
  """

  def __init__(self):
    pass

  def all_status(self):
    """Return names, hall numbers, and the washers/dryers available for all rooms in the system

    >>> all_laundry = l.all_status()
    """
    r = requests.get('https://www.laundryalert.com/cgi-bin/penn6389/LMPage?Login=True')
    print r.status_code
    if r.status_code == 200:
      parsed = BeautifulSoup(r.text)
      info_table = parsed.find_all('table')[2]

      hall_dict = dict()

      # This bit of code generates a dict of hallname->hall number by
      # parsing the link href of each room
      for link in info_table.find_all('a', class_='buttlink'):
        def get_hall_no(href):
          return int(re.search(r"Halls=(\d+)", href).group(1))
        hall_dict[link.get_text().strip()] = get_hall_no(link.get('href'))

      # Parse the table into the relevant data
      data = [filter(lambda x: len(x) > 0, [val.get_text().strip() for val in row.find_all('td')]) for row in info_table.find_all('tr')]

      # Remove the header row and all empty rows
      data_improved = (filter(lambda x: len(x) > 0, data))[1:]

      # Construct the final JSON
      laundry_dict = dict()
      for row in data_improved[1:]:
        room_dict = dict()
        room_dict['washers_available'] = int(row[1])
        room_dict['dryers_available'] = int(row[2])
        room_dict['washers_in_use'] = int(row[3])
        room_dict['dryers_in_use'] = int(row[4])
        room_dict['hall_no'] = hall_dict[row[0]]
        laundry_dict[row[0]] = room_dict
      return laundry_dict


  def hall_status(self, hall_no):
    """Return the status of each specific washer/dryer in a particular laundry room.

    :param hall_no:
       integer corresponding to the id number for the hall. Thus number is returned as part of the all_status call.

    >>> english_house = l.hall_status(2)
    """
    try:
      num = int(hall_no)
    except ValueError:
      raise ValueError("Room Number must be integer")

    r = requests.get('https://www.laundryalert.com/cgi-bin/penn6389/LMRoom?Halls=' + str(num))
    if r.status_code == 200:
      parsed = BeautifulSoup(r.text, 'html5lib')
      tables = parsed.find_all('table')
      hall_name = tables[2].get_text().strip()
      info_table = tables[4]
      data = [filter(lambda x: len(x) > 0, [val.get_text().strip() for val in row.find_all('td')]) for row in info_table.find_all('tr')]
      data_improved = (filter(lambda x: len(x) > 0, data))[1:]
      def toDict(data_row):
        d = dict()
        d['number'] = data_row[0]
        d['machine_type'] = data_row[1]
        d['available'] = data_row[2] == u'Available'
        if len(data_row) == 4:
          d['time_left'] = data_row[3]
        else:
          d['time_left'] = None
        return d

      return {'machines': map(toDict, data_improved), 'hall_name': hall_name}
    else:
      return {'error': 'The laundry api is currently unavailable.'}
