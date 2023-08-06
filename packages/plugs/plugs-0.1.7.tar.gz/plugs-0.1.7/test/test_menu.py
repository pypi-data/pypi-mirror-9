from plugs.menus import *

def test_merge_menu():
    """
    >>> from uliweb.utils.sorteddict import SortedDict
    >>> menus = {'subs':[
    ...         {'name':'request', 'title':'Test1', 'subs':[
    ...             {'name':'request_all', 'title':'Test2'},
    ...             {'name':'request_unfinished', 'title':'Test3'},
    ...         ]},
    ...     ]
    ... }
    >>> load_menu([('menus', menus)])
    <SortedDict {'menus':{'id': 'menus', 'subs': [{'id': 'menus/request', 'title': 'Test1', 'subs': [{'id': 'request/request_all', 'subs': [], 'name': 'request_all', 'title': 'Test2'}, {'id': 'request/request_unfinished', 'subs': [], 'name': 'request_unfinished', 'title': 'Test3'}], 'name': 'request'}], 'name': 'menus'}}>
    """
    
def test_i18n_menu():
    """
    >>> from uliweb.utils.sorteddict import SortedDict
    >>> from uliweb.i18n import ugettext_lazy as _
    >>> menus = {'subs':[
    ...         {'name':'request', 'title':_('Test1'), 'subs':[
    ...             {'name':'request_all', 'title':'Test2'},
    ...             {'name':'request_unfinished', 'title':'Test3'},
    ...         ]},
    ...     ]
    ... }
    >>> load_menu([('menus', menus)])
    <SortedDict {'menus':{'id': 'menus', 'subs': [{'id': 'menus/request', 'title': ugettext_lazy('Test1'), 'subs': [{'id': 'request/request_all', 'subs': [], 'name': 'request_all', 'title': 'Test2'}, {'id': 'request/request_unfinished', 'subs': [], 'name': 'request_unfinished', 'title': 'Test3'}], 'name': 'request'}], 'name': 'menus'}}>
    """
