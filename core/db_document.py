#!/usr/bin/env python
# -*- coding: utf-8 -*-
from core.db_connect import *
from bson import json_util
from flask_login import UserMixin, current_user
from flask import url_for
from datetime import datetime
from mongoengine import *

class AuditMixin:
    created_date = DateTimeField(default=lambda: datetime.now())
    created_by = StringField()
    modified_date = DateTimeField()
    modified_by = StringField()

    def save(self, *args, **kwargs):
        try:
            user = current_user.get_id() if current_user and current_user.is_authenticated else 'system'
        except:
            user = 'system'
            
        if not self.id:
            # Document is being created
            self.created_date = datetime.now()
            self.created_by = user
        
        # Always update modified info on save
        self.modified_date = datetime.now()
        self.modified_by = user
        
        return super().save(*args, **kwargs)

#Date Fields must be named name_date, e.g. contact_date
#This is to make sure that string dates like 01.01.2016 are saved as date objects
#functions to convert strings to date objects are in crud.py (create / update)

#every document needs a required name field !!!

#converts mongo to Json and formats _date properly
def mongoToJson(document):
    data = document.to_mongo()
    
    # Format all date fields (including audit fields)
    for key, value in data.items():
        if key in ['created_date', 'modified_date'] or key.find('_date') != -1:
            try:
                data[key] = document[key].strftime('%d.%m.%Y %H:%M')
            except:
                pass
        elif key.find('filter') != -1:
            try:
                i = 0
                for filter in document[key]:
                    if '_date' in filter['field']:
                        data[key][i]['value'] = document[key][i]['value'].strftime('%d.%m.%Y')
                    i += 1
            except:
                pass

    return json_util.dumps(data)

class CustomQuerySet(QuerySet):
    def to_json(self):
        return "[%s]" % (",".join([doc.to_json() for doc in self]))

class Default(DynamicDocument):
    document_name = StringField(default='')
    document_url = StringField(default='')
    collection_name = StringField(default='')
    collection_url = StringField(default='')
    page_name_document = StringField(default='')
    page_name_collection = StringField(default='')
    collection_title = StringField(default='')
    menu = DictField(default={})
    
    def to_json(self):
        return mongoToJson(self)
    
def getDefaults(name):
    print(f"[DEBUG] getDefaults called with name={name}")
    defaults = None
    
    def create_document(doc_class):
        try:
            return doc_class()
        except Exception as e:
            print(f"[DEBUG] Error creating document instance: {str(e)}")
            return None
    
    if name == 'filter':
        defaults = ['filter', 'filter', 'Filter','Filter', Filter, create_document(Filter), 'filters']
    elif name == 'user' or name == 'users':
        defaults = ['user', 'users', 'User','Users', User, create_document(User), 'users']
    elif name == 'file' or name == 'files':
        defaults = ['file', 'files', 'File','Files', File, create_document(File), 'files']
    elif name == 'example' or name == 'examples':
        defaults = ['example', 'examples', 'Example','Example', Example, create_document(Example), 'examples']
    elif name == 'model' or name == 'models':
        defaults = ['model', 'models', 'Model','Models', Model, create_document(Model), 'models']
    elif name == 'history':
        defaults = ['history', 'history', 'History','Histories', History, create_document(History), 'history']
    elif name == 'prompt' or name == 'prompts':
        print("[DEBUG] Found prompt match")
        defaults = ['prompt', 'prompts', 'Prompt','Prompts', Prompt, create_document(Prompt), 'prompts']

    print(f"[DEBUG] defaults={defaults}")
    if defaults:
        try:
            d = Default()
            d.document_name = defaults[0]
            d.document_url = url_for('doc', name=defaults[0])
            d.collection_name = defaults[1]
            d.collection_url = url_for('list', collection=defaults[1])
            d.page_name_document = defaults[2]
            d.page_name_collection = defaults[3]
            d.collection_title = defaults[3]
            d.collection = defaults[4]
            d.document = defaults[5]
            if d.document is None:
                print("[DEBUG] Failed to create document instance")
                return None
            d.menu = {defaults[6]: 'open active', defaults[1]: 'open active'}
            print("[DEBUG] Created Default object successfully")
            return d
        except Exception as e:
            print(f"[DEBUG] Error creating Default object: {str(e)}")
            return None
    else:
        print("[DEBUG] No defaults found")
        return None

class User(UserMixin, Document):
    firstname = StringField(required=True)
    name = StringField(required=True)
    email = StringField(required=True, unique=True)
    pw_hash = StringField(required=True)
    csrf_token = StringField()
    salutation = StringField()
    comment = StringField()
    role = StringField(default='user')
    created_date = DateTimeField(default=datetime.now)
    modified_date = DateTimeField(default=datetime.now)
    created_by = StringField()
    modified_by = StringField()
    
    meta = {
        'collection': 'user',
        'queryset_class': CustomQuerySet
    }
    def searchFields(self):
        return ['email','firstname','name']
    def fields(self, list_order = False):
        email = {'name' :  'email', 'label' : 'Email', 'class' : '', 'type' : 'SingleLine', 'required' : True,'full_width':True}
        salutation = {'name' :  'salutation', 'label' : 'Anrede', 'class' : '', 'type' : 'SimpleListField','full_width':False}
        firstname = {'name' :  'firstname', 'label' : 'Vorname', 'class' : '', 'type' : 'SingleLine', 'full_width':False}
        name = {'name' :  'name', 'label' : 'Nachname', 'class' : '', 'type' : 'SingleLine','full_width':False}
        comment = {'name' :  'comment', 'label' : 'Kommentar', 'class' : '', 'type' : 'MultiLine','full_width':True}
        role = {'name' :  'role', 'label' : 'Rolle', 'class' : '', 'type' : 'SimpleListField','full_width':False}
        
        if list_order != None and list_order == True:
            #fields in the overview table of the collection
            return [firstname,name,email,role] if current_user.is_admin else [firstname,name,email]
            
        #fields in the form
        fields = [email,salutation,firstname,name,comment]
        if current_user.is_admin:
            fields.append(role)
        return fields
    def to_json(self):
        return mongoToJson(self)
    def get_id(self):
        """Return the unique identifier for Flask-Login"""
        return str(self.id)

    @property
    def is_admin(self):
        """Check if user has admin role"""
        return self.role == 'admin'
    
    def can_view_user(self, user_id):
        """Check if user has permission to view a specific user profile"""
        return self.is_admin or str(self.id) == str(user_id)

class File(AuditMixin, DynamicDocument):
    name = StringField(required=True, min_length=4)
    owner_id = StringField(required=True)  # Add owner_id field
    meta = {'queryset_class': CustomQuerySet}
    
    def searchFields(self):
        return ['name']
    
    def fields(self, list_order = False):
        name = {'name': 'name', 'label': 'Name', 'class': '', 'type': 'SingleLine', 'required': True, "full_width": False}
        category = {'name': 'category', 'label': 'Kategorie', 'class': 'hidden-xs', 'type': 'TextField', "full_width": False}
        if list_order:
            return [name, category]
        return [name, category]
    
    def can_access(self, user):
        """Check if a user can access this file"""
        return user.is_admin or str(user.id) == str(self.owner_id)
    
    def save(self, *args, **kwargs):
        if not self.owner_id and current_user and current_user.is_authenticated:
            self.owner_id = str(current_user.id)
        return super().save(*args, **kwargs)

    def to_json(self):
        return mongoToJson(self)

class Filter(AuditMixin, DynamicDocument):
    name = StringField(required=True,min_length=4)
    meta = {'queryset_class': CustomQuerySet}
    def searchFields(self):
        return ['name']
    def fields(self, list_order = False):
        name = {'name' :  'name', 'label' : 'Name', 'class' : '', 'type' : 'SingleLine', 'required' : True}
        category = {'name' :  'category', 'label' : 'Kategorie', 'class' : '', 'type' : 'SingleLine'}

        if list_order != None and list_order == True:
            #fields in the overview table of the collection
            return [name, category]
        return [name, category]
    def to_json(self):
        return mongoToJson(self)

#example of a DynamicDocument with all available fields
#fields are then used in the form_elements.html to create the form
#the fields are then used in the db_crud.py to create the document
class Example(AuditMixin, DynamicDocument):
    name = StringField(required=True, min_length=1)
    email = StringField(required=True, min_length=1)
    salutation = StringField(default='')
    firstname = StringField(default='')
    comment = StringField(default='')
    active = StringField(default='Off')
    newsletter = StringField(default='Off')
    event_date = DateField(default=None, null=True)
    age_int = IntField(default=None, null=True)
    salary_float = FloatField(default=None, null=True)
    ai_provider = StringField(default='')
    user_search = StringField(default='')
    files = StringField(default='')
    more_files = StringField(default='')
    link = StringField(default='')
    
    meta = {'queryset_class': CustomQuerySet}
    
    #these are the search fields for the search field in the document list overview page
    def searchFields(self):
        return ['name', 'email', 'firstname']
        
    def fields(self, list_order = False):
        # Field Types Documentation needs these corrections:
        
        # SingleLine: Text input field with 'input' class
        # MultiLine: Textarea field with 'textarea' class
        # CheckBox: Switch toggle with 'switch switch-primary' class
        # SimpleListField: Select dropdown with 'select max-w-sm' class
        # AdvancedListField: Enhanced select dropdown with 'select max-w-sm' class
        # Date: Flatpickr date picker with 'input max-w-sm' class (format: DD.MM.YYYY)
        # IntField: Number input with 'input' class
        # FloatField: Number input with 'input' class
        # FileField: File upload with 'input max-w-sm' class
        # ButtonField: Button with 'btn btn-primary' class
        # DocumentField: Search field with 'searchField' class and dropdown functionality

        # Additional Field Properties:
        # id: Used for element identification (required for all fields)
        # value: Current field value
        # value_id: (DocumentField only) ID of selected document
        # SimpleListField: (SimpleListField only) Array of {value, name} objects
        # AdvancedListField: (AdvancedListField only) Array of {value, name} objects

        #full_width is used to create a full width field in the form
        #if full_width is set to True, the field will take up the full width of the form
        #if full_width is set to False, the field will take up half the width of the form
        #required is used to make the field required in the form

        #list of fields for the form
        #SingleLine is a single line text field (input type text)
        #MultiLine is a multi line text field (input type textarea)
        #CheckBox is a checkbox field (input type checkbox, we are using a switch in the frontend)
        #SimpleListField is a simple list field (input type select)
        #AdvancedListField is a advanced list field (input type select with search)
        #DateField is a date field (input type date, this uses Flatpickr and flatpickr.js needs to be included in the frontend)
        #IntField is a integer field (input type number)
        #FloatField is a float field (input type number)
        #FileField is a file field (input type file)

        name = {'name': 'name', 'label': 'Name', 'class': '', 'type': 'SingleLine', 'required': True, 'full_width': True}
        email = {'name': 'email', 'label': 'Email', 'class': '', 'type': 'SingleLine', 'required': True, 'full_width': True}
        salutation = {'name': 'salutation', 'label': 'Anrede', 'class': '', 'type': 'SimpleListField', 'full_width': False}
        firstname = {'name': 'firstname', 'label': 'Vorname', 'class': '', 'type': 'SingleLine', 'full_width': False}
        comment = {'name': 'comment', 'label': 'Kommentar', 'class': '', 'type': 'MultiLine', 'full_width': True}
        active = {'name': 'active', 'label': 'Aktiv', 'class': '', 'type': 'CheckBox', 'full_width': False}
        newsletter = {'name': 'newsletter', 'label': 'Newsletter', 'class': '', 'type': 'CheckBox', 'full_width': False}
        event_date = {'name': 'event_date', 'label': 'Event-Datum', 'class': 'hidden-xs', 'type': 'Date', 'full_width': False}
        age_int = {'name': 'age_int', 'label': 'Alter', 'class': 'hidden-xs', 'type': 'IntField', 'full_width': False}
        salary_float = {'name': 'salary_float', 'label': 'Gehalt', 'class': 'hidden-xs', 'type': 'FloatField', 'full_width': False}
        ai_provider = {'name': 'ai_provider', 'label': 'Firma', 'class': 'hidden-xs', 'type': 'AdvancedListField', 'full_width': False}
        user_search = {'name': 'user_search', 'label': 'User', 'class': '', 'type': 'DocumentField', 'full_width': False, 'module': 'user', 'document_field': 'email'}
        files = {'name': 'files', 'label': 'Files', 'class': 'hidden-xs', 'type': 'FileField', 'full_width': True}
        more_files = {'name': 'more_files', 'label': 'More Files', 'class': 'hidden-xs', 'type': 'FileField', 'full_width': True}
        link = {'name': 'link', 'label': 'Link', 'class': '', 'type': 'ButtonField', 'full_width': False, 'link': '/d/testing'}

        #fields in the overview table of the collection
        if list_order:
            return [name, email, firstname]
        #fields in the form
        return [name, email, salutation, firstname, comment, active, newsletter, event_date, 
                age_int, salary_float, ai_provider, user_search, files, more_files, link]

    def to_json(self):
        return mongoToJson(self)

#AI Documents
#AI Chat Bot Code
class Model(AuditMixin, DynamicDocument):
    provider = StringField(required=True, min_length=1)
    model = StringField(required=True, min_length=1)
    name = StringField(required=True, min_length=1)

    meta = {'queryset_class': CustomQuerySet}

    def searchFields(self):
        return ['provider', 'model', 'name']

    def fields(self, list_order=False):
        provider = {'name': 'provider', 'label': 'Provider', 'class': '', 'type': 'SingleLine', 'required': True, 'full_width': True}
        model = {'name': 'model', 'label': 'Model', 'class': '', 'type': 'SingleLine', 'required': True, 'full_width': True}
        name = {'name': 'name', 'label': 'Name', 'class': '', 'type': 'SingleLine', 'required': True, 'full_width': True}

        if list_order:
            return [name, provider, model]
        return [name, provider, model]

    def to_json(self):
        return mongoToJson(self)

class History(AuditMixin, DynamicDocument):
    user_id = StringField(required=True)  # Store user ID instead of username
    chat_started = IntField()
    messages = StringField()
    first_message = StringField()
    link = StringField(default='')
    file_ids = ListField(StringField())
    
    def searchFields(self):
        return ['messages','first_message']
    
    def fields(self, list_order=False):
        user_id = {'name': 'user_id', 'label': 'User ID', 'class': '', 'type': 'SingleLine', 'required': True, 'full_width': False}
        chat_started = {'name': 'chat_started', 'label': ' Started', 'class': '', 'type': 'IntField', 'required': True, 'full_width': False}
        first_message = {'name': 'first_message', 'label': 'First Message', 'class': '', 'type': 'SingleLine', 'required': False, 'full_width': True}
        messages = {'name': 'messages', 'label': 'Messages', 'class': '', 'type': 'MultiLine', 'required': False, 'full_width': True}
        link = {'name': 'link', 'label': 'Chat', 'class': '', 'type': 'ButtonField', 'full_width': False, 'link': '/chat/history'}
        if list_order:
            return [link, first_message]
        return [user_id, first_message, chat_started, messages, link]
    
    def can_view(self, user):
        """Check if a user can view this history"""
        return user.is_admin or str(user.id) == str(self.user_id)

class Prompt(AuditMixin, DynamicDocument):
    name = StringField(required=True, min_length=1)
    welcome_message = StringField(required=True, min_length=1)
    system_message = StringField(required=True, min_length=1)
    prompt = StringField(required=True, min_length=1)
    link = StringField(default='')
    files = StringField(default='')

    meta = {
        'collection': 'prompts',
        'queryset_class': CustomQuerySet
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.link:
            self.link = '/chat/prompt'

    def searchFields(self):
        return ['name', 'system_message', 'prompt']

    def fields(self, list_order=False):
        name = {'name': 'name', 'label': 'Name', 'class': '', 'type': 'SingleLine', 'required': True, 'full_width': True}
        welcome_message = {'name': 'welcome_message', 'label': 'Welcome Message', 'class': '', 'type': 'MultiLine', 'required': True, 'full_width': True}
        system_message = {'name': 'system_message', 'label': 'System Message', 'class': '', 'type': 'MultiLine', 'required': True, 'full_width': True}
        prompt = {'name': 'prompt', 'label': 'Prompt', 'class': '', 'type': 'MultiLine', 'required': True, 'full_width': True}
        link = {'name': 'link', 'label': 'Use Prompt', 'class': '', 'type': 'ButtonField', 'full_width': False, 'link': '/chat/prompt'}
        files = {'name': 'files', 'label': 'Files', 'class': 'hidden-xs', 'type': 'FileField', 'full_width': True}

        if list_order:
            return [link, name, prompt]
        return [name, welcome_message, system_message, prompt, files, link]

    def to_json(self):
        return mongoToJson(self)
