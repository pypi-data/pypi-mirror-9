# -*- coding: utf-

"""               
wsgi.py
                  
:Created: 12 Jun 2014  
:Author: tim    
"""


from spyne.server.wsgi import WsgiApplication as _SpyneWsgiApplication

from spyne_smev.server import _AllYourInterfaceDocuments


class WsgiApplication(_SpyneWsgiApplication):

    def __init__(self, app, chunked=True, max_content_length=2 * 1024 * 1024,
                 block_length=8 * 1024):
        super(WsgiApplication, self).__init__(app, chunked, max_content_length,
                                              block_length)
        self.doc = _AllYourInterfaceDocuments(app.interface)
