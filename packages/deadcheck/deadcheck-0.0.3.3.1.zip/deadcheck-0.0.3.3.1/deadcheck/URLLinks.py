'''
Created on Dec 3, 2013

This class was created to store the details of the URL links that are being processed and all the 
child URL that are extracted from that specific link under process. 

Each Link has a parent link and parent Title along with its own title and link information. This calss
also makes it a point to store the information like Last modification date of the file, size of the file
and time taken to download the file and time taken to parse and process the content of the file. 

Different variables are used for storing these information along with the values like If the link is broken 
or not, if link is processed, status information, comment/additional Information along with type of the link that
current URL refers to. 

Getter and setter methods are provided to set and get the values from anywhere using the URLLinks type of object. 

This also includes custom functions that return the data in more user friendly way that can be used for dispalying
in the logs or for reporting purpose. 
 
@author: harshanarayana

@change:     2013-12-03    Initial Draft. A custom URLLinks class to Store and access information pertaining to 
                           a Single URL in Question
             2013-12-10    Additional Functionality included to Support the Report Generation in HTML Format
             2013-12-17    Documentation Updated.
             2014-07-23    Minor changes made into info() function to avoid Character Encoding issue that might be 
                           encountered during the Runtime. 
'''

__version__ = "0.0.4"
__date__ = "06th December 2013"
__author__ = "Harsha Narayana"

import re

class URLLinks(object):
    '''
    A custom Class created for storing the information of the URL that is extracted and processed. 
    An object of this type is created for Each link that was extracted and processed from the Base URL that was given as input.
    
    @param parentLink     : Parent URL of the Link Being Processed. If the Link being processed is base URL the the URL itself is
                            the parent URL. 
    @param parentTitle    : Title Of the Parent URL Page. 
    @param childLink      : URL for the Current URL that was extracted. 
    @param childTitme     : Link Name as appears in the <a href> tag. 
    @param isProcessed    : Variable used for checking if the Link is Processed. Default False.
                            Processed     : True            Not Processed     : False
    @param isBroken       : Variable used for Storing Broken status of the Link. 
                            Broken        : True            Not Broken        : False
    @param size           : Size of the File being represented by the URL. i.e. childLink. 
    @param dlTime         : Time Taken to Download the file in seconds. 
    @param checkTim       : Time taken to process and parse the file content downloaded and create Child Entries. 
    @param lastModified   : Last Modified date for the file being pointed by the childLink
    @param info           : Additional information about the Link. This will be set after the link is processed. 
    @param status         : Variable used for storing status Infomration. (OK, WARNING, ERROR, SKIPPED, EXEMPTED )
    @param lType          : Type of URL. i.e MIME Type  
    '''


    def __init__(self, parentLink, parentTitle, childLink, childTitle, isProcessed = False, isBroken = False, size = 0, dlTime = 0, 
                 checkTime = 0, lastModified = None, info = None, status = None, lType = None):
        '''
        Constructor with default values provided for some of the parameters. These values are later 
        set while processing the contents.
        
        @param parentLink     : Parent URL of the Link Being Processed. If the Link being processed is base 
                                URL the the URL itself is the parent URL. 
        @param parentTitle    : Title Of the Parent URL Page. 
        @param childLink      : URL for the Current URL that was extracted. 
        @param childTitme     : Link Name as appears in the <a href> tag. 
        @param isProcessed    : Variable used for checking if the Link is Processed. Default False.
                                Processed     : True            Not Processed     : False
        @param isBroken       : Variable used for Storing Broken status of the Link. 
                                Broken        : True            Not Broken        : False
        @param size           : Size of the File being represented by the URL. i.e. childLink. 
        @param dlTime         : Time Taken to Download the file in seconds. 
        @param checkTim       : Time taken to process and parse the file content downloaded and create Child Entries. 
        @param lastModified   : Last Modified date for the file being pointed by the childLink
        @param info           : Additional information about the Link. This will be set after the link is processed. 
        @param status         : Variable used for storing status Infomration. (OK, WARNING, ERROR, SKIPPED, EXEMPTED )
        @param lType          : Type of URL. i.e MIME Type           
        
        '''
        self.__parentLink = parentLink
        self.__childLink = childLink
        self.__parentTitle = parentTitle
        self.__childTitle = childTitle
        self.__isProcessed = isProcessed
        self.__isBroken = isBroken
        self.__size = size
        self.__dlTime = dlTime
        self.__checkTime = checkTime
        self.__lastModified = lastModified
        self.__info = info
        self.__status = status
        self.__lType = lType
        self.__childURLs = []
    
    def addChild(self, value):
        '''
        Method created for adding a new Object of the type URLLinks into self.__childURLs
        Each element added is a URL extracted from the current page being processed. Valid / Invalid both will be 
        present. Status of Validity is changed later on based on the code. 
        '''
        self.__childURLs.append(value)
                    
    def getChildren(self):
        '''
        Method used for returning all child URL object. 
        Return type is a list of URLLinks object. 
        '''
        return self.__childURLs
    
    def getParentLink(self):
        '''
        Get Method for __parentLink param. 
        
        @return: URLLinks.__parentLink
        '''    
        return self.__parentLink
    
    def getParentTitle(self):
        '''
        Get method for __parentTitle param
        
        @return: URLLinks.__parentTitle
        '''
        return self.__parentTitle
    
    def getChildLink(self):
        '''
        Get method for __childLink param
        
        @return: URLLinks.__childLink
        '''
        return self.__childLink
    
    def getChildTitle(self):
        '''
        Get method for __childTitle param
        
        @return: URLLinks.__childTitle
        '''
        return self.__childTitle
    
    def isProcessed(self):
        '''
        Get method that returns the Processed state of the Link. 
        
        @return: URLLinks.__isProcessed         True : Processed     False : Not Processed
        '''
        return self.__isProcessed
    
    def isBroken(self):
        '''
        Get method that returns the Broken state of the Link. 
        
        @return: URLLinks.__isBroken         True : Broken     False : Not Broken
        '''
        return self.__isBroken
    
    def getSize(self):
        '''
        Get method that returns the file size for the Link being processed. 
        
        @return:  URLLinks.__size
        '''
        return self.__size
    
    def getDLTime(self):
        '''
        Get Method that returns the time taken to download the link being processed. 
        
        @return:    URLLinks.__dlTime
        '''
        return self.__dlTime 
    
    def getCheckTime(self):
        '''
        Get method that returns the Tiem taken to perform the check on that specific link. 
        
        @return: URLLinks.__checkTime
        '''
        return self.__checkTime
    
    def getLastModified(self):
        '''
        Get method that returns that last modified date of the file that is represented by the entity self.__childLink
        
        @return: URLLinks.__lastModified    eg : 'Wed, 11 Aug 2010 22:40:44 GMT'
        '''
        return self.__lastModified
    
    def getInfo(self):
        '''
        Get method that returns the info string that belongs to the Object. Usually an Exception / any other entity that is pertaining to the link. 
        
        @return:  URLLinks.__info
        '''
        return self.__info
    
    def getStatus(self):
        '''
        Get Method that returns the Status of the Link under Question. 
        
        @return: URLLinks.__status     Values = Valid / Warning / Error 
        '''
        return self.__status   
    
    def getType(self):
        '''
        Get method that returns the type of the link that is being processed. 
        
        @return: URLLinks.__lType
        '''
        return self.__lType
    
    def getParents(self):
        '''
        Get method that returns the Parent Link information in the form of a Tuple. 
        
        @return: (URLLinks.__parentLink, URLLinks.__parentTitle)
        '''
        return(self.__parentLink, self.__parentTitle)
    
    def get(self):
        '''
        Get method that returns the link information in the form of a tuple. 
        
        @return: (URLLinks.__childLink, URLLinks.__childTitle)
        '''
        return(self.__childLink, self.__childTitle)
    
    def setParentLink(self, parentLink):
        '''
        Set method for Parent Link
        
        @param parentLink : Value for Parent Link. 
        '''
        self.__parentLink = parentLink
        
    def setParentTitle(self, parentTitle):
        '''
        Set Method for ParentTitle
        '''
        self.__parentTitle = parentTitle
        
    def setChildLink(self, childLink):
        '''
        Set method for Child Link 
        '''
        self.__childLink = childLink
        
    def setChildTitle(self, childTitle):
        '''
        Set method for Child Title
        '''
        self.__childTitle = childTitle
        
    def setProcessed(self, isProcessed):
        '''
        Set Method for Processed State of the Object. 
        '''
        self.__isProcessed = isProcessed
        
    def setBroken(self, isBroken):
        '''
        Set method for Broken State of the Object
        '''
        self.__isBroken = isBroken
    
    def setSize(self, size):
        '''
        Set method for File size. 
        '''
        self.__size = size
        
    def setDLTime(self, dlTime):
        '''
        Set method for Variable that stores download time.
        '''
        self.__dlTime = dlTime
    
    def setCheckTime(self, checkTime):
        '''
        Set method for Processing Time
        '''
        self.__checkTime = checkTime
        
    def setLastModified(self, lastModified):
        '''
        Set method for Last modified date of the Object
        '''
        self.__lastModified = lastModified
        
    def setInfo(self, info):
        '''
        Set method for Additional Info variable. 
        '''
        self.__info = info
        
    def setStatus(self, status):
        '''
        Set method for Status
        '''
        self.__status = status
    
    def setType(self, lType):
        '''
        Set method for MIME Type of the Object URL
        '''
        self.__lType = lType
            
    def setParent(self, parentLink, parentTitle):
        '''
        Set method for Parent Link and Parent Title. Uses Tuple type of Arg. 
        '''
        self.__parentLink = parentLink
        self.__parentTitle = parentTitle
    
    def set(self, childLink, childTitle):
        '''
        Set method for Child Link and Child Title. 
        '''
        self.__childLink = childLink
        self.__childTitle = childTitle
        
    def info(self):
        '''
            Custom Function Writtten to extract Info from the Object that can be printed easily. 
            
            This method returns a variable formed by combining the data obtained from different
            get methods to generate a variable that can be used to print contents into the log 
            and / or STDOUT. 
        
            @return: infoString    :    String Type variable. 
            
        '''
        infoString = ''
        infoString += '\nCurrent URL           : ' + str(self.getChildLink())
        infoString += '\nCurrent URL Title     : ' + str(repr(self.getChildTitle())) 
        infoString += '\nParent URL            : ' + str(self.getParentLink())
        infoString += '\nParent Title          : ' + str(repr(self.getParentTitle()))
        infoString += '\nStatus                : ' + str(self.getStatus())
        infoString += '\nIs Broken             : ' + str(self.isBroken())
        infoString += '\nIs Processed          : ' + str(self.isProcessed())
        infoString += '\nFile Size             : ' + str(self.getSize())
        infoString += '\nLink Type             : ' + str(self.getType())
        infoString += '\nDownload Time         : ' + str(self.getDLTime())
        infoString += '\nProcessing Time       : ' + str(self.getCheckTime())
        infoString += '\nLast Modified         : ' + str(self.getLastModified())
        infoString += '\nInfo                  : ' + str(self.getInfo())
        return infoString
    
    def getCount(self):
        '''
        Method used for Obtaining Summary information of the Child Entries that belongs to an object of URLLinks type.
        
        This method is used for obtaining the count of different type of information that are being reported into the 
        final html page generated for the object under process. 
        
        This returns an array of values containing the count of different entities in the order in which they are 
        printed on to the report html file. 
        
        @return: retData         : array[errorCount, warningCount, exemtpionCount, skipCount, timeCount]
        '''
        retData = []
        __errCount = 0
        __warCount = 0
        __exeCount = 0
        __skiCount = 0
        __timCount = 0.0
        retData.append(len(self.getChildren()))
        for item in self.getChildren():
            if ( 'ERROR' in item.getStatus().upper()):
                __errCount += 1
            elif ( 'WARNING' in item.getStatus().upper()):
                __warCount += 1
            elif ( 'EXEMPTED' in item.getStatus().upper()):
                __exeCount += 1
            elif ( 'SKIPPED' in item.getStatus().upper()):
                __skiCount += 1
            else:
                pass
            
            if ( isinstance(item.getCheckTime(),float)):
                __timCount += item.getCheckTime() 
            
        retData.append(__errCount)
        retData.append(__warCount)
        retData.append(__exeCount)
        retData.append(__skiCount)
        retData.append(__timCount)
        return retData
    
    def __getStatusRow(self):
        '''
        Private member fucntion used for obtaining the Status row infomraiton in the HTML compatible tag format. 
        
        Return different values based on the Type of Status. Regular expressions are used for making necessary
        substituion based on the status type.
        
        @return: rowString     : String variable. 
        '''
        rowString = '<td bgcolor="#FFFFCC" class="$rowClassName">$statusInfo</td>'
        statusInfo = self.getStatus().upper()

        if ( 'ERROR' in statusInfo and ':' in statusInfo):
            rowString = re.sub('\$rowClassName', 'error', rowString) 
        elif ( statusInfo == 'OK' ):
            rowString = re.sub('\$rowClassName', 'ok', rowString)
        else:
            rowString = re.sub('\$rowClassName', 'other', rowString)
            
        rowString = re.sub('\$statusInfo', statusInfo, rowString)
        return rowString
    
    def __getIsProcessed(self):
        '''
        Private Member function used for getting Processed status
        '''
        rowString = '<td class="$rowClassName">$isProcessed</td>'
        if ( self.isProcessed()):
            rowString = re.sub('\$rowClassName', 'ok', rowString)
        else:
            rowString = re.sub('\$rowClassName', 'other', rowString)
            
        rowString = re.sub('\$isProcessed', str(self.isProcessed()), rowString)
        return rowString
    
    def __getIsBroken(self):
        '''
        Private member function used for obtaining Broken state of the Object. 
        '''
        rowString = '<td bgcolor="#FFFFCC" class="$rowClassName">$isBroken</td>'
        
        if ( self.isBroken()):
            rowString = re.sub('\$rowClassName', 'ok', rowString)
        else:
            rowString = re.sub('\$rowClassName', 'other', rowString)
            
        rowString = re.sub('\$isBroken', str(self.isBroken()), rowString)
        return rowString
    
    def getReportInfo(self):
        '''
        Member function used for obtaining and returning the data in the format that can be used by the REPORT object. 
        
        This returns an array of object containing information in the order in which the contents are printed onto the 
        report html file. 
        
        We use the get method to obtain and format the necessary information that can later be used for reporting. 
        
        @return: retData
                 array [ childLink, childTitle, parentLink, parentTitle, status, isProcessed, isBroken, linkType, size, 
                         downloadtime, lastModified, checktime, additionInfo ]
        '''
        retData = []
        retData.append(self.getChildLink())
        retData.append(repr(self.getChildTitle()))
        retData.append(self.getParentLink())
        retData.append(repr(self.getParentTitle()))
        retData.append(self.__getStatusRow())
        retData.append(self.__getIsProcessed())
        retData.append(self.__getIsBroken())
        retData.append(self.getType())
        retData.append(self.getSize())
        retData.append(self.getDLTime())
        retData.append(self.getLastModified())
        retData.append(self.getCheckTime())
        retData.append(self.getInfo())
        return retData