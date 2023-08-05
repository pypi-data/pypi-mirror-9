#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @date: Thu May 24 10:41:42 CEST 2012
#
# Copyright (C) 2011-2012 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""The YouTube Faces database protocol interface. Please refer to http://www.cs.tau.ac.il/~wolf/ytfaces for information how to get a copy of the original data.

.. note::
  There has been errata data published for the database.
  These errata is **not** considered in the protocols (yet).

The YouTube database consists of 10 different splits, which are called "fold" here (to be consistent with the LFW database).
In each fold 9/10 of the database are used for training, and one for evaluation.
In **this implementation** of the YouTube protocols, up to 7/10 of the data is used for training (``groups='world'``),
2/10 are used for development (to estimate a threshold; ``groups='dev'``) and the last 1/10 is finally used to evaluate the system (``groups='eval'``).

To compute recognition results, please execute experiments on all 10 protocols (``protocol='fold1'`` ... ``protocol='fold10'``)
and average the resulting classification results (cf. http://vis-www.cs.umass.edu/lfw for details on scoring).

The design of this implementation differs slightly compared to the one from http://www.cs.tau.ac.il/~wolf/ytfaces.
Originally, only lists of image pairs are provided by the creators of the YouTube database.
To be consistent with other Bob databases, here the lists are split up into files to be enrolled, and probe files.
The files to be enrolled are always the first file in the pair, while the second pair item is used as probe.

.. note::
  When querying probe files, please **always** query probe files for a specific model id: ``objects(..., purposes = 'probe', model_ids = (model_id,))``.
  In this case, you will follow the default protocols given by the database.

When querying training files ``objects(..., groups='world')``, you will automatically end up with the "image restricted configuration".
When you want to respect the "unrestricted configuration" (cf. README on http://vis-www.cs.umass.edu/lfw),
please query the files that belong to the pairs, via ``objects(..., groups='world', world_type='unrestricted')``

If you want to stick to the original protocol and use only the pairs for training and testing, feel free to query the ``pairs`` function.

.. note::
  The pairs that are provided using the ``pairs`` function, and the files provided by the ``objects`` function (see note above) correspond to the identical model/probe pairs.
  Hence, either of the two approaches should give the same recognition results.

"""

from .query import Database
from .models import Client, Directory, Pair

def get_config():
  """Returns a string containing the configuration information.
  """

  import pkg_resources

  packages = pkg_resources.require(__name__)
  this = packages[0]
  deps = packages[1:]

  retval =  "%s: %s (%s)\n" % (this.key, this.version, this.location)
  retval += "  - python dependencies:\n"
  for d in deps: retval += "    - %s: %s (%s)\n" % (d.key, d.version, d.location)

  return retval.strip()

# gets sphinx autodoc done right - don't remove it
__all__ = [_ for _ in dir() if not _.startswith('_')]
