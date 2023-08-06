#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: saaj
'''


import os.path

import pagecalc
import cherrypy
import jinja2


config = {
  'global' : {
    'server.socket_host' : '127.0.0.1',
    'server.socket_port' : 8008,
    'server.thread_pool' : 8
  },
  '/jumping' : {
    'pagination' : {
      'items' : 10, # items per page
      'pages' : 5,  # pages to display
    }
  },
  '/sliding' : {
    'pagination' : {
      'items' : 8, # items per page
      'pages' : 4,  # pages to display
    }
  }
}

path = os.path.abspath(os.path.dirname(__file__))
view = jinja2.Environment(loader = jinja2.FileSystemLoader(path))
view.globals['url'] = cherrypy.url
template = view.get_template('index.html')


class Model:
  
  _data = [i**2 for i in range(100)]
  
  
  def count(self):
    return len(self._data)
  
  def list(self, page, limit):
    return self._data[(page - 1) * limit:page * limit]
  

class Controller:
  
  @cherrypy.expose
  def index(self):
    return template.render()
  
  def example(self, page, style):
    model = Model()
    
    pagination = cherrypy.request.config['pagination']
    paginator  = pagecalc.Paginator(model.count(), pagination['items'], pagination['pages'], style)
    
    return template.render(
      data      = model.list(page, pagination['items']),
      paginator = paginator.paginate(page)
    )
  
  @cherrypy.expose
  def jumping(self, page = 1):
    return self.example(int(page), pagecalc.jumping)
  
  @cherrypy.expose
  def sliding(self, page = 1):
    return self.example(int(page), pagecalc.sliding)


if __name__ == '__main__':
  cherrypy.quickstart(Controller(), '/', config)

