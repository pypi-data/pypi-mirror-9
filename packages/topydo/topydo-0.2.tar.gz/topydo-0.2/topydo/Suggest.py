# Topydo - A todo.txt client written in Python.
# Copyright (C) 2014 Bram Schoenmakers <me@bramschoenmakers.nl>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re

def _normalize(p_term):
    """ Normalizes a term. """
    return re.sub(r'\W', '', p_term).lower()

def distance(p_vector):
    """ Returns the Euclidean distance of a vector. """
    return pow(sum(pow(p_vector[i], 2) for i in range(p_vector)), 0.5)

def similar_items(p_query, p_documents):
    for term in p_query.split():
        term = _normalize(term)

        # for document in p_documents:

