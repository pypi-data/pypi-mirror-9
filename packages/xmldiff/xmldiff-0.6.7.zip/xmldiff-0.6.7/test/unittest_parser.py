# Copyright (c) 2000 LOGILAB S.A. (Paris, FRANCE).
# http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
""" unit tests for xmldiff.
"""
      
import unittest
import cStringIO 
from copy import deepcopy    
#import xmldiff.ezs
from xmldiff.objects import *
from xmldiff.ezs import trees_equal
import sys

class Tree2TreeKnownValues(unittest.TestCase):
    """
    This class check that source_vector functions give known result
    with known input
    """
    
    DATA = cStringIO.StringIO("""
  <memory>
  <mailbox path="/var/spool/mail/syt"/>
  <email_addr mine="yes">syt@logilab.org</email_addr>
  <server-socket1 port="7776" recipe="pia.PDA"/>
   <bookmark-file type="netscape">/home/syt/.netscape/bookmarks.html</bookmark-file>
   <!-- proxy -->
  <server-socket2 port="7777" recipe="proxy.Web proxy"/>
  <junkbuster-method value="18" />
  <spoken-languages>
   <language1 name="english" code="en" />
   <language2 name="francais" code="fr" />
  </spoken-languages>
</memory>
""")   
    from xmldiff.parser import SaxHandler
    from xml.sax import make_parser
    dh = SaxHandler(1, 1)
    parser = make_parser()
    parser.setContentHandler(dh)
    parser.parse(DATA)
    xmltree1 = dh.get_tree() 

    DATA = cStringIO.StringIO("""
   <memory>
  <mailbox path="/var/spooool/mail/syt"/>
  <email_addr mine="yes">syt@logab.org</email_addr>
  <server-socket1 port="7776" recipe="pia.PDA"/>
  <bookmark-file>/home/syt/.netscape/bookmarks.html</bookmark-file>
  <!-- proxy -->
  <junkbuster-method value="18" />
  <server-socket2 port="7777" recipe="proxy.Web proxy"/>
  <spoken-languages>
   <language1 code="en" name="english"/>
   <language2 name="francais" code="fr" />
   <language3 name="martien" code="ma"/>
  </spoken-languages>
</memory>
""")
    dh.__init__(1, 1)
    parser.parse(DATA)
    xmltree2 = dh.get_tree() 

    # those variables may change if the "DATA" string change
    # this is the post order numbers
    HKNOWN_VALUES = {
        'N/a[0]': 14,
        'a/a[0]': 1,
        'N/a[0]/b[0]': 3,
        'b/a[0]/b[0]': 2,
        'N/a[0]/c[0]': 5,
        'c/a[0]/c[0]': 4,
        'N/a[0]/d[0]': 13,
        'd/a[0]/d[0]': 6,
        'N/a[0]/d[0]/e[0]': 10,
        'e/a[0]/d[0]/e[0]': 7,
        'N/a[0]/d[0]/e[0]/h[0]': 9,
        'h/a[0]/d[0]/e[0]/h[0]': 8,
        'N/a[0]/d[0]/f[0]': 12,
        'f/a[0]/d[0]/f[0]': 11
        }

    dh.__init__(1, 1)
    parser.parse(cStringIO.StringIO("""
    <a>
      <b/>
      <c>
      </c>
      <d>
        <e>
          <h/>
        </e>
        <f>
        </f>
      </d>
    </a>
    """))
    tree1 = dh.get_tree()
                 
    dh.__init__(1, 1)
    parser.parse(cStringIO.StringIO("""
    <a>
      <c/>
      <b>
      </b>
      <d>
        <e>
          <h/>
        </e>
        <f><j/>
        </f>
      </d>
    </a>
    """))
    tree2 = dh.get_tree()


    def setUp (self):
        """ called before each test from this class """
        self.nl1, self.nl2 = [], []

        
##     def test_po_known_values(self):
##         """
##         post_order should give known result with known input
##         """
##         ezsc = ezs.EzsCorrector() 
##         ezsc._post_order(self.tree1, self.nl1, TRUE)
##         num = 1
##         for node in self.nl1[:-1]:
##             self.assert_(num == self.HKNOWN_VALUES[node[N_VALUE] + f_xpath(node)],
##                          'Post order Error for '+f_xpath(node))
##             num = num + 1

##     def test_st_known_values(self):
##         """
##         swap_trees should give known result with known input
##         """
##         ezsc = ezs.EzsCorrector()
##         ezsc._post_order(self.tree1, self.nl1, TRUE)
##         n1 = self.tree1[N_CHILDS][0][N_CHILDS][1]
##         s1 = self.tree1[N_CHILDS][0][N_CHILDS][2]
##         self.assert_(ezs.swap_trees(n1, s1, n1, s1) == ezs.C_INFINI, 'SWAP')
##         self.assert_(ezs.swap_trees(n1, s1, s1, n1) == ezs.C_SWAP, 'SWAP')

##     def test_ezs_known_values(self):
##         """
##         ezs should give known result with known input
##         """
##         ezsc = ezs.EzsCorrector()
##         actions = ezsc.process_trees(self.tree1, self.tree2)
##         action_list1= ['append', 'swap']
##         for i in range(len(actions)):
##             self.assert_(actions[i][A_DESC] == action_list1[i])

##         actions = ezsc.process_trees(self.xmltree1, self.xmltree2)
##         #import format
##         #format.factions_print(actions)
##         action_list1= ['insert-after', 'remove', 'update', 'update', 'swap']
##         for i in range(len(actions)):
##             self.assert_(actions[i][0] == action_list1[i])

        
    def test_sanity(self):
        """
        global sanity check for do() function
        """
        self.assert_(trees_equal(self.tree1, self.tree1),
                     'Tree unequal error')
        self.assert_(not trees_equal(self.tree1, self.tree2),
                     'Tree equal error')
        #        print  "SOURCE TREE"
        #        xml_print(self.tree1)
        #        print  "DESTINATION TREE"
        #        xml_print(self.tree2)


def suite():
    """return the unitest suite"""
    loader = unittest.TestLoader()
    module = sys.modules[__name__]
    if __name__ == '__main__' and len(sys.argv) > 1:
        return loader.loadTestsFromNames(sys.argv[1:], module)
    return loader.loadTestsFromModule(module)

def Run(runner=None):
    """run tests"""
    testsuite = suite()
    if runner is None:
        runner = unittest.TextTestRunner()
        # uncomment next line to write tests results in a file
        #runner.__init__(open('tests.log','w+'))    
    return runner.run(testsuite)
    
if __name__ == '__main__':
    Run()
