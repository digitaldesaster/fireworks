#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append('core')
from core.db_document import File, Prompt
from core.db_connect import *
import os

import json,datetime
from flask import session
from flask_login import current_user

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
        print(f"[DEBUG] eraseDocument called with id={id}, collection={collection.__name__}")
        object_id = ObjectId(id)
        document = collection.objects(_id=object_id).first()
        
        if document is not None:
            print(f"[DEBUG] Found document to delete: {document.to_json()}")
            
            # Get base path for constructing absolute paths
            base_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
            print(f"[DEBUG] Base path: {base_path}")
            
            # Handle file deletion for both File collection and associated files
            if collection == File:
                # Check if user has permission to delete this file
                if not document.can_access(current_user):
                    print(f"[DEBUG] Access denied for file deletion: {id}")
                    return {'status': 'error', 'message': 'Access denied. You can only delete your own files.'}
                
                # Check if file is used by any prompt
                prompts_using_file = Prompt.objects(document_id=str(id))
                if prompts_using_file:
                    print(f"[DEBUG] File {id} is used by prompts, cannot delete")
                    return {'status': 'error', 'message': 'File is used by one or more prompts and cannot be deleted'}
                    
                # Direct file document deletion
                try:
                    # Use the same path construction as upload_files
                    file_path = os.path.join(base_path, document.path, f"{id}.{document.file_type}")
                    print(f"[DEBUG] Attempting to delete file at: {file_path}")
                    print(f"[DEBUG] File exists: {os.path.exists(file_path)}")
                    
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        print(f"[DEBUG] Successfully deleted file: {file_path}")
                    else:
                        print(f'[DEBUG] Physical file not found at: {file_path}')
                except Exception as e:
                    print(f'[DEBUG] Error deleting physical file: {str(e)}')
                    return {'status': 'error', 'message': f'Error deleting physical file: {str(e)}'}
                
                try:
                    document.delete()
                    print(f"[DEBUG] Successfully deleted file document from database")
                    return {'status': 'ok', 'message': 'deleted'}
                except Exception as e:
                    print(f'[DEBUG] Error deleting file document: {str(e)}')
                    return {'status': 'error', 'message': f'Error deleting file document: {str(e)}'}
            else:
                # For non-File collections, handle associated files
                file_ids = []
                
                # Check for files linked by document_id
                associated_files = File.objects(document_id=str(id))
                file_ids.extend([str(f.id) for f in associated_files])
                
                # Check for files in file_ids array (used by History documents)
                if hasattr(document, 'file_ids') and document.file_ids:
                    file_ids.extend(document.file_ids)
                
                # Remove duplicates
                file_ids = list(set(file_ids))
                print(f"[DEBUG] Found {len(file_ids)} associated files")
                print(f"[DEBUG] File IDs to process: {file_ids}")
                
                deleted_files = []
                failed_files = []
                
                for file_id in file_ids:
                    try:
                        print(f"[DEBUG] Processing associated file: {file_id}")
                        file_doc = File.objects(id=file_id).first()
                        if not file_doc:
                            print(f"[DEBUG] File document not found: {file_id}")
                            failed_files.append(file_id)
                            continue
                            
                        # Check if file is used by any prompt
                        prompts_using_file = Prompt.objects(document_id=str(file_id))
                        if prompts_using_file:
                            print(f"[DEBUG] File {file_id} is used by prompts, skipping")
                            failed_files.append(file_id)
                            continue
                        
                        # Check if user has permission to delete this file
                        if not file_doc.can_access(current_user):
                            print(f"[DEBUG] Access denied for associated file deletion: {file_id}")
                            failed_files.append(file_id)
                            continue
                            
                        # Delete physical file
                        # Use the same path construction as upload_files
                        file_path = os.path.join(base_path, file_doc.path, f"{file_id}.{file_doc.file_type}")
                        print(f"[DEBUG] Attempting to delete associated file at: {file_path}")
                        print(f"[DEBUG] File exists: {os.path.exists(file_path)}")
                        
                        if os.path.exists(file_path):
                            os.remove(file_path)
                            print(f"[DEBUG] Successfully deleted associated file: {file_path}")
                        else:
                            print(f'[DEBUG] Physical file not found at: {file_path}')
                        
                        # Delete file document
                        file_doc.delete()
                        deleted_files.append(file_id)
                        print(f"[DEBUG] Successfully deleted associated file document: {file_id}")
                    except Exception as e:
                        print(f'[DEBUG] Error deleting associated file {file_id}: {str(e)}')
                        failed_files.append(file_id)
                
                try:
                    document.delete()
                    status_msg = 'deleted'
                    if failed_files:
                        status_msg += f' (some associated files could not be deleted: {", ".join(map(str, failed_files))})'
                    print(f"[DEBUG] Successfully deleted main document with status: {status_msg}")
                    return {'status': 'ok', 'message': status_msg}
                except Exception as e:
                    print(f'[DEBUG] Error deleting main document: {str(e)}')
                    return {'status': 'error', 'message': f'Error deleting document: {str(e)}'}
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
