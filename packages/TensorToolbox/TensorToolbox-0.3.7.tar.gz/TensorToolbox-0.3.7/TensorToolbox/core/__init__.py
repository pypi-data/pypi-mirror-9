# -*- coding: utf-8 -*-

#!/usr/bin/env python

#
# This file is part of TensorToolbox.
#
# TensorToolbox is free software: you can redistribute it and/or modify
# it under the terms of the LGNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TensorToolbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# LGNU Lesser General Public License for more details.
#
# You should have received a copy of the LGNU Lesser General Public License
# along with TensorToolbox.  If not, see <http://www.gnu.org/licenses/>.
#
# DTU UQ Library
# Copyright (C) 2014-2015 The Technical University of Denmark
# Scientific Computing Section
# Department of Applied Mathematics and Computer Science
#
# Author: Daniele Bigoni
#

import auxiliary
from auxiliary import *
import storage
from storage import *
import tensor_wrapper
from tensor_wrapper import *
import candecomp
from candecomp import *
import TensorTrainVec
from TensorTrainVec import *
import WeightedTensorTrainVec
from WeightedTensorTrainVec import *
import TensorTrainMat
from TensorTrainMat import *
import QuanticsTensorTrainVec
from QuanticsTensorTrainVec import *
import QuanticsTensorTrainMat
from QuanticsTensorTrainMat import *
import SpectralTensorTrain 
from SpectralTensorTrain import *

__all__ = []
__all__ += auxiliary.__all__
__all__ += storage.__all__
__all__ += tensor_wrapper.__all__
__all__ += candecomp.__all__
__all__ += TensorTrainVec.__all__
__all__ += WeightedTensorTrainVec.__all__
__all__ += TensorTrainMat.__all__
__all__ += QuanticsTensorTrainVec.__all__
__all__ += QuanticsTensorTrainMat.__all__
__all__ += SpectralTensorTrain.__all__

__author__ = "Daniele Bigoni"
__copyright__ = """Copyright 2014, The Technical University of Denmark"""
__credits__ = ["Daniele Bigoni"]
__maintainer__ = "Daniele Bigoni"
__email__ = "dabi@imm.dtu.dk"
__status__ = "Production"
