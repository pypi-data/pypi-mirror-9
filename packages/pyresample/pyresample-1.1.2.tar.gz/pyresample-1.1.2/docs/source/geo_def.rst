Geometry definitions
====================
The module **pyresample.geometry** contains classes for describing different kinds of types
of remote sensing data geometries. The use of the different classes is described below.

Remarks
-------

All longitudes and latitudes provided to **pyresample.geometry** must be in degrees.
Longitudes must additionally be in the [-180;+180[ validity range.

As of version 1.1.1, the **pyresample.geometry** contructors will check the range of 
longitude values, send a warning if some of them fall outside validity range, 
and automatically correct the invalid values into [-180;+180[. 

Use function **utils.wrap_longitudes** for wrapping longitudes yourself.

AreaDefinition
--------------

The cartographic definition of grid areas used by Pyresample is contained in an object of type AreaDefintion. 
The following arguments are needed to initialize an area:

* **area_id** ID of area  
* **name**: Description
* **proj_id**: ID of projection 
* **proj_dict**: Proj4 parameters as dict
* **x_size**: Number of grid columns
* **y_size**: Number of grid rows
* **area_extent**: (x_ll, y_ll, x_ur, y_ur)

where

* **x_ll**: projection x coordinate of lower left corner of lower left pixel
* **y_ll**: projection y coordinate of lower left corner of lower left pixel
* **x_ur**: projection x coordinate of upper right corner of upper right pixel
* **y_ur**: projection y coordinate of upper right corner of upper right pixel

Creating an area definition:

.. doctest::
	
 >>> from pyresample import geometry
 >>> area_id = 'ease_sh'
 >>> name = 'Antarctic EASE grid'
 >>> proj_id = 'ease_sh'
 >>> proj4_args = 'proj=laea, lat_0=-90, lon_0=0, a=6371228.0, units=m'
 >>> x_size = 425
 >>> y_size = 425
 >>> area_extent = (-5326849.0625,-5326849.0625,5326849.0625,5326849.0625)
 >>> proj_dict = {'a': '6371228.0', 'units': 'm', 'lon_0': '0',
 ...              'proj': 'laea', 'lat_0': '-90'}
 >>> area_def = geometry.AreaDefinition(area_id, name, proj_id, proj_dict, x_size,
 ...                                    y_size, area_extent)
 >>> print area_def
 Area ID: ease_sh
 Name: Antarctic EASE grid
 Projection ID: ease_sh
 Projection: {'a': '6371228.0', 'units': 'm', 'lon_0': '0', 'proj': 'laea', 'lat_0': '-90'}
 Number of columns: 425
 Number of rows: 425
 Area extent: (-5326849.0625, -5326849.0625, 5326849.0625, 5326849.0625)

pyresample.utils
****************
The utils module of pyresample has convenience functions for constructing
area defintions. The function **get_area_def** can construct an area definition
based on area extent and a proj4-string or a list of proj4 arguments.

.. doctest::
	
 >>> from pyresample import utils
 >>> area_id = 'ease_sh'
 >>> area_name = 'Antarctic EASE grid'
 >>> proj_id = 'ease_sh'
 >>> proj4_args = '+proj=laea +lat_0=-90 +lon_0=0 +a=6371228.0 +units=m'
 >>> x_size = 425
 >>> y_size = 425
 >>> area_extent = (-5326849.0625,-5326849.0625,5326849.0625,5326849.0625)
 >>> area_def = utils.get_area_def(area_id, area_name, proj_id, proj4_args, 
 ...                  			   x_size, y_size, area_extent)
 >>> print area_def
 Area ID: ease_sh
 Name: Antarctic EASE grid
 Projection ID: ease_sh
 Projection: {'a': '6371228.0', 'units': 'm', 'lon_0': '0', 'proj': 'laea', 'lat_0': '-90'}
 Number of columns: 425
 Number of rows: 425
 Area extent: (-5326849.0625, -5326849.0625, 5326849.0625, 5326849.0625)


The **load_area** function can be used to parse area definitions from a configuration file. 
Assuming the file **/tmp/areas.cfg** exists with the following content

.. code-block:: bash

 REGION: ease_sh {
	NAME:           Antarctic EASE grid
	PCS_ID:         ease_sh
        PCS_DEF:        proj=laea, lat_0=-90, lon_0=0, a=6371228.0, units=m
        XSIZE:          425
        YSIZE:          425
        AREA_EXTENT:    (-5326849.0625,-5326849.0625,5326849.0625,5326849.0625)
 };

 REGION: ease_nh {
        NAME:           Arctic EASE grid
        PCS_ID:         ease_nh
        PCS_DEF:        proj=laea, lat_0=90, lon_0=0, a=6371228.0, units=m
        XSIZE:          425
        YSIZE:          425
        AREA_EXTENT:    (-5326849.0625,-5326849.0625,5326849.0625,5326849.0625)
 };

An area definition dict can be read using

.. doctest::

 >>> from pyresample import utils
 >>> area = utils.load_area('/tmp/areas.cfg', 'ease_nh')
 >>> print area
 Area ID: ease_nh
 Name: Arctic EASE grid
 Projection ID: ease_nh
 Projection: {'a': '6371228.0', 'units': 'm', 'lon_0': '0', 'proj': 'laea', 'lat_0': '90'}
 Number of columns: 425
 Number of rows: 425
 Area extent: (-5326849.0625, -5326849.0625, 5326849.0625, 5326849.0625)

Note: In the configuration file **REGION** maps to **area_id** and **PCS_ID** maps to **proj_id**.

Several area definitions can be read at once using the region names in an argument list

.. doctest::

 >>> from pyresample import utils
 >>> nh_def, sh_def = utils.load_area('/tmp/areas.cfg', 'ease_nh', 'ease_sh')
 >>> print sh_def
 Area ID: ease_sh
 Name: Antarctic EASE grid
 Projection ID: ease_sh
 Projection: {'a': '6371228.0', 'units': 'm', 'lon_0': '0', 'proj': 'laea', 'lat_0': '-90'}
 Number of columns: 425
 Number of rows: 425
 Area extent: (-5326849.0625, -5326849.0625, 5326849.0625, 5326849.0625)

GridDefinition
--------------
If the lons and lats grid values are known the area definition information can be skipped for some types
of resampling by using a GridDefinition object instead an AreaDefinition object.

.. doctest::

 >>> import numpy as np
 >>> from pyresample import geometry
 >>> lons = np.ones((100, 100))
 >>> lats = np.ones((100, 100))
 >>> grid_def = geometry.GridDefinition(lons=lons, lats=lats)
 
SwathDefinition
---------------
A swath is defined by the lon and lat values of the data points

.. doctest::

 >>> import numpy as np
 >>> from pyresample import geometry
 >>> lons = np.ones((500, 20))
 >>> lats = np.ones((500, 20))
 >>> swath_def = geometry.SwathDefinition(lons=lons, lats=lats)
 
Two swaths can be concatenated if their coloumn count matches

.. doctest::

 >>> import numpy as np
 >>> from pyresample import geometry
 >>> lons1 = np.ones((500, 20))
 >>> lats1 = np.ones((500, 20))
 >>> swath_def1 = geometry.SwathDefinition(lons=lons1, lats=lats1)
 >>> lons2 = np.ones((300, 20))
 >>> lats2 = np.ones((300, 20))
 >>> swath_def2 = geometry.SwathDefinition(lons=lons2, lats=lats2)
 >>> swath_def3 = swath_def1.concatenate(swath_def2) 
 
Geographic coordinates and boundaries
-------------------------------------
A ***definition** object allows for retrieval of geographic coordinates using array slicing (slice stepping is currently not supported).

All ***definition** objects exposes the coordinates **lons**, **lats** and **cartesian_coords**. 
AreaDefinition exposes the full set of projection coordinates as **projection_x_coords** and **projection_y_coords** 

Get full coordinate set:

.. doctest::
	
 >>> from pyresample import utils
 >>> area_id = 'ease_sh'
 >>> area_name = 'Antarctic EASE grid'
 >>> proj_id = 'ease_sh'
 >>> proj4_args = '+proj=laea +lat_0=-90 +lon_0=0 +a=6371228.0 +units=m'
 >>> x_size = 425
 >>> y_size = 425
 >>> area_extent = (-5326849.0625,-5326849.0625,5326849.0625,5326849.0625)
 >>> area_def = utils.get_area_def(area_id, area_name, proj_id, proj4_args, 
 ...                  			   x_size, y_size, area_extent)
 >>> lons = area_def.lons[:]

Get slice of coordinate set:

.. doctest::
	
 >>> from pyresample import utils
 >>> area_id = 'ease_sh'
 >>> area_name = 'Antarctic EASE grid'
 >>> proj_id = 'ease_sh'
 >>> proj4_args = '+proj=laea +lat_0=-90 +lon_0=0 +a=6371228.0 +units=m'
 >>> x_size = 425
 >>> y_size = 425
 >>> area_extent = (-5326849.0625,-5326849.0625,5326849.0625,5326849.0625)
 >>> area_def = utils.get_area_def(area_id, area_name, proj_id, proj4_args, 
 ...                  			   x_size, y_size, area_extent)
 >>> cart_subset = area_def.cartesian_coords[100:200, 350:]
 
If only the 1D range of a projection coordinate is required it can be extraxted using the **proj_x_coord** or **proj_y_coords** property of a geographic coordinate

.. doctest::
	
 >>> from pyresample import utils
 >>> area_id = 'ease_sh'
 >>> area_name = 'Antarctic EASE grid'
 >>> proj_id = 'ease_sh'
 >>> proj4_args = '+proj=laea +lat_0=-90 +lon_0=0 +a=6371228.0 +units=m'
 >>> x_size = 425
 >>> y_size = 425
 >>> area_extent = (-5326849.0625,-5326849.0625,5326849.0625,5326849.0625)
 >>> area_def = utils.get_area_def(area_id, area_name, proj_id, proj4_args, 
 ...                  			   x_size, y_size, area_extent)
 >>> proj_x_range = area_def.proj_x_coord
 
Spherical geometry operations
-----------------------------
Some basic spherical operations are available for ***definition** objects. The spherical geometry operations
are calculated based on the corners of a GeometryDefinition (2D SwathDefinition or Grid/AreaDefinition) and assuming the edges are great circle arcs.

It can be tested if geometries overlaps

.. doctest::

 >>> import numpy as np	
 >>> from pyresample import utils
 >>> area_id = 'ease_sh'
 >>> area_name = 'Antarctic EASE grid'
 >>> proj_id = 'ease_sh'
 >>> proj4_args = '+proj=laea +lat_0=-90 +lon_0=0 +a=6371228.0 +units=m'
 >>> x_size = 425
 >>> y_size = 425
 >>> area_extent = (-5326849.0625,-5326849.0625,5326849.0625,5326849.0625)
 >>> area_def = utils.get_area_def(area_id, area_name, proj_id, proj4_args, 
 ...                  			   x_size, y_size, area_extent)
 >>> lons = np.array([[-40, -11.1], [9.5, 19.4], [65.5, 47.5], [90.3, 72.3]])
 >>> lats = np.array([[-70.1, -58.3], [-78.8, -63.4], [-73, -57.6], [-59.5, -50]])
 >>> swath_def = geometry.SwathDefinition(lons, lats)
 >>> print swath_def.overlaps(area_def)
 True
 
The fraction of overlap can be calculated

.. doctest::

 >>> import numpy as np	
 >>> from pyresample import utils
 >>> area_id = 'ease_sh'
 >>> area_name = 'Antarctic EASE grid'
 >>> proj_id = 'ease_sh'
 >>> proj4_args = '+proj=laea +lat_0=-90 +lon_0=0 +a=6371228.0 +units=m'
 >>> x_size = 425
 >>> y_size = 425
 >>> area_extent = (-5326849.0625,-5326849.0625,5326849.0625,5326849.0625)
 >>> area_def = utils.get_area_def(area_id, area_name, proj_id, proj4_args, 
 ...                  			   x_size, y_size, area_extent)
 >>> lons = np.array([[-40, -11.1], [9.5, 19.4], [65.5, 47.5], [90.3, 72.3]])
 >>> lats = np.array([[-70.1, -58.3], [-78.8, -63.4], [-73, -57.6], [-59.5, -50]])
 >>> swath_def = geometry.SwathDefinition(lons, lats)
 >>> overlap_fraction = swath_def.overlap_rate(area_def)
 
And the polygon defining the (great circle) boundaries over the overlapping area can be calculated

.. doctest::

 >>> import numpy as np	
 >>> from pyresample import utils
 >>> area_id = 'ease_sh'
 >>> area_name = 'Antarctic EASE grid'
 >>> proj_id = 'ease_sh'
 >>> proj4_args = '+proj=laea +lat_0=-90 +lon_0=0 +a=6371228.0 +units=m'
 >>> x_size = 425
 >>> y_size = 425
 >>> area_extent = (-5326849.0625,-5326849.0625,5326849.0625,5326849.0625)
 >>> area_def = utils.get_area_def(area_id, area_name, proj_id, proj4_args, 
 ...                  			   x_size, y_size, area_extent)
 >>> lons = np.array([[-40, -11.1], [9.5, 19.4], [65.5, 47.5], [90.3, 72.3]])
 >>> lats = np.array([[-70.1, -58.3], [-78.8, -63.4], [-73, -57.6], [-59.5, -50]])
 >>> swath_def = geometry.SwathDefinition(lons, lats)
 >>> overlap_polygon = swath_def.intersection(area_def)
 
It can be tested if a (lon, lat) point is inside a GeometryDefinition

.. doctest::

 >>> import numpy as np	
 >>> from pyresample import utils
 >>> area_id = 'ease_sh'
 >>> area_name = 'Antarctic EASE grid'
 >>> proj_id = 'ease_sh'
 >>> proj4_args = '+proj=laea +lat_0=-90 +lon_0=0 +a=6371228.0 +units=m'
 >>> x_size = 425
 >>> y_size = 425
 >>> area_extent = (-5326849.0625,-5326849.0625,5326849.0625,5326849.0625)
 >>> area_def = utils.get_area_def(area_id, area_name, proj_id, proj4_args, 
 ...                  			   x_size, y_size, area_extent)
 >>> print (0, -90) in area_def
 True
     
