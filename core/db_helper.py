#!/usr/bin/env python
# -*- coding: utf-8 -*-
from core.db_connect import *

from core.db_modules import *
from core.db_date import dbDates
import json

def searchDocuments(collection, searchFields,start = 0, limit = 10, search = '',filter='',product_name='',mode=''):
    searchAnd = []
    searchDict={}

    if (search != None and search !=''):
        searchArray = []
        for name in searchFields:
            #search contains string, option i means case insentive
            searchArray.append({name: {'$regex': search, '$options' : 'i'}})

        searchDict = {'$or': searchArray}

        if filter !='':
            searchAnd = getFilterDict(filter)

        if product_name!='':
            searchAnd.append({'name' : product_name})

        if searchAnd != []:
            searchDict['$and'] = searchAnd

        if mode =='channels':
            recordsTotal = collection.objects(__raw__=searchDict).count()
            documents = collection.objects(__raw__=searchDict).order_by('category_id').skip(start).limit(limit)
        else:
            recordsTotal = collection.objects(__raw__=searchDict).count()
            documents = collection.objects(__raw__=searchDict).skip(start).limit(limit)
        return processDocuments(documents,recordsTotal,start,limit)
    else:
        if filter !='':
            searchDict = {}
            searchAnd = getFilterDict(filter)
            if searchAnd !=[]:
                if product_name!='':
                    searchAnd.append({'name' : product_name})
                searchDict['$and'] = searchAnd
                if mode =='channels':
                    recordsTotal = collection.objects(__raw__=searchDict).count()
                    documents = collection.objects(__raw__=searchDict).order_by('category_id').skip(start).limit(limit)
                else:
                    recordsTotal = collection.objects(__raw__=searchDict).count()
                    documents = collection.objects(__raw__=searchDict).skip(start).limit(limit)
                return processDocuments(documents,recordsTotal,start,limit)
            else:
                return {'status' : 'error', 'message' : 'no filter found' }
        else:
            if product_name!='':
                searchDict['$and'] = [{'name' : product_name}]
                if mode =='channels':
                    recordsTotal = collection.objects(__raw__=searchDict).count()
                    documents = collection.objects(__raw__=searchDict).order_by('category_id').skip(start).limit(limit)
                else:
                    recordsTotal = collection.objects(__raw__=searchDict).count()
                    documents = collection.objects(__raw__=searchDict).skip(start).limit(limit)
                return processDocuments(documents,recordsTotal,start,limit)
            else:
                if mode=='channels':
                    recordsTotal = collection.objects().count()
                    documents = collection.objects.order_by('category_id').skip(start).limit(limit)

                else:
                    recordsTotal = collection.objects().count()
                    documents = collection.objects.skip(start).limit(limit)
                return processDocuments(documents,recordsTotal,start,limit)




def getFile(file_id):
    file = File.objects(id=file_id).first()
    if file !=None:
        return {'status' : 'ok','message' :'', 'data' : file.to_json()}
    else:
        return {'status' : 'error', 'message' : 'no file found' }


def getDocumentsByID(collection,name, start=0, limit = 10,id=''):
    if id !='':
        recordsTotal = collection.objects(__raw__ = {name: {'$regex': id}}).count()
        documents = collection.objects(__raw__ = {name: {'$regex': id}}).skip(start).limit(limit)
        return processDocuments(documents,recordsTotal,start,limit)
    else:
        return processDocuments(None, recordsTotal,start,limit)

def getDocumentName(id, mode,field):
    default = getDefaults(mode)
    try:
        document = default.collection.objects(id = id).only(field).first()
        if document:
            return document[field]
        return ''
    except:
        return ''

def getFilter(category):
    data = []
    try:
        filters = Filter.objects(category = category)
        if filters != None :
            for filter in filters:
                #print filter
                name = filter.name
                filter_id = str(filter.id)
                data.append({'name' : name,'id' : filter_id})
            return data
    except:
        return []

def getMailTemplates(category):
    data = []
    try:
        templates = MailTemplate.objects(category = category)
        if templates != None :
            for template in templates:
                #print filter
                name = template.name
                template_id = str(template.id)
                data.append({'name' : name,'id' : template_id})
            return data
    except:
        return []

def processDocuments(documents, recordsTotal,start,limit):

    print ('processDocuments')

    prev = 0
    if start - limit > -1:
        prev = start - limit

    last = None

    i = start
    z = 0

    next = 0
    if start + limit < recordsTotal:
        next = start + limit
        last = recordsTotal - limit

    end = start + limit

    if recordsTotal > 0:
        start = start + 1
        if end > recordsTotal:
            end = recordsTotal


    if documents != None:
        return {'status' : 'ok','message' :'', 'data' : documents.to_json(),'recordsTotal' : recordsTotal, 'limit' : limit,'prev' : prev, 'next' : next, 'start' : start,'end' : end,'last' : last}
    return {'status' : 'error', 'message' : 'no documents found' }
def getFilterDict(filter_id):
    data = []
    try:
        filter = Filter.objects(id=filter_id).first()
        if 'filter' in filter:
            for x in filter['filter']:

                if x['field'].find('_date') == -1:
                    if x['operator'] =='is':
                        data.append({x['field'] : x['value']})
                    elif x['operator'] =='contains':
                        data.append({x['field'] : { '$regex' : x['value'],'$options' : 'i' }})
                    elif x['operator'] == 'is_not':
                        data.append({x['field'] : { '$ne' : x['value'] }})
                    elif x['operator'] == 'starts_with':
                        data.append({x['field'] : { '$regex' : '^'+x['value'] }})
                else:
                    if x['value'] =='current_week':
                        data.append({x['field'] : dbDates().thisWeek()})
                    elif x['value'] =='current_month':
                        data.append({x['field'] : dbDates().thisMonth()})
                    elif x['value'] =='current_year':
                        data.append({x['field'] : dbDates().thisYear()})
                    elif x['operator'] =='is_gte':
                        data.append({x['field'] : {'$gte': x['value']}})
                    elif x['operator'] =='is_lt':
                        data.append({x['field'] : {'$lt': x['value']}})
    except:
        pass
    return data
