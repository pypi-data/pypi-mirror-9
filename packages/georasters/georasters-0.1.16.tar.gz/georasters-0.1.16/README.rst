GeoRasters
===========

|BuildStatus|_ 
|CoverageStatus|_
|PyPiVersion|_
|PyPiDownloads|_

The ``GeoRasters`` package is a python module that provides a fast and flexible
tool to work with GIS raster files. It provides the GeoRaster class, which makes working with rasters quite transparent and easy.
In a way it tries to do for rasters what GeoPandas does for geometries.

It includes tools to 

- Merge rasters
- Plot rasters
- Extract information from rasters
- Given a point (lat,lon) find its location in a raster
- Aggregate rasters to lower resolutions
- Align two rasters of different sizes to common area and size
- Get all the geographical information of raster
- Create GeoTiff files easily
- Load GeoTiff files as masked numpy rasters

Install
-------

.. code-block:: python
    
    pip install git+git://github.com/ozak/georasters.git
    pip install georasters
   
Example Usage: GeoRasters
-------------------------

.. code-block:: python
    
    import georasters as gr
    
    # Load data
    raster = './data/slope.tif'
    data = gr.from_file(raster)
    
    # Plot data
    data.plot()
    
    # Get some stats
    data.mean()
    data.sum()
    data.std()
    
Example Merge GeoRasters:
-------------------------

.. code-block:: python

    import georasters as gr
    import matplotlib.pyplot as plt
    
    # Import raster
    raster = os.path.join(DATA, 'pre1500.tif')
    data = gr.from_file(raster)
    (xmin,xsize,x,ymax,y,ysize)=data.geot
    
    # Split raster in two
    data1 = gr.GeoRaster(data.raster[:data.shape[0]/2,:], data.geot, 
                          nodata_value=data.nodata_value, projection=data.projection, datatype=data.datatype)
    data2 = gr.GeoRaster(data.raster[data.shape[0]/2:,:], (xmin,xsize,x,ymax+ysize*data.shape[0]/2,y,ysize), 
                          nodata_value=data.nodata_value, projection=data.projection, datatype=data.datatype)

    # Plot both parts and save them
    plt.figure(figsize=(12,8))
    data1.plot()
    plt.savefig(os.path.join(DATA,'data1.png'), bbox_inches='tight')

.. image :: ./tests/data/data1.png
    
.. code-block:: python

    plt.figure(figsize=(12,8))
    data2.plot()
    plt.savefig(os.path.join(DATA,'data2.png'), bbox_inches='tight')
    
.. image :: ./tests/data/data2.png
    
.. code-block:: python

    # Generate merged raster
    
    data3 = data1.union(data2)
    
    # Plot it and save the figure
    
    plt.figure(figsize=(12,8))
    data3.plot()
    plt.savefig(os.path.join(DATA,'data3.png'), bbox_inches='tight')
    
.. image :: ./tests/data/data3.png
    

Another Merge:
--------------


Example Usage: Other functions
------------------------------

.. code-block:: python
    
    import georasters as gr
    
    # Get info on raster
    NDV, xsize, ysize, GeoT, Projection, DataType = gr.get_geo_info(raster)
    
    # Load raster
    data = load_tiff(raster)
       
    # Find location of point (x,y) on raster, e.g. to extract info at that location
    col, row = gr.map_pixel(x,y,GeoT[1],GeoT[-1], GeoT[0],GeoT[3])
    value = data[row,col]
    
    # Agregate raster by summing over cells in order to increase pixel size by e.g. 10
    gr.aggregate(data,NDV,(10,10))
    
    # Align two rasters
    data2 = load_tiff(raster2)
    (alignedraster_o, alignedraster_a, GeoT_a) = gr.align_rasters(raster, raster2, how=np.mean)
    
    # Create GeoRaster
    A=gr.GeoRaster(data, GeoT, nodata_value=NDV)

    # Load another raster
    NDV, xsize, ysize, GeoT, Projection, DataType = gr.get_geo_info(raster2)
    data = load_tiff(raster2)
    B=gr.GeoRaster(data2, GeoT, nodata_value=NDV)
    
    # Plot Raster
    A.plot()
    
    # Merge both rasters and plot
    C=B.merge(A)
    C.plot()
    
Issues
------

Find a bug? Report it via github issues by providing

- a link to download the smallest possible raster and vector dataset necessary to reproduce the error
- python code or command to reproduce the error
- information on your environment: versions of python, gdal and numpy and system memory

.. |BuildStatus| image:: https://api.travis-ci.org/ozak/georasters.png
.. _BuildStatus: https://travis-ci.org/ozak/georasters

.. |CoverageStatus| image:: https://coveralls.io/repos/ozak/georasters/badge.png
.. _CoverageStatus: https://coveralls.io/r/ozak/georasters

.. |PyPiVersion| image:: https://pypip.in/v/georasters/badge.png
.. _PyPiVersion: http://pypi.python.org/pypi/georasters

.. |PyPiDownloads| image:: https://pypip.in/d/georasters/badge.png
.. _PyPiDownloads: http://pypi.python.org/pypi/georasters