'''
Created on Dec 28, 2014

@author: Rob
'''

class BaseMapRenderer(object):
    def __init__(self, map, **options):
        '''
        :type map: Map
        '''
        
        self.options=options
        self.map=map 
    
    def RenderMap(self,filename_tpl, basedir='.', renderflags=0, z=None, **kwargs):
        return