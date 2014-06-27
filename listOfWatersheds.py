# ***************************************************************************   
# *	Name: List of watersheds and datasets available for each watershed  *
# *	Author: Lisa Paul Palathingal                                       *
# ***************************************************************************

import requests
import json
import zipfile
import os

# Function Name: listOfWatersheds
# Function Description: The function first displays a list of watersheds available from gstore (from the url specified below). User selects a watershed from the list and the function prints the datasets available for the selected watershed. When the user selects a dataset from the list, function downloads the selected dataset.

def listOfWatersheds():
    '''
    Hi
    '''
    count = 0
    wIndex = 1
    listOfWatershedNames = []
    listOfCollectionIds = []
    listOfDatasetNames = []
    listOfDatasetIds = []

    rWatersheds = requests.get('http://gstore.unm.edu/apps/epscor/search/collections.json?version=3')
    rData = rWatersheds.json()
    wResults = rData['results']

    #Get the length of Watershed list
    countOfWatersheds = rData['subtotal']

    #displays the name of all watersheds
    print "\n\nName of watersheds available:\n\n"
    for wResult in wResults:
        print wIndex, ":", wResult['name']
        wIndex += 1
        listOfWatershedNames.append(wResult['name']) #create a list of names of watersheds
        listOfCollectionIds.append(wResult['uuid']) #create a list of uuids of watersheds
    
    #User selects a name from the list of watersheds
    while True:
        nameOfWatershed = input("\n\nSelect a watershed: ")
        if 1 <= nameOfWatershed <= countOfWatersheds:
            print "\n\nDatasets available for %s:" %listOfWatershedNames[nameOfWatershed - 1]
            break
        else:
            print "Invalid Option. Please try again"   
    
    #get uuid of selected watershed
    while count < countOfWatersheds:
        if listOfWatershedNames[nameOfWatershed - 1] == listOfWatershedNames[count]:
            uid = listOfCollectionIds[count] #collection identifier
            break
        else:
            count += 1  
  
    # Function Name: listOfDataSets
    # Function Description: The user is asked to select a name of dataset from the list. Once the user selects the datset, zip file of the dataset is downloaded from gstore.
    def listOfDataSets(uid):
        start = 1
        rIndex = 1
        
        #url containing the datasets for the selected watershed
        rDatasets = requests.get('http://gstore.unm.edu/apps/epscor/search/collection/%s/datasets.json?version=3' %uid) 
        rrData = rDatasets.json()
        dResults = rrData['results']
        print "\n\n"

        #Get the length of Dataset
        lengthOfDataset = rrData['subtotal']

        #displays the name of all datasets
        for dResult in dResults:
            print rIndex, ":", dResult['name']
            rIndex += 1
            listOfDatasetNames.append(dResult['name']) #create a list of names of datsets
            listOfDatasetIds.append(dResult['uuid']) #create a list of uuids of datasets
           
        while True:
            indexOfDataSet = input("\n\nSelect the name of dataset to be downloaded: \t")

            if 1 <= indexOfDataSet <= lengthOfDataset:
                while start <= lengthOfDataset:
                    if indexOfDataSet == start:
                        uuid = listOfDatasetIds[start - 1]
                        basename = listOfDatasetNames[start - 1]
                        break
                    else:
                        start += 1
                
                print "Downloading ..."

                #Downloading the file
                rDownload = requests.get('http://gstore.unm.edu/apps/epscor/datasets/%s/%s.original.tif' %(uuid, basename))
                with open("/home/likewise-open/UNR/lpalathingal/Desktop/%s.zip" %basename, "wb") as code:	  
                    code.write(rDownload.content)
                print "\nDownloading completed\n"   
                zip = zipfile.ZipFile(r'%s.zip' %basename)

                #unzip the file
                zip.extractall(r'%s' %basename)

                #List the name of files available from the downloaded file
                print "Files available are:\n"
                dirList = os.listdir(basename)
                for fname in dirList:
                    print fname                           
                break
            else:
                print "Invalid option. Please try again"                      
                    
    listOfDataSets(uid)  
    while True:
        answer = raw_input("\nDo you want to download more datasets? (Yes/No):\t")
        if answer == "Yes":
            listOfDataSets(uid)
        else:
            print "\n"
            break
     
if __name__ == "__main__":
    listOfWatersheds()
    while True:
        answer = raw_input("\nDo you want to select another watershed? (Yes/No):\t")
        if answer == "Yes":
            listOfWatersheds()
        else:
            print "\n"
            break


