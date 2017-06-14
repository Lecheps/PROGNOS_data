import AquaMonitor
import datetime
import pandas as pd
#import numpy as np



def getLangtjernData(username,password,root,fromDate,toDate) :
    weatherFile = 'langtjern_weather.csv'
    lakeFile = 'langtjern_lake.csv'
    outletFile = 'langtjern_outlet.csv'
    inletFile = 'langtjern_inlet.csv'

    fromDate = datetime.datetime.strptime(fromDate,"%Y/%m/%d").date()
    toDate = datetime.datetime.strptime(toDate,"%Y/%m/%d").date()
    expires = datetime.date.today() + datetime.timedelta( days=1 )
    
    token = AquaMonitor.login("AquaServices", username, password)
    
    def make_file(title, filename, stationid, datatype) :
        where = "sample_date>=" + datetime.datetime.strftime(fromDate, '%d.%m.%Y') \
            + " and sample_date<" + datetime.datetime.strftime(toDate, '%d.%m.%Y') \
            + " and datatype=" + datatype
        data = {
            "Expires": expires.strftime('%Y.%m.%d'),
            "Title": title,
            "Files":[{
                "Filename": filename,
                "ContentType":"text/csv"}],
            "Definition":{
                "Format":"csv",
                "StationIds": [ stationid ],
                "DataWhere": where
            }
        }
        resp = AquaMonitor.createDatafile(token, data)
        return resp["Id"]
    
    
    def download_file(id, filename) :
        archived = False
        while not archived:
            resp = AquaMonitor.getArchive(token, id)
            archived = resp.get("Archived")
        path = root + filename
        AquaMonitor.download(token, id, filename, path)


    
    #Four measurement id's can be obtained from Langtjern
    weatherFileId = make_file('Langtjern weather', weatherFile, 62040, 'Air')
    lakeFileId = make_file('Langtjern lake', lakeFile, 50472, 'Water')
    outletFileId = make_file('Langtjern outlet', outletFile, 51356, 'Water')
    inletFileId = make_file('Langtjern inlet', inletFile, 63098, 'Water')
    
    download_file(weatherFileId, weatherFile)
    download_file(lakeFileId, lakeFile)
    download_file(inletFileId, inletFile)
    download_file(outletFileId, outletFile)
    
    allData = {}
    
    #Putting the data into the right format
    #First placing dataframes in a dictionary
    allData['weather'] = pd.read_csv(root + weatherFile,    delimiter=';', encoding='utf-16')
    allData['lake']    = pd.read_csv(root + lakeFile,       delimiter=';', encoding='utf-16')
    allData['outlet']  = pd.read_csv(root + outletFile,     delimiter=';', encoding='utf-16')
    allData['inlet']   = pd.read_csv(root + inletFile,      delimiter=';', encoding='utf-16')
    
    #Make the index of the dataframes a timestamp, storing only float data (hopefully measurements)
    for key, i in allData.iteritems():
        i.set_index(pd.to_datetime(i["SampleDate_dato"].map(str) + ' ' + i["SampleDate_tid"],format = '%d.%m.%Y %H:%M:%S',utc=True),inplace=True)
        allData[key] = i.loc[:,i.dtypes == 'float64']
    return allData
    
