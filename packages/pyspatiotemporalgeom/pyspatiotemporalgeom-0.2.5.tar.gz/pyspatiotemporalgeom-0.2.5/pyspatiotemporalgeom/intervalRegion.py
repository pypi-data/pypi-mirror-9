#    Copyright (c) 2014 Mark McKenney
#
#    Permission is hereby granted, free of charge, to any person obtaining a copy
#    of this software and associated documentation files (the "Software"), to deal
#    in the Software without restriction, including without limitation the rights
#    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#    copies of the Software, and to permit persons to whom the Software is
#    furnished to do so, subject to the following conditions:
#
#    The above copyright notice and this permission notice shall be included in
#    all copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#    THE SOFTWARE.




'''
intervalRegion.py
  
Code to define and manipulate interval regions

'''

from pyspatiotemporalgeom.utilities import regionInterpolator

def interpolateRegions(region1,region2, startTime, endTime, noTriIntersectionChecks = False ):
  '''
  This is just a wrapper that calls ``pyspatiotemporalgeom.utilities.regionInterpolater.interpolate()``.  The documentation for that function is copied here:

  This is where the magic happens.  Create an interpolation between two well-formed regions over a time interval (defined by ``startTime`` and ``endTime``) such that at every instant within that time interval, the region resulting from the interpolation at that instant conforms to the type definition of complex regions as defined in [1].  Note that the various region generators and region creation functions int he region.py file create well formed regions according to [1].  In otherwords, the moving region resulting from this function conforms to the type definition of moving regions in [2].

  This function is an extension of the algorithm in [3] to handle both simple (1 simple cycle with no holes) regions and complex regions.


  [1] Markus Schneider and Thomas Behr. 2006. Topological relationships between complex spatial objects. ACM Trans. Database Syst. 31, 1 (March 2006), 39-81. DOI=10.1145/1132863.1132865 http://doi.acm.org/10.1145/1132863.1132865

  
  [2] Ralf Hartmut Guting, Michael H. Bohlen, Martin Erwig, Christian S. Jensen, Nikos A. Lorentzos, Markus Schneider, and Michalis Vazirgiannis. 2000. A foundation for representing and querying moving objects. ACM Trans. Database Syst. 25, 1 (March 2000), 1-42. DOI=10.1145/352958.352963 http://doi.acm.org/10.1145/352958.352963
  
  [3] Mark McKenney and James Webb. 2010. Extracting moving regions from spatial data. In Proceedings of the 18th SIGSPATIAL International Conference on Advances in Geographic Information Systems (GIS '10). ACM, New York, NY, USA, 438-441. DOI=10.1145/1869790.1869856 http://doi.acm.org/10.1145/1869790.1869856

  Input:

  1. r1, r2: two well formed regions represented as lists of hlafsegments.  Any of the region creation functions in region.py will do.
  2. startTime, endTime:  two numbers defining a time interval.  These numbers are used as the 3D dimension when extrapolating into 3D space.
  3. noTriIntersectionChecks. See paper [3].  The algorithm first creates an interpolation between the input regions.  It is possible that the interpolation will result in a self-intersecting region at some point.  The triangle/triangle intersection test is then performed.  This test is very computationally intensive (especially for python) and can take a LONG time to compute.  If you pass a ``True`` for this argument, the tri/tri intersection test is skipped, and the interpolation returned AS-IS (possibly with self-intersections).  This makes the algorithm :math:`O(n \lg n)` instead of :math:`O(n^2)`.

  Output:

  A 3-tuple.  See [3].  The algorithm will create at MOST, 3 interval regions to describe the interpolation of r1 to r2 over the defined time interval.  Not all 3 interval regions are always required, so 1 or 2 of the values in the tuple may be ``None``, but a 3 tuple is ALWAYS returned.  If the ``noTriIntersectionChecks`` argument is set to ``True``, or the original interpolation succeeds, then the return value will look like this: ``(None, triList, None)``.

  Any non-``None`` value in the return tuple will be a list of trinagles describing the movinement of line segments in r1 as they travel across the defined interval to r2 (between intermediate states of r1 and r2 if necessary).

  '''
  return regionInterpolator.interpolate( region1, region2, startTime, endTime, noTriIntersectionChecks )




