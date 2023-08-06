"""openbts.components
manages components in the OpenBTS application suite
"""

from openbts.core import BaseComponent
from openbts.exceptions import InvalidRequestError

class OpenBTS(BaseComponent):
  """Manages communication to an OpenBTS instance.

  Args:
    address: tcp socket for the zmq connection
  """

  def __init__(self, **kwargs):
    address = kwargs.pop('address', 'tcp://127.0.0.1:45060')
    super(OpenBTS, self).__init__(**kwargs)
    self.socket.connect(address)

  def __repr__(self):
    return 'OpenBTS component'

  def monitor(self):
    """Monitor channel loads, queue sizes and noise levels.

    See 3.4.4 of the OpenBTS 4.0 Manual for more info.

    Returns:
      Response instance
    """
    message = {
      'command': 'monitor',
      'action': '',
      'key': '',
      'value': ''
    }
    return self._send_and_receive(message)


class SIPAuthServe(BaseComponent):
  """Manages communication to the SIPAuthServe service.

  Args:
    address: tcp socket for the zmq connection
  """

  def __init__(self, **kwargs):
    address = kwargs.pop('address', 'tcp://127.0.0.1:45064')
    super(SIPAuthServe, self).__init__(**kwargs)
    self.socket.connect(address)

  def __repr__(self):
    return 'SIPAuthServe component'

  def count_subscribers(self):
    """Counts the total number of subscribers.

    Returns:
      integer number of subscribers
    """
    try:
      result = self.get_subscribers()
      return len(result)
    except InvalidRequestError:
      # 404 -- no subscribers found.
      return 0

  def get_subscribers(self, imsi=None):
    """Gets subscribers, optionally filtering by IMSI.

    Args:
      imsi: the IMSI to search by

    Returns:
      an array of subscriber dicts, themselves of the form: {
        'name': 'IMSI000123',
        'ip': '127.0.0.1',
        'port': '8888',
        'numbers': ['5551234', '5556789'],
        'account_balance': '1000',
      }

    Raises:
      InvalidRequestError if no qualified entry exists
    """
    qualifiers = {}
    if imsi:
      qualifiers['name'] = imsi
    fields = ['name', 'ipaddr', 'port']
    message = {
      'command': 'sip_buddies',
      'action': 'read',
      'match': qualifiers,
      'fields': fields,
    }
    try:
      response = self._send_and_receive(message)
      subscribers = response.data
    except InvalidRequestError:
      subscribers = []
    # Now attach the associated numbers, account balance and caller_id info.
    for subscriber in subscribers:
      subscriber['numbers'] = self.get_numbers(subscriber['name'])
      subscriber['account_balance'] = self.get_account_balance(
          subscriber['name'])
      subscriber['caller_id'] = self.get_caller_id(subscriber['name'])
    return subscribers

  def get_ipaddr(self, imsi):
    """Get the IP address of a subscriber."""
    fields = ['ipaddr']
    qualifiers = {
      'name': imsi
    }
    message = {
      'command': 'sip_buddies',
      'action': 'read',
      'match': qualifiers,
      'fields': fields,
    }
    response = self._send_and_receive(message)
    return response.data[0]['ipaddr']

  def get_port(self, imsi):
    """Get the port of a subscriber."""
    fields = ['port']
    qualifiers = {
      'name': imsi
    }
    message = {
      'command': 'sip_buddies',
      'action': 'read',
      'match': qualifiers,
      'fields': fields,
    }
    response = self._send_and_receive(message)
    return response.data[0]['port']

  def get_caller_id(self, imsi):
    """Get the caller ID of a subscriber."""
    fields = ['callerid']
    qualifiers = {
      'name': imsi
    }
    message = {
      'command': 'sip_buddies',
      'action': 'read',
      'match': qualifiers,
      'fields': fields,
    }
    response = self._send_and_receive(message)
    return response.data[0]['callerid']

  def get_numbers(self, imsi=None):
    """Get just the numbers (exten) associated with an IMSI.

    If imsi is None, get all dialdata.
    """
    fields = ['exten']
    qualifiers = {}
    if imsi:
      qualifiers['dial'] = imsi
    message = {
      'command': 'dialdata_table',
      'action': 'read',
      'match': qualifiers,
      'fields': fields,
    }
    response = self._send_and_receive(message)
    return [d['exten'] for d in response.data]

  def add_number(self, imsi, number):
    """Associate a new number with an IMSI.

    If the number's already been added, do nothing.
    """
    if number in self.get_numbers(imsi):
      return False
    message = {
      'command': 'dialdata_table',
      'action': 'create',
      'fields': {
        'dial': str(imsi),
        'exten': str(number),
      }
    }
    return self._send_and_receive(message)

  def delete_number(self, imsi, number):
    """De-associate a number with an IMSI."""
    # First see if the number is attached to the subscriber.
    numbers = self.get_numbers(imsi)
    if number not in numbers:
      raise ValueError('number %s not attached to IMSI %s' % (number, imsi))
    # Check if this is the only associated number.
    if len(numbers) == 1:
      raise ValueError('cannot delete number %s as it is the only number'
                       ' associated with IMSI %s' % (number, imsi))
    # See if this number is the caller ID.  If it is, promote another number
    # to be caller ID.
    if number == self.get_caller_id(imsi):
      numbers.remove(number)
      new_caller_id = numbers[-1]
      self.update_caller_id(imsi, new_caller_id)
    # Finally, delete the number.
    message = {
      'command': 'dialdata_table',
      'action': 'delete',
      'match': {
        'dial': str(imsi),
        'exten': str(number),
      }
    }
    result = self._send_and_receive(message)
    return result

  def create_subscriber(self, imsi, msisdn, ipaddr, port, ki=''):
    """Add a subscriber.

    Technically we don't need every subscriber to have a number, but we'll just
    enforce this by convention.  We will also set the convention that a
    subscriber's name === their imsi.  Some things in NM are keyed on 'name'
    however, so we have to use both when making queries and updates.

    If the 'ki' argument is given, OpenBTS will use full auth.  Otherwise the
    system will use cache auth.  The values of IMSI, MSISDN and ki will all
    be cast to strings before the message is sent.

    Args:
      imsi: IMSI of the subscriber
      msisdn: MSISDN of the subscriber (their phone number)
      ipaddr: IP of the subscriber's OpenBTS instance
      port: port of the subscriber's OpenBTS instance
      ki: authentication key of the subscriber

    Returns:
      Response instance

    Raises:
      ValueError if the IMSI is already registered
    """
    # First we search for this IMSI to see if it is already registered.
    result = self.get_subscribers(imsi=imsi)
    if result:
      raise ValueError('IMSI %s is already registered.' % imsi)
    message = {
      'command': 'subscribers',
      'action': 'create',
      'fields': {
        'imsi': str(imsi),
        'msisdn': str(msisdn),
        'ipaddr': str(ipaddr),
        'port': str(port),
        'name': str(imsi),
        'ki': str(ki)
      }
    }
    response = self._send_and_receive(message)
    self.add_number(imsi, msisdn)
    return response

  def delete_subscriber(self, imsi):
    """Delete a subscriber by IMSI.

    Args:
      imsi: the IMSI of the to-be-deleted subscriber

    Returns:
      Response instance
    """
    message = {
      'command': 'subscribers',
      'action': 'delete',
      'match': {
        'imsi': str(imsi)
      }
    }
    response = self._send_and_receive(message)
    return response

  def update_ipaddr(self, imsi, new_ipaddr):
    """Updates a subscriber's IP address."""
    message = {
      'command': 'sip_buddies',
      'action': 'update',
      'match': {
        'name': imsi
      },
      'fields': {
        'ipaddr': new_ipaddr
      }
    }
    return self._send_and_receive(message)

  def update_port(self, imsi, new_port):
    """Updates a subscriber's port."""
    message = {
      'command': 'sip_buddies',
      'action': 'update',
      'match': {
        'name': imsi
       },
      'fields': {
        'port': new_port,
       }
    }
    return self._send_and_receive(message)

  def update_caller_id(self, imsi, new_caller_id):
    """Updates a subscriber's caller_id."""
    if new_caller_id not in self.get_numbers(imsi):
      raise ValueError('new caller id %s is not yet associated with subscriber'
                       ' %s' % (new_caller_id, imsi))
    message = {
      'command': 'sip_buddies',
      'action': 'update',
      'match': {
        'name': imsi
       },
      'fields': {
        'callerid': new_caller_id,
       }
    }
    return self._send_and_receive(message)

  def get_imsi_from_number(self, number):
    """Translate a number into an IMSI.

    Args:
      number: a phone number

    Returns:
      the matching IMSI

    Raises:
      InvalidRequestError if the number does not exist
    """
    qualifiers = {
      'exten': number
    }
    fields = ['dial', 'exten']
    message = {
      'command': 'dialdata_table',
      'action': 'read',
      'match': qualifiers,
      'fields': fields,
    }
    result = self._send_and_receive(message)
    return result.data[0]['dial']

  def get_account_balance(self, imsi):
    """Get the account balance of a subscriber."""
    fields = ['account_balance']
    qualifiers = {
      'name': imsi
    }
    message = {
      'command': 'sip_buddies',
      'action': 'read',
      'match': qualifiers,
      'fields': fields,
    }
    response = self._send_and_receive(message)
    return response.data[0]['account_balance']

  def update_account_balance(self, imsi, new_account_balance):
    """Updates a subscriber's account_balance.

    Args:
      imsi: the subscriber-of-interest
      new_account_balance: value of the new balance (str)

    Raises:
      TypeError if the new balance is not a string
    """
    if not isinstance(new_account_balance, str):
      raise TypeError
    message = {
      'command': 'sip_buddies',
      'action': 'update',
      'match': {
        'name': imsi
      },
      'fields': {
        'account_balance': new_account_balance
      }
    }
    return self._send_and_receive(message)


class SMQueue(BaseComponent):
  """Manages communication to the SMQueue service.

  Args:
    address: tcp socket for the zmq connection
  """

  def __init__(self, **kwargs):
    address = kwargs.pop('address', 'tcp://127.0.0.1:45063')
    super(SMQueue, self).__init__(**kwargs)
    self.socket.connect(address)

  def __repr__(self):
    return 'SMQueue component'
