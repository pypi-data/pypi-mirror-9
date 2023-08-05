
def info(self):
	s = ""
	from .core import IntStringDict
	d = lambda x: x if not isinstance(x,IntStringDict) else dict(x)
	p = lambda x: str(d(x)).replace("\n","\n           \t")
	s += "idco query:\t{}\n".format(p(self.get_idco_query()))
	s += "alts query:\t{}\n".format(p(self.get_alts_query()))
	s += "choice:    \t{}\n".format(p(self.choice))
	s += "weight:    \t{}\n".format(p(self.weight))
	s += "avail:     \t{}".format(p(self.avail))
	return s


_weight_doc = """\
This attribute names the column in the main table that defines the weight for each case.
Set it to an empty string, or 1.0, to assign all cases equal weight.
"""

weight = property(lambda self: self.get_weight_column(), lambda self,w: self.set_weight_column(str(w)), None, _weight_doc)


def set_choice(self, x):
	if isinstance(x,str):
		self.set_choice_column(x)
	else:
		self.set_choice_column_map(x)

def get_choice(self):
	x = self.get_choice_column()
	if x!="":
		return x
	return self.get_choice_column_map()


_doc_choice = """\
This attributes defines the choices. It has two styles:

	* When set to a string, the string names the column of the main table that identifies
	  the choice for each case.  The indicated column should contain integer values
	  corresponding to the alternative codes.

	* When set to a dict, the dict should contain {integer:string} key/value pairs, where
	  each key is an integer value corresponding to an alternative code, and each
	  value is a string identifying a column in the main table; that column should
	  contain a value indication whether the alternative was chosen. Usually this will be
	  a binary dummy variable, although it need not be. For certain specialized models,
	  values other than 0 or 1 may be appropriate.

The choice of style is a matter of convenience; the same data can be expressed with either
style as long as the choices are binary.

"""

choice = property(lambda self: self.get_choice(), lambda self,w: self.set_choice(w), None, _doc_choice)


def set_avail(self, x):
	if isinstance(x,int) and x==1:
		self.set_avail_all()
	elif isinstance(x,bool) and x is True:
		self.set_avail_all()
	else:
		self.set_avail_column_map(x)

def get_avail(self):
	if self.all_alts_always_available():
		return True
	return self.get_avail_column_map()


_avail_doc ="""\
This attributes defines the availability of alternatives for each case.  If set to `True`,
then all alternatives are available to all cases.  Otherwise, this attribute should be a
dict that contains {integer:string} key/value pairs, where
each key is an integer value corresponding to an alternative code, and each
value is a string identifying a column in the main table; that column should
contain a value indicating whether the alternative is available. This must be
a binary dummy variable.
"""

avail = property(lambda self: self.get_avail(), lambda self,w: self.set_avail(w), None, _avail_doc)


_alts_query_doc = """\
This attribute defines a SQL query that evaluates to an larch_alternatives table. The table
should have the following features:

	* Column 1: id (integer) a key for every alternative observed in the sample
	* Column 2: name (text) a name for each alternative
"""

alts_query = property(lambda self: self.get_alts_query(), lambda self,w: self.set_alts_query(w), None, _alts_query_doc)



_idco_query_doc = """\
This attribute defines a SQL query that evaluates to an larch_idco table. The table
should have the following features:

	* Column 1: caseid (integer) a key for every case observed in the sample
	* Column 2+ can contain any explanatory data, typically numeric data, although non-numeric data is allowable.

If the main table is named "data" typically this query will be::

	SELECT _rowid_ AS caseid, * FROM data

"""

idco_query = property(lambda self: self.get_idco_query(), lambda self,w: self.set_idco_query(w), None, _idco_query_doc)


_alts_values_doc = """\
This attribute defines a set of alternative codes and names, as a dictionary
that contains {integer:string} key/value pairs, where
each key is an integer value corresponding to an alternative code, and each
value is a string giving a descriptive name for the alternative.
When assigning to this attribute, a
query is defined that can be used with no table.

.. warning:: Using this method will overwrite :attr:`alts_query`
"""




alts_values = property(lambda self: self._get_alts_values(), lambda self,w: self.set_alts_values(w), None, _alts_values_doc)





## Load these methods into core.QuerySetSimpleCO

import_these = dict(locals())
from .core import QuerySetSimpleCO
for k,f in import_these.items():
	if len(k)>0 and k[0]!='_':
		setattr(QuerySetSimpleCO,k,f)
