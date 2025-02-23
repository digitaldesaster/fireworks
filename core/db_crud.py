#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append('core')
from core.db_document import File
from core.db_connect import *
import os

import json,datetime
from flask import session

from db_default import getCounter
from bson import ObjectId

def createDocument(form_data, document, request=None):
    print(f"[DEBUG] Starting createDocument with form_data keys: {form_data.keys()}")
    # Remove csrf_token before processing
    form_data = {k: v for k, v in form_data.items() if k != 'csrf_token'}
    
    try:
        # Initialize document with default values if it's a new document
        if isinstance(document, type):
            document = document()
        
        # Handle counter if needed
        try:
            counter_name = document.getCounterName()
            counter = getCounter(counter_name)
            document[counter_name] = counter
        except Exception as e:
            print(f"[DEBUG] Counter error: {str(e)}")

        # Process all non-file fields
        for key in form_data.keys():
            if key.startswith('files_'):
                continue
                
            if form_data[key] is None or (isinstance(form_data[key], list) and not form_data[key]):
                continue

            if key.endswith('_hidden'):
                base_key = key.replace('_hidden', '')
                if form_data[key]:
                    document[f"{base_key}_id"] = form_data[key]
                continue

            if form_data[key] == '':
                continue

            if '_date' in key:
                try:
                    document[key] = datetime.datetime.strptime(form_data[key], "%d.%m.%Y") if form_data[key] else None
                except ValueError as e:
                    return {'status': 'error', 'message': f'Invalid date format for field {key}'}
            elif '_int' in key:
                try:
                    document[key] = int(form_data[key]) if form_data[key] else None
                except ValueError:
                    return {'status': 'error', 'message': f'Invalid integer value for field {key}'}
            elif '_float' in key:
                try:
                    document[key] = float(form_data[key]) if form_data[key] else None
                except ValueError:
                    return {'status': 'error', 'message': f'Invalid float value for field {key}'}
            elif key != 'id':
                document[key] = form_data[key]

        # Save document
        try:
            document.save()
            return {'status': 'ok', 'message': '', 'data': document.to_json()}
            
        except ValidationError as e:
            print(f"[DEBUG] Validation error: {str(e)}")
            return {'status': 'error', 'message': f'validation error: {str(e)}', 'data': document.to_json()}
        except Exception as e:
            print(f"[DEBUG] Save error: {str(e)}")
            return {'status': 'error', 'message': f'document not created: {str(e)}'}

    except Exception as e:
        print(f"[DEBUG] Error in createDocument: {str(e)}")
        return {'status': 'error', 'message': f'Error creating document: {str(e)}'}

def updateDocument(form_data, document, collection):
    # Remove csrf_token before processing
    form_data = {k: v for k, v in form_data.items() if k != 'csrf_token'}
    
    try:
        print(f"[DEBUG] Updating document with id={form_data['id']}")
        object_id = ObjectId(form_data['id'])
        document = collection.objects(_id=object_id).first()
        
        if document is None:
            return {'status': 'error', 'message': 'document not found'}

        for key in form_data.keys():
            if key == 'id':  # Skip id field
                continue

            # Handle document search fields
            if key.endswith('_hidden'):
                base_key = key.replace('_hidden', '')
                if '_search' in base_key:
                    # Clear both the search field and its ID if hidden field is empty
                    if not form_data[key]:
                        document[base_key] = ''
                        document[f"{base_key}_id"] = ''
                    else:
                        document[f"{base_key}_id"] = form_data[key]
                else:
                    if base_key in form_data:
                        document[base_key] = form_data[base_key]  # Will be "On" if checked
                    else:
                        document[base_key] = "Off"  # Default to Off if unchecked
                continue

            # Handle different field types
            if '_date' in key:
                try:
                    document[key] = datetime.datetime.strptime(form_data[key], "%d.%m.%Y") if form_data[key] else None
                except:
                    return {'status': 'error', 'message': 'error preparing form date field'}
            elif '_int' in key:
                document[key] = int(form_data[key]) if form_data[key] else None
            elif '_float' in key:
                document[key] = float(form_data[key].replace(',','.')) if form_data[key] else None
            else:
                document[key] = form_data[key]

        # Save document
        try:
            document.save()
            return {'status': 'ok', 'message': '', 'data': document.to_json()}
        except ValidationError as e:
            print(f"Validation error: {str(e)}")
            return {'status': 'error', 'message': f'validation error: {str(e)}', 'data': document.to_json()}
        except Exception as e:
            print(f"Error saving document: {str(e)}")
            return {'status': 'error', 'message': f'error saving document: {str(e)}'}
            
    except Exception as e:
        print(f"[DEBUG] Error in updateDocument: {str(e)}")
        return {'status': 'error', 'message': f'Error updating document: {str(e)}'}

def eraseDocument(id, document, collection):
    try:
        print(f"[DEBUG] Attempting to delete document with id={id}")
        object_id = ObjectId(id)
        document = collection.objects(_id=object_id).first()
        
        if document is not None:
            print(f"[DEBUG] Found document to delete: {document.to_json()}")
            
            # Handle file deletion for both File collection and associated files
            if collection == File:
                # Direct file document deletion
                try:
                    file_path = os.path.join(document.path, f"{id}.{document.file_type}")
                    os.remove(file_path)
                    print(f"[DEBUG] Deleted associated file: {file_path}")
                except FileNotFoundError:
                    print('[DEBUG] File not found, continuing with document deletion')
            else:
                # Delete associated files from File collection
                associated_files = File.objects(document_id=str(id))
                for file_doc in associated_files:
                    try:
                        file_path = os.path.join(file_doc.path, f"{file_doc.id}.{file_doc.file_type}")
                        os.remove(file_path)
                        file_doc.delete()
                        print(f"[DEBUG] Deleted associated file: {file_path}")
                    except FileNotFoundError:
                        print(f'[DEBUG] File not found for {file_doc.id}, continuing with deletion')
                    except Exception as e:
                        print(f'[DEBUG] Error deleting associated file: {str(e)}')
                    
            document.delete()
            print(f"[DEBUG] Document deleted successfully")
            return {'status': 'ok', 'message': 'deleted'}
        else:
            print(f"[DEBUG] No document found with id={id}")
            return {'status': 'error', 'message': 'document not found'}
    except Exception as e:
        print(f"[DEBUG] Error in eraseDocument: {str(e)}")
        return {'status': 'error', 'message': f'Error deleting document: {str(e)}'}

def getDocument(id, document, collection):
    try:
        print(f"[DEBUG] Querying collection {collection.__name__} for document with id={id}")
        # Convert string id to ObjectId
        object_id = ObjectId(id)
        print(f"[DEBUG] Using ObjectId: {object_id}")
        
        # Try direct query first
        document = collection.objects(_id=object_id).first()
        
        if document is None:
            # Try alternate query structure
            document = collection.objects(__raw__={'_id': {'$oid': id}}).first()
        
        if document is not None:
            #print(f"[DEBUG] Found document: {document.to_json()}")
            return {'status': 'ok', 'message': '', 'data': document.to_json()}
        else:
            # Let's print all documents in collection to debug
            all_docs = collection.objects().limit(1)
            print(f"[DEBUG] Sample document from collection: {[doc.to_json() for doc in all_docs]}")
            print(f"[DEBUG] No document found with id={id} in collection {collection.__name__}")
            return {'status': 'error', 'message': f'Document not found in {collection.__name__}'}
    except Exception as e:
        print(f"[DEBUG] Error in getDocument: {str(e)}")
        return {'status': 'error', 'message': f'Error retrieving document: {str(e)}'}
