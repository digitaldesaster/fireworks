#!/usr/bin/env python
# -*- coding: utf-8 -*-
from core.db_connect import *
from bson import json_util, ObjectId
from flask_login import UserMixin

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

class User(DynamicDocument, UserMixin):
    firstname = StringField()
    name = StringField()
    email = StringField()
    pw_hash = StringField()
    role = StringField()
    csrf_token = StringField()
    modified_by = StringField()
    modified_date = DateTimeField()
    salutation = StringField()
    comment = StringField()
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
        if list_order != None and list_order == True:
            #fields in the overview table of the collection
            return [firstname,name,email]
        return [email,salutation,firstname,name,comment]
    def to_json(self):
        return mongoToJson(self)
    def get_id(self):
        return str(self.email)

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

#example of a DynamicDocument with all available fields
#fields are then used in the form_elements.html to create the form
#the fields are then used in the db_crud.py to create the document
class Testing(DynamicDocument):
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
