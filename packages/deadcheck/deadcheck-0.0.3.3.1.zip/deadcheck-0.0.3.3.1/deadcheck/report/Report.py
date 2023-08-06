'''
Created on Dec 12, 2013

This Module was created to facilitate the generation of the Report in a pretty format which can 
be used with the deadcheck module. 

This module uses a bunch of Pre-designed templates to generate the report in a pretty format. 
As per the existing code the reports are classified based on the Depth of the Link to which 
they belong. 

Each objec that is processed for that level is created as one html file report. There is no specific 
control over what type of links are reported in the files. ( Will be implemented. ) 

The report so generated also makes use of a css file to format the Content in the UI. You can 
customize the css file to get the report in a way that is more suitable for you. However, care is to 
be ensured that the file is placed in its original location for the report generation to work flawlessly. 

@author: Harsha Narayana

@change:     2013-12-13    Initial Draft
             2013-12-17    Documentation Updated.
             2014-03-12    __writeTableData module updated to fix UnicodeEncodeError.    
                           Bug #3 : https://www.assembla.com/spaces/deadcheck/tickets/3#/activity/ticket:
                           Bug #1 : https://github.com/harshanarayana/deadcheck/issues/1
'''

__version__ = "0.0.3"
__author__ = "Harsha Narayana"
__date__ = "Dec 12, 2013"

import os
import re 

class Report(object):
    '''
        A Custom class created for the purpose of Handling the Report Generation process of deadcheck Utility. 
        This packages uses a preset template format linked to a custom CSS to generate the report and format them. 
        The template files that are used for the purpose of generating the Report are placed under /Templates folder
        inside report package. 
        
        @param dataSer      : Object of type URLLinks. All children of this object are extracted and printed onto the 
                              report. 
        @param outFile      : Output File
        @param templatePath : Template Path for report generation. If no argument is provided, then a value is extracted 
                              in runtime.  
    '''

    def __init__(self, dataSet, outFile, templatePath):
        '''
        Constructor
        
        @param dataSer      : Object of type URLLinks. All children of this object are extracted and printed onto the 
                              report. 
        @param outFile      : Output File
        @param templatePath : Template Path for report generation. If no argument is provided, then a value is extracted 
                              in runtime.
        '''
        self.__dataSet = dataSet
        self.__outFile = outFile 
        self.__outDir = None
        if ( templatePath == None):
            self.__templatePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Templates')
        else:
            self.__templatePath = templatePath 
        #self.__setOutDir()
        
    def __setOutDir(self):
        '''
            Private Set Method for self.__outDir Parameter.
            
            @param self: Reference to Self.  
        '''
        self.__outDir = os.path.dirname(self.__outFile)
    
    def __getTemplatePath(self):
        '''
            Private Get method for self.__templatePath
            
            @return: self.__templatePath
        '''
        return self.__templatePath
        
    def getOutDir(self):
        '''
            Get Method for self.__outDir
            
            @return: self.__outDir 
        '''
        return self.__outDir
    
    def getOutFile(self):
        '''
            Get Method for self.__outFile
            
            @return: self.__outFile
        '''
        return self.__outFile
    
    def getDataSet(self):
        '''
            Get method for obtainign a refernece to dataSet variable. 
            
            @return: self.__dataSet
        '''
        return self.__dataSet
    
    def generate(self):
        '''
            Main method that needs to be called from the Source module to generate the report. 
            
            Calls internal private modules __generateHead, __writeTableData and __generateTail to generate the report. 
            A reference to the report generated is returned back to the main programme for further usage if need be. 
            
            @param self: Called using an object of Report class. 
            
            @return: self.__outFile
        '''
        self.__generateHead()
        obj = self.getDataSet()
        self.__writeTableData(obj)
        self.__generateTail(obj)
        return self.getOutFile()
    
    def __writeTableData(self, obj):
        '''
            Private Member function that is used for Population the Report Data in the form of a table using the 
            table.template file. 
            
            We read the template from the file table.template and use the Regular expression to replace the Entries 
            that are to be displayed in the report in the form of a table. 
            
            Each Child entry of the 'obj' variable is populated as a table with all related information displayed as 
            one independent row of that specific table. 
            
            All type of links are reported at the moment. There is no control over what type of contents are to be 
            reported. 
            
            @param self    : Self Reference. 
            @param obj     : Object of the type URLLinks. This is used to loop through all the Child entry and generate 
                             the report for those children in the form of a table. 
            
            @return: None
        '''
        template = self.__getTableTemplate()
        outFile = self.getOutFile()
        with open(outFile, 'a') as oStream:
            for element in obj.getChildren():
                info = element.getReportInfo()
                # Bugfix : 2014-03-12    __writeTableData module updated to fix UnicodeEncodeError.
                info = [ str(repr(item)) for item in info]
                for line in template:
                    line = line.lstrip().rstrip()
                    if ( '$cLinkUrl' in line ):
                        line = re.sub('\$cLinkUrl', info[0], line)
                    
                    if ( '$cLinkTitle' in line ):
                        line = re.sub('\$cLinkTitle', info[1], line)
                        
                    if ( '$pLinkUrl' in line ):
                        line = re.sub('\$pLinkUrl', info[2], line)
                    
                    if ( '$pLinkTitle' in line ):
                        line = re.sub('\$pLinkTitle', info[3], line)
                    
                    if ( '$statusInfo' in line ):
                        line = re.sub('.*', info[4], line)
                    
                    if ( '$isProcessed' in line ):
                        line = re.sub('.*', info[5], line)
                        
                    if ( '$isBroken' in line ):
                        line = re.sub('.*', info[6], line)
                    
                    if ( '$linkType' in line):
                        line  = re.sub('\$linkType', info[7], line)
                        
                    if ( '$fileSize' in line ):
                        line = re.sub('\$fileSize', info[8], line)
                    
                    if ( '$downTime' in line ):
                        line = re.sub('\$downTime', info[9], line)
                        
                    if ( '$lastChanged' in line ):
                        line = re.sub('\$lastChanged', info[10], line)
                        
                    if ( '$processTime' in line ):
                        line = re.sub( '\$processTime', info[11], line)
                        
                    if ( '$addInfo' in line ):
                        line = re.sub( '\$addInfo', info[12], line)
                    
                    line = re.sub("'","",line)    
                    oStream.write('%s' %(line))
            oStream.close()
                
    def __getTableTemplate(self):
        '''
            Private member function used for Obtaining the Table template from the file table.template
            
            @param self : Self reference. 
            
            @return: template     : Array containing each line of file table.template as one value. 
            
        '''
        template = []
        tableFile = os.path.abspath(os.path.join(self.__getTemplatePath(), 'table.template')) 
        with open(tableFile, 'r') as iStream:
            for line in iStream:
                line = line.lstrip().rstrip()
                template.append(line)
                
        return template
    
    def __generateHead(self):
        '''
            Private member funtion used for generating and populating the Report file with HTML header contents. 
            This is also used for finding and linking the CSS file that is used for Prettying up the Report. 
            
            @param self : Reference to self. 
            
            @return:  None
            
        '''
        cssPath = os.path.abspath(os.path.join(self.__getTemplatePath(), 'Report.css'))
        headFile = os.path.abspath(os.path.join(self.__getTemplatePath(), 'head.template'))
        outFile = self.getOutFile()
        with open(outFile, 'w') as oStream:
            with open(headFile, 'r') as iSteam:
                for line in iSteam:
                    if ( '$cssFilePath' in line):
                        line = re.sub('\$cssFilePath', repr(cssPath), line.lstrip().rstrip())
                    line = line.lstrip().rstrip()
                    oStream.write('%s\n' %(line))
        
        oStream.close()
        iSteam.close()
        
    def __generateTail(self, obj):
        '''
            Private Member function used for Generating the HTML tail content for the Report. 
            
            This is also used for generating a summary information of the Link entries that are displayed 
            on this specific report for the Specific URLLinks type object.
            
            @param self : Self reference
            @param obj  : Object of type URLLinks
             
        '''
        iCount = obj.getCount()
        # Bugfix : 2014-03-12    __generateTail module updated to fix UnicodeEncodeError.
        iCount = [str(repr(item)) for item in iCount]
        tailFile = os.path.abspath(os.path.join(self.__getTemplatePath(), 'tail.template'))
        outFile = self.getOutFile()
        with open(outFile,'a') as oStream:
            with open(tailFile, 'r') as iStream:
                for line in iStream:
                    line = line.lstrip().rstrip()
                    if ( '$totalLinkCount' in line):
                        line = re.sub('\$totalLinkCount', iCount[0], line)
                    
                    if ( '$totalErrorCount' in line):
                        line = re.sub('\$totalErrorCount', iCount[1], line)
                        
                    if ( '$totalWarningCount' in line):
                        line = re.sub('\$totalWarningCount', iCount[2], line)
                        
                    if ( '$totalExemptCount' in line):
                        line = re.sub('\$totalExemptCount', iCount[3], line)
                        
                    if ( '$totalSkipCount' in line):
                        line = re.sub('\$totalSkipCount', iCount[4], line)
                        
                    if ( '$totalTimeCount' in line):
                        line = re.sub('\$totalTimeCount', iCount[5], line)
                        
                    oStream.write('%s' %(line))
        oStream.close()
        iStream.close()
        
    