#!/usr/bin/env python
# -*- coding: utf-8 -*-
from core.db_connect import *
from bson import json_util

#Date Fields must be named name_date, e.g. contact_date
#This is to make sure that string dates like 01.01.2016 are saved as date objects
#functions to convert strings to date objects are in crud.py (create / update)

#every document needs a required name field !!!

#converts mongo to Json and formats _date properly
def mongoToJson(document):
    data = document.to_mongo()
    #format all _date fields

    for key,value in data.items():
        if key.find('_date') !=-1:
            try:
                #print data[key]
                data[key] = document[key].strftime('%d.%m.%Y %H:%M')
                #print data[key]
            except:
                pass
        elif key.find('filter') !=-1:
            try:
                i=0
                for filter in document[key]:
                    if '_date' in filter['field']:
                        data[key][i]['value'] = document[key][i]['value'].strftime('%d.%m.%Y')
                    i=i+1
            except:
                pass

    return json_util.dumps(data)

class CustomQuerySet(QuerySet):
    def to_json(self):
        return "[%s]" % (",".join([doc.to_json() for doc in self]))

class User(DynamicDocument):
    email = StringField(required=True,min_length=1)
    salutation = StringField(default='')
    firstname = StringField(default='')
    name = StringField(default='')
    # comment = StringField(default='')
    # active = StringField(default='off')
    # newsletter = StringField(default='off')
    # event_date = DateField(default=None)
    # age_int = IntField(default=None) # required=True,min_length=4,unique=True
    # salary_float = FloatField(default=None)
    # ai_provider= StringField(default='')
    # user = StringField(default='')
    # files = StringField(default='')
    # more_files = StringField(default='')
    # link = StringField(default='')
    
    meta = {'queryset_class': CustomQuerySet}
    def searchFields(self):
        return ['email','firstname','name']
    def fields(self, list_order = False):
        email = {'name' :  'email', 'label' : 'Email', 'class' : '', 'type' : 'SingleLine', 'required' : True,'full_width':True}
        salutation = {'name' :  'salutation', 'label' : 'Anrede', 'class' : '', 'type' : 'SimpleListField','full_width':False}
        firstname = {'name' :  'firstname', 'label' : 'Vorname', 'class' : '', 'type' : 'SingleLine', 'full_width':False}
        name = {'name' :  'name', 'label' : 'Nachname', 'class' : '', 'type' : 'SingleLine','full_width':False}
        # comment = {'name' :  'comment', 'label' : 'Kommentar', 'class' : '', 'type' : 'MultiLine','full_width':True}
        # active = {'name' :  'active', 'label' : 'Aktiv', 'class' : '', 'type' : 'CheckBox', 'full_width':False}
        # newsletter = {'name' :  'newsletter', 'label' : 'Newsletter', 'class' : '', 'type' : 'CheckBox', 'full_width':False}
        # event_date = {'name' :  'event_date', 'label' : 'Event-Datum', 'class' : 'hidden-xs', 'type' : 'Date', 'full_width':False}
        # age_int = {'name' :  'age_int', 'label' : 'Alter', 'class' : 'hidden-xs', 'type' : 'IntField', 'full_width':False}
        # salary_float = {'name' :  'salary_float', 'label' : 'Gehalt', 'class' : 'hidden-xs', 'type' : 'FloatField', 'full_width':False}
        # ai_provider = {'name' :  'ai_provider', 'label' : 'Firma', 'class' : 'hidden-xs', 'type' : 'AdvancedListField', 'full_width':False}
        # user = {'name' :  'user', 'label' : 'User', 'class' : '', 'type' : 'DocumentField', 'full_width':False,'module' : 'user','document_field':'email'}
        # files = {'name' :  'files', 'label' : 'Files', 'class' : 'hidden-xs', 'type' : 'FileField','full_width':True}
        # more_files = {'name' :  'more_files', 'label' : 'More Files', 'class' : 'hidden-xs', 'type' : 'FileField','full_width':True}
        # link = {'name' :  'link', 'label' : 'Link', 'class' : '', 'type' : 'ButtonField','full_width':False,'link':'/d/user'}

        if list_order != None and list_order == True:
            #fields in the overview table of the collection
            return [firstname,name,email]
        return [email,salutation,firstname,name]
    def to_json(self):
        return mongoToJson(self)

class File(DynamicDocument):
    name = StringField(required=True,min_length=4)
    meta = {'queryset_class': CustomQuerySet}
    def searchFields(self):
        return ['name']
    def fields(self, list_order = False):
        name = {'name' :  'name', 'label' : 'Name', 'class' : '', 'type' : 'SingleLine', 'required' : True,"full_width" : False}
        category = {'name' :  'category', 'label' : 'Kategorie', 'class' : 'hidden-xs', 'type' : 'TextField',"full_width" : False}
        document_id = {'name' :  'document_id', 'label' : 'Dokument', 'class' : 'hidden-xs', 'type' : 'TextField',"full_width" : True}

        if list_order != None and list_order == True:
            #fields in the overview table of the collection
            return [name]
        return [name]
    def to_json(self):
        return mongoToJson(self)
class Filter(DynamicDocument):
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

#AI Chat Bot Code
class Model(DynamicDocument):
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

class History(DynamicDocument):
    username = StringField()
    chat_started = IntField()
    messages = StringField()
    first_message = StringField()
    link = StringField(default='')
    def searchFields(self):
        return ['messages','first_message']
    def fields(self, list_order=False):
        username = {'name': 'username', 'label': 'Username', 'class': '', 'type': 'SingleLine', 'required': True, 'full_width': False}
        chat_started = {'name': 'chat_started', 'label': ' Started', 'class': '', 'type': 'IntField', 'required': True, 'full_width': False}
        first_message = {'name': 'first_message', 'label': 'First Message', 'class': '', 'type': 'SingleLine', 'required': False, 'full_width': True}
        messages = {'name': 'messages', 'label': 'Messages', 'class': '', 'type': 'MultiLine', 'required': False, 'full_width': True}
        link = {'name' :  'link', 'label' : 'Chat', 'class' : '', 'type' : 'ButtonField','full_width':False,'link':'/chat/history'}
        if list_order:
            return [username, first_message,chat_started,link]
        return [username,first_message,chat_started, messages,link]
        
class Prompt(DynamicDocument):
    name = StringField(required=True, min_length=1)
    welcome_message = StringField(required=True, min_length=1)
    system_message = StringField(required=True, min_length=1)
    prompt = StringField(required=True, min_length=1)
    link = StringField(default='')
    files = StringField(default='')

    meta = {'queryset_class': CustomQuerySet}

    def searchFields(self):
        return ['name', 'system_message', 'prompt']

    def fields(self, list_order=False):
        name = {'name': 'name', 'label': 'Name', 'class': '', 'type': 'SingleLine', 'required': True, 'full_width': True}
        welcome_message = {'name': 'welcome_message', 'label': 'Welcome Message', 'class': '', 'type': 'MultiLine', 'required': True, 'full_width': True}
        system_message = {'name': 'system_message', 'label': 'System Message', 'class': '', 'type': 'MultiLine', 'required': True, 'full_width': True}
        prompt = {'name': 'prompt', 'label': 'Prompt', 'class': '', 'type': 'MultiLine', 'required': True, 'full_width': True}
        link = {'name' :  'link', 'label' : 'Use Prompt', 'class' : '', 'type' : 'ButtonField','full_width':False,'link':'/chat/prompt'}
        files = {'name' :  'files', 'label' : 'Files', 'class' : 'hidden-xs', 'type' : 'FileField','full_width':True}

        if list_order:
            return [name,welcome_message, system_message, prompt,link]
        return [name,welcome_message, system_message, prompt,files,link]

    def to_json(self):
        return mongoToJson(self)
