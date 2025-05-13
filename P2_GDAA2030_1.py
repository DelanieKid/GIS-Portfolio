""" Assignment 2: Script 1

Analyzing the Shelburn wildfire burn marks with near infrared and short wave
infrared bands. Contains modified Copernicus Sentinel data 2023.
"""

__author__ = "Delanie Kidnie"


import pystac_client
import planetary_computer
import rasterio
import rasterio.dtypes
import rasterio.transform
from rasterio.windows import Window
from rasterio.warp import reproject, Resampling
import numpy as np
import rasterio.windows
import fiona.crs


catalog = pystac_client.Client.open('https://planetarycomputer.microsoft.com/api/stac/v1',
    modifier=planetary_computer.sign_inplace)

before_id = 'S2A_MSIL2A_20230523T151651_R025_T19TGJ_20230524T010343'

after_id = 'S2B_MSIL2A_20230806T151659_R025_T19TGJ_20230806T211758'


after = catalog.search(collections=['sentinel-2-l2a'], ids=after_id)
before = catalog.search(collections=['sentinel-2-l2a'], ids=before_id)


# upscale swir band from 20 to 10 m
bounds = [767760.0,4827590.0,801670.0,4847040.0]
for item in after.item_collection():
    with (rasterio.open(item.assets['B12'].href) as after_swir,
        rasterio.open(item.assets['B08'].href) as after_nir):
        profile = after_swir.profile
        print(profile['count'])
        swir_window = rasterio.windows.from_bounds(*bounds,
                                                after_swir.transform)
        swir_window_transform = rasterio.windows.transform(swir_window,
                                                        after_swir.transform)
        swir_band_20 = after_swir.read(indexes=1, window=swir_window)
        swir_band_10 = np.empty((int(swir_window.height * 2),
                                int(swir_window.width * 2)), dtype=swir_band_20.dtype)
        profile['transform'] = rasterio.Affine(
            a=10,
            b=swir_window_transform.b,
            c=swir_window_transform.c,
            d=swir_window_transform.d,
            e=-10,
            f=swir_window_transform.f
        )
        profile['width'] = swir_window.width * 2
        profile['height'] = swir_window.height * 2
        after_B12, transform = reproject(
            source=swir_band_20,
            destination=swir_band_10,
            src_transform=swir_window_transform,
            dst_transform=profile['transform'],
            resampling=Resampling.nearest,
            src_crs=after_swir.crs,
            dst_crs=after_swir.crs
        )
        profile['dtype'] = rasterio.float64


        # download nir band
        nir_window = rasterio.windows.from_bounds(*bounds,
                                                after_nir.transform)
        nir_window_transform = rasterio.windows.transform(nir_window, after_nir.transform)
        after_B08 = after_nir.read(indexes=1, window=nir_window)

        after_B12 = np.expand_dims(after_B12,0)
        after_B08 = np.expand_dims(after_B08,0)

        top = np.subtract(after_B08[0], after_B12[0], dtype=rasterio.float64)

        bottom = (after_B08[0] + after_B12[0])
        after_NBR = np.divide(top, bottom, dtype=rasterio.float64)
    
# Prepare imagery from before the fire
for item in before.item_collection():
    with(rasterio.open(item.assets['B12'].href) as before_swir,
         rasterio.open(item.assets['B08'].href) as before_nir):
        profile = before_swir.profile
        print(profile['count'])
        swir_window = rasterio.windows.from_bounds(*bounds,
                                                before_swir.transform)
        swir_window_transform = rasterio.windows.transform(swir_window,
                                                        before_swir.transform)
        swir_band_20 = before_swir.read(indexes=1, window=swir_window)
        swir_band_10 = np.empty((int(swir_window.height * 2),
                                int(swir_window.width * 2)), dtype=swir_band_20.dtype)
        profile['width'] = swir_window.width * 2
        profile['height'] = swir_window.height * 2
        profile['transform'] = rasterio.Affine(
            a=10,
            b=swir_window_transform.b,
            c=swir_window_transform.c,
            d=swir_window_transform.d,
            e=-10,
            f=swir_window_transform.f
        )
        profile['dtype'] = rasterio.float64
        before_B12, transform = reproject(
            source=swir_band_20,
            destination=swir_band_10,
            src_transform=swir_window_transform,
            dst_transform=profile['transform'],
            resampling=Resampling.nearest,
            src_crs=before_swir.crs,
            dst_crs=before_swir.crs
        )


        # download nir band
        nir_window = rasterio.windows.from_bounds(*bounds,
                                                before_nir.transform)
        nir_window_transform = rasterio.windows.transform(nir_window, before_nir.transform)
        before_B08 = before_nir.read(indexes=1, window=nir_window)

        before_B12 = np.expand_dims(before_B12,0)
        before_B08 = np.expand_dims(before_B08,0)

        top = np.subtract(before_B08[0], before_B12[0], dtype=rasterio.float64)
        bottom = (before_B08[0] + before_B12[0])

        before_NBR = np.divide(top, bottom, dtype=rasterio.float64)

before_NBR = np.nan_to_num(before_NBR)
BurnSeverity = np.subtract(before_NBR, after_NBR, dtype = rasterio.float64)
BurnSeverity = np.expand_dims(BurnSeverity,0)


profile = {
    'driver': 'GTiff',
    'dtype': rasterio.float64,
    'width': 3391,
    'height': 1945,
    'crs': fiona.crs.from_epsg(32619),
    'count': 1,
    'transform': rasterio.transform.from_bounds(*bounds, width=3391, height=1945)
}

with rasterio.open('burn_severity.tif', 'w', **profile) as output:
    output.write(BurnSeverity[0], indexes=1)    