Pyhull is a Python wrapper to Qhull (http://www.qhull.org/) for the
computation of the convex hull, Delaunay triangulation and Voronoi diagram.
It is written as a Python C extension, with both high-level and low-level
interfaces to qhull.

Pyhull has been tested to scale to 10,000 7D points for convex hull
calculations (results in ~ 10 seconds), and 10,000 6D points for Delaunay
triangulations and Voronoi tesselations (~ 100 seconds). Higher number of
points and higher dimensions should be accessible depending on your machine,
but may take a significant amount of time.

For more details or to report bugs, please visit the pyhull GitHub page at
https://github.com/shyuep/pyhull or the documentation page at
http://packages.python.org/pyhull/.


