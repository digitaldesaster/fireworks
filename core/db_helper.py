#!/usr/bin/env python
# -*- coding: utf-8 -*-
from core.db_connect import *
from core.db_date import dbDates
from core.db_document import File, getDefaults, Filter
import json
import os

def searchDocuments(collection, searchFields, start=0, limit=10, search='', filter=None, product_name='', mode=''):
    print(f"[DEBUG] searchDocuments called with filter={filter}")
    searchDict = {}

    # Handle search term if provided
    if search and search.strip():
        searchArray = []
        for name in searchFields:
            searchArray.append({name: {'$regex': search, '$options': 'i'}})
        searchDict = {'$or': searchArray}

    # Handle filter
    if filter:
        if isinstance(filter, str):
            # For string filters, use getFilterDict
            filter_dict = getFilterDict(filter)
            print(f"[DEBUG] Filter string converted to: {filter_dict}")
            if filter_dict:
                if searchDict:
                    if '$and' not in searchDict:
                        searchDict = {'$and': [searchDict]}
                    searchDict['$and'].extend(filter_dict)
                else:
                    searchDict = {'$and': filter_dict}
        else:
            # For direct dictionary filters (like user_id filter)
            print(f"[DEBUG] Using direct filter: {filter}")
            if searchDict:
                if '$and' not in searchDict:
                    searchDict = {'$and': [searchDict, filter]}
                else:
                    searchDict['$and'].append(filter)
            else:
                searchDict.update(filter)

    # Handle product name
    if product_name:
        product_filter = {'name': product_name}
        if searchDict:
            if '$and' not in searchDict:
                searchDict = {'$and': [searchDict, product_filter]}
            else:
                searchDict['$and'].append(product_filter)
        else:
            searchDict = product_filter

    print(f"[DEBUG] Final search dict: {searchDict}")

    try:
        # Test the query first
        test_count = collection.objects(__raw__=searchDict).count()
        print(f"[DEBUG] Test query found {test_count} documents")
        
        # Apply the query
        if mode == 'channels':
            recordsTotal = collection.objects(__raw__=searchDict).count()
            documents = collection.objects(__raw__=searchDict).order_by('category_id').skip(start).limit(limit)
        else:
            recordsTotal = collection.objects(__raw__=searchDict).count()
            documents = collection.objects(__raw__=searchDict).skip(start).limit(limit)

        return processDocuments(documents, recordsTotal, start, limit)
    except Exception as e:
        print(f"[DEBUG] Error in searchDocuments: {str(e)}")
        print(f"[DEBUG] Collection: {collection}")
        print(f"[DEBUG] Search dict: {searchDict}")
        return {'status': 'error', 'message': str(e)}




def getFile(file_id):
    try:
        file = File.objects(id=file_id).first()
        if file is not None:
            # Get the base directory (where the application is running)
            base_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
            
            # Check relative path
            file_path = os.path.join(file.path, f"{file_id}.{file.file_type}")
            if os.path.exists(file_path):
                print(f"[DEBUG] File exists at path: {file_path}")
                return {'status': 'ok', 'message': '', 'data': file.to_json()}
            
            # Check absolute path
            abs_path = os.path.join(base_path, file.path, f"{file_id}.{file.file_type}")
            if os.path.exists(abs_path):
                print(f"[DEBUG] File exists at absolute path: {abs_path}")
                return {'status': 'ok', 'message': '', 'data': file.to_json()}
            
            # Check if the file exists in the category folder
            if hasattr(file, 'category') and file.category:
                category_path = os.path.join(base_path, 'core', 'documents', file.category, f"{file_id}.{file.file_type}")
                if os.path.exists(category_path):
                    print(f"[DEBUG] File found in category folder: {category_path}")
                    # Update the file path in the database
                    file.path = os.path.join('core', 'documents', file.category)
                    file.save()
                    return {'status': 'ok', 'message': '', 'data': file.to_json()}
            
            print(f"[DEBUG] Physical file not found at: {file_path}")
            # Just return the file data anyway and let download_file handle the rest
            return {'status': 'ok', 'message': '', 'data': file.to_json()}
        else:
            print(f"[DEBUG] No file record found for id: {file_id}")
            return {'status': 'error', 'message': 'File record not found'}
    except Exception as e:
        print(f"[DEBUG] Error in getFile: {str(e)}")
        return {'status': 'error', 'message': str(e)}


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

# def getMailTemplates(category):
#     data = []
#     try:
#         templates = MailTemplate.objects(category = category)
#         if templates != None :
#             for template in templates:
#                 #print filter
#                 name = template.name
#                 template_id = str(template.id)
#                 data.append({'name' : name,'id' : template_id})
#             return data
#     except:
#         return []

def processDocuments(documents, recordsTotal, start, limit):
    print('processDocuments')
    
    # Handle case where documents is None
    if documents is None:
        return {'status': 'error', 'message': 'no documents found'}

    # Calculate pagination values
    prev = max(0, start - limit) if start - limit > -1 else 0
    next = start + limit if start + limit < recordsTotal else None
    last = recordsTotal - limit if recordsTotal > limit else None
    
    # Adjust start and end values
    end = min(start + limit, recordsTotal)
    display_start = start + 1 if recordsTotal > 0 else start

    # Return successful response even if no documents found (empty list is valid)
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
