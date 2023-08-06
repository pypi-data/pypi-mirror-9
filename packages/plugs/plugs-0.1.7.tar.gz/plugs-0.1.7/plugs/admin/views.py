#coding=utf-8
from uliweb import expose, functions

@expose('/admin')
class AdminView(object):
    def __init__(self):
        pass
    
    @expose('')
    def index(self):
        return {}