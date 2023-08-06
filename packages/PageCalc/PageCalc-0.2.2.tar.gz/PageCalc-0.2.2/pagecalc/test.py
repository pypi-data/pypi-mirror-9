'''
@author: saaj
'''


import unittest

import pagecalc


class TestPaginator(unittest.TestCase):
  
  def setUp(self):
    self.testee = pagecalc.Paginator(total = 987, by = 20) 
  
  def testPages(self):
    self.assertEqual(50, self.testee.pages)
    
    self.testee.by = 3 
    self.assertEqual(329, self.testee.pages)
    
    self.testee.total = 988
    self.assertEqual(330, self.testee.pages)
    
    self.testee.by = 1 
    self.assertEqual(988, self.testee.pages)
    
    self.testee.total = 1
    self.assertEqual(1, self.testee.pages)
    
    self.testee.total = 0
    self.assertEqual(0, self.testee.pages)
    
    self.testee.by = 0
    self.assertRaises(AssertionError, lambda: self.testee.pages)
    
    self.testee.by    = 1
    self.testee.total = -1
    self.assertRaises(AssertionError, lambda: self.testee.pages)
    
  def testSliding(self):
    self.testee.style  = pagecalc.sliding
    self.testee.length = 8
    
    expected = {
      'item' : {
        'pageCount'  : 20, 
        'perPage'    : 20,
        'totalCount' : 987
      },
      'page' : {
        'count'    : 50,
        'current'  : 44,
        'first'    : 1,
        'last'     : 50,
        'next'     : 45,
        'previous' : 43,
        'range'    : [41, 42, 43, 44, 45, 46, 47, 48]
      }
    } 
    self.assertEqual(expected, _listPageRange(self.testee.paginate(44)))
    
    expected['page'] = {
      'count'    : 50,
      'current'  : 1,
      'first'    : 1,
      'last'     : 50,
      'next'     : 2,
      'previous' : None,
      'range'    : [1, 2, 3, 4, 5, 6, 7, 8]              
    }
    self.assertEqual(expected, _listPageRange(self.testee.paginate(1)))
    
    expected['page'] = {
      'count'    : 50,
      'current'  : 3,
      'first'    : 1,
      'last'     : 50,
      'next'     : 4,
      'previous' : 2,
      'range'    : [1, 2, 3, 4, 5, 6, 7, 8]              
    }
    self.assertEqual(expected, _listPageRange(self.testee.paginate(3)))
    
    expected['page'] = {
      'count'    : 50,
      'current'  : 5,
      'first'    : 1,
      'last'     : 50,
      'next'     : 6,
      'previous' : 4,
      'range'    : [2, 3, 4, 5, 6, 7, 8, 9]              
    }
    self.assertEqual(expected, _listPageRange(self.testee.paginate(5)))
    
    expected['item']['pageCount'] = 7
    expected['page'] = {
      'count'    : 50,
      'current'  : 50,
      'first'    : 1,
      'last'     : 50,
      'next'     : None,
      'previous' : 49,
      'range'    : [43, 44, 45, 46, 47, 48, 49, 50]              
    }
    self.assertEqual(expected, _listPageRange(self.testee.paginate(50)))    
    
    self.assertEqual(expected, _listPageRange(self.testee.paginate(65)))    
    
  def testJumping(self):
    self.testee.style  = pagecalc.jumping
    self.testee.length = 8
    
    expected = {
      'item' : {
        'pageCount'  : 20, 
        'perPage'    : 20,
        'totalCount' : 987
      },
      'page' : {
        'count'    : 50,
        'current'  : 44,
        'first'    : 1,
        'last'     : 50,
        'next'     : 45,
        'previous' : 43,
        'range'    : [41, 42, 43, 44, 45, 46, 47, 48]
      }
    } 
    self.assertEqual(expected, _listPageRange(self.testee.paginate(44)))
    
    for p in range(1, 9):
      expected['page'] = {
        'count'    : 50,
        'current'  : p,
        'first'    : 1,
        'last'     : 50,
        'next'     : p + 1,
        'previous' : p - 1 if p > 1 else None,
        'range'    : [1, 2, 3, 4, 5, 6, 7, 8]              
      }
      self.assertEqual(expected, _listPageRange(self.testee.paginate(p)))
      
    expected['page'] = {
      'count'    : 50,
      'current'  : 9,
      'first'    : 1,
      'last'     : 50,
      'next'     : 10,
      'previous' : 8,
      'range'    : [9, 10, 11, 12, 13, 14, 15, 16]              
    }
    self.assertEqual(expected, _listPageRange(self.testee.paginate(9)))
    
    expected['item']['pageCount'] = 7
    expected['page'] = {
      'count'    : 50,
      'current'  : 50,
      'first'    : 1,
      'last'     : 50,
      'next'     : None,
      'previous' : 49,
      'range'    : [49, 50]              
    }
    self.assertEqual(expected, _listPageRange(self.testee.paginate(50)))
    
    self.assertEqual(expected, _listPageRange(self.testee.paginate(65)))
    
    
def _listPageRange(result):
  '''As py3 returns range class from ``range()`` it needs to be converted'''
  
  result['page']['range'] = list(result['page']['range'])
  return result
  
  