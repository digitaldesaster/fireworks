#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json,os,csv,base64
from core.db_helper import searchDocuments, getFile, getDocumentsByID, getFilter, processDocuments, getFilterDict, getDocumentName
from core.db_crud import getDocument, updateDocument, createDocument, eraseDocument
from core.db_default import Setting, getDefaultList
from core.db_document import File, getDefaults

from pypdf import PdfReader
    
import datetime

from werkzeug.utils import secure_filename

from flask_login import current_user

import sys
sys.path.append('core')
from flask import redirect, url_for, flash
from bson import ObjectId

UPLOAD_FOLDER = 'temp'
DOCUMENT_FOLDER = 'documents'

import logging
current_path = os.path.dirname(os.path.realpath(__file__)) + '/'
# logging.basicConfig(format='%(asctime)s %(message)s\n\r',filename=current_path+'import_leads.log', level=logging.INFO,filemode='w')


from flask import render_template, redirect, url_for, jsonify, flash

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','csv','md'])

def getRequestData(request):
    limit = request.args.get('limit')
    start = request.args.get('start')
    search = request.args.get('search')
    id = request.args.get('id')
    filter = request.args.get('filter')
    product_name = request.args.get('product_name')
    offer_id = request.args.get('offer_id')

    if product_name == None:
        product_name=''
    if search == None:
        search = ''
    if filter == None:
        filter = ''
    if id == None:
        id = ''
    if start == None:
        start = 0
    else:
        start = int(start)
    if limit == None:
        limit = 50
    else:
        limit = int(limit)

    end = start + limit

    if offer_id == None:
        offer_id=''



    return start,limit,end,search, id,filter,product_name,offer_id

def initData():
    data = []
    prev = None
    next = None
    last = None
    recordsTotal = 0  # Initialize to 0 instead of None

    return data, prev, next, last, recordsTotal

def loadData(mydata):
    if (mydata['status'] == 'ok'):
        data = json.loads(mydata['data'])
        prev = mydata['prev']
        next = mydata['next']
        last = mydata['last']
        start = mydata['start']
        end = mydata['end']
        recordsTotal = mydata['recordsTotal']

        #pages = mydata['pages']
        i=0
        for x in data:
            data[i]['id'] = x['_id']['$oid']
            i=i+1
        return data,start,end,prev,next,recordsTotal,last
    return None

def getList(name, request, filter=None, return_json=False):
    print(f"[DEBUG] getList called for {name}")
    default = getDefaults(name)
    if default == None:
        print("[DEBUG] No defaults found")
        return redirect(url_for('index'))
        
    # Check if user can list this collection
    if not default.document.can_list(current_user):
        print("[DEBUG] User cannot list this collection")
        flash('Access denied.', 'error')
        return redirect(url_for('index'))
        
    data, prev, next, last, recordsTotal = initData()
    start,limit,end,search,id,filter_param,product_name,offer_id = getRequestData(request)
    
    filter_data = getFilter(default.document_name)
    mode = default.collection_name
    
    # Get access control filter for this document type
    access_filter = default.document.get_list_filter(current_user)
    print(f"[DEBUG] Access filter: {access_filter}")
    
    # Combine all filters
    combined_filter = {}
    if access_filter:
        combined_filter.update(access_filter)
    if filter:
        combined_filter.update(filter)
    if filter_param:
        filter_dict = getFilterDict(filter_param)
        combined_filter.update(filter_dict)
    
    print(f"[DEBUG] Combined filter: {combined_filter}")

    # Process the search query with combined filters
    # Pass empty dict if no filter to avoid "no filter found" error
    filter_to_use = combined_filter if combined_filter else {}
    mydata = searchDocuments(default.collection, default.document.searchFields(), 
                           start, limit, search, filter_to_use, product_name, mode)
    print(f"[DEBUG] Search results: {mydata}")

    processedData = loadData(mydata)
    if processedData:
        data, start, end, prev, next, recordsTotal, last = processedData
        print(f"[DEBUG] Found {recordsTotal} records")
        recordsTotal = int(recordsTotal) if recordsTotal is not None else 0
        if return_json:
            return jsonify({
                'status': 'ok',
                'message': 'success',
                'data': data,
                'recordsTotal': recordsTotal,
                'prev': prev,
                'next': next,
                'last': last,
                'start': start,
                'end': end
            })

    table_header = default.document.fields(list_order = True)
    table_content = tableContent(data, table_header)

    try:
        table = request.args.get('table')
        if table:
            return render_template('/base/collection/table.html',
                                 menu=default.menu,
                                 documents=data,
                                 prev=prev,
                                 next=next,
                                 limit=limit,
                                 start=start,
                                 total=recordsTotal,
                                 end=end,
                                 search=search,
                                 id=id,
                                 offer_id=offer_id,
                                 last=last,
                                 page_name_collection=default.page_name_collection,
                                 collection_name=default.collection_name,
                                 collection_url=default.collection_url,
                                 document_url=default.document_url,
                                 mode=mode,
                                 table_header=table_header,
                                 table_content=table_content,
                                 filter=filter_param,
                                 filter_data=filter_data,
                                 show_new_button=True,
                                 product_name=product_name)
    except:
        pass

    return render_template('/base/collection/collection.html',
                         menu=default.menu,
                         documents=data,
                         prev=prev,
                         next=next,
                         limit=limit,
                         start=start,
                         total=recordsTotal,
                         end=end,
                         search=search,
                         id=id,
                         offer_id=offer_id,
                         last=last,
                         page_name_collection=default.page_name_collection,
                         collection_name=default.collection_name,
                         collection_url=default.collection_url,
                         document_url=default.document_url,
                         mode=mode,
                         table_header=table_header,
                         table_content=table_content,
                         filter=filter_param,
                         filter_data=filter_data,
                         show_new_button=True,
                         product_name=product_name)

def handleDocument(name, id, request, return_json=False):
    try:
        default = getDefaults(name)
        if default is None:
            flash('Invalid document type', 'error')
            return redirect(url_for('index'))

        # For existing documents, verify access
        if id:
            doc = default.collection.objects(_id=ObjectId(id)).first()
            if not doc or not doc.can_access(current_user):
                flash('Access denied.', 'error')
                return redirect(url_for('list', collection=default.collection_name))

        # For new documents
        else:
            # Check if user can list (create new) documents of this type
            if not default.document.can_list(current_user):
                flash('Access denied.', 'error')
                return redirect(url_for('index'))
                
            # Set user_id for new documents if they use it
            if request.method == 'POST' and hasattr(default.document, 'user_id'):
                form_data = htmlFormToDict(request.form)
                form_data['user_id'] = str(current_user.id)
                request.form = form_data

        print(f"[DEBUG] Got defaults: document_name={default.document_name}, collection_name={default.collection_name}")
        mode = default.document_name

        # Initialize empty document data for new documents
        data = {}
        if not id:
            print("[DEBUG] Creating new document")
            try:
                # Get the document instance that was already created in getDefaults
                doc = default.document
                if doc is None:
                    raise Exception("Failed to get document instance")
                data = json.loads(doc.to_json())
                data['id'] = ''  # Empty ID for new document
                # Set user_id for new history documents
                if name == 'history':
                    data['user_id'] = str(current_user.id)
            except Exception as e:
                print(f"[DEBUG] Error initializing new document: {str(e)}")
                flash('Error creating new document', 'error')
                return redirect(url_for('index'))

        page = {
            'title': f"{'Add' if not id else 'Edit'} {default.page_name_document}",
            'collection_title': default.collection_title,
            'document_name': default.document_name,
            'document_url': default.document_url,
            'collection_url': default.collection_url,
            'document_title': default.page_name_document
        }
        
        form_data = htmlFormToDict(request.form)
        print(f"[DEBUG] Form data: {form_data}")
        category_fields = []

        if name=='filter':
            form_data = prepFilterData(form_data)

        if request.method == 'POST':
            print("[DEBUG] Processing POST request")
            if (form_data.get('id') and form_data['id'] not in ['', 'None', None]):
                print(f'[DEBUG] Updating Document with ID: {form_data["id"]}')
                data = updateDocument(form_data, default.document, default.collection)
            else:
                print('[DEBUG] Creating new Document')
                data = createDocument(form_data, default.document, request)

            if (data['status'] == 'ok'):
                data = json.loads(data['data'])
                data['id'] = data['_id']['$oid']
                file_status = upload_files(request, default.collection_name, data['id'])
                print(f"[DEBUG] File status: {file_status}")
                if return_json:
                    return json.dumps(data)
                return redirect(url_for('doc', name=default.document_name) + '/' + data['id'])
            else:
                print(f"[DEBUG] Error in POST: {data.get('message', 'Unknown error')}")
                return json.dumps(data)

        elif request.method == 'GET':
            print(f"[DEBUG] Processing GET request with id={id}")
            if id:
                print(f'[DEBUG] Getting Document with ID: {id}')
                data = getDocument(id, default.document, default.collection)
                print(f"[DEBUG] getDocument result: {data}")
                if (data['status'] == 'ok'):
                    page = {'title': 'Edit ' + default.page_name_document, 'collection_title': default.collection_title, 'document_name': default.document_name, 'document_url': default.document_url, 'collection_url': default.collection_url, 'document_title': default.page_name_document}
                    data = json.loads(data['data'])
                    data['id'] = data['_id']['$oid']
                    
                    files = json.loads(File.objects(document_id=data['id']).to_json())
                    print(f"[DEBUG] Found files: {files}")
                    for file in files:
                        if not data.get(file['element_id']):
                            data[file['element_id']] = []
                        file['id'] = file['_id']['$oid']
                        file.pop('_id', None)
                        data[file['element_id']].append(file)
                    
                    if return_json:
                        return json.dumps(data)

                    if 'category' in data and name == 'filter':
                        category_fields = getFields(data['category'])
                else:
                    print(f"[DEBUG] Error getting document: {data.get('message', 'Unknown error')}")
                    print(f"[DEBUG] Redirecting to list with name={default.collection_name}")
                    return redirect(url_for('list', collection=default.collection_name))

        print("[DEBUG] Getting elements")
        elements = getElements(data, default.document)
        #print(f"[DEBUG] Elements: {elements}")
        return render_template('/base/document/form.html', elements=elements, menu=default.menu, page=page, document=data, mode=mode, category_fields=category_fields)
    except Exception as e:
        print(f"[DEBUG] Error in handleDocument: {str(e)}")
        flash('An error occurred while processing your request', 'error')
        return redirect(url_for('index'))

def deleteDocument(request):
    type = request.args.get('type')
    id = request.args.get('id')
    print(f"[DEBUG] deleteDocument called with type={type}, id={id}")
    
    if not id:
        print("[DEBUG] No ID provided")
        return {'status': 'error', 'message': 'no id'}
        
    # Special handling for file deletions
    if type == 'files':
        print(f"[DEBUG] Handling file deletion for id={id}")
        data = eraseDocument(id, File, File)
        print(f"[DEBUG] File deletion result: {data}")
    else:
        print(f"[DEBUG] Handling document deletion for type={type}, id={id}")
        default = getDefaults(type)
        if default == []:
            print(f"[DEBUG] No defaults found for type={type}")
            return {'status': 'error', 'message': 'no document found'}
        data = eraseDocument(id, default.document, default.collection)
        print(f"[DEBUG] Document deletion result: {data}")
        
    if data['status'] == 'ok':
        print("[DEBUG] Deletion successful")
        return {'status': 'ok', 'message': 'document deleted'}
    else:
        print(f"[DEBUG] Deletion failed: {data.get('message', 'unknown error')}")
        return {'status': 'error', 'message': data.get('message', 'document not deleted')}

def tableContent(documents, table_header):
    print(f"[DEBUG] Creating table content for {len(documents)} documents")
    tableContent = []

    for document in documents:
        print(f"[DEBUG] Processing document: {document}")
        tableRow = []
        for field in table_header:
            if field['name'] in document.keys() and 'id' in document.keys():
                value = document[field['name']]
                
                # Handle date fields
                if field['name'].find('_date') != -1:
                    if isinstance(value, dict) and '$date' in value:
                        date = value['$date']
                        value = datetime.datetime.fromtimestamp(date/1000).strftime('%d.%m.%Y')
                
                # Handle link fields for history
                if field['type'] == 'ButtonField' and field.get('link') == '/chat/history':
                    link = f"{field['link']}/{document['id']}"
                    tableRow.append({
                        'name': field['name'],
                        'value': value,
                        'class': field['class'],
                        'id': document['id'],
                        'type': field['type'],
                        'link': link,
                        'label': field['label']
                    })
                else:
                    tableRow.append({
                        'name': field['name'],
                        'value': value,
                        'class': field['class'],
                        'id': document['id'],
                        'type': field['type'],
                        'label': field.get('label', field['name'])
                    })
            else:
                print(f"[DEBUG] Field {field['name']} not found in document or no id")
                tableRow.append('')
        
        if tableRow:  # Only add rows that have content
            tableContent.append(tableRow)
            
    print(f"[DEBUG] Created {len(tableContent)} table rows")
    return tableContent

def getElements(data, document):
    elements=[]
    fields = document.fields()
    for field in fields:
        if not 'required' in field:
            required = False
        else:
            required = True
        if field['type'] == 'SimpleDocumentField':
            elements.append({'type' : getDefaultList(field['name'], Category, 'SimpleDocumentField'), 'name' : field['name'], 'value' : '', 'id' : field['name'], 'label' : field['label'], 'required' : required,'full_width':field['full_width']})
        elif field['type'] == 'SimpleListField':
            elements.append({'type' : 'SimpleListField', 'SimpleListField':getDefaultList(field['name'], Setting, 'SimpleListField'), 'name' : field['name'], 'value' : '', 'id' : field['name'], 'label' : field['label'], 'required' : required,'full_width':field['full_width']})
        elif field['type'] == 'AdvancedListField':
            elements.append({'type' : 'AdvancedListField','AdvancedListField': getDefaultList(field['name'], Setting, 'AdvancedListField'), 'name' : field['name'], 'value' : '', 'id' : field['name'], 'label' : field['label'], 'required' : required,'full_width':field['full_width']})
        elif field['type'] == 'DocumentField':
            elements.append({'type' : 'DocumentField', 'name' : field['name'], 'value' : '' , 'id' : field['name'], 'label' : field['label'], 'required' : required,'full_width':field['full_width'],'module':field['module'],'document_field':field['document_field']})
        elif field['type'] == 'EditorField':
            elements.append({'type' : 'EditorField', 'name' : field['name'], 'value' : '' , 'id' : field['name'], 'label' : field['label'], 'required' : required,'full_width':field['full_width']})

        elif field['type'] == 'DateInfo':
            pass
        elif field['type'] == 'CheckBox':
            elements.append({'type' : field['type'], 'name' : field['name'], 'value' : 0, 'id' : field['name'], 'label' : field['label'], 'required' : required,'full_width':field['full_width']})
        elif field['type'] == 'ButtonField':
            elements.append({'type': field['type'], 'name' : field['name'], 'value' : '', 'id' : field['name'], 'label' : field['label'], 'required' : required,'full_width':field['full_width'],'link':field['link']})
        else:
            elements.append({'type': field['type'], 'name' : field['name'], 'value' : '', 'id' : field['name'], 'label' : field['label'], 'required' : required,'full_width':field['full_width']})

    return fillElements(elements,data)

def fillElements(elements, data):
    # Check if data is empty or None
    if not data or not isinstance(data, dict):
        return elements
        
    for element in elements:
        if element['name'] in data:
            element['value'] = data[element['name']]
            if element['type'] == 'DocumentField':
                id = data.get(f"{element['name']}_id", '')  # Get ID with fallback to empty string
                if id and id != '0815':
                    element['value'] = getDocumentName(data[element['name']], element['module'], element['document_field'])
                    element['document_id'] = id
                    element['url'] = url_for('doc', name=element['module'], id=id)
                else:
                    element['value'] = ''

    return elements
    
def htmlFormToDict(form_data):
    if not form_data:
        return {}
        
    try:
        # Handle ImmutableMultiDict from Flask
        if hasattr(form_data, 'getlist'):
            return {key: form_data.getlist(key)[0] for key in form_data.keys()}
        # Handle regular dict
        elif isinstance(form_data, dict):
            return form_data
        # Handle list of dicts with name/value pairs
        elif isinstance(form_data, list):
            return {item['name']: item['value'] for item in form_data if 'name' in item and 'value' in item}
        else:
            print(f"[DEBUG] Unexpected form_data type: {type(form_data)}")
            return {}
    except Exception as e:
        print(f"[DEBUG] Error in htmlFormToDict: {str(e)}")
        return {}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def upload_files(request, category='', document_id=''):
    status = {'status': 'ok', 'files': []}

    if request.method == 'POST':
        # Get base path for consistent path handling
        base_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        
        # Extract element IDs directly from the file input names
        element_ids = [key.split('files_', 1)[1] for key in request.files.keys()]

        for element_id in element_ids:
            status[element_id] = []  # Initialize list for this element_id
            files = request.files.getlist(f'files_{element_id}')
            if not files or files[0].filename == '':
                continue  # Skip if no files are selected

            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    try:
                        # Use consistent path structure
                        relative_path = os.path.join('core', 'documents', category) if category else os.path.join('core', UPLOAD_FOLDER)
                        absolute_path = os.path.join(base_path, relative_path)
                        
                        print(f"[DEBUG] Upload path (absolute): {absolute_path}")
                        print(f"[DEBUG] Upload path (relative): {relative_path}")

                        if not os.path.exists(absolute_path):
                            print(f"[DEBUG] Creating directory: {absolute_path}")
                            os.makedirs(absolute_path)

                        file_type = filename.rsplit('.', 1)[1]
                        fileDB = File(
                            name=filename, 
                            path=relative_path,  # Store relative path
                            category=category, 
                            file_type=file_type, 
                            document_id=document_id, 
                            element_id=element_id,
                            user_id=str(current_user.id)  # Set the user_id to current user's ID
                        )
                        fileDB.save()
                        fileID = getDocumentID(fileDB)

                        file_save_path = os.path.join(absolute_path, f"{fileID}.{file_type}")
                        print(f"[DEBUG] Saving file to: {file_save_path}")
                        file.save(file_save_path)

                        status[element_id].append({
                            'id': fileID, 
                            'name': filename, 
                            'path': os.path.join(relative_path, f"{fileID}.{file_type}")
                        })

                    except Exception as e:
                        status = {'status': 'error', 'message': f'Error while saving File! / {str(e)}'}
                        return json.dumps(status)
                else:
                    status = {'status': 'error', 'message': 'Filetype not allowed!'}
                    return json.dumps(status)

    return json.dumps(status)

def getDocumentID(document):
    document = json.loads(document.to_json())
    id = document['_id']['$oid']
    return id

def prepFilterData(form_data):
    fields = []
    db_fields = []
    i=0
    for key in form_data:
        if 'field_' in key:
            fieldNumber = key.split('_')[1]
            fields.append(fieldNumber)
    for fieldNumber in fields:
        try:
            value = form_data['value_' + str(fieldNumber)]
            del(form_data['value_' + str(fieldNumber)])
        except:
            value = form_data['date_value_' + str(fieldNumber)]
            value = datetime.datetime.strptime(value, "%d.%m.%Y")
            del(form_data['date_value_' + str(fieldNumber)])

        operator = form_data['operator_' + str(fieldNumber)]
        field = form_data['field_' + str(fieldNumber)]
        db_fields.append({'field' : field,'operator':operator,'value':value,'nr':str(i)})

        del(form_data['field_' + str(fieldNumber)])
        del(form_data['operator_' + str(fieldNumber)])
        i=i+1

    form_data['filter'] = db_fields
    return form_data

#only pdf/txt files are supported for now
def prepare_context_from_files(files):
    result = {
        "status": "error",
        "data": "",
        "character_count": 0
    }
    
    print(f"[DEBUG] prepare_context_from_files called with {len(files)} files")
    
    if not files:
        print("[DEBUG] No files provided")
        result["status"] = "error"
        result["data"] = "No files provided"
        return result

    try:
        combined_text = []
        base_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        print(f"[DEBUG] Base path for file reading: {base_path}")
        
        for file in files:
            try:
                print(f"[DEBUG] Processing file: {file.get('name', 'Unknown')}")
                # Convert MongoDB document to dict if needed
                if hasattr(file, 'to_mongo'):
                    file = file.to_mongo().to_dict()
                    print("[DEBUG] Converted MongoDB document to dict")
                
                # Get file ID consistently
                if isinstance(file.get('_id'), dict) and '$oid' in file['_id']:
                    file_id = file['_id']['$oid']
                elif isinstance(file.get('_id'), str):
                    file_id = file['_id']
                else:
                    file_id = str(file['_id'])
                print(f"[DEBUG] File ID: {file_id}")
                
                # Build full file path
                file_path = os.path.join(base_path, file['path'], f"{file_id}.{file['file_type'].lower()}")
                print(f"[DEBUG] Full file path: {file_path}")
                
                if not os.path.exists(file_path):
                    print(f"[DEBUG] File not found at path: {file_path}")
                    continue
                
                print(f"[DEBUG] Reading file: {file['name']}")
                file_content = f"\nContent of File: {file['name']}\n{'='*50}\n"
                
                if file['file_type'].lower() == 'pdf':
                    try:
                        with open(file_path, 'rb') as pdf_file:
                            pdf_reader = PdfReader(pdf_file)
                            print(f"[DEBUG] PDF has {len(pdf_reader.pages)} pages")
                            for page_num in range(len(pdf_reader.pages)):
                                page = pdf_reader.pages[page_num]
                                text = page.extract_text()
                                if text:
                                    print(f"[DEBUG] Extracted text from page {page_num + 1}")
                                    text = ' '.join(text.split())
                                    text = text.replace(' .', '.').replace(' ,', ',')
                                    paragraphs = text.split('\n')
                                    formatted_text = '\n\n'.join(p.strip() for p in paragraphs if p.strip())
                                    file_content += formatted_text + "\n\n"
                                else:
                                    print(f"[DEBUG] No text found on page {page_num + 1}")
                                    file_content += "[No text found on this page]\n\n"
                    except Exception as e:
                        print(f"[DEBUG] Error reading PDF {file['name']}: {str(e)}")
                        continue
                        
                elif file['file_type'].lower() == 'txt':
                    try:
                        with open(file_path, 'r', encoding='utf-8') as txt_file:
                            text = txt_file.read()
                            print(f"[DEBUG] Read {len(text)} characters from text file")
                            file_content += text
                    except Exception as e:
                        print(f"[DEBUG] Error reading TXT {file['name']}: {str(e)}")
                        continue
                        
                file_content += f"\n{'='*50}\n"
                print(f"[DEBUG] Added {len(file_content)} characters of content")
                combined_text.append(file_content)
                
            except Exception as e:
                print(f"[DEBUG] Error processing file: {str(e)}")
                continue
            
        if combined_text:
            result["status"] = "ok"
            result["data"] = "\n".join(combined_text)
            result["character_count"] = len(result["data"])
            print(f"[DEBUG] Successfully combined {len(combined_text)} files with total {result['character_count']} characters")
        else:
            print("[DEBUG] No content could be extracted from files")
            result["status"] = "error"
            result["data"] = "No content could be extracted from files"
            
    except Exception as e:
        print(f"[DEBUG] Error in prepare_context_from_files: {str(e)}")
        result["status"] = "error"
        result["data"] = f"Error processing files: {str(e)}"

    return result

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def upload_file(file, category='history'):
    """Handle file upload for chat functionality and return file context"""
    try:
        if not file:
            print("[DEBUG] No file object provided")
            return {'status': 'error', 'message': 'No file provided'}
            
        if not hasattr(file, 'filename'):
            print("[DEBUG] File object has no filename attribute")
            return {'status': 'error', 'message': 'Invalid file object'}
            
        if not file.filename:
            print("[DEBUG] Empty filename")
            return {'status': 'error', 'message': 'No file selected'}
            
        print(f"[DEBUG] Processing file: {file.filename}")
        filename = secure_filename(file.filename)
        
        # More robust file type extraction
        try:
            file_type = filename.rsplit('.', 1)[1].lower() if '.' in filename else None
            if not file_type:
                print("[DEBUG] Could not extract file type")
                return {'status': 'error', 'message': 'Could not determine file type'}
        except Exception as e:
            print(f"[DEBUG] Error extracting file type: {str(e)}")
            return {'status': 'error', 'message': 'Invalid file type'}
            
        if not allowed_file(filename):
            print(f"[DEBUG] File type {file_type} not allowed")
            return {'status': 'error', 'message': f'File type {file_type} not allowed'}
        
        if file_type not in ['pdf', 'txt', 'jpeg', 'jpg', 'png']:
            print(f"[DEBUG] Unsupported file type: {file_type}")
            return {'status': 'error', 'message': 'Only PDF, TXT, and image files are supported'}
            
        # Get base path and construct relative/absolute paths consistently
        base_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        relative_path = os.path.join('core', 'documents', category)
        absolute_path = os.path.join(base_path, relative_path)
        
        print(f"[DEBUG] Upload base path: {base_path}")
        print(f"[DEBUG] Upload relative path: {relative_path}")
        print(f"[DEBUG] Upload absolute path: {absolute_path}")
        
        if not os.path.exists(absolute_path):
            print(f"[DEBUG] Creating directory: {absolute_path}")
            os.makedirs(absolute_path)
            
        fileDB = File(
            name=filename,
            path=relative_path,
            category=category,
            file_type=file_type,
            user_id=str(current_user.id)
        )
        fileDB.save()
        fileID = str(fileDB.id)
        
        file_save_path = os.path.join(absolute_path, f"{fileID}.{file_type}")
        print(f"[DEBUG] Saving file to: {file_save_path}")
        file.save(file_save_path)
        
        response = {
            'status': 'ok',
            'file_id': fileID,
            'filename': filename,
            'name': filename,
            'file_type': file_type,
            'type': file_type,
            'path': relative_path
        }
        
        # Always get context for text-based files
        if file_type in ['pdf', 'txt']:
            try:
                # Convert fileDB to dict format expected by prepare_context_from_files
                file_dict = {
                    '_id': fileID,
                    'name': filename,
                    'path': relative_path,
                    'file_type': file_type
                }
                
                print(f"[DEBUG] Getting context for file: {file_dict}")
                context = prepare_context_from_files([file_dict])
                
                if context['status'] == 'ok':
                    print(f"[DEBUG] Successfully extracted context with {context['character_count']} characters")
                    response['content'] = context['data']
                    response['character_count'] = context['character_count']
                else:
                    print(f"[DEBUG] Context extraction failed: {context['data']}")
                    response['content'] = f"[Error extracting content from {filename}]"
            except Exception as e:
                print(f"[DEBUG] Error getting file context: {str(e)}")
                response['content'] = f"[Error processing {filename}: {str(e)}]"
                
        # Add base64 for images
        elif file_type in ['jpeg', 'jpg', 'png']:
            try:
                response['base64_image'] = encode_image(file_save_path)
            except Exception as e:
                print(f"[DEBUG] Error encoding image: {str(e)}")
                response['base64_image'] = None
                
        print(f"[DEBUG] Upload successful, returning response: {response}")
        return response
        
    except Exception as e:
        print(f"[DEBUG] Upload error: {str(e)}")
        return {'status': 'error', 'message': str(e)}

