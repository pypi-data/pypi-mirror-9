Reprojection
============

Rasterio can map the pixels of a destination raster with an associated
coordinate reference system and transform to the pixels of a source image with
a different coordinate reference system and transform. This process is known as
reprojection.

Rasterio's ``rasterio.warp.reproject()`` is a very geospatial-specific analog
to SciPy's ``scipy.ndimage.interpolation.geometric_transform()`` [1]_.

The code below reprojects between two arrays, using no pre-existing GIS
datasets.  ``rasterio.warp.reproject()`` has two positional arguments: source
and destination.  The remaining keyword arguments parameterize the reprojection
transform.

.. code-block:: python

    import numpy
    import rasterio
    from rasterio import Affine as A
    from rasterio.warp import reproject, RESAMPLING

    with rasterio.drivers():

        # As source: a 512 x 512 raster centered on 0 degrees E and 0
        # degrees N, each pixel covering 15".
        rows, cols = src_shape = (512, 512)
        d = 1.0/240 # decimal degrees per pixel
        # The following is equivalent to 
        # A(d, 0, -cols*d/2, 0, -d, rows*d/2).
        src_transform = A.translation(-cols*d/2, rows*d/2) * A.scale(d, -d)
        src_crs = {'init': 'EPSG:4326'}
        source = numpy.ones(src_shape, numpy.uint8)*255

        # Destination: a 1024 x 1024 dataset in Web Mercator (EPSG:3857)
        # with origin at 0.0, 0.0.
        dst_shape = (1024, 1024)
        dst_transform = [-237481.5, 425.0, 0.0, 237536.4, 0.0, -425.0]
        dst_crs = {'init': 'EPSG:3857'}
        destination = numpy.zeros(dst_shape, numpy.uint8)

        reproject(
            source, 
            destination, 
            src_transform=src_transform,
            src_crs=src_crs,
            dst_transform=dst_transform,
            dst_crs=dst_crs,
            resampling=RESAMPLING.nearest)

        # Assert that the destination is only partly filled.
        assert destination.any()
        assert not destination.all()


See `examples/reproject.py <https://github.com/mapbox/rasterio/blob/master/examples/reproject.py>`__ for code that writes the destination array to a GeoTIFF file. I've 
uploaded the resulting file to a Mapbox map to demonstrate that the reprojection is
correct: https://a.tiles.mapbox.com/v3/sgillies.hfek2oko/page.html?secure=1#6/0.000/0.033.

Reprojecting a GeoTIFF dataset
------------------------------

Here's a more real-world example of using ``reproject()`` to make an output dataset zoomed out by a factor of 2.
Methods of the ``rasterio.Affine`` class help us generate the output dataset's transform matrix and, thereby, its
spatial extent. 

.. code-block:: python

    import numpy
    import rasterio
    from rasterio import Affine as A
    from rasterio.warp import reproject, RESAMPLING

    with rasterio.open('rasterio/tests/data/RGB.byte.tif') as src:
        src_transform = src.affine

        # Zoom out by a factor of 2 from the center of the source
        # dataset. The destination transform is the product of the
        # source transform, a translation down and to the right, and
        # a scaling.
        dst_transform = src_transform*A.translation(
            -src.width/2.0, -src.height/2.0)*A.scale(2.0)

        data = src.read()

        kwargs = src.meta
        kwargs['transform'] = dst_transform

        with rasterio.open('/tmp/zoomed-out.tif', 'w', **kwargs) as dst:

            for i, band in enumerate(data, 1):
                dest = numpy.zeros_like(band)

                reproject(
                    band,
                    dest,
                    src_transform=src_transform,
                    src_crs=src.crs,
                    dst_transform=dst_transform,
                    dst_crs=src.crs,
                    resampling=RESAMPLING.nearest)

                dst.write_band(i, dest)

.. image:: https://farm8.staticflickr.com/7399/16390100651_54f01b8601_b_d.jpg)

References
----------

.. [1] http://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.interpolation.geometric_transform.html#scipy.ndimage.interpolation.geometric_transform

