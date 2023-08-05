"""template automatic tests

:organization: SecondWeb
:copyright: 2001-2010 SECONDWEB S.A.S. (Paris, FRANCE), license is LGPL v2.
:contact: http://www.secondweb.fr/ -- mailto:contact@secondweb.fr
:license: GNU Lesser General Public License, v2.1 - http://www.gnu.org/licenses
"""

from logilab.common.testlib import unittest_main
from cubicweb.devtools.testlib import AutomaticWebTest

class AutomaticWebTest(AutomaticWebTest): pass

if __name__ == '__main__':
    unittest_main()
