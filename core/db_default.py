#!/usr/bin/env python
# -*- coding: utf-8 -*-
from db_connect import *
from core.db_document import getDefaults

import csv,json

from datetime import date

class Setting(DynamicDocument):
    name = StringField(required=True,min_length=4)
    description = StringField()
    type = StringField(required = True)

def initDefault():
    Setting.drop_collection()
    settings = []
    settings.append(Setting(name = 'salutation', lable_name='Anrede', type = 'SimpleListField', values = ['','Herr', 'Frau']))
   
    #settings.append(Setting(name = 'ai_provider', lable_name='A.I. Provider', type = 'AdvancedListField',values = [{'' : ''},{'OpenAI' : 'open_ai'},{'Anthropic' :'anthropic'},{'Meta' :'meta'}]))
  
    languages = ['Deutsch', 'Englisch', 'Französich', 'Spanisch']
    settings.append(Setting(name = 'language', lable_name = 'Sprachen', type = 'SimpleListField', values = languages))
   
    # Add roles
    roles = ['admin', 'user']
    settings.append(Setting(name = 'role', lable_name = 'Rollen', type = 'SimpleListField', values = roles))

    # my_number = Setting(name = 'My Number', lable_name = 'Rechnungs-Nr', type ='Counter', value=1000, year = year)
    # settings.append(my_number)

    for setting in settings:
        setting.save()
    #MultiLine, SingleLine, SingleSelection, MultiSelection, Date, Number, Counter, Label

def prepListField(db_values,type):
    array=[]
    for x in db_values:
        if type =='AdvancedListField':
            for key in x:
                array.append({'name' : key,'value' : x[key]})
        elif type == 'SimpleListField':
            array.append({'name' : x,'value' : x})
    return array

def getDefaultList(name, collection, type):
    if type == 'SimpleDocumentField':
        array=[]
        documents = collection.objects()
        #array.append({'name':document.name, 'value':0})
        for document in documents:
            array.append({'name':document.name, 'value':json.loads(document.to_json())['_id']['$oid']})
        return array
    document = collection.objects(name = name).first()
    if document != None:
        return prepListField(document.values,type)

def getCounter(name):
    document = Setting.objects(name = name).first()
    if document != None:
        if document.value != None:
            document.value = int(document.value) + 1
            document.save()
            return str(document.value)
    return 0

#initDefault()
