#!/usr/bin/env python
# coding=utf-8

import os
import threading
import subprocess
import signal

try:
    from commands import getoutput
    def command_exist(command_string):
        return getoutput('which ' + \
                         command_string.split(' ')[0])
except ImportError:
    def command_exist(command_string):
        # return subprocess.Popen(
        #    ['which', 
        #     command_string.split(' ')[0]])
        return os.path.exists(os.path.join('/usr/bin', 
                                           command_string.split(' ')[0]))
        

class BasePlayer:
    def __init__(self, play_file):
        self.__sys_player = 'mplayer' # default
        self.__stdin = None # subprocess.PIPE
        self.__stdout = subprocess.PIPE
        self.__stderr = subprocess.PIPE

        self.__play_file = play_file # local or remote
        self.__player_handler = ''
        self.__pause_flag = False

        self._set_sys_player(['mpg123', 'madplay'])
        
    def _set_sys_player(self, sys_player_list):
        for each in sys_player_list:
            if command_exist(each):
                self.__sys_player = each
                return self.__sys_player

    def _handler(self):
        assert self.__play_file

        self.__player_handler = subprocess.Popen(
            [
                self.__sys_player, self.__play_file, 
            ], 
            stdin=self.__stdin, 
            stdout=self.__stdout, 
            stderr=self.__stderr)
        return self.__player_handler

    def _exchange_status(self, send_signal=None):
        if not send_signal:
            return self.__player_handler

        self.__player_handler.send_signal(send_signal)
        return self.__player_handler

    def switch(self):
        if not self.__pause_flag:
            return self.pause()
        return self.resume()
        
    def stop(self):
        assert self.__player_handler
        return self._exchange_status(signal.SIGQUIT)

    def start(self):
        return self._handler()

    def pause(self):
        assert self.__player_handler
        self.__pause_flag = True
        return self._exchange_status(signal.SIGSTOP)

    def resume(self):
        assert self.__player_handler
        self.__pause_flag = False
        return self._exchange_status(signal.SIGCONT)


