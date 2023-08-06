#!/usr/local/bin/python2.7
# encoding: utf-8
'''
run -- shortdesc   

Script that can be used for Running the Python Utility Deadcheck from the CLI

@author:    Harsha Narayana
        
@copyright: 2013. All rights reserved.
        
@license:   MIT

@contact:   harsha2k4@gmail.com

@change:    2013-12-09     : Initial Draft
            2013-12-13     : Script Updated to Support the Usage of the Report generation module to 
                             create a Report based on the depth of link being processed. 
            2015-03-10     : Converted -out Parameter to Mandatory Parameter. 
'''

__verion__ = "0.0.3"
__date__ = "09th December 2013"
__author__ = "Harsha Narayana"

import argparse
from deadcheck.deadcheck import Deadcheck
from deadcheck.report.Report import Report
import deadcheck.report
import os

# Parser For CLI using argparse utility. 
parser = argparse.ArgumentParser(description='CLI Parser / Run Utility for deadcheck Tool.')

def checkKey(key):
    return args.__dict__.has_key(key) and args.__dict__[key] != None

def printError(message):
    print("ERROR : %s" %(message))

def checkAndValidate():
    if ( not checkKey('_url') and ('http' not in args.__dict__['_url'] or '://' not in args.__dict__['_url'])):
        printError('-url is a mandatory Argument and it must consist of http(s)://')

def runScript():
    dCheck = Deadcheck(args.__dict__['_url'], proxy=args.__dict__['_proxy'], username=args.__dict__['_username'], password=args.__dict__['_password']
                       , auth_base=args.__dict__['_auth_base'], verbose=args.__dict__['_verbose'], log=args.__dict__['_log'], 
                       exempt=args.__dict__['_exempt'], depth=args.__dict__['_depth'])
    
    if ( not os.path.isdir(args.__dict__['_out']) and args.__dict__['_out'] != None):
        os.mkdir(args.__dict__['_out'])
        
    dCheck.process()
    return dCheck

def printDetails(dCheck):
    outFile = open('report.txt','w')
    for key in range(args.__dict__['_depth']+1):
        fileCount = 0
        for elements in dCheck.getAll()[key]:
            if ( args.__dict__['_out'] != None ):
                rptPath = os.path.join(args.__dict__['_out'],'level'+str(key))
                if ( not os.path.isdir(rptPath)):
                    os.mkdir(os.path.join(args.__dict__['_out'],'level'+str(key)))
                rptFile = os.path.join(rptPath, 'file'+str(fileCount)+'.html')
                fileCount += 1 
                rpt = Report(elements, rptFile, os.path.join(os.path.dirname(os.path.abspath(deadcheck.report.__file__)), 'Templates'))
                rptFile = rpt.generate()
                print 'File Name : ' + str(rptFile)
            for element in elements.getChildren():
                print '-----------------------------'
                print element.info()
                print '\n Number Of Children : ' + str(len(element.getChildren()))
                outFile.write("%s\n" %(element.info()))
    outFile.close()
            
parser.add_argument('-url', action='store', type=str, dest='_url',
                    metavar='BaseURLToAnalyze', required=True, help='Base URL of the Webpage on which the deadlinks are to be analyzed.')

parser.add_argument('-proxy', action='store', type=str, dest='_proxy',
                    metavar='ProxyURL', help='Proxy URL in http(s)://<proxyAddress>:<port> format.')

parser.add_argument('-username', action='store', type=str, dest='_username',
                    metavar='Username', help='User name to be used for accessing password Protected pages. If any.')

parser.add_argument('-password', action='store', type=str, dest='_password',
                    metavar='Password', help='Password that needs to be used for accessing protected pages. If any.')

parser.add_argument('-auth_base', action='store', type=str, dest='_auth_base',
                    metavar='BaseURL/SuperURL', help='Super URL that needs to be used for Authenticating Password Protected pages. If no value is provided, base URl is used. ')

parser.add_argument('-log', action='store', type=str, dest='_log',
                    metavar='Logfile', help='Log file that needs to be used for Storing log information.')

parser.add_argument('-exempt', action='store', type=str, dest='_exempt',
                    metavar='ExceptionFile', help='Exception file containing a list of URL that needs to be exempted. One entry per line. Or use Wildcard Entries. ')

parser.add_argument('-depth', action='store', type=int, dest='_depth',
                    metavar='Depth', default=1, help='Depth to which the links are to be analyzed. Default = 1')

parser.add_argument('-v', action='store_true', dest='_verbose', default=True, help='Choose if the logs are to be displayed in the CLI')

parser.add_argument('-out', action='store', type=str, dest='_out',
                    metavar='OututDirectory', required=True, help='Output Directory to generate the reports.')

args = parser.parse_args()

d = runScript()
printDetails(d)
