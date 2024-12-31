#!/usr/bin/env python
# -*- coding: utf-8 -*-
from core.db_connect import *
from core.db_modules import *
from core.db_date import dbDates
from core.db_document import File, getDefaults
import json
import os

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
    try:
        file = File.objects(id=file_id).first()
        if file is not None:
            # Verify file exists on disk
            file_path = os.path.join(file.path, f"{file_id}.{file.file_type}")
            if os.path.exists(file_path):
                return {'status': 'ok', 'message': '', 'data': file.to_json()}
            else:
                print(f"[DEBUG] Physical file not found at: {file_path}")
                return {'status': 'error', 'message': 'Physical file not found'}
        else:
            print(f"[DEBUG] No file record found for id: {file_id}")
            return {'status': 'error', 'message': 'File record not found'}
    except Exception as e:
        print(f"[DEBUG] Error in getFile: {str(e)}")
        return {'status': 'error', 'message': f'Error retrieving file: {str(e)}'}


def getDocumentsByID(collection, name, start=0, limit=10, id=''):
    if not id:
        # Return empty result set when no id is provided
        return {
            'status': 'ok',
            'message': '',
            'data': '[]',
            'recordsTotal': 0,
            'limit': limit,
            'prev': 0,
            'next': None,
            'start': 0,
            'end': 0,
            'last': None
        }
        
    try:
        recordsTotal = collection.objects(__raw__={name: {'$regex': id}}).count()
        documents = collection.objects(__raw__={name: {'$regex': id}}).skip(start).limit(limit)
        return processDocuments(documents, recordsTotal, start, limit)
    except Exception as e:
        print(f"[DEBUG] Error in getDocumentsByID: {str(e)}")
        return {'status': 'error', 'message': 'Error retrieving documents'}

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

def processDocuments(documents, recordsTotal, start, limit):
    print('processDocuments')
    
    # Handle case where documents is None or recordsTotal is not defined
    if documents is None or recordsTotal is None:
        return {'status': 'error', 'message': 'no documents found'}

    # Calculate pagination values
    prev = max(0, start - limit) if start - limit > -1 else 0
    next = start + limit if start + limit < recordsTotal else None
    last = recordsTotal - limit if recordsTotal > limit else None
    
    # Adjust start and end values
    end = min(start + limit, recordsTotal)
    display_start = start + 1 if recordsTotal > 0 else start

    return {
        'status': 'ok',
        'message': '',
        'data': documents.to_json(),
        'recordsTotal': recordsTotal,
        'limit': limit,
        'prev': prev,
        'next': next,
        'start': display_start,
        'end': end,
        'last': last
    }

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
