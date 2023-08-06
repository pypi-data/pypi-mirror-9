
********
PageCalc
********

PageCalc is a *Python* `pagination <http://en.wikipedia.org/wiki/Pagination>`_ library. In contrary 
to many auto-magical solutions this package is just a calculator. I.e. it doesn't interfere with 
database queries, result-sets, collection or what not. Nor it is involved in templating. The 
purpose of the package is calculation of pages based on:
  
  * total item number,
  * items per page,
  * current page,
  * number of pages to display,
  * pagination style.
  
The package can be used to paginate models designed for a paged listing and to 
handle external pre-paginated data sources. Basically the idea is same as in 
`this Flask snippet <http://flask.pocoo.org/snippets/44/>`_. 

Return value of ``Paginator.paginate`` is a ``dict`` that has the following structure:

.. code-block:: python

  {
    'item' : {
      # actual number of items at current page 
      'pageCount' : 20,
      # items per page 
      'perPage' : 20,
      # total number of items
      'totalCount' : 987
    },
    'page' : {
      # total number of pages
      'count' : 50,
      # number of current page
      'current' : 44,
      # number of first page
      'first' : 1,
      # number of last page
      'last' : 50,
      # number of next page, None for last page
      'next' : 45,
      # number of previous page, None for first page
      'previous' : 43,
      # displaying window page range
      'range' : [41, 42, 43, 44]
    }
  } 

For more details look at the package's 
`test suite <https://bitbucket.org/saaj/pagecalc/src/tip/pagecalc/test.py>`_.


Pagination styles
=================
The package provides two pagination styles.

Sliding
-------
Active page stays in center of displayed pages, except for beginning and ending pages. Displayed
page window advances with active page, making it slide.  

.. code-block:: text

      [1]  2   3   4  » →
  ← «  1  [2]  3   4  » →
  ← «  2  [3]  4   5  » →
  ← «  3  [4]  5   6  » →
  ← «  4  [5]  6   7  » →
  ← «  4   5  [6]  7  » →
  ← «  4   5   6  [7]
  
Jumping
-------
Active page moves from lower to upper bound of displayed page window. When active page is a
last page of the window, next move makes the window jump to next page rage.

.. code-block:: text

      [1]  2   3   4  » →
  ← «  1  [2]  3   4  » →
  ← «  1   2  [3]  4  » →
  ← «  1   2   3  [4] » →
  ← « [5]  6   7      » →
  ← «  5  [6]  7      » →
  ← «  5   6  [7]    


Usage
=====

In controller code, on *CherryPy* example, it can look something like:

.. code-block:: python

  class Controller:
  
    @cherrypy.expose
    def news(self, page = 1):
      page      = int(page)
      model     = Model()
      paginator = pagecalc.Paginator(total = model.count(), by = 10)
      
      data  = model.list(page, limit = 10)
      pages = paginator.paginate(page)
    
      return template.render(data = data, paginator = pages)
      
      
Pagination *Jinja2* template can look like:

.. code-block:: text

   {% if paginator and paginator.page.count > 1 %}
     <div id='paginator'>
       Pages:
       {% if paginator.page.previous %}
         <a href='{{ url(qs = {"page" : paginator.page.previous}) }}'>←</a>
         <a href='{{ url(qs = {"page" : paginator.page.first}) }}'>«</a>
       {% endif %}
       {% for page in paginator.page.range %}
         <a href='{{ url(qs = {"page" : page}) }}'{% if paginator.page.current == page %} class='active'{% endif %}>
           {{ page }}
         </a>
       {% endfor %}
       {% if paginator.page.next %}
         <a href='{{ url(qs = {"page" : paginator.page.last}) }}'>»</a>
         <a href='{{ url(qs = {"page" : paginator.page.next}) }}'>→</a>
       {% endif %}
     </div>
   {% endif %}


Example app
-----------
The package contains an example app that demonstrates pagination and the styles. To run it, 
type in terminal:

.. code-block:: text
  
  virtualenv pagecalctest
  source pagecalctest/bin/activate
  pip install pagecalc
  pip install cherrypy
  pip install jinja2
  python pagecalctest/lib/python2.7/site-packages/pagecalc/example/app.py
  
Then navigate your browser to `<http://127.0.0.1:8008/>`_. Note, that last path may vary depending 
on platform and *Python* version.

