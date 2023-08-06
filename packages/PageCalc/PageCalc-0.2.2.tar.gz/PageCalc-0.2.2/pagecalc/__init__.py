# -*- coding: utf-8 -*-
'''
@author: saaj
'''


from math import ceil


def sliding(paginator, page):
  '''Sliding window pagination style. Example:
        [1] 2  3  4  » →
    ← «  1 [2] 3  4  » →
    ← «  2 [3] 4  5  » →
    ← «  3 [4] 5  6  » →
    ← «  4 [5] 6  7  » →
    ← «  4  5 [6] 7  » →
    ← «  4  5  6 [7]
  '''
  
  length = min(paginator.length, paginator.pages)
  center = int(ceil(length / 2.0))
  
  # enough space to put window with centered active page 
  if page - center > paginator.pages - length:
    start = paginator.pages - length + 1
  else:
    start = max(page - center, 0) + 1

  return range(start, min(start + length, paginator.pages + 1))

def jumping(paginator, page):
  '''Jumping window pagination style. Example:
        [1] 2  3  4  » →
    ← «  1 [2] 3  4  » →
    ← «  1  2 [3] 4  » →
    ← «  1  2  3 [4] » →
    ← « [5] 6  7     » →
    ← «  5 [6] 7     » →
    ← «  5  6 [7]    
  '''
  
  steps = page % paginator.length or paginator.length
  start = page - steps + 1
  return range(start, min(start + paginator.length, paginator.pages + 1))


class Paginator(object):
  
  length = None
  '''Displayed pages number -- window length, default is 10'''
  
  style = None
  '''Pagination style, module provides ``sliding`` and ``jumping``, default is ``sliding``'''
  
  total = None
  '''Total number of items'''
   
  by = None
  '''Items per page to paginate by'''
  
  
  def __init__(self, total, by, length = 10, style = sliding):
    self.total  = total
    self.by     = by
    self.length = length
    self.style  = style
      
  @property
  def pages(self):
    '''Computes total page number'''
    
    assert self.total >= 0
    assert self.by > 0
    
    return int(ceil(self.total / float(self.by)))
    
  def paginate(self, page = 1):
    assert self.length > 0
    
    assert page > 0
    page = min(page, self.pages)
    
    pageResult = {
      'previous': page - 1 if page > 1 else None,
      'first'   : 1,
      'count'   : self.pages,
      'current' : page,
      'range'   : self.style(self, page),
      'last'    : self.pages if self.pages else 1,
      'next'    : page + 1 if page < self.pages else None,
    } 
    itemResult = {
      'totalCount' : self.total,
      'pageCount'  : self.by if page * self.by < self.total else self.total % self.by,
      'perPage'    : self.by
    }
    
    return dict(page = pageResult, item = itemResult)

