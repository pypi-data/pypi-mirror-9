######################################################################
# Copyright (C) 2013 Jaakko Luttinen
#
# This file is licensed under Version 3.0 of the GNU General Public
# License. See LICENSE for a text of the license.
######################################################################

######################################################################
# This file is part of BayesPy.
#
# BayesPy is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# BayesPy is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BayesPy.  If not, see <http://www.gnu.org/licenses/>.
######################################################################

"""
Package for Bayesian inference engines

Inference engines
-----------------

.. autosummary::
   :toctree: generated/

   VB

Parameter expansions
--------------------

.. autosummary::
   :toctree: generated/

   vmp.transformations.RotationOptimizer
   vmp.transformations.RotateGaussian
   vmp.transformations.RotateGaussianARD
   vmp.transformations.RotateGaussianMarkovChain
   vmp.transformations.RotateSwitchingMarkovChain
   vmp.transformations.RotateVaryingMarkovChain
   vmp.transformations.RotateMultiple
"""

from .vmp.vmp import VB
