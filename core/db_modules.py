# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
# from core.db_document import *

# from flask import url_for

# class Default():
#     document_name = ''
#     document_url = ''
#     collection_name = ''
#     collection_url = ''
#     page_name_document = ''
#     page_name_collection = ''
#     collection_title = ''
#     collection = None
#     document = None
#     menu = {}

# def getDefaults(name):
#     defaults = None
    
#     if name == 'filter':
#         defaults = ['filter', 'filter', 'Filter','Filter', Filter, Filter(), 'settings']
#     elif name == 'user' or name == 'users':
#         defaults = ['user', 'users', 'User','Users', User, User(), 'users']
#     elif name == 'file' or name == 'files':
#         defaults = ['file', 'files', 'File','Files', File, File(), 'files']
#     elif name == 'testing':
#         defaults = ['testing', 'testing', 'Testing','Testing', Testing, Testing(), 'testing']

#     if defaults:
#         d = Default()
#         d.document_name = defaults[0]
#         d.document_url = url_for('doc',name = defaults[0])
#         d.collection_name = defaults[1]
#         d.collection_url = url_for('list',name = defaults[1])
#         d.page_name_document = defaults[2]
#         d.page_name_collection = defaults[3]
#         d.collection_title = defaults[3]
#         d.collection = defaults[4]
#         d.document = defaults[5]
#         d.menu = {defaults[6] : 'open active',defaults[1] : 'open active'}
#         return d
#     else:
#         return None
