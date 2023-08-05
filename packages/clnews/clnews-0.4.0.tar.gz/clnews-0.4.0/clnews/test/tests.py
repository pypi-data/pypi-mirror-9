#!/usr/bin/env python

import unittest
import datetime
import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '../'))

from news import * 
from shell import *
from data_structure import *
from exception import *
import config

class TestNews(unittest.TestCase):

    def setUp(self):
        self.url = 'http://rss.cnn.com/rss/edition_world.rss'
        self.channel = Channel('cnn', self.url)
        self.event = Event('title', 'url', datetime.datetime.now())

    # test Event
    def test_event_object(self):
        # invalid date
        # event = Event('title', 'url', 'string date')

        self.assertEqual(str(self.event), "%s, %s" % (self.event.title, 
                         self.event.url))

    def test_remove_html(self):
        html = '<div class"class">test test test<img src="src"/></div>'
        output = self.event._remove_html(html)
        self.assertEqual(output, 'test test test')

    # test Channel
    def test__get_data(self):
        data = self.channel._get_data()
        self.assertTrue(isinstance(data, list))

        # corrupted url
        self.channel.url = self.url[:-15]
        self.assertRaises(ChannelDataNotFound, self.channel._get_data)

    def test_get_events(self):
        events = self.channel.get_events()
        self.assertTrue(isinstance(events, list))
        self.assertTrue(isinstance(events[0], Event))
        self.assertEqual(str(events[0]), "%s, %s" % (events[0].title, 
                         events[0].url))


class TestCommand(unittest.TestCase):
    def setUp(self):
        self.command = Command('name', 'desc')

    def test_command_list(self):
        command = CommandList()
        command.execute()
        self.assertTrue(isinstance(command.buffer, list))
        self.assertTrue(isinstance(command.buffer[0], tuple))

        channels = config.CHANNELS
        keys = channels.keys()
        self.assertEqual(command.buffer, 
                         [(ch, channels[ch]["name"]) for ch in keys])
        
    def test_test_command_get(self):
        channel_name = 'cnn'
        channel_url = 'http://rss.cnn.com/rss/edition_world.rss'
        ch = Channel(channel_name, channel_url)
        command = CommandGet(channel_name, channel_url)
        
        events = ch.get_events()
        command.execute()
        self.assertEqual(len(events), len(command.buffer))


class TestShell(unittest.TestCase):

    def setUp(self):
        self.shell = Shell()

    def test_analyse_input(self):
        # command does not exist
        
        self.assertRaises(ShellCommandDoesNotExist, 
                          self.shell._analyse_input, 'false_command')

        # test .help command
        output = self.shell._analyse_input('.help')
        self.assertTrue(isinstance(output, CommandHelp))

        # test .list command
        output = self.shell._analyse_input('.list')
        self.assertTrue(isinstance(output, CommandList))

        # test .get with few options
        self.assertRaises(ShellCommandChannelNotFound, 
                          self.shell._analyse_input, '.get')

        # test .get with not available channel
        self.assertRaises(ShellCommandChannelNotFound, 
                          self.shell._analyse_input, '.get false_channel')
        

if __name__ == '__main__':
    unittest.main()
