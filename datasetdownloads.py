from pprint import pprint
from lxml import etree
#import xml.etree.ElementTree as ET
import requests
import json
import zipfile
import os
import progressbar
import time
import sys

def   listWatersheds():

    '''
    listWatersheds function contacts GSTORE and returns a list of watersheds.
    '''
    
    wIndex = 1
    collectionNames = []
    collectionIds = []
   
    rWatersheds = requests.get('http://gstore.unm.edu/apps/epscor/search/collections.json?version=3&theme=Climate')
    rData = rWatersheds.json()
    watershedResults = rData['results']

    #Get the length of Watershed list
    countOfWatersheds = rData['subtotal']

    #displays the name of all watersheds
    print "\n\nName of watersheds available:\n\n"
    for wResult in watershedResults:
        print wIndex, ":", wResult['name']
        wIndex += 1
        collectionNames.append(wResult['name']) 
        collectionIds.append(wResult['uuid']) 

    return countOfWatersheds, collectionNames, collectionIds


def getWatershedDetails(userWatershedChoice, wDetails):
    
    '''
    getWatershedDetails function finds out the uid of the selected watershed
    '''

    nameOfWatershed = wDetails[1][userWatershedChoice - 1]
    uidOfWatershed = wDetails[2][userWatershedChoice - 1]

    return nameOfWatershed, uidOfWatershed


def   listDatasets(nameOfWatershed, uidOfWatershed):

    '''
    listDatasets function contacts GSTORE and returns a list of datasets.
    '''

    rIndex = 1
    datasetNames = []
    datasetIds = []
        
    rDatasets = requests.get('http://gstore.unm.edu/apps/epscor/search/collection/%s/datasets.json?version=3' %uidOfWatershed) 
    rrData = rDatasets.json()
    dataResults = rrData['results']
    
    #Get the length of Dataset list
    countOfDatasets = rrData['subtotal']

    #displays the name of all datasets
    print "\n\nDatasets available for %s: " %nameOfWatershed, "\n\n"
    for dResult in dataResults:
        print rIndex, ":", dResult['name']
        rIndex += 1
        datasetNames.append(dResult['name']) 
        datasetIds.append(dResult['uuid']) 

    return countOfDatasets, datasetNames, datasetIds  


def getDatasetDetails(userDatasetChoice, dDetails):
    
    '''
    getWatershedDetails function finds out the uid of the selected watershed
    '''

    nameOfDataset = dDetails[1][userDatasetChoice - 1]
    uidOfDataset = dDetails[2][userDatasetChoice - 1]

    return nameOfDataset, uidOfDataset


def getCapabilities(uidOfDataset):

    '''
    getCapabilities function finds out the coverage name from the GetCapabilities response
    '''

    #Dataset service description
    serviceDescription_url = requests.get('http://gstore.unm.edu/apps/epscor/datasets/%s/services.json' %uidOfDataset)
    serviceDescription_data = serviceDescription_url.json() 
    
       
    #WCS GetCapabilities request from dataset service description
    cap_url = serviceDescription_data['services'][1]['wcs']
    r_cap = requests.get(cap_url)
    
    with open("capabilities.xml", "wb") as code:	  
        code.write(r_cap.content)
    
    tree = etree.parse('capabilities.xml')
        
    #Coverage Name
    identifier = tree.find('.//{http://www.opengis.net/wcs/1.1}Identifier')
    coverageName = identifier.text
       
    return coverageName


def describeCoverage(uidOfDataset, coverageName):
   
    '''
    describeCoverage function finds out the Supported format, CRS, BoundingBox coordinates from the DescribeCoverage response
    '''

    bboxValues = []
    
    #DescribeCoverage request
    desCoverage_url = 'http://gstore.unm.edu/apps/epscor/datasets/%s/services/ogc/wcs?VERSION=1.1.2&SERVICE=WCS&REQUEST=DescribeCoverage&VERSION=1.0.0&COVERAGE=%s' %(uidOfDataset, coverageName)
    r_desCoverage = requests.get(desCoverage_url)

    with open("coverage.xml", "wb") as code:	  
        code.write(r_desCoverage.content)

    tree = etree.parse('coverage.xml')
       
    
    #Supported Format
    formats = tree.find('.//{http://www.opengis.net/wcs}formats')
    supportedFormat = formats.text
    
    
    #CRS
    crs = tree.find('.//{http://www.opengis.net/wcs}requestResponseCRSs')
    CRS = crs.text
        

    #Bounding Box coordinates
    envelopeValue = tree.findall('.//{http://www.opengis.net/gml}Envelope')
    posValue = envelopeValue[1].findall('{http://www.opengis.net/gml}pos')
    boundingBox1 = posValue[0].text
    fValues = boundingBox1.split()
    for fvalue in fValues: 
        bboxValues.append(fvalue)
    boundingBox2 = posValue[1].text
    lValues = boundingBox2.split()
    for lvalue in lValues: 
        bboxValues.append(lvalue)
    coordinates = bboxValues[0]+","+ bboxValues[1]+","+ bboxValues[2]+","+ bboxValues[3]
            
    return supportedFormat, coordinates, CRS


def downloadDataset(nameOfDataset, uidOfDataset, supportedFormat, coverageName, coordinates, CRS):

    '''
    downloadDataset function downloads the datset using GetCoverage request
    '''

    progress = progressbar.ProgressBar()

    #GetCoverage request
    getCoverage_url = 'http://gstore.unm.edu/apps/epscor/datasets/%s/services/ogc/wcs?SERVICE=WCS&VERSION=1.0.0&REQUEST=GetCoverage&FORMAT=%s&COVERAGE=%s&BBOX=%s&CRS=%s&RESPONSE_CRS=%s&WIDTH=500&HEIGHT=400' %(uidOfDataset, supportedFormat, coverageName, coordinates, CRS, CRS)
    r_getCoverage = requests.get(getCoverage_url) 
    
    directoryName = "Datasets"
    if not os.path.exists(directoryName):
        os.makedirs(directoryName)

    print "\nDownloading ..."
    for i in progress(range(50)): 
        with open(os.path.join(directoryName, nameOfDataset), "w") as f:	  
            f.write(r_getCoverage.content)
        time.sleep(0.1)
    print "\nDownloading completed\n"  
    

def multipleDatasetSelect(watershedDetails):
 
    '''
    multipleDatasetSelect function asks user for more dataset selects
    '''

    while True:
        userMDChoice = raw_input("\nDo you want to download more datasets? (Yes/No):\t")
        if userMDChoice == "Yes":
            dsteps(watershedDetails)
        elif userMDChoice == "No":
            multipleWatershedSelect()
        else:
            print "Invalid Choice"


def multipleWatershedSelect():

    '''
    multipleWatershedSelect function asks user for more watershed selects
    '''
    
    while True:
        userMWChoice = raw_input("\nDo you want to select another watershed? (Yes/No):\t")
        if userMWChoice == "Yes":
            steps()
        elif userMWChoice == "No":
            print "\n\n"
            sys.exit()
        else:
            print "Invalid Choice"
      
      
def steps():
    wDetails = listWatersheds()

    while True:
        try: 
            userWatershedChoice = raw_input("\n\nSelect an option: ")
            userWatershedChoice = int(userWatershedChoice)
            if 1 <= userWatershedChoice <= wDetails[0]:
                break
            else:
                print "Invalid option. Please try again..."    
        except ValueError:
            print "No valid integer!Please try again..." 

    watershedDetails = getWatershedDetails(userWatershedChoice, wDetails)
    dsteps(watershedDetails)

  
def dsteps(watershedDetails):
    dDetails = listDatasets(watershedDetails[0], watershedDetails[1])

    while True:
        try:
            userDatasetChoice = raw_input("\n\nSelect an option: ")
            userDatasetChoice = int(userDatasetChoice)
            if 1 <= userDatasetChoice <= dDetails[0]:
                break
            else:
                print "Invalid option. Please try again."
        except ValueError:
            print "No valid integer!Please try again..." 

    datasetDetails = getDatasetDetails(userDatasetChoice, dDetails)
    coverageName = getCapabilities(datasetDetails[1])
    desCoverage = describeCoverage(datasetDetails[1], coverageName)
    downloadDataset(datasetDetails[0], datasetDetails[1], desCoverage[0], coverageName, desCoverage[1], desCoverage[2])
    multipleDatasetSelect(watershedDetails)
    
            
if __name__ == "__main__":
    steps()
    
    
    
    
   
        
    
   
    
