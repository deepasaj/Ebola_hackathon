#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bottle import route, run, response
import csv
import json
import datetime
import urllib
import urllib2
from os import environ
from bottle import static_file

@route('/districts/lat_long')
def getDistrictsLatLong():
    result = pruneDataSet()
    districtLatLongList = []
    uniqueDistricts=findUniqueValues("district", result)
    for district in uniqueDistricts:
        districtLatLongList.append(getLatLong(district))
    return {"districtsCoord": districtLatLongList}

@route('/districts/density')
def computeDistrictDensity():
    results = pruneDataSet()
    densities = []
    for result in results:
        resultDistrict = result["district"]
        resultDate = result["call_date"]
        districtFlag=0
        for density in densities:
            if density["district"] == resultDistrict:
                districtFlag=1
                dateFlag=0
                for dateRange in density["dateRanges"]:
                    if dateRange["date"] == resultDate:
                        dateRange["count"]+=1
                        dateFlag=1
                if dateFlag==0:
                    density["dateRanges"].append({"date": resultDate, "count": 1})
        if districtFlag == 0:
            dateRange=[]
            dateRange.append({"date": resultDate, "count": 1})
            densities.append({"district": resultDistrict, "dateRanges": dateRange})
    return {"densities": densities}

@route('/ui/<filename:re:.*>')
def root(filename):
    return static_file(filename, root="ui")

def pruneDataSet():
    result=[]
    response.content_type = 'application/json'
    ebola_source_file=open('ebola.csv', 'r')
    field_names = ("call_date","call_time","province","district")
    csv_file_reader = csv.DictReader(ebola_source_file, field_names)
    next(csv_file_reader)
    for row in csv_file_reader:
        if validDate(row["call_date"]):
           result.append(row)
    return result


def findUniqueValues(key, result):
    lookup = {}
    uniqueValues = []
    for item in result:
        name = item[key]
        if not (name in lookup):
            lookup[name] = 1
            uniqueValues.append(name)
    return uniqueValues

def validDate(dateString):
  result = True
  try:
    datetime.datetime.strptime(dateString, '%d/%m/%Y')
  except ValueError, e:
    result = False
  return result

def getLatLong(district):
    api_key = 'AIzaSyDOjBGZEBvLCpHXkNvl-bBBxKHhzAeSaqU'
    address = urllib.quote(district+',Sierra Leone')
    url = 'https://maps.googleapis.com/maps/api/geocode/json?address='+address+'&key='+api_key
    response = json.loads(urllib2.urlopen(url).read())
    co_ord=response["results"][0]["geometry"]["location"]
    return {"name": district, "lat": co_ord["lat"], "lng": co_ord["lng"]}

run(host="0.0.0.0", port=int(environ.get('PORT', 8080)));
