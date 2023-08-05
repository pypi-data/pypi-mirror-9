######################################################### encoding: utf-8 ######
#
#  Copyright 2007-2015 Jeffrey Newman.
#
#  This file is part of Larch.
#
#  Larch is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Larch is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Larch.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
#
#  This example file shows commands needed to replicate the model given in 
#  BIOGEME's example file: 04modifVariables.py
#  http://biogeme.epfl.ch/swissmetro/examples.html
#
################################################################################

from .. import larch
import os

# Set example data for this model
with open(os.path.join(larch._directory_,"examples","swissmetro00data.py")) as f:
	code = compile(f.read(), "swissmetro00data.py", 'exec')
	exec(code, globals(), globals())

def model(d=None):
	if d is None: d = data()
	m = larch.Model(d)
	m.title = "swissmetro example 04 (transforms)"
	
	# ModelObject.utility.co(<idCO data column>,<alternative code>,[<parameter name>])
	#	Adds a linear component to the utility of the indicated alternative.
	#	The data column is a string and can be any idCO data column or a pre-calculated 
	#	value derived from one or more idCO data columns, or no data columns at all.
	#	Note: there is no need to declare a parameter name seperately from this 
	#	command. Default values will be assumed for parameters that are not previously
	#	declared.
	m.utility.co("1",1,"ASC_TRAIN") 
	m.utility.co("1",3,"ASC_CAR") 
	m.utility.co("TRAIN_TT",1,"B_TIME")
	m.utility.co("SM_TT",2,"B_TIME")
	m.utility.co("CAR_TT",3,"B_TIME")
	m.utility.co("log(((TRAIN_CO*(GA==0))/100.0)+((TRAIN_CO*(GA==0))==0))",1,"B_LOGCOST")
	m.utility.co("log(((SM_CO*(GA==0))/100.0)+((SM_CO*(GA==0))==0))",2,"B_LOGCOST")
	m.utility.co("log((CAR_CO/100.0)+(CAR_CO==0))",3,"B_LOGCOST")

	# ModelObject.option
	#	A structure that defines certain options to be applied when estimating
	#	models.
	m.option.calculate_std_err = True
	
	return m # Returns the model object from the model() function.

############################# END OF EXAMPLE FILE ##############################
