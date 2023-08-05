# -*- coding: utf-8 -*-
# This file automatically created while building Larch. Do not edit manually.
configuration='Debug'
time='03:58:39 PM CST'
date='28 Jan 2015'
day='Wednesday'
version='v3.1.9-1-g36b2dd0'

build='%s (%s, %s %s)'%(version,day,date,time)
from .apsw import apswversion, sqlitelibversion
from .utilities import dicta
versions = dicta({
'larch':version,
'apsw':apswversion(),
'sqlite':sqlitelibversion(),
})

try:
	import numpy
	versions['numpy'] = numpy.version.version
except:
	versions['numpy'] = 'failed'

try:
	import scipy
	versions['scipy'] = scipy.version.version
except:
	versions['scipy'] = 'failed'

try:
	import pandas
	versions['pandas'] = pandas.version.version
except:
	versions['pandas'] = 'failed'

import sys
versions['python'] = "{0}.{1}.{2} {3}".format(*(sys.version_info))
build_config='Larch %s built on %s, %s %s'%(configuration,day,date,time)
