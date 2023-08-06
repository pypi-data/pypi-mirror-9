'''
Created on Nov 29, 2013

A custom class that is used for Creating and Processing deadlink check related entities. 

This is the base class that is used from the Run script for the purpose of analyzing the deadlinks in a
base URL. 

@author: harshanarayana

@change:    2013-11-29    Initial Draft
            2013-12-06    Re-Structured the Code to support Data suitable for liche output format. 
            2013-12-10    Minor Chnages made into the Script to support the Report Generation.
            2013-12-17    Documentaiton Updated
            2014-03-27    __cleanupJavaScript functionality included to provide low level URL extraction for 
                          javascript:openWindow method used for URL Opening. <Further enhancement required>.
            2014-07-16    Additional Support for RegExp in Exemptions file and Logging Information Included.
            2014-07-17    Change Implemented to Avoid AttributeError When the RegExp Fails to Match the URL.
            2014-07-28    Additional class 'DeadcheckAPI' was included to support the Usage of the tool through
                          command line to perform the analysis of individual URLs
            2015-03-10    Proxy Support issue Fixed inside DeadcheckAPI
            2015-03-10    Authentication Support issue Fixed inside DeadcheckAPI
'''

__version__ = "0.0.8"
__date__ = "3rd March, 2015"
__author__ = "Harsha Narayana"


from ErrorHandler import ArgumentMissingError
from ErrorCodes import ErrorCodes
import logging
import urllib2
from lxml import etree
from URLLinks import URLLinks
import time
import urlparse
import httplib
import re

class Deadcheck(object):
    '''
        A custom class created for the Purpose of Handling the Deadlink analysis process. 
        
        This takes in the Arguments from either the CLI processed function call / object creation method and
        handles the arguments to process and extract necessary information. 
        
        These data so created are later used for the purpose of generating the report using Report modules. 
    '''
    
    # Hash used for Storing the Level Based URLLink Objects. Each level stores a list of object that belong to that specific level
    # and are valid for the purpose of Processing further. 
    __levelBasedLinks = {}
    # Hash used for storing the information of the URL that are already processed. This is used to avoid the ducplicate processing
    # of the links and hence saving considerable about of valuable time. 
    __ProcessedLinks = {}
    # List of Exempted links of Expressions. Any link matcing one or more entity in this array is exempted from processing. 
    __exemptedItems = []
         
    def __init__(self, url, proxy=None, username=None, password=None, auth_base=None, verbose=True, log=None, exempt=None, depth=1):
        '''
        Constructor. 
        
        @param url      : Base URL which needs to be analyzed for Deadlinks. 
        @param proxy    : Proxy URL that needs to be used in case if you are running the tool from a machine in which
                          access to the Internet is provided through a Proxy site.
                          Format : <proxyURL>:<port>
        @param username : Username that needs to be used for accesing a password protected page during analysis. If any. 
                          If no informaiton is provided, such links will be branded as WARNINGS. 
        @param passsword : Password for accessing protected page. 
        @param auth_base : Base URL that can be used to authenticate the Protected pages. If no value is provided, then base url
                           that is being analyzed itself is used as the SUPER URL. 
        @param exempt   : File containing the list of links that are to be exmepted. Or pattern which are to be considered for 
                          exempting the URL from processing. 
        @param verbose  : Dispaly STDOUT Messages during processing. 
        @param log      : Log file name. 
        @param depth    : Depth to which the links are to be processed. Default = 1. i.e All links that are part of the Base URL are 
                          processed and analyzed for deadlinks.
     
        '''
        self._url = url
        self._proxy = proxy
        self._username = username
        self._password = password
        self._auth_base = auth_base
        self._verbose = verbose
        self._log = log
        self._exempt = exempt
        self._depth = depth
        self.__verifyAndValidate()
        self.__checkAndSetUrlLib()
        self.__processBaseURL()

    def getAll(self):
        '''
        Get method of Level Based URLLink objects. 
        
        @return: Deadcheck.__levelBasedLinks
        '''
        return Deadcheck.__levelBasedLinks
    
    def get_depth(self):
        '''
        Get method for Depth
        '''
        return self._depth
    
    def set_depth(self,value):
        '''
        Set method for Depth
        '''
        self._depth = value
        
    def get_dict(self):
        '''
        Get method for __dict__ variable of Deadcheck class. 
        
        @return: self.__dict__
        '''
        return self.__dict__


    def get_url(self):
        '''
        Get method for URL
        '''
        return self.__url


    def get_proxy(self):
        
        '''
        Get method for Proxy
        '''
        return self.__proxy


    def get_verbose(self):
        '''
        Get metod for Verbose status
        '''
        return self.__verbose


    def get_log(self):
        '''
        Get method for Log file information
        '''
        return self.__log


    def get_exempt(self):
        '''
        Get method for Exempted file
        '''
        return self.__exempt


    def __set_url(self, value):
        self.__url = value


    def __set_proxy(self, value):
        self.__proxy = value


    def __set_username(self, value):
        self.__username = value


    def __set_password(self, value):
        self.__password = value


    def __set_auth_base(self, value):
        self.__auth_base = value


    def set_verbose(self, value):
        self.__verbose = value


    def set_log(self, value):
        self.__log = value


    def set_exempt(self, value):
        self.__exempt = value

        
    def __verifyAndValidate(self):
        '''
        Private member that is called from __init__ to verify and validate the Arguments that are used for creating
        Deadcheck type of Objects. 
        '''
        self.__checkAndSetLog()    
        if ( not self.__checkKey('_url')):
            raise ArgumentMissingError('Paramenter for argument \'-url\' is missing.','-url')
        
        if ( not self.__checkKey('_proxy')):
            self.__printWarning('No Proxy Information provided. If you are running the tool on a machine that accesses internet through Proxy, the check will fail.')
        
        if (self.__checkKey('_username') and self.__checkKey('_password')):
            if ( not self.__checkKey('_auth_base')):
                self.__printWarning('No super URL provided for Authenticating password Protected pages. Base URL will be used instead.')
        else:
            self.__printWarning('No password protected pages will be processed.')
        
        if ( not self.__checkKey('_exempt')):
            self.__printMessage('No exemptions file provided. All the links will be considered valid.')
            
    
    def __checkAndSetUrlLib(self):
        '''
        Private member function called for Analyzing and setting Proxy settings for the urllib2. 
        
        This helps in accessing and downloading the contenst from the web for later processing and
        parsing of the contents.
        '''
        __proxy = None
        __auth = None
        __opener = None
        
        if ( self.__checkKey('_proxy')):
            __proxy = urllib2.ProxyHandler({'http':self.__dict__['_proxy'], 'https':self.__dict__['_proxy']})
            __opener = urllib2.build_opener(__proxy)
            
        if ( self.__checkKey('_username') and self.__checkKey('_password')):
            passManager = urllib2.HTTPPasswordMgrWithDefaultRealm()
            if ( self.__checkKey('_auth_base')):
                passManager.add_password(None, self.__dict__['_auth_base'], self.__dict__['_username'], self.__dict__['_password'])
            else:
                passManager.add_password(None, self.__dict__['_url'], self.__dict__['_username'], self.__dict__['_password'])
            
            __auth = urllib2.HTTPBasicAuthHandler(passManager)
            __opener = urllib2.build_opener(__auth)
            
        if ( __opener != None ):
            urllib2.install_opener(__opener)
            
    def __checkAndSetLog(self):
        '''
        Private member function used for Settingup configuration of the logger module. 
        '''
        if ( self.__checkKey('_verbose')):
            if ( self.__checkKey('_log')):
                logging.basicConfig(level=logging.DEBUG, filename=self.__dict__['_log'], format='%(name)s : %(levelname)s : %(message)s')
            else:
                logging.basicConfig(level=logging.DEBUG, format='%(name)s : %(levelname)s : %(message)s')
        else:
            logging.basicConfig(level=logging.ERROR)
    
    def __size(self, size):
        '''
        Private member function used for Converting bytes into Human readable file size for display purpose. 
        
        '''
        for x in ['bytes','KB','MB','GB']:
            if size < 1024.0 and size > -1024.0:
                return "%3.1f%s" % (size, x)
            size /= 1024.0
        return "%3.1f%s" % (size, 'TB')
     
    def __checkIfError(self, value):
        '''
        Private member function to check if the Value retured from the function __getDataFromURL is an Errors. 
        
        '''
        if ( 'HTTPError' in value or 'URLError' in value or 'HTTPException' in value or 'Generic Exception' in value):
            return True
        else:
            return False
    def __raiseError(self, value, *url):
        '''
        Private member function used for raising different types of Errors that one may encounter 
        during the processign or downloading of the page. 
        
        This value is used for setting the status of the URLLinks objects and the same is used for 
        reporting purpose later on. 
        '''
        if ( value[0] == 'HTTPError'):
            eCode = ErrorCodes(int(value[1]))
            raise urllib2.HTTPError(url[0], int(value[1]), eCode.getError(), None, None)
        elif ( value[0] == 'URLError'):
            raise urllib2.URLError(value[1])
        elif ( value[0] == 'HTTPException'):
            raise httplib.HTTPException(value[1])
        elif ( value[0] == 'Generic Exception'):
            raise Exception(value[0] + ' : ' + value[1])
        
    def __processBaseURL(self):
        '''
        Private member function used for Processing the base URL.
        
        Process the base URL and extract the links from them and create URLLinks object for each links extracted. 
        Each of these objects are pushed as the child entry of the Main URLLinks object created for the Base URL. 
        
        These child objects are later accessed in a loop and processed further to check for their validity, depending 
        on the depth to which they belong. 
        '''
        ts = time.time()
        handle = self.__getDataFromURL(self.__dict__['_url'])
        ted = time.time()
        dlTime = ted - ts
        if ( self.__checkIfError(handle)):
            if ( handle[0] == 'HTTPError'):
                eCode = ErrorCodes(int(handle[1]))
                einfo = eCode.getError()[1]
            else:
                einfo = handle[1]
            urlObject = URLLinks(self.__dict__['_url'], None, self.__dict__['_url'], None, isProcessed=True, isBroken=True, 
                                 size='<Unknown>', dlTime=dlTime, checkTime=dlTime, lastModified='<Unknwon>', info=einfo,status=handle[0] + ' : ' + handle[1], lType='<Unknwon>')
            self.__printError(handle[0] + ' : ' + handle[1] + ' : ' + einfo)
            self.__raiseError(handle, self.__dict__['_url'])
            return urlObject
        else:
            ts = time.time()
            htmlData = urllib2.urlopen(self.__dict__['_url'])
            ted = time.time()
            data = etree.HTML(htmlData.read())
            dlTime  =   ted - ts
            title = self.__getURLTitle(data)
            links = self.__links(data)
            (lTtype, lastChagned, size) = self.__getURLInfo(handle)
            status = 'OK'
            urlObj = URLLinks(self.__dict__['_url'], title, self.__dict__['_url'], title, isProcessed=True, isBroken=False, size=size, dlTime=dlTime, 
                              lastModified=lastChagned, info='Successfully Processed', status=status, lType=lTtype)
            
            for link in links:
                cLink = str(link.attrib['href']).lstrip().rstrip()
                if ( cLink.startswith('#') or cLink.startswith('.') or cLink.startswith('..') or self.__dict__['_url'] not in cLink):
                    cLink = urlparse.urljoin(self.__dict__['_url'], cLink)
                
                if ( self.__dict__['_url'] in cLink):
                    cTitle = link.text
                    temp = URLLinks(self.__dict__['_url'], title, cLink, cTitle)
                    urlObj.addChild(temp)
            te = time.time()
            cTime = te - ts
            urlObj.setCheckTime(cTime)
            Deadcheck.__levelBasedLinks[0] = []
            Deadcheck.__levelBasedLinks[0].append(urlObj)
    
    def __loadExempt(self):
        '''
        Private member function used for Loading Exemptions from the Import File. 
        '''
        try:
            with open(str(self.__dict__['_exempt'])) as eFile:
                for line in eFile:
                    Deadcheck.__exemptedItems.append(line.lstrip().rstrip())
        except IOError:
            self.__printWarning('Unable to get information from the exceptions file.')
    
    def __checkExempt(self, url):
        '''
        Private member function used for chekcing if the URL being processed is exempted. 
        
        The exemptions file can contain the exact link or the pattern that will have to be exempted. 
        If a match is found in either, that specific link is exempted and the next is picked up for processing. 

        Status of the object which was exempted is set apropriately based on the return value of this method. 
        '''
        exItem = Deadcheck.__exemptedItems
        if ( len(exItem) > 0 ):
            exItem = [ str(item) if not str(item).startswith('*') else '.'+str(item) for item in exItem]
            exItem = '|'.join(exItem)
            pattern = re.compile(exItem)
            match = pattern.match(url, re.I)
            if ( match != None):
                return True
            else:
                return False
        else:
            return False
        
    def process(self):
        '''
        Method that will be called using the Deadcheck object from the Main script to instruct the 
        module to process the links based on the depth to which they belong to. 
        
        Each of the link is extracted from the childURL list that belongs to the parent URLLinks object and 
        processed after checking for exemptions. 
        
        Based on the processing, the apropriate parameters and values are set using the set method available in the
        URLLinks class. 
        
        Each page being processed has its own list of the Child URL that are extracted and pushed into an array. 
        
        These list of URLs are processed during the next depth / level value. 
        
        '''
        self.__loadExempt()
        if ( self.get_depth() == 0 ):
            self.__analyze() 
        else:
            for level in range(self.get_depth()+1):
                Deadcheck.__levelBasedLinks[level+1] = []
                for vobj in self.getAll()[level]:
                    for obj in vobj.getChildren():
                        t1 = time.time()
                        (url, title) = obj.get()
                        #if ( not Deadcheck.__ProcessedLinks.has_key(url) and not self.__checkExempt(url) and 'javascript' not in url.lower()):
                        if ( not Deadcheck.__ProcessedLinks.has_key(url) and not self.__checkExempt(url) ):
                            Deadcheck.__ProcessedLinks[url] = 1
                            # Process javascript:openWindow type URL to extract necessary links. 
                            self.__printMessage("Processing Link : " + url);
                            if ( 'javascript' in url.lower()):
                                url = self.__cleanupJavaScript(url)
                                
                            ts = time.time()
                            handle = self.__getDataFromURL(url)
                            ted = time.time()
                            if ( self.__checkIfError(handle)):
                                if ( handle[0] == 'HTTPError'):
                                    eCode = ErrorCodes(int(handle[1]))
                                    einfo = eCode.getError()[1]
                                else:
                                    einfo = handle[1]
                                obj.setInfo(einfo)
                                obj.setProcessed(True)
                                obj.setBroken(True)
                                obj.setStatus(handle[0] + ' : ' + str(handle[1]))
                                obj.setDLTime(ted-ts)
                                obj.setSize('<Unknown>')
                                obj.setLastModified('<Unknown>')
                                obj.setType('<Unknown>')
                                obj.setCheckTime(ted-ts)
                                
                                print 'Broken ' + str(obj.get()) 
                                self.__printError('Broken Link ' + str(obj.get()));
                            else:
                                ts = time.time()
                                htmlData = urllib2.urlopen(url)
                                ted = time.time()
                                data = etree.HTML(htmlData.read())
                                dlTime = ted - ts
                                title = self.__getURLTitle(data)
                                links = self.__links(data)
                                (lTtype, lastChagned, size) = self.__getURLInfo(htmlData)
                                status = 'OK'
                                urlObj = URLLinks(url, title, url, title, isProcessed=True, isBroken=False, size=size, dlTime=dlTime, lastModified=lastChagned, 
                                                  info='Successfully Processed', status=status, lType=lTtype)
                                
                                for link in links:
                                    cLink = str(link.attrib['href']).lstrip().rstrip()
                                    if ( cLink.startswith('#') or cLink.startswith('.') or cLink.startswith('..') or url not in cLink):
                                        cLink = urlparse.urljoin(url, cLink)
                                    
                                    if ( self.__dict__['_url'] in cLink):
                                        cTitle = link.text
                                        temp = URLLinks(url, title, cLink, cTitle, status='UNPROCESSED')
                                        urlObj.addChild(temp)
                                te = time.time()
                                cTime = te - ts
                                urlObj.setCheckTime(cTime)
                                Deadcheck.__levelBasedLinks[level+1].append(urlObj)
                                t2 = time.time()
                                obj.setInfo('Successfully Processed.')
                                obj.setProcessed(True)
                                obj.setBroken(False)
                                obj.setStatus('OK')
                                obj.setDLTime(dlTime)
                                obj.setSize(size)
                                obj.setLastModified(lastChagned)
                                obj.setType(lTtype)
                                obj.setCheckTime(t2-t1)
                        else:
                                if ( self.__checkExempt(url)):
                                    obj.setInfo('Exempted based on the Input file : ' + self.__dict__['_exempt'])
                                    obj.setStatus('EXEMPTED')
                                    self.__printWarning("URL Exempted : " + url);
                                elif ( 'javascript' in url ):
                                    obj.setInfo('Javascript Links are not processed. Implementation underway.')
                                    obj.setStatus('WARNING')
                                else:
                                    obj.setInfo('URL Already Processed. Will not be processed again.')
                                    obj.setStatus('SKIPPED')
                                    self.__printWarning("Skipping URL : " + url);    
                                obj.setProcessed(True)
                                obj.setBroken(False)
                                obj.setDLTime(None)
                                obj.setSize(None)
                                obj.setLastModified(None)
                                obj.setType(None)
                                obj.setCheckTime(None)
    def __analyze(self):
        '''
        Support For Analyzing Independed URL if required. 
        Return Data will be a String Containing the analysis Results
        ''' 
        pass  
          
    # 2014-03-27    : Javascript clean up added for low level processing of URL. 
    def __cleanupJavaScript(self, url):
        '''
        Private member method used for cleaning up javascript:openWindow method. 
        
        This is just a basic verion of the cleanup functionality that might not be a perfect one. 
        
        Further development is suggested. Also, Please verify the results obtained using this. 
        '''
        
        '''
        Change Implemented to Avoid AttributeError When the RegExp Fails to Match the URL. 
        Date             2014-07-17
        Bug              #3
        User             Harsha Narayana
        Comment          Testing completed for Bug Fix, Upto 4th Level from Base URL. 
        '''
        # Replace all " with ' for RegExp Matching. 
        url = re.sub('"',"'", url) 
        tempPath = urlparse.urlparse(url).path
        tempURL = re.search("(?P<url>http\s?://[^\s].[^\s]+',')", tempPath).group("url")
        cleanURL = re.sub("','","",tempURL)
        return cleanURL
        
    def __getURLTitle(self, handle):
        '''
        Private member method used for Obtaining the data of the <title> tag. 
        
        If there is no valid <title> tag exists, <Unknown> is used as the value instread. 
        '''
        if handle == None:
            title = '<Unknown>'
            return title
        tData = handle.find('.//title')
        if tData == None:
            title = '<Unknown>'
        else:
            title = tData.text
        
        return title
    
    def __getURLInfo(self, handle):
        '''
        Private member function used for obtaining the file size and last modifed date of the URL under process. 
        '''
        if ( handle.info().dict.has_key('last-modified')):
            lastModified = handle.info()['last-modified']
        else:
            lastModified = '<Unknown>'
        
        if ( handle.info().dict.has_key('content-length')):
            size = self.__size(int(handle.info()['content-length']))
        else:
            size = '<Unknown>'
        
        linkType = handle.info().gettype()
        
        return (linkType, lastModified, size)
    
    def __links(self, handle):
        '''
        Private member method used for obtaining a list of URL extracted from the data downloaded. 
        
        urllib2 is used for dowloading the data and lxml is used for processing and extracting the 
        valid list of URL that can later be processed based on the condition and requirement. 
        '''
        if handle == None:
            return []
        return handle.findall('.//*[@href]')
            
    def __getDataFromURL(self, urlLink):
        '''
        Private member method that downloads the Data for a URL and returns the information to the 
        calling function which is later used for processing and extracting purpose. 
        '''
        try:
            htmlData = urllib2.urlopen(urlLink, timeout=10)
            return (htmlData)
        except urllib2.HTTPError, e:
            error = ('HTTPError', str(e.getcode()))
            return error
        except urllib2.URLError, e:
            error = ('URLError', str(e.reason))
            return error
        except httplib.HTTPException, e:
            error = ('HTTPException', str(e.message))
            return error
        except Exception, e:
            error = ('Generic Exception', e.message)
            return error
            
    def __printMessage(self, message):
        '''
        Print Log Message
        '''
        logging.info(message)
        
    def __printWarning(self, message):
        '''
        Print Warning message
        '''
        logging.warning(message)
        
    def __printError(self, message):
        '''
        Print Error Message
        '''
        logging.error(message)
                    
    def __checkKey(self,key):
        '''
        Private member method that checks and verifies if a value in the self.__dict__ is set and not None. 
        '''
        return self.__dict__.has_key(key) and self.__dict__[key] != None        
    
    
class DeadcheckAPI(object):
    '''
       A Custom Class Created to support the usage of the Tool in the command line. 
       
       This class allows the user to check and validate each URL manually based on their requirement. 
    '''
    ## Constructor
    def __init__(self, proxy = None, username = None, password = None, auth_base = None):
        self._proxy = proxy
        self._username = username
        self._password = password
        self._auth_base = auth_base
        self.__configure();
        
    def __configure(self):
        __proxy = None
        __auth = None
        __opener = None
        
        if ( self.__checkKey('_proxy')):
            __proxy = urllib2.ProxyHandler({'http':self.__dict__['_proxy'], 'https':self.__dict__['_proxy']})
            __opener = urllib2.build_opener(__proxy)
            
            
        # Fixed on 2015-03-10 to Correct the Authentication Support Issue inside the DeadcheckAPI class.
        if ( self.__checkKey('_username') and self.__checkKey('_password')):
            passManager = urllib2.HTTPPasswordMgrWithDefaultRealm()
            if ( self.__checkKey('_auth_base')):
                passManager.add_password(None, self.__dict__['_auth_base'], self.__dict__['_username'], self.__dict__['_password'])
            else:
                passManager.add_password(None, self.__dict__['_url'], self.__dict__['_username'], self.__dict__['_password'])
            
            __auth = urllib2.HTTPBasicAuthHandler(passManager)
            __opener = urllib2.build_opener(__auth)
            
        # Fixed on 2015-03-10 to Correct the Proxy Support Issue inside the DeadcheckAPI class.
        if ( __opener != None ):
            urllib2.install_opener(__opener)
                
                        
    def __checkKey(self, key):
        return self.__dict__.has_key(key) and self.__dict__[key] != None
    
    def __size(self, size):
        '''
        Private member function used for Converting bytes into Human readable file size for display purpose. 
        
        '''
        for x in ['bytes','KB','MB','GB']:
            if size < 1024.0 and size > -1024.0:
                return "%3.1f%s" % (size, x)
            size /= 1024.0
        return "%3.1f%s" % (size, 'TB')
    
    def __getDataFromURL(self, urlLink):
        '''
        Private member method that downloads the Data for a URL and returns the information to the 
        calling function which is later used for processing and extracting purpose. 
        '''
        try:
            htmlData = urllib2.urlopen(urlLink, timeout=10)
            return (htmlData)
        except urllib2.HTTPError, e:
            error = ('HTTPError', str(e.getcode()))
            return error
        except urllib2.URLError, e:
            error = ('URLError', str(e.reason))
            return error
        except httplib.HTTPException, e:
            error = ('HTTPException', str(e.message))
            return error
        except Exception, e:
            error = ('Generic Exception', e.message)
            return error
            
    def amIDead(self, urlToCheck):
        return self.__analyze(urlToCheck)
        
    def __analyze(self, url):
        ts = time.time()
        handle = self.__getDataFromURL(url)
        ted = time.time()
        dlTime = ted - ts
        if ( self.__checkIfError(handle)):
            if ( handle[0] == 'HTTPError'):
                eCode = ErrorCodes(int(handle[1]))
                einfo = eCode.getError()[1]
            else:
                einfo = handle[1]
            urlObject = URLLinks(url, None, url, None, isProcessed=True, isBroken=True, 
                                 size='<Unknown>', dlTime=dlTime, checkTime=dlTime, lastModified='<Unknwon>', info=einfo,status=handle[0] + ' : ' + handle[1], lType='<Unknwon>')
            return urlObject
        else:
            ts = time.time()
            htmlData = urllib2.urlopen(url)
            ted = time.time()
            data = etree.HTML(htmlData.read())
            dlTime  =   ted - ts
            title = self.__getURLTitle(data)
            links = self.__links(data)
            (lTtype, lastChagned, size) = self.__getURLInfo(handle)
            status = 'OK'
            urlObj = URLLinks(url, title, url, title, isProcessed=True, isBroken=False, size=size, dlTime=dlTime, 
                              lastModified=lastChagned, info='Successfully Processed', status=status, lType=lTtype)
            for link in links:
                cLink = str(link.attrib['href']).lstrip().rstrip()
                if ( cLink.startswith('#') or cLink.startswith('.') or cLink.startswith('..') or url not in cLink):
                    cLink = urlparse.urljoin(url, cLink)
                
                if ( url in cLink):
                    cTitle = link.text
                    temp = URLLinks(url, title, cLink, cTitle)
                    urlObj.addChild(temp)
            te = time.time()
            cTime = te - ts
            urlObj.setCheckTime(cTime)
            
            return urlObj
                    
    def __links(self, handle):
        '''
        Private member method used for obtaining a list of URL extracted from the data downloaded. 
        
        urllib2 is used for dowloading the data and lxml is used for processing and extracting the 
        valid list of URL that can later be processed based on the condition and requirement. 
        '''
        if handle == None:
            return []
        return handle.findall('.//*[@href]')
                
    def __getURLTitle(self, handle):
        '''
        Private member method used for Obtaining the data of the <title> tag. 
        
        If there is no valid <title> tag exists, <Unknown> is used as the value instread. 
        '''
        if handle == None:
            title = '<Unknown>'
            return title
        tData = handle.find('.//title')
        if tData == None:
            title = '<Unknown>'
        else:
            title = tData.text
        
        return title
    
    def __checkIfError(self, value):
        '''
        Private member function to check if the Value retured from the function __getDataFromURL is an Errors. 
        
        '''
        if ( 'HTTPError' in value or 'URLError' in value or 'HTTPException' in value or 'Generic Exception' in value):
            return True
        else:
            return False

    def __getURLInfo(self, handle):
        '''
        Private member function used for obtaining the file size and last modifed date of the URL under process. 
        '''
        if ( handle.info().dict.has_key('last-modified')):
            lastModified = handle.info()['last-modified']
        else:
            lastModified = '<Unknown>'
        
        if ( handle.info().dict.has_key('content-length')):
            size = self.__size(int(handle.info()['content-length']))
        else:
            size = '<Unknown>'
        
        linkType = handle.info().gettype()
        
        return (linkType, lastModified, size)