"""
.. module:: news
   :platform: Unix
      :synopsis: This module contains the interface of the events' retrieval 

      .. moduleauthor:: Alexandros Ntavelos <a.ntavelos@gmail.com>

      """
import re
import datetime
import feedparser

from exception import ChannelDataNotFound, ChannelServerError, \
ChannelRetrieveEventsError

class Event(object):
    """ Wraps up the data of an event."""

    def __init__(self, title, url, date, summary=""):
        """ Initializes the class.
                
        Args: 
            title (str): The title of the event.
            url (str): The URL of the event    
            date (str): The date of the event.
        
        Kwargs:
            summary (str): The summary title of the event.
        """
        self.title = title
        self.url = url
        self.date = date
        self.summary = self._remove_html(summary)

    def _remove_html(self, str):
        p = re.compile(r'<.*?>')
        str = p.sub('', str)
        
        return str

    def __repr__(self):
        return "%s, %s" % (self.title, self.url)

class Channel(object):
    """ Implements the Channel functionality."""


    def __init__(self, name, url):
        """ Initializes the class.

        Args:
            name (str): The name of the channel.
            url (str): The URL of the channel.
        """
        self.name = name
        self.url = url
        self.events = []

    def _get_data(self):
        
       response = feedparser.parse(self.url)

       if response.status == 200:
           pass
       elif response.status == 404:
           raise ChannelDataNotFound
       else:
           raise ChannelServerError

       return response.entries

    def get_events(self):
        """ Retrieves the current events.

        Raises:
            ChannelRetrieveEventsError: An error occured while retrieving the
            events.
        """
        event_entries = self._get_data()
        
        try:
            self.events = [Event(e.title, e.link, e.published, e.summary) 
                           for e 
                           in event_entries]
        except TypeError:
            # when the event list is not a list as it should
            raise ChannelRetrieveEventsError

        return self.events

