'''
Created on Dec 4, 2013

A custom Error Handler class created for Custom Errors. 

@author: harshanarayana

@change:     2013-12-04    Initial Draft. A custom Class that can be used for Handling Custom Exceptions. Additional Info will be added 
                           during the course of development. 
             2013-12-17    Documentaion Updated. 
'''
__version__ = "0.0.1"
__date__ = "06th December 2013"
__author__ = "Harsha Narayana"

class ArgumentMissingError(Exception):
    
    def __init__(self, message, argName):
        self.__argName = argName
        self.__message = message

    def get_arg_name(self):
        return self.__argName


    def get_message(self):
        return self.__message


    def set_arg_name(self, value):
        self.__argName = value


    def set_message(self, value):
        self.__message = value

    def __str__(self, *args, **kwargs):
        return repr(self.message)
    
    arg = property(get_arg_name, set_arg_name, "Missing Argument in the Input")
    message = property(get_message, set_message, "Error Message to display")