########################################################
# Started Logging At: 2015-03-04 16:26:56
########################################################
########################################################
# Started Logging At: 2015-03-04 16:27:00
########################################################
########################################################
# # Started Logging At: 2015-03-04 16:27:01
########################################################
from spectral_cube import SpectralCube
import numpy as np
cube_array = np.zeros([5,5,5])
cube_array = np.zeros([5,5,5])
print(cube_array.shape, cube_array.size)
from spectral_cube import SpectralCube
from astropy.wcs import WCS
import numpy as np
cube_array = np.zeros([5,5,5])
print(cube_array.shape, cube_array.size)
cube_wcs = WCS(naxis=3)
cube_wcs = WCS(naxis=3)
cube_wcs
#[Out]# <astropy.wcs.wcs.WCS at 0x10de69ec0>
cube_wcs = WCS(naxis=3)
cube_wcs,cube_wcs.to_header()
#[Out]# (<astropy.wcs.wcs.WCS at 0x10de69e18>,
#[Out]#  WCSAXES =                    3 / Number of coordinate axes                      
#[Out]#  CRPIX1  =                  0.0 / Pixel coordinate of reference point            
#[Out]#  CRPIX2  =                  0.0 / Pixel coordinate of reference point            
#[Out]#  CRPIX3  =                  0.0 / Pixel coordinate of reference point            
#[Out]#  CDELT1  =                  1.0 / Coordinate increment at reference point        
#[Out]#  CDELT2  =                  1.0 / Coordinate increment at reference point        
#[Out]#  CDELT3  =                  1.0 / Coordinate increment at reference point        
#[Out]#  CRVAL1  =                  0.0 / Coordinate value at reference point            
#[Out]#  CRVAL2  =                  0.0 / Coordinate value at reference point            
#[Out]#  CRVAL3  =                  0.0 / Coordinate value at reference point            
#[Out]#  LATPOLE =                 90.0 / [deg] Native latitude of celestial pole        )
cube_wcs = WCS(naxis=3)
cube_wcs.wcs.ctype=['RA','DEC','VELO']
cube_wcs,cube_wcs.to_header()
#[Out]# (<astropy.wcs.wcs.WCS at 0x10de69d70>,
#[Out]#  WCSAXES =                    3 / Number of coordinate axes                      
#[Out]#  CRPIX1  =                  0.0 / Pixel coordinate of reference point            
#[Out]#  CRPIX2  =                  0.0 / Pixel coordinate of reference point            
#[Out]#  CRPIX3  =                  0.0 / Pixel coordinate of reference point            
#[Out]#  CDELT1  =                  1.0 / [deg] Coordinate increment at reference point  
#[Out]#  CDELT2  =                  1.0 / [deg] Coordinate increment at reference point  
#[Out]#  CDELT3  =                  1.0 / [m/s] Coordinate increment at reference point  
#[Out]#  CUNIT1  = 'deg'                / Units of coordinate increment and value        
#[Out]#  CUNIT2  = 'deg'                / Units of coordinate increment and value        
#[Out]#  CUNIT3  = 'm/s'                / Units of coordinate increment and value        
#[Out]#  CTYPE1  = 'RA'                 / Coordinate type codeundefined projection       
#[Out]#  CTYPE2  = 'DEC'                / Coordinate type codeundefined projection       
#[Out]#  CTYPE3  = 'VELO'               / Relativistic velocity (linear)                 
#[Out]#  CRVAL1  =                  0.0 / [deg] Coordinate value at reference point      
#[Out]#  CRVAL2  =                  0.0 / [deg] Coordinate value at reference point      
#[Out]#  CRVAL3  =                  0.0 / [m/s] Coordinate value at reference point      
#[Out]#  LATPOLE =                 90.0 / [deg] Native latitude of celestial pole        
#[Out]#  RADESYS = 'ICRS'               / Equatorial coordinate system                   )
cube_wcs = WCS(naxis=3)
cube_wcs.wcs.ctype=['RA','DEC','VELO']
cube_wcs,cube_wcs.to_header()
#[Out]# (<astropy.wcs.wcs.WCS at 0x10de69f68>,
#[Out]#  WCSAXES =                    3 / Number of coordinate axes                      
#[Out]#  CRPIX1  =                  0.0 / Pixel coordinate of reference point            
#[Out]#  CRPIX2  =                  0.0 / Pixel coordinate of reference point            
#[Out]#  CRPIX3  =                  0.0 / Pixel coordinate of reference point            
#[Out]#  CDELT1  =                  1.0 / [deg] Coordinate increment at reference point  
#[Out]#  CDELT2  =                  1.0 / [deg] Coordinate increment at reference point  
#[Out]#  CDELT3  =                  1.0 / [m/s] Coordinate increment at reference point  
#[Out]#  CUNIT1  = 'deg'                / Units of coordinate increment and value        
#[Out]#  CUNIT2  = 'deg'                / Units of coordinate increment and value        
#[Out]#  CUNIT3  = 'm/s'                / Units of coordinate increment and value        
#[Out]#  CTYPE1  = 'RA'                 / Coordinate type codeundefined projection       
#[Out]#  CTYPE2  = 'DEC'                / Coordinate type codeundefined projection       
#[Out]#  CTYPE3  = 'VELO'               / Relativistic velocity (linear)                 
#[Out]#  CRVAL1  =                  0.0 / [deg] Coordinate value at reference point      
#[Out]#  CRVAL2  =                  0.0 / [deg] Coordinate value at reference point      
#[Out]#  CRVAL3  =                  0.0 / [m/s] Coordinate value at reference point      
#[Out]#  LATPOLE =                 90.0 / [deg] Native latitude of celestial pole        
#[Out]#  RADESYS = 'ICRS'               / Equatorial coordinate system                   )
cube = SpectralCube(data=cube, wcs=wcs)
cube = SpectralCube(data=cube_array, wcs=wcs)
cube = SpectralCube(data=cube_array, wcs=cube_wcs)
cube = SpectralCube(data=cube_array, wcs=cube_wcs)
cube
#[Out]# SpectralCube with shape=(5, 5, 5):
#[Out]#  n_x: 5  type_x: RA        unit_x: deg
#[Out]#  n_y: 5  type_y: DEC       unit_y: deg
#[Out]#  n_s: 5  type_s: VELO      unit_s: m / s
from spectral_cube import SpectralCube
from astropy.wcs import WCS
import numpy as np
cube_array = np.zeros([3,4,5])
print(cube_array.shape, cube_array.size)
cube_wcs = WCS(naxis=3)
cube_wcs.wcs.ctype=['RA','DEC','VELO']
cube_wcs,cube_wcs.to_header()
#[Out]# (<astropy.wcs.wcs.WCS at 0x10c401f68>,
#[Out]#  WCSAXES =                    3 / Number of coordinate axes                      
#[Out]#  CRPIX1  =                  0.0 / Pixel coordinate of reference point            
#[Out]#  CRPIX2  =                  0.0 / Pixel coordinate of reference point            
#[Out]#  CRPIX3  =                  0.0 / Pixel coordinate of reference point            
#[Out]#  CDELT1  =                  1.0 / [deg] Coordinate increment at reference point  
#[Out]#  CDELT2  =                  1.0 / [deg] Coordinate increment at reference point  
#[Out]#  CDELT3  =                  1.0 / [m/s] Coordinate increment at reference point  
#[Out]#  CUNIT1  = 'deg'                / Units of coordinate increment and value        
#[Out]#  CUNIT2  = 'deg'                / Units of coordinate increment and value        
#[Out]#  CUNIT3  = 'm/s'                / Units of coordinate increment and value        
#[Out]#  CTYPE1  = 'RA'                 / Coordinate type codeundefined projection       
#[Out]#  CTYPE2  = 'DEC'                / Coordinate type codeundefined projection       
#[Out]#  CTYPE3  = 'VELO'               / Relativistic velocity (linear)                 
#[Out]#  CRVAL1  =                  0.0 / [deg] Coordinate value at reference point      
#[Out]#  CRVAL2  =                  0.0 / [deg] Coordinate value at reference point      
#[Out]#  CRVAL3  =                  0.0 / [m/s] Coordinate value at reference point      
#[Out]#  LATPOLE =                 90.0 / [deg] Native latitude of celestial pole        
#[Out]#  RADESYS = 'ICRS'               / Equatorial coordinate system                   )
cube = SpectralCube(data=cube_array, wcs=cube_wcs)
cube
#[Out]# SpectralCube with shape=(3, 4, 5):
#[Out]#  n_x: 5  type_x: RA        unit_x: deg
#[Out]#  n_y: 4  type_y: DEC       unit_y: deg
#[Out]#  n_s: 3  type_s: VELO      unit_s: m / s
cube.moment0(axis=0)
#[Out]# <Projection [[ 0., 0., 0., 0., 0.],
#[Out]#              [ 0., 0., 0., 0., 0.],
#[Out]#              [ 0., 0., 0., 0., 0.],
#[Out]#              [ 0., 0., 0., 0., 0.]] m / s>
cube.moment0(axis=1)
#[Out]# <Projection [[ 0., 0., 0., 0., 0.],
#[Out]#              [ 0., 0., 0., 0., 0.],
#[Out]#              [ 0., 0., 0., 0., 0.]] deg>
cube[:,2,2]
#[Out]# <OneDSpectrum [ 0., 0., 0.]>
cube = SpectralCube(data=cube_array, wcs=cube_wcs, unit=u.K)
cube
import numpy as np
from spectral_cube import SpectralCube
from astropy.wcs import WCS
from astropy import units as u
cube_array = np.zeros([3,4,5])
print(cube_array.shape, cube_array.size)
cube_wcs = WCS(naxis=3)
cube_wcs.wcs.ctype=['RA','DEC','VELO']
cube_wcs,cube_wcs.to_header()
#[Out]# (<astropy.wcs.wcs.WCS at 0x10e983788>,
#[Out]#  WCSAXES =                    3 / Number of coordinate axes                      
#[Out]#  CRPIX1  =                  0.0 / Pixel coordinate of reference point            
#[Out]#  CRPIX2  =                  0.0 / Pixel coordinate of reference point            
#[Out]#  CRPIX3  =                  0.0 / Pixel coordinate of reference point            
#[Out]#  CDELT1  =                  1.0 / [deg] Coordinate increment at reference point  
#[Out]#  CDELT2  =                  1.0 / [deg] Coordinate increment at reference point  
#[Out]#  CDELT3  =                  1.0 / [m/s] Coordinate increment at reference point  
#[Out]#  CUNIT1  = 'deg'                / Units of coordinate increment and value        
#[Out]#  CUNIT2  = 'deg'                / Units of coordinate increment and value        
#[Out]#  CUNIT3  = 'm/s'                / Units of coordinate increment and value        
#[Out]#  CTYPE1  = 'RA'                 / Coordinate type codeundefined projection       
#[Out]#  CTYPE2  = 'DEC'                / Coordinate type codeundefined projection       
#[Out]#  CTYPE3  = 'VELO'               / Relativistic velocity (linear)                 
#[Out]#  CRVAL1  =                  0.0 / [deg] Coordinate value at reference point      
#[Out]#  CRVAL2  =                  0.0 / [deg] Coordinate value at reference point      
#[Out]#  CRVAL3  =                  0.0 / [m/s] Coordinate value at reference point      
#[Out]#  LATPOLE =                 90.0 / [deg] Native latitude of celestial pole        
#[Out]#  RADESYS = 'ICRS'               / Equatorial coordinate system                   )
cube = SpectralCube(data=cube_array, wcs=cube_wcs, unit=u.K)
cube
cube.moment0(axis=0)
#[Out]# <Projection [[ 0., 0., 0., 0., 0.],
#[Out]#              [ 0., 0., 0., 0., 0.],
#[Out]#              [ 0., 0., 0., 0., 0.],
#[Out]#              [ 0., 0., 0., 0., 0.]] m / s>
cube.moment0(axis=1)
#[Out]# <Projection [[ 0., 0., 0., 0., 0.],
#[Out]#              [ 0., 0., 0., 0., 0.],
#[Out]#              [ 0., 0., 0., 0., 0.]] deg>
cube[:,2,2]
#[Out]# <OneDSpectrum [ 0., 0., 0.]>
get_ipython().magic(u'pinfo SpectralCube')
cube = SpectralCube(data=cube_array, wcs=cube_wcs, meta=dict(unit=u.K))
cube
#[Out]# SpectralCube with shape=(3, 4, 5):
#[Out]#  n_x: 5  type_x: RA        unit_x: deg
#[Out]#  n_y: 4  type_y: DEC       unit_y: deg
#[Out]#  n_s: 3  type_s: VELO      unit_s: m / s
cube = SpectralCube(data=cube_array, wcs=cube_wcs, meta=dict(BUNIT=u.K))
cube
#[Out]# SpectralCube with shape=(3, 4, 5) and unit=K:
#[Out]#  n_x: 5  type_x: RA        unit_x: deg
#[Out]#  n_y: 4  type_y: DEC       unit_y: deg
#[Out]#  n_s: 3  type_s: VELO      unit_s: m / s
cube = SpectralCube(data=cube_array*u.K, wcs=cube_wcs)
cube
#[Out]# SpectralCube with shape=(3, 4, 5) and unit=K:
#[Out]#  n_x: 5  type_x: RA        unit_x: deg
#[Out]#  n_y: 4  type_y: DEC       unit_y: deg
#[Out]#  n_s: 3  type_s: VELO      unit_s: m / s
cube.moment0(axis=0)
#[Out]# <Projection [[ 0., 0., 0., 0., 0.],
#[Out]#              [ 0., 0., 0., 0., 0.],
#[Out]#              [ 0., 0., 0., 0., 0.],
#[Out]#              [ 0., 0., 0., 0., 0.]] K m / s>
cube.moment0(axis=1)
#[Out]# <Projection [[ 0., 0., 0., 0., 0.],
#[Out]#              [ 0., 0., 0., 0., 0.],
#[Out]#              [ 0., 0., 0., 0., 0.]] deg K>
cube[:,2,2]
#[Out]# <OneDSpectrum [ 0., 0., 0.] K>
import numpy as np
from spectral_cube import SpectralCube
from astropy.wcs import WCS
from astropy import units as u
cube_array = np.zeros([3,4,5])
print(cube_array.shape, cube_array.size)
cube_wcs = WCS(naxis=3)
cube_wcs.wcs.ctype=['RA','DEC','VELO']
cube_wcs,cube_wcs.to_header()
#[Out]# (<astropy.wcs.wcs.WCS at 0x10e983e18>,
#[Out]#  WCSAXES =                    3 / Number of coordinate axes                      
#[Out]#  CRPIX1  =                  0.0 / Pixel coordinate of reference point            
#[Out]#  CRPIX2  =                  0.0 / Pixel coordinate of reference point            
#[Out]#  CRPIX3  =                  0.0 / Pixel coordinate of reference point            
#[Out]#  CDELT1  =                  1.0 / [deg] Coordinate increment at reference point  
#[Out]#  CDELT2  =                  1.0 / [deg] Coordinate increment at reference point  
#[Out]#  CDELT3  =                  1.0 / [m/s] Coordinate increment at reference point  
#[Out]#  CUNIT1  = 'deg'                / Units of coordinate increment and value        
#[Out]#  CUNIT2  = 'deg'                / Units of coordinate increment and value        
#[Out]#  CUNIT3  = 'm/s'                / Units of coordinate increment and value        
#[Out]#  CTYPE1  = 'RA'                 / Coordinate type codeundefined projection       
#[Out]#  CTYPE2  = 'DEC'                / Coordinate type codeundefined projection       
#[Out]#  CTYPE3  = 'VELO'               / Relativistic velocity (linear)                 
#[Out]#  CRVAL1  =                  0.0 / [deg] Coordinate value at reference point      
#[Out]#  CRVAL2  =                  0.0 / [deg] Coordinate value at reference point      
#[Out]#  CRVAL3  =                  0.0 / [m/s] Coordinate value at reference point      
#[Out]#  LATPOLE =                 90.0 / [deg] Native latitude of celestial pole        
#[Out]#  RADESYS = 'ICRS'               / Equatorial coordinate system                   )
cube = SpectralCube(data=cube_array*u.K, wcs=cube_wcs)
cube
#[Out]# SpectralCube with shape=(3, 4, 5) and unit=K:
#[Out]#  n_x: 5  type_x: RA        unit_x: deg
#[Out]#  n_y: 4  type_y: DEC       unit_y: deg
#[Out]#  n_s: 3  type_s: VELO      unit_s: m / s
cube.moment0(axis=0)
#[Out]# <Projection [[ 0., 0., 0., 0., 0.],
#[Out]#              [ 0., 0., 0., 0., 0.],
#[Out]#              [ 0., 0., 0., 0., 0.],
#[Out]#              [ 0., 0., 0., 0., 0.]] K m / s>
cube.moment0(axis=1)
#[Out]# <Projection [[ 0., 0., 0., 0., 0.],
#[Out]#              [ 0., 0., 0., 0., 0.],
#[Out]#              [ 0., 0., 0., 0., 0.]] deg K>
cube[:,2,2]
#[Out]# <OneDSpectrum [ 0., 0., 0.] K>
from pyspeckit.cubes.cubes import baseline_cube
baseline_cube(cube)
baseline_cube(cube[:])
baseline_cube(cube[...])
baseline_cube(cube.filled_data[:])
baseline_cube(cube.filled_data[:], polyorder=1)
#[Out]# array([[[ 0.,  0.,  0.,  0.,  0.],
#[Out]#         [ 0.,  0.,  0.,  0.,  0.],
#[Out]#         [ 0.,  0.,  0.,  0.,  0.],
#[Out]#         [ 0.,  0.,  0.,  0.,  0.]],
#[Out]# 
#[Out]#        [[ 0.,  0.,  0.,  0.,  0.],
#[Out]#         [ 0.,  0.,  0.,  0.,  0.],
#[Out]#         [ 0.,  0.,  0.,  0.,  0.],
#[Out]#         [ 0.,  0.,  0.,  0.,  0.]],
#[Out]# 
#[Out]#        [[ 0.,  0.,  0.,  0.,  0.],
#[Out]#         [ 0.,  0.,  0.,  0.,  0.],
#[Out]#         [ 0.,  0.,  0.,  0.,  0.],
#[Out]#         [ 0.,  0.,  0.,  0.,  0.]]])
wiggles = np.polyval(np.linspace(0,1), [1,1,1])
x = np.linspace(0,1)
wiggles = np.polyval(x, [1,1,1])
pl.plot(x,wiggles)
import pylab as pl
x = np.linspace(0,1)
wiggles = np.polyval(x, [1,1,1])
pl.plot(x,wiggles)
x = np.linspace(0,1)
wiggles = np.polyval([1,1,1],x)
pl.plot(x,wiggles)
#[Out]# [<matplotlib.lines.Line2D at 0x1127281d0>]
x = np.linspace(0,1)
wiggles = np.polyval([1,-1,1],x)
pl.plot(x,wiggles)
#[Out]# [<matplotlib.lines.Line2D at 0x113034a10>]
x = np.linspace(0,1)
wiggles = np.polyval([-1, 1,-1,1],x)
pl.plot(x,wiggles)
#[Out]# [<matplotlib.lines.Line2D at 0x11314a790>]
x = np.linspace(0,1)
wiggles = np.polyval([-1, 2,-1,1],x)
pl.plot(x,wiggles)
#[Out]# [<matplotlib.lines.Line2D at 0x113218dd0>]
np.repeat(wiggles,[5,3])
np.tile([1,2,3],[3,4,5])
#[Out]# array([[[1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3],
#[Out]#         [1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3],
#[Out]#         [1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3],
#[Out]#         [1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3]],
#[Out]# 
#[Out]#        [[1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3],
#[Out]#         [1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3],
#[Out]#         [1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3],
#[Out]#         [1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3]],
#[Out]# 
#[Out]#        [[1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3],
#[Out]#         [1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3],
#[Out]#         [1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3],
#[Out]#         [1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3]]])
np.tile([1,2,3],[5,4,3])
#[Out]# array([[[1, 2, 3, 1, 2, 3, 1, 2, 3],
#[Out]#         [1, 2, 3, 1, 2, 3, 1, 2, 3],
#[Out]#         [1, 2, 3, 1, 2, 3, 1, 2, 3],
#[Out]#         [1, 2, 3, 1, 2, 3, 1, 2, 3]],
#[Out]# 
#[Out]#        [[1, 2, 3, 1, 2, 3, 1, 2, 3],
#[Out]#         [1, 2, 3, 1, 2, 3, 1, 2, 3],
#[Out]#         [1, 2, 3, 1, 2, 3, 1, 2, 3],
#[Out]#         [1, 2, 3, 1, 2, 3, 1, 2, 3]],
#[Out]# 
#[Out]#        [[1, 2, 3, 1, 2, 3, 1, 2, 3],
#[Out]#         [1, 2, 3, 1, 2, 3, 1, 2, 3],
#[Out]#         [1, 2, 3, 1, 2, 3, 1, 2, 3],
#[Out]#         [1, 2, 3, 1, 2, 3, 1, 2, 3]],
#[Out]# 
#[Out]#        [[1, 2, 3, 1, 2, 3, 1, 2, 3],
#[Out]#         [1, 2, 3, 1, 2, 3, 1, 2, 3],
#[Out]#         [1, 2, 3, 1, 2, 3, 1, 2, 3],
#[Out]#         [1, 2, 3, 1, 2, 3, 1, 2, 3]],
#[Out]# 
#[Out]#        [[1, 2, 3, 1, 2, 3, 1, 2, 3],
#[Out]#         [1, 2, 3, 1, 2, 3, 1, 2, 3],
#[Out]#         [1, 2, 3, 1, 2, 3, 1, 2, 3],
#[Out]#         [1, 2, 3, 1, 2, 3, 1, 2, 3]]])
np.tile([1,2,3],[5,4,3]).shape
#[Out]# (5, 4, 9)
np.tile([1,2,3],[5,4,1]).shape
#[Out]# (5, 4, 3)
np.tile([1,2,3],[5,4,1])
#[Out]# array([[[1, 2, 3],
#[Out]#         [1, 2, 3],
#[Out]#         [1, 2, 3],
#[Out]#         [1, 2, 3]],
#[Out]# 
#[Out]#        [[1, 2, 3],
#[Out]#         [1, 2, 3],
#[Out]#         [1, 2, 3],
#[Out]#         [1, 2, 3]],
#[Out]# 
#[Out]#        [[1, 2, 3],
#[Out]#         [1, 2, 3],
#[Out]#         [1, 2, 3],
#[Out]#         [1, 2, 3]],
#[Out]# 
#[Out]#        [[1, 2, 3],
#[Out]#         [1, 2, 3],
#[Out]#         [1, 2, 3],
#[Out]#         [1, 2, 3]],
#[Out]# 
#[Out]#        [[1, 2, 3],
#[Out]#         [1, 2, 3],
#[Out]#         [1, 2, 3],
#[Out]#         [1, 2, 3]]])
wiggle_cube = SpectralCube(data=np.tile(wiggles,[5,3,1])*u.K, wcs=cube_wcs)
wiggle_cube = SpectralCube(data=np.tile(wiggles,[5,3,1])*u.K, wcs=cube_wcs)
wiggle_cube = SpectralCube(data=np.tile(wiggles,[5,3,1])*u.K, wcs=cube_wcs)
wiggle_cube
#[Out]# SpectralCube with shape=(5, 3, 50) and unit=K:
#[Out]#  n_x: 50  type_x: RA        unit_x: deg
#[Out]#  n_y: 3  type_y: DEC       unit_y: deg
#[Out]#  n_s: 5  type_s: VELO      unit_s: m / s
wiggle_cube = SpectralCube(data=np.tile(wiggles,[5,3,1]).T*u.K, wcs=cube_wcs)
wiggle_cube
#[Out]# SpectralCube with shape=(50, 3, 5) and unit=K:
#[Out]#  n_x: 5  type_x: RA        unit_x: deg
#[Out]#  n_y: 3  type_y: DEC       unit_y: deg
#[Out]#  n_s: 50  type_s: VELO      unit_s: m / s
wiggle_cube.moment0(axis=0).quicklook()
wiggle_cube.moment0(axis=1).quicklook()
wiggle_cube[:,0,0].quicklook()
wiggle_cube[:,0,0].quicklook()
wiggle_cube[0,:,0].quicklook()
wiggle_cube[:,0,0].quicklook()
wiggle_cube[:,0,0].quicklook()
baseline_cube(wiggle_cube.filled_data[:], polyorder=1)
#[Out]# array([[[ 0.12861308,  0.12861308,  0.12861308,  0.12861308,  0.12861308],
#[Out]#         [ 0.12861308,  0.12861308,  0.12861308,  0.12861308,  0.12861308],
#[Out]#         [ 0.12861308,  0.12861308,  0.12861308,  0.12861308,  0.12861308]],
#[Out]# 
#[Out]#        [[ 0.10711183,  0.10711183,  0.10711183,  0.10711183,  0.10711183],
#[Out]#         [ 0.10711183,  0.10711183,  0.10711183,  0.10711183,  0.10711183],
#[Out]#         [ 0.10711183,  0.10711183,  0.10711183,  0.10711183,  0.10711183]],
#[Out]# 
#[Out]#        [[ 0.08722556,  0.08722556,  0.08722556,  0.08722556,  0.08722556],
#[Out]#         [ 0.08722556,  0.08722556,  0.08722556,  0.08722556,  0.08722556],
#[Out]#         [ 0.08722556,  0.08722556,  0.08722556,  0.08722556,  0.08722556]],
#[Out]# 
#[Out]#        [[ 0.06890326,  0.06890326,  0.06890326,  0.06890326,  0.06890326],
#[Out]#         [ 0.06890326,  0.06890326,  0.06890326,  0.06890326,  0.06890326],
#[Out]#         [ 0.06890326,  0.06890326,  0.06890326,  0.06890326,  0.06890326]],
#[Out]# 
#[Out]#        [[ 0.05209394,  0.05209394,  0.05209394,  0.05209394,  0.05209394],
#[Out]#         [ 0.05209394,  0.05209394,  0.05209394,  0.05209394,  0.05209394],
#[Out]#         [ 0.05209394,  0.05209394,  0.05209394,  0.05209394,  0.05209394]],
#[Out]# 
#[Out]#        [[ 0.03674659,  0.03674659,  0.03674659,  0.03674659,  0.03674659],
#[Out]#         [ 0.03674659,  0.03674659,  0.03674659,  0.03674659,  0.03674659],
#[Out]#         [ 0.03674659,  0.03674659,  0.03674659,  0.03674659,  0.03674659]],
#[Out]# 
#[Out]#        [[ 0.02281022,  0.02281022,  0.02281022,  0.02281022,  0.02281022],
#[Out]#         [ 0.02281022,  0.02281022,  0.02281022,  0.02281022,  0.02281022],
#[Out]#         [ 0.02281022,  0.02281022,  0.02281022,  0.02281022,  0.02281022]],
#[Out]# 
#[Out]#        [[ 0.01023383,  0.01023383,  0.01023383,  0.01023383,  0.01023383],
#[Out]#         [ 0.01023383,  0.01023383,  0.01023383,  0.01023383,  0.01023383],
#[Out]#         [ 0.01023383,  0.01023383,  0.01023383,  0.01023383,  0.01023383]],
#[Out]# 
#[Out]#        [[-0.00103358, -0.00103358, -0.00103358, -0.00103358, -0.00103358],
#[Out]#         [-0.00103358, -0.00103358, -0.00103358, -0.00103358, -0.00103358],
#[Out]#         [-0.00103358, -0.00103358, -0.00103358, -0.00103358, -0.00103358]],
#[Out]# 
#[Out]#        [[-0.01104302, -0.01104302, -0.01104302, -0.01104302, -0.01104302],
#[Out]#         [-0.01104302, -0.01104302, -0.01104302, -0.01104302, -0.01104302],
#[Out]#         [-0.01104302, -0.01104302, -0.01104302, -0.01104302, -0.01104302]],
#[Out]# 
#[Out]#        [[-0.01984547, -0.01984547, -0.01984547, -0.01984547, -0.01984547],
#[Out]#         [-0.01984547, -0.01984547, -0.01984547, -0.01984547, -0.01984547],
#[Out]#         [-0.01984547, -0.01984547, -0.01984547, -0.01984547, -0.01984547]],
#[Out]# 
#[Out]#        [[-0.02749195, -0.02749195, -0.02749195, -0.02749195, -0.02749195],
#[Out]#         [-0.02749195, -0.02749195, -0.02749195, -0.02749195, -0.02749195],
#[Out]#         [-0.02749195, -0.02749195, -0.02749195, -0.02749195, -0.02749195]],
#[Out]# 
#[Out]#        [[-0.03403344, -0.03403344, -0.03403344, -0.03403344, -0.03403344],
#[Out]#         [-0.03403344, -0.03403344, -0.03403344, -0.03403344, -0.03403344],
#[Out]#         [-0.03403344, -0.03403344, -0.03403344, -0.03403344, -0.03403344]],
#[Out]# 
#[Out]#        [[-0.03952095, -0.03952095, -0.03952095, -0.03952095, -0.03952095],
#[Out]#         [-0.03952095, -0.03952095, -0.03952095, -0.03952095, -0.03952095],
#[Out]#         [-0.03952095, -0.03952095, -0.03952095, -0.03952095, -0.03952095]],
#[Out]# 
#[Out]#        [[-0.04400547, -0.04400547, -0.04400547, -0.04400547, -0.04400547],
#[Out]#         [-0.04400547, -0.04400547, -0.04400547, -0.04400547, -0.04400547],
#[Out]#         [-0.04400547, -0.04400547, -0.04400547, -0.04400547, -0.04400547]],
#[Out]# 
#[Out]#        [[-0.04753802, -0.04753802, -0.04753802, -0.04753802, -0.04753802],
#[Out]#         [-0.04753802, -0.04753802, -0.04753802, -0.04753802, -0.04753802],
#[Out]#         [-0.04753802, -0.04753802, -0.04753802, -0.04753802, -0.04753802]],
#[Out]# 
#[Out]#        [[-0.05016957, -0.05016957, -0.05016957, -0.05016957, -0.05016957],
#[Out]#         [-0.05016957, -0.05016957, -0.05016957, -0.05016957, -0.05016957],
#[Out]#         [-0.05016957, -0.05016957, -0.05016957, -0.05016957, -0.05016957]],
#[Out]# 
#[Out]#        [[-0.05195114, -0.05195114, -0.05195114, -0.05195114, -0.05195114],
#[Out]#         [-0.05195114, -0.05195114, -0.05195114, -0.05195114, -0.05195114],
#[Out]#         [-0.05195114, -0.05195114, -0.05195114, -0.05195114, -0.05195114]],
#[Out]# 
#[Out]#        [[-0.05293373, -0.05293373, -0.05293373, -0.05293373, -0.05293373],
#[Out]#         [-0.05293373, -0.05293373, -0.05293373, -0.05293373, -0.05293373],
#[Out]#         [-0.05293373, -0.05293373, -0.05293373, -0.05293373, -0.05293373]],
#[Out]# 
#[Out]#        [[-0.05316832, -0.05316832, -0.05316832, -0.05316832, -0.05316832],
#[Out]#         [-0.05316832, -0.05316832, -0.05316832, -0.05316832, -0.05316832],
#[Out]#         [-0.05316832, -0.05316832, -0.05316832, -0.05316832, -0.05316832]],
#[Out]# 
#[Out]#        [[-0.05270593, -0.05270593, -0.05270593, -0.05270593, -0.05270593],
#[Out]#         [-0.05270593, -0.05270593, -0.05270593, -0.05270593, -0.05270593],
#[Out]#         [-0.05270593, -0.05270593, -0.05270593, -0.05270593, -0.05270593]],
#[Out]# 
#[Out]#        [[-0.05159755, -0.05159755, -0.05159755, -0.05159755, -0.05159755],
#[Out]#         [-0.05159755, -0.05159755, -0.05159755, -0.05159755, -0.05159755],
#[Out]#         [-0.05159755, -0.05159755, -0.05159755, -0.05159755, -0.05159755]],
#[Out]# 
#[Out]#        [[-0.04989418, -0.04989418, -0.04989418, -0.04989418, -0.04989418],
#[Out]#         [-0.04989418, -0.04989418, -0.04989418, -0.04989418, -0.04989418],
#[Out]#         [-0.04989418, -0.04989418, -0.04989418, -0.04989418, -0.04989418]],
#[Out]# 
#[Out]#        [[-0.04764681, -0.04764681, -0.04764681, -0.04764681, -0.04764681],
#[Out]#         [-0.04764681, -0.04764681, -0.04764681, -0.04764681, -0.04764681],
#[Out]#         [-0.04764681, -0.04764681, -0.04764681, -0.04764681, -0.04764681]],
#[Out]# 
#[Out]#        [[-0.04490646, -0.04490646, -0.04490646, -0.04490646, -0.04490646],
#[Out]#         [-0.04490646, -0.04490646, -0.04490646, -0.04490646, -0.04490646],
#[Out]#         [-0.04490646, -0.04490646, -0.04490646, -0.04490646, -0.04490646]],
#[Out]# 
#[Out]#        [[-0.04172411, -0.04172411, -0.04172411, -0.04172411, -0.04172411],
#[Out]#         [-0.04172411, -0.04172411, -0.04172411, -0.04172411, -0.04172411],
#[Out]#         [-0.04172411, -0.04172411, -0.04172411, -0.04172411, -0.04172411]],
#[Out]# 
#[Out]#        [[-0.03815077, -0.03815077, -0.03815077, -0.03815077, -0.03815077],
#[Out]#         [-0.03815077, -0.03815077, -0.03815077, -0.03815077, -0.03815077],
#[Out]#         [-0.03815077, -0.03815077, -0.03815077, -0.03815077, -0.03815077]],
#[Out]# 
#[Out]#        [[-0.03423744, -0.03423744, -0.03423744, -0.03423744, -0.03423744],
#[Out]#         [-0.03423744, -0.03423744, -0.03423744, -0.03423744, -0.03423744],
#[Out]#         [-0.03423744, -0.03423744, -0.03423744, -0.03423744, -0.03423744]],
#[Out]# 
#[Out]#        [[-0.0300351 , -0.0300351 , -0.0300351 , -0.0300351 , -0.0300351 ],
#[Out]#         [-0.0300351 , -0.0300351 , -0.0300351 , -0.0300351 , -0.0300351 ],
#[Out]#         [-0.0300351 , -0.0300351 , -0.0300351 , -0.0300351 , -0.0300351 ]],
#[Out]# 
#[Out]#        [[-0.02559478, -0.02559478, -0.02559478, -0.02559478, -0.02559478],
#[Out]#         [-0.02559478, -0.02559478, -0.02559478, -0.02559478, -0.02559478],
#[Out]#         [-0.02559478, -0.02559478, -0.02559478, -0.02559478, -0.02559478]],
#[Out]# 
#[Out]#        [[-0.02096745, -0.02096745, -0.02096745, -0.02096745, -0.02096745],
#[Out]#         [-0.02096745, -0.02096745, -0.02096745, -0.02096745, -0.02096745],
#[Out]#         [-0.02096745, -0.02096745, -0.02096745, -0.02096745, -0.02096745]],
#[Out]# 
#[Out]#        [[-0.01620413, -0.01620413, -0.01620413, -0.01620413, -0.01620413],
#[Out]#         [-0.01620413, -0.01620413, -0.01620413, -0.01620413, -0.01620413],
#[Out]#         [-0.01620413, -0.01620413, -0.01620413, -0.01620413, -0.01620413]],
#[Out]# 
#[Out]#        [[-0.01135581, -0.01135581, -0.01135581, -0.01135581, -0.01135581],
#[Out]#         [-0.01135581, -0.01135581, -0.01135581, -0.01135581, -0.01135581],
#[Out]#         [-0.01135581, -0.01135581, -0.01135581, -0.01135581, -0.01135581]],
#[Out]# 
#[Out]#        [[-0.00647349, -0.00647349, -0.00647349, -0.00647349, -0.00647349],
#[Out]#         [-0.00647349, -0.00647349, -0.00647349, -0.00647349, -0.00647349],
#[Out]#         [-0.00647349, -0.00647349, -0.00647349, -0.00647349, -0.00647349]],
#[Out]# 
#[Out]#        [[-0.00160817, -0.00160817, -0.00160817, -0.00160817, -0.00160817],
#[Out]#         [-0.00160817, -0.00160817, -0.00160817, -0.00160817, -0.00160817],
#[Out]#         [-0.00160817, -0.00160817, -0.00160817, -0.00160817, -0.00160817]],
#[Out]# 
#[Out]#        [[ 0.00318915,  0.00318915,  0.00318915,  0.00318915,  0.00318915],
#[Out]#         [ 0.00318915,  0.00318915,  0.00318915,  0.00318915,  0.00318915],
#[Out]#         [ 0.00318915,  0.00318915,  0.00318915,  0.00318915,  0.00318915]],
#[Out]# 
#[Out]#        [[ 0.00786747,  0.00786747,  0.00786747,  0.00786747,  0.00786747],
#[Out]#         [ 0.00786747,  0.00786747,  0.00786747,  0.00786747,  0.00786747],
#[Out]#         [ 0.00786747,  0.00786747,  0.00786747,  0.00786747,  0.00786747]],
#[Out]# 
#[Out]#        [[ 0.0123758 ,  0.0123758 ,  0.0123758 ,  0.0123758 ,  0.0123758 ],
#[Out]#         [ 0.0123758 ,  0.0123758 ,  0.0123758 ,  0.0123758 ,  0.0123758 ],
#[Out]#         [ 0.0123758 ,  0.0123758 ,  0.0123758 ,  0.0123758 ,  0.0123758 ]],
#[Out]# 
#[Out]#        [[ 0.01666313,  0.01666313,  0.01666313,  0.01666313,  0.01666313],
#[Out]#         [ 0.01666313,  0.01666313,  0.01666313,  0.01666313,  0.01666313],
#[Out]#         [ 0.01666313,  0.01666313,  0.01666313,  0.01666313,  0.01666313]],
#[Out]# 
#[Out]#        [[ 0.02067846,  0.02067846,  0.02067846,  0.02067846,  0.02067846],
#[Out]#         [ 0.02067846,  0.02067846,  0.02067846,  0.02067846,  0.02067846],
#[Out]#         [ 0.02067846,  0.02067846,  0.02067846,  0.02067846,  0.02067846]],
#[Out]# 
#[Out]#        [[ 0.0243708 ,  0.0243708 ,  0.0243708 ,  0.0243708 ,  0.0243708 ],
#[Out]#         [ 0.0243708 ,  0.0243708 ,  0.0243708 ,  0.0243708 ,  0.0243708 ],
#[Out]#         [ 0.0243708 ,  0.0243708 ,  0.0243708 ,  0.0243708 ,  0.0243708 ]],
#[Out]# 
#[Out]#        [[ 0.02768914,  0.02768914,  0.02768914,  0.02768914,  0.02768914],
#[Out]#         [ 0.02768914,  0.02768914,  0.02768914,  0.02768914,  0.02768914],
#[Out]#         [ 0.02768914,  0.02768914,  0.02768914,  0.02768914,  0.02768914]],
#[Out]# 
#[Out]#        [[ 0.0305825 ,  0.0305825 ,  0.0305825 ,  0.0305825 ,  0.0305825 ],
#[Out]#         [ 0.0305825 ,  0.0305825 ,  0.0305825 ,  0.0305825 ,  0.0305825 ],
#[Out]#         [ 0.0305825 ,  0.0305825 ,  0.0305825 ,  0.0305825 ,  0.0305825 ]],
#[Out]# 
#[Out]#        [[ 0.03299986,  0.03299986,  0.03299986,  0.03299986,  0.03299986],
#[Out]#         [ 0.03299986,  0.03299986,  0.03299986,  0.03299986,  0.03299986],
#[Out]#         [ 0.03299986,  0.03299986,  0.03299986,  0.03299986,  0.03299986]],
#[Out]# 
#[Out]#        [[ 0.03489022,  0.03489022,  0.03489022,  0.03489022,  0.03489022],
#[Out]#         [ 0.03489022,  0.03489022,  0.03489022,  0.03489022,  0.03489022],
#[Out]#         [ 0.03489022,  0.03489022,  0.03489022,  0.03489022,  0.03489022]],
#[Out]# 
#[Out]#        [[ 0.0362026 ,  0.0362026 ,  0.0362026 ,  0.0362026 ,  0.0362026 ],
#[Out]#         [ 0.0362026 ,  0.0362026 ,  0.0362026 ,  0.0362026 ,  0.0362026 ],
#[Out]#         [ 0.0362026 ,  0.0362026 ,  0.0362026 ,  0.0362026 ,  0.0362026 ]],
#[Out]# 
#[Out]#        [[ 0.03688599,  0.03688599,  0.03688599,  0.03688599,  0.03688599],
#[Out]#         [ 0.03688599,  0.03688599,  0.03688599,  0.03688599,  0.03688599],
#[Out]#         [ 0.03688599,  0.03688599,  0.03688599,  0.03688599,  0.03688599]],
#[Out]# 
#[Out]#        [[ 0.03688939,  0.03688939,  0.03688939,  0.03688939,  0.03688939],
#[Out]#         [ 0.03688939,  0.03688939,  0.03688939,  0.03688939,  0.03688939],
#[Out]#         [ 0.03688939,  0.03688939,  0.03688939,  0.03688939,  0.03688939]],
#[Out]# 
#[Out]#        [[ 0.0361618 ,  0.0361618 ,  0.0361618 ,  0.0361618 ,  0.0361618 ],
#[Out]#         [ 0.0361618 ,  0.0361618 ,  0.0361618 ,  0.0361618 ,  0.0361618 ],
#[Out]#         [ 0.0361618 ,  0.0361618 ,  0.0361618 ,  0.0361618 ,  0.0361618 ]],
#[Out]# 
#[Out]#        [[ 0.03465223,  0.03465223,  0.03465223,  0.03465223,  0.03465223],
#[Out]#         [ 0.03465223,  0.03465223,  0.03465223,  0.03465223,  0.03465223],
#[Out]#         [ 0.03465223,  0.03465223,  0.03465223,  0.03465223,  0.03465223]]])
baseline_cube(wiggle_cube.filled_data[:], polyorder=2)
#[Out]# array([[[ 0.04698042,  0.04698042,  0.04698042,  0.04698042,  0.04698042],
#[Out]#         [ 0.04698042,  0.04698042,  0.04698042,  0.04698042,  0.04698042],
#[Out]#         [ 0.04698042,  0.04698042,  0.04698042,  0.04698042,  0.04698042]],
#[Out]# 
#[Out]#        [[ 0.03547501,  0.03547501,  0.03547501,  0.03547501,  0.03547501],
#[Out]#         [ 0.03547501,  0.03547501,  0.03547501,  0.03547501,  0.03547501],
#[Out]#         [ 0.03547501,  0.03547501,  0.03547501,  0.03547501,  0.03547501]],
#[Out]# 
#[Out]#        [[ 0.02516808,  0.02516808,  0.02516808,  0.02516808,  0.02516808],
#[Out]#         [ 0.02516808,  0.02516808,  0.02516808,  0.02516808,  0.02516808],
#[Out]#         [ 0.02516808,  0.02516808,  0.02516808,  0.02516808,  0.02516808]],
#[Out]# 
#[Out]#        [[ 0.01600864,  0.01600864,  0.01600864,  0.01600864,  0.01600864],
#[Out]#         [ 0.01600864,  0.01600864,  0.01600864,  0.01600864,  0.01600864],
#[Out]#         [ 0.01600864,  0.01600864,  0.01600864,  0.01600864,  0.01600864]],
#[Out]# 
#[Out]#        [[ 0.00794567,  0.00794567,  0.00794567,  0.00794567,  0.00794567],
#[Out]#         [ 0.00794567,  0.00794567,  0.00794567,  0.00794567,  0.00794567],
#[Out]#         [ 0.00794567,  0.00794567,  0.00794567,  0.00794567,  0.00794567]],
#[Out]# 
#[Out]#        [[ 0.00092818,  0.00092818,  0.00092818,  0.00092818,  0.00092818],
#[Out]#         [ 0.00092818,  0.00092818,  0.00092818,  0.00092818,  0.00092818],
#[Out]#         [ 0.00092818,  0.00092818,  0.00092818,  0.00092818,  0.00092818]],
#[Out]# 
#[Out]#        [[-0.00509482, -0.00509482, -0.00509482, -0.00509482, -0.00509482],
#[Out]#         [-0.00509482, -0.00509482, -0.00509482, -0.00509482, -0.00509482],
#[Out]#         [-0.00509482, -0.00509482, -0.00509482, -0.00509482, -0.00509482]],
#[Out]# 
#[Out]#        [[-0.01017433, -0.01017433, -0.01017433, -0.01017433, -0.01017433],
#[Out]#         [-0.01017433, -0.01017433, -0.01017433, -0.01017433, -0.01017433],
#[Out]#         [-0.01017433, -0.01017433, -0.01017433, -0.01017433, -0.01017433]],
#[Out]# 
#[Out]#        [[-0.01436136, -0.01436136, -0.01436136, -0.01436136, -0.01436136],
#[Out]#         [-0.01436136, -0.01436136, -0.01436136, -0.01436136, -0.01436136],
#[Out]#         [-0.01436136, -0.01436136, -0.01436136, -0.01436136, -0.01436136]],
#[Out]# 
#[Out]#        [[-0.01770691, -0.01770691, -0.01770691, -0.01770691, -0.01770691],
#[Out]#         [-0.01770691, -0.01770691, -0.01770691, -0.01770691, -0.01770691],
#[Out]#         [-0.01770691, -0.01770691, -0.01770691, -0.01770691, -0.01770691]],
#[Out]# 
#[Out]#        [[-0.02026197, -0.02026197, -0.02026197, -0.02026197, -0.02026197],
#[Out]#         [-0.02026197, -0.02026197, -0.02026197, -0.02026197, -0.02026197],
#[Out]#         [-0.02026197, -0.02026197, -0.02026197, -0.02026197, -0.02026197]],
#[Out]# 
#[Out]#        [[-0.02207754, -0.02207754, -0.02207754, -0.02207754, -0.02207754],
#[Out]#         [-0.02207754, -0.02207754, -0.02207754, -0.02207754, -0.02207754],
#[Out]#         [-0.02207754, -0.02207754, -0.02207754, -0.02207754, -0.02207754]],
#[Out]# 
#[Out]#        [[-0.02320462, -0.02320462, -0.02320462, -0.02320462, -0.02320462],
#[Out]#         [-0.02320462, -0.02320462, -0.02320462, -0.02320462, -0.02320462],
#[Out]#         [-0.02320462, -0.02320462, -0.02320462, -0.02320462, -0.02320462]],
#[Out]# 
#[Out]#        [[-0.02369421, -0.02369421, -0.02369421, -0.02369421, -0.02369421],
#[Out]#         [-0.02369421, -0.02369421, -0.02369421, -0.02369421, -0.02369421],
#[Out]#         [-0.02369421, -0.02369421, -0.02369421, -0.02369421, -0.02369421]],
#[Out]# 
#[Out]#        [[-0.02359731, -0.02359731, -0.02359731, -0.02359731, -0.02359731],
#[Out]#         [-0.02359731, -0.02359731, -0.02359731, -0.02359731, -0.02359731],
#[Out]#         [-0.02359731, -0.02359731, -0.02359731, -0.02359731, -0.02359731]],
#[Out]# 
#[Out]#        [[-0.02296492, -0.02296492, -0.02296492, -0.02296492, -0.02296492],
#[Out]#         [-0.02296492, -0.02296492, -0.02296492, -0.02296492, -0.02296492],
#[Out]#         [-0.02296492, -0.02296492, -0.02296492, -0.02296492, -0.02296492]],
#[Out]# 
#[Out]#        [[-0.02184804, -0.02184804, -0.02184804, -0.02184804, -0.02184804],
#[Out]#         [-0.02184804, -0.02184804, -0.02184804, -0.02184804, -0.02184804],
#[Out]#         [-0.02184804, -0.02184804, -0.02184804, -0.02184804, -0.02184804]],
#[Out]# 
#[Out]#        [[-0.02029767, -0.02029767, -0.02029767, -0.02029767, -0.02029767],
#[Out]#         [-0.02029767, -0.02029767, -0.02029767, -0.02029767, -0.02029767],
#[Out]#         [-0.02029767, -0.02029767, -0.02029767, -0.02029767, -0.02029767]],
#[Out]# 
#[Out]#        [[-0.0183648 , -0.0183648 , -0.0183648 , -0.0183648 , -0.0183648 ],
#[Out]#         [-0.0183648 , -0.0183648 , -0.0183648 , -0.0183648 , -0.0183648 ],
#[Out]#         [-0.0183648 , -0.0183648 , -0.0183648 , -0.0183648 , -0.0183648 ]],
#[Out]# 
#[Out]#        [[-0.01610043, -0.01610043, -0.01610043, -0.01610043, -0.01610043],
#[Out]#         [-0.01610043, -0.01610043, -0.01610043, -0.01610043, -0.01610043],
#[Out]#         [-0.01610043, -0.01610043, -0.01610043, -0.01610043, -0.01610043]],
#[Out]# 
#[Out]#        [[-0.01355558, -0.01355558, -0.01355558, -0.01355558, -0.01355558],
#[Out]#         [-0.01355558, -0.01355558, -0.01355558, -0.01355558, -0.01355558],
#[Out]#         [-0.01355558, -0.01355558, -0.01355558, -0.01355558, -0.01355558]],
#[Out]# 
#[Out]#        [[-0.01078122, -0.01078122, -0.01078122, -0.01078122, -0.01078122],
#[Out]#         [-0.01078122, -0.01078122, -0.01078122, -0.01078122, -0.01078122],
#[Out]#         [-0.01078122, -0.01078122, -0.01078122, -0.01078122, -0.01078122]],
#[Out]# 
#[Out]#        [[-0.00782837, -0.00782837, -0.00782837, -0.00782837, -0.00782837],
#[Out]#         [-0.00782837, -0.00782837, -0.00782837, -0.00782837, -0.00782837],
#[Out]#         [-0.00782837, -0.00782837, -0.00782837, -0.00782837, -0.00782837]],
#[Out]# 
#[Out]#        [[-0.00474802, -0.00474802, -0.00474802, -0.00474802, -0.00474802],
#[Out]#         [-0.00474802, -0.00474802, -0.00474802, -0.00474802, -0.00474802],
#[Out]#         [-0.00474802, -0.00474802, -0.00474802, -0.00474802, -0.00474802]],
#[Out]# 
#[Out]#        [[-0.00159117, -0.00159117, -0.00159117, -0.00159117, -0.00159117],
#[Out]#         [-0.00159117, -0.00159117, -0.00159117, -0.00159117, -0.00159117],
#[Out]#         [-0.00159117, -0.00159117, -0.00159117, -0.00159117, -0.00159117]],
#[Out]# 
#[Out]#        [[ 0.00159117,  0.00159117,  0.00159117,  0.00159117,  0.00159117],
#[Out]#         [ 0.00159117,  0.00159117,  0.00159117,  0.00159117,  0.00159117],
#[Out]#         [ 0.00159117,  0.00159117,  0.00159117,  0.00159117,  0.00159117]],
#[Out]# 
#[Out]#        [[ 0.00474802,  0.00474802,  0.00474802,  0.00474802,  0.00474802],
#[Out]#         [ 0.00474802,  0.00474802,  0.00474802,  0.00474802,  0.00474802],
#[Out]#         [ 0.00474802,  0.00474802,  0.00474802,  0.00474802,  0.00474802]],
#[Out]# 
#[Out]#        [[ 0.00782837,  0.00782837,  0.00782837,  0.00782837,  0.00782837],
#[Out]#         [ 0.00782837,  0.00782837,  0.00782837,  0.00782837,  0.00782837],
#[Out]#         [ 0.00782837,  0.00782837,  0.00782837,  0.00782837,  0.00782837]],
#[Out]# 
#[Out]#        [[ 0.01078122,  0.01078122,  0.01078122,  0.01078122,  0.01078122],
#[Out]#         [ 0.01078122,  0.01078122,  0.01078122,  0.01078122,  0.01078122],
#[Out]#         [ 0.01078122,  0.01078122,  0.01078122,  0.01078122,  0.01078122]],
#[Out]# 
#[Out]#        [[ 0.01355558,  0.01355558,  0.01355558,  0.01355558,  0.01355558],
#[Out]#         [ 0.01355558,  0.01355558,  0.01355558,  0.01355558,  0.01355558],
#[Out]#         [ 0.01355558,  0.01355558,  0.01355558,  0.01355558,  0.01355558]],
#[Out]# 
#[Out]#        [[ 0.01610043,  0.01610043,  0.01610043,  0.01610043,  0.01610043],
#[Out]#         [ 0.01610043,  0.01610043,  0.01610043,  0.01610043,  0.01610043],
#[Out]#         [ 0.01610043,  0.01610043,  0.01610043,  0.01610043,  0.01610043]],
#[Out]# 
#[Out]#        [[ 0.0183648 ,  0.0183648 ,  0.0183648 ,  0.0183648 ,  0.0183648 ],
#[Out]#         [ 0.0183648 ,  0.0183648 ,  0.0183648 ,  0.0183648 ,  0.0183648 ],
#[Out]#         [ 0.0183648 ,  0.0183648 ,  0.0183648 ,  0.0183648 ,  0.0183648 ]],
#[Out]# 
#[Out]#        [[ 0.02029767,  0.02029767,  0.02029767,  0.02029767,  0.02029767],
#[Out]#         [ 0.02029767,  0.02029767,  0.02029767,  0.02029767,  0.02029767],
#[Out]#         [ 0.02029767,  0.02029767,  0.02029767,  0.02029767,  0.02029767]],
#[Out]# 
#[Out]#        [[ 0.02184804,  0.02184804,  0.02184804,  0.02184804,  0.02184804],
#[Out]#         [ 0.02184804,  0.02184804,  0.02184804,  0.02184804,  0.02184804],
#[Out]#         [ 0.02184804,  0.02184804,  0.02184804,  0.02184804,  0.02184804]],
#[Out]# 
#[Out]#        [[ 0.02296492,  0.02296492,  0.02296492,  0.02296492,  0.02296492],
#[Out]#         [ 0.02296492,  0.02296492,  0.02296492,  0.02296492,  0.02296492],
#[Out]#         [ 0.02296492,  0.02296492,  0.02296492,  0.02296492,  0.02296492]],
#[Out]# 
#[Out]#        [[ 0.02359731,  0.02359731,  0.02359731,  0.02359731,  0.02359731],
#[Out]#         [ 0.02359731,  0.02359731,  0.02359731,  0.02359731,  0.02359731],
#[Out]#         [ 0.02359731,  0.02359731,  0.02359731,  0.02359731,  0.02359731]],
#[Out]# 
#[Out]#        [[ 0.02369421,  0.02369421,  0.02369421,  0.02369421,  0.02369421],
#[Out]#         [ 0.02369421,  0.02369421,  0.02369421,  0.02369421,  0.02369421],
#[Out]#         [ 0.02369421,  0.02369421,  0.02369421,  0.02369421,  0.02369421]],
#[Out]# 
#[Out]#        [[ 0.02320462,  0.02320462,  0.02320462,  0.02320462,  0.02320462],
#[Out]#         [ 0.02320462,  0.02320462,  0.02320462,  0.02320462,  0.02320462],
#[Out]#         [ 0.02320462,  0.02320462,  0.02320462,  0.02320462,  0.02320462]],
#[Out]# 
#[Out]#        [[ 0.02207754,  0.02207754,  0.02207754,  0.02207754,  0.02207754],
#[Out]#         [ 0.02207754,  0.02207754,  0.02207754,  0.02207754,  0.02207754],
#[Out]#         [ 0.02207754,  0.02207754,  0.02207754,  0.02207754,  0.02207754]],
#[Out]# 
#[Out]#        [[ 0.02026197,  0.02026197,  0.02026197,  0.02026197,  0.02026197],
#[Out]#         [ 0.02026197,  0.02026197,  0.02026197,  0.02026197,  0.02026197],
#[Out]#         [ 0.02026197,  0.02026197,  0.02026197,  0.02026197,  0.02026197]],
#[Out]# 
#[Out]#        [[ 0.01770691,  0.01770691,  0.01770691,  0.01770691,  0.01770691],
#[Out]#         [ 0.01770691,  0.01770691,  0.01770691,  0.01770691,  0.01770691],
#[Out]#         [ 0.01770691,  0.01770691,  0.01770691,  0.01770691,  0.01770691]],
#[Out]# 
#[Out]#        [[ 0.01436136,  0.01436136,  0.01436136,  0.01436136,  0.01436136],
#[Out]#         [ 0.01436136,  0.01436136,  0.01436136,  0.01436136,  0.01436136],
#[Out]#         [ 0.01436136,  0.01436136,  0.01436136,  0.01436136,  0.01436136]],
#[Out]# 
#[Out]#        [[ 0.01017433,  0.01017433,  0.01017433,  0.01017433,  0.01017433],
#[Out]#         [ 0.01017433,  0.01017433,  0.01017433,  0.01017433,  0.01017433],
#[Out]#         [ 0.01017433,  0.01017433,  0.01017433,  0.01017433,  0.01017433]],
#[Out]# 
#[Out]#        [[ 0.00509482,  0.00509482,  0.00509482,  0.00509482,  0.00509482],
#[Out]#         [ 0.00509482,  0.00509482,  0.00509482,  0.00509482,  0.00509482],
#[Out]#         [ 0.00509482,  0.00509482,  0.00509482,  0.00509482,  0.00509482]],
#[Out]# 
#[Out]#        [[-0.00092818, -0.00092818, -0.00092818, -0.00092818, -0.00092818],
#[Out]#         [-0.00092818, -0.00092818, -0.00092818, -0.00092818, -0.00092818],
#[Out]#         [-0.00092818, -0.00092818, -0.00092818, -0.00092818, -0.00092818]],
#[Out]# 
#[Out]#        [[-0.00794567, -0.00794567, -0.00794567, -0.00794567, -0.00794567],
#[Out]#         [-0.00794567, -0.00794567, -0.00794567, -0.00794567, -0.00794567],
#[Out]#         [-0.00794567, -0.00794567, -0.00794567, -0.00794567, -0.00794567]],
#[Out]# 
#[Out]#        [[-0.01600864, -0.01600864, -0.01600864, -0.01600864, -0.01600864],
#[Out]#         [-0.01600864, -0.01600864, -0.01600864, -0.01600864, -0.01600864],
#[Out]#         [-0.01600864, -0.01600864, -0.01600864, -0.01600864, -0.01600864]],
#[Out]# 
#[Out]#        [[-0.02516808, -0.02516808, -0.02516808, -0.02516808, -0.02516808],
#[Out]#         [-0.02516808, -0.02516808, -0.02516808, -0.02516808, -0.02516808],
#[Out]#         [-0.02516808, -0.02516808, -0.02516808, -0.02516808, -0.02516808]],
#[Out]# 
#[Out]#        [[-0.03547501, -0.03547501, -0.03547501, -0.03547501, -0.03547501],
#[Out]#         [-0.03547501, -0.03547501, -0.03547501, -0.03547501, -0.03547501],
#[Out]#         [-0.03547501, -0.03547501, -0.03547501, -0.03547501, -0.03547501]],
#[Out]# 
#[Out]#        [[-0.04698042, -0.04698042, -0.04698042, -0.04698042, -0.04698042],
#[Out]#         [-0.04698042, -0.04698042, -0.04698042, -0.04698042, -0.04698042],
#[Out]#         [-0.04698042, -0.04698042, -0.04698042, -0.04698042, -0.04698042]]])
result = baseline_cube(wiggle_cube.filled_data[:], polyorder=2)
pl.plot(result[:,0,0])
#[Out]# [<matplotlib.lines.Line2D at 0x114f3dad0>]
result_order1 = baseline_cube(wiggle_cube.filled_data[:], polyorder=1)
result_order2 = baseline_cube(wiggle_cube.filled_data[:], polyorder=2)
pl.plot(result1[:,0,0], 'b')
pl.plot(result1[:,0,0], 'r')
result_order1 = baseline_cube(wiggle_cube.filled_data[:], polyorder=1)
result_order2 = baseline_cube(wiggle_cube.filled_data[:], polyorder=2)
pl.plot(result_order1[:,0,0], 'b')
pl.plot(result_order2[:,0,0], 'r')
#[Out]# [<matplotlib.lines.Line2D at 0x11502a410>]
In principle, the polynomial fitting should be able to remove this structure...
result_order1 = baseline_cube(wiggle_cube.filled_data[:], polyorder=1)
result_order2 = baseline_cube(wiggle_cube.filled_data[:], polyorder=2)
result_order3 = baseline_cube(wiggle_cube.filled_data[:], polyorder=3)

pl.plot(result_order1[:,0,0], 'b')
pl.plot(result_order2[:,0,0], 'r')
pl.plot(result_order3[:,0,0], 'k')
#[Out]# [<matplotlib.lines.Line2D at 0x1151fc410>]
result_order3
#[Out]# array([[[ -4.44089210e-16,  -4.44089210e-16,  -4.44089210e-16,
#[Out]#           -4.44089210e-16,  -4.44089210e-16],
#[Out]#         [ -4.44089210e-16,  -4.44089210e-16,  -4.44089210e-16,
#[Out]#           -4.44089210e-16,  -4.44089210e-16],
#[Out]#         [ -4.44089210e-16,  -4.44089210e-16,  -4.44089210e-16,
#[Out]#           -4.44089210e-16,  -4.44089210e-16]],
#[Out]# 
#[Out]#        [[ -3.33066907e-16,  -3.33066907e-16,  -3.33066907e-16,
#[Out]#           -3.33066907e-16,  -3.33066907e-16],
#[Out]#         [ -3.33066907e-16,  -3.33066907e-16,  -3.33066907e-16,
#[Out]#           -3.33066907e-16,  -3.33066907e-16],
#[Out]#         [ -3.33066907e-16,  -3.33066907e-16,  -3.33066907e-16,
#[Out]#           -3.33066907e-16,  -3.33066907e-16]],
#[Out]# 
#[Out]#        [[ -2.22044605e-16,  -2.22044605e-16,  -2.22044605e-16,
#[Out]#           -2.22044605e-16,  -2.22044605e-16],
#[Out]#         [ -2.22044605e-16,  -2.22044605e-16,  -2.22044605e-16,
#[Out]#           -2.22044605e-16,  -2.22044605e-16],
#[Out]#         [ -2.22044605e-16,  -2.22044605e-16,  -2.22044605e-16,
#[Out]#           -2.22044605e-16,  -2.22044605e-16]],
#[Out]# 
#[Out]#        [[ -2.22044605e-16,  -2.22044605e-16,  -2.22044605e-16,
#[Out]#           -2.22044605e-16,  -2.22044605e-16],
#[Out]#         [ -2.22044605e-16,  -2.22044605e-16,  -2.22044605e-16,
#[Out]#           -2.22044605e-16,  -2.22044605e-16],
#[Out]#         [ -2.22044605e-16,  -2.22044605e-16,  -2.22044605e-16,
#[Out]#           -2.22044605e-16,  -2.22044605e-16]],
#[Out]# 
#[Out]#        [[ -1.11022302e-16,  -1.11022302e-16,  -1.11022302e-16,
#[Out]#           -1.11022302e-16,  -1.11022302e-16],
#[Out]#         [ -1.11022302e-16,  -1.11022302e-16,  -1.11022302e-16,
#[Out]#           -1.11022302e-16,  -1.11022302e-16],
#[Out]#         [ -1.11022302e-16,  -1.11022302e-16,  -1.11022302e-16,
#[Out]#           -1.11022302e-16,  -1.11022302e-16]],
#[Out]# 
#[Out]#        [[  0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
#[Out]#            0.00000000e+00,   0.00000000e+00],
#[Out]#         [  0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
#[Out]#            0.00000000e+00,   0.00000000e+00],
#[Out]#         [  0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
#[Out]#            0.00000000e+00,   0.00000000e+00]],
#[Out]# 
#[Out]#        [[  1.11022302e-16,   1.11022302e-16,   1.11022302e-16,
#[Out]#            1.11022302e-16,   1.11022302e-16],
#[Out]#         [  1.11022302e-16,   1.11022302e-16,   1.11022302e-16,
#[Out]#            1.11022302e-16,   1.11022302e-16],
#[Out]#         [  1.11022302e-16,   1.11022302e-16,   1.11022302e-16,
#[Out]#            1.11022302e-16,   1.11022302e-16]],
#[Out]# 
#[Out]#        [[  1.11022302e-16,   1.11022302e-16,   1.11022302e-16,
#[Out]#            1.11022302e-16,   1.11022302e-16],
#[Out]#         [  1.11022302e-16,   1.11022302e-16,   1.11022302e-16,
#[Out]#            1.11022302e-16,   1.11022302e-16],
#[Out]#         [  1.11022302e-16,   1.11022302e-16,   1.11022302e-16,
#[Out]#            1.11022302e-16,   1.11022302e-16]],
#[Out]# 
#[Out]#        [[  2.22044605e-16,   2.22044605e-16,   2.22044605e-16,
#[Out]#            2.22044605e-16,   2.22044605e-16],
#[Out]#         [  2.22044605e-16,   2.22044605e-16,   2.22044605e-16,
#[Out]#            2.22044605e-16,   2.22044605e-16],
#[Out]#         [  2.22044605e-16,   2.22044605e-16,   2.22044605e-16,
#[Out]#            2.22044605e-16,   2.22044605e-16]],
#[Out]# 
#[Out]#        [[  2.22044605e-16,   2.22044605e-16,   2.22044605e-16,
#[Out]#            2.22044605e-16,   2.22044605e-16],
#[Out]#         [  2.22044605e-16,   2.22044605e-16,   2.22044605e-16,
#[Out]#            2.22044605e-16,   2.22044605e-16],
#[Out]#         [  2.22044605e-16,   2.22044605e-16,   2.22044605e-16,
#[Out]#            2.22044605e-16,   2.22044605e-16]],
#[Out]# 
#[Out]#        [[  2.22044605e-16,   2.22044605e-16,   2.22044605e-16,
#[Out]#            2.22044605e-16,   2.22044605e-16],
#[Out]#         [  2.22044605e-16,   2.22044605e-16,   2.22044605e-16,
#[Out]#            2.22044605e-16,   2.22044605e-16],
#[Out]#         [  2.22044605e-16,   2.22044605e-16,   2.22044605e-16,
#[Out]#            2.22044605e-16,   2.22044605e-16]],
#[Out]# 
#[Out]#        [[  3.33066907e-16,   3.33066907e-16,   3.33066907e-16,
#[Out]#            3.33066907e-16,   3.33066907e-16],
#[Out]#         [  3.33066907e-16,   3.33066907e-16,   3.33066907e-16,
#[Out]#            3.33066907e-16,   3.33066907e-16],
#[Out]#         [  3.33066907e-16,   3.33066907e-16,   3.33066907e-16,
#[Out]#            3.33066907e-16,   3.33066907e-16]],
#[Out]# 
#[Out]#        [[  2.22044605e-16,   2.22044605e-16,   2.22044605e-16,
#[Out]#            2.22044605e-16,   2.22044605e-16],
#[Out]#         [  2.22044605e-16,   2.22044605e-16,   2.22044605e-16,
#[Out]#            2.22044605e-16,   2.22044605e-16],
#[Out]#         [  2.22044605e-16,   2.22044605e-16,   2.22044605e-16,
#[Out]#            2.22044605e-16,   2.22044605e-16]],
#[Out]# 
#[Out]#        [[  3.33066907e-16,   3.33066907e-16,   3.33066907e-16,
#[Out]#            3.33066907e-16,   3.33066907e-16],
#[Out]#         [  3.33066907e-16,   3.33066907e-16,   3.33066907e-16,
#[Out]#            3.33066907e-16,   3.33066907e-16],
#[Out]#         [  3.33066907e-16,   3.33066907e-16,   3.33066907e-16,
#[Out]#            3.33066907e-16,   3.33066907e-16]],
#[Out]# 
#[Out]#        [[  3.33066907e-16,   3.33066907e-16,   3.33066907e-16,
#[Out]#            3.33066907e-16,   3.33066907e-16],
#[Out]#         [  3.33066907e-16,   3.33066907e-16,   3.33066907e-16,
#[Out]#            3.33066907e-16,   3.33066907e-16],
#[Out]#         [  3.33066907e-16,   3.33066907e-16,   3.33066907e-16,
#[Out]#            3.33066907e-16,   3.33066907e-16]],
#[Out]# 
#[Out]#        [[  4.44089210e-16,   4.44089210e-16,   4.44089210e-16,
#[Out]#            4.44089210e-16,   4.44089210e-16],
#[Out]#         [  4.44089210e-16,   4.44089210e-16,   4.44089210e-16,
#[Out]#            4.44089210e-16,   4.44089210e-16],
#[Out]#         [  4.44089210e-16,   4.44089210e-16,   4.44089210e-16,
#[Out]#            4.44089210e-16,   4.44089210e-16]],
#[Out]# 
#[Out]#        [[  4.44089210e-16,   4.44089210e-16,   4.44089210e-16,
#[Out]#            4.44089210e-16,   4.44089210e-16],
#[Out]#         [  4.44089210e-16,   4.44089210e-16,   4.44089210e-16,
#[Out]#            4.44089210e-16,   4.44089210e-16],
#[Out]#         [  4.44089210e-16,   4.44089210e-16,   4.44089210e-16,
#[Out]#            4.44089210e-16,   4.44089210e-16]],
#[Out]# 
#[Out]#        [[  4.44089210e-16,   4.44089210e-16,   4.44089210e-16,
#[Out]#            4.44089210e-16,   4.44089210e-16],
#[Out]#         [  4.44089210e-16,   4.44089210e-16,   4.44089210e-16,
#[Out]#            4.44089210e-16,   4.44089210e-16],
#[Out]#         [  4.44089210e-16,   4.44089210e-16,   4.44089210e-16,
#[Out]#            4.44089210e-16,   4.44089210e-16]],
#[Out]# 
#[Out]#        [[  4.44089210e-16,   4.44089210e-16,   4.44089210e-16,
#[Out]#            4.44089210e-16,   4.44089210e-16],
#[Out]#         [  4.44089210e-16,   4.44089210e-16,   4.44089210e-16,
#[Out]#            4.44089210e-16,   4.44089210e-16],
#[Out]#         [  4.44089210e-16,   4.44089210e-16,   4.44089210e-16,
#[Out]#            4.44089210e-16,   4.44089210e-16]],
#[Out]# 
#[Out]#        [[  5.55111512e-16,   5.55111512e-16,   5.55111512e-16,
#[Out]#            5.55111512e-16,   5.55111512e-16],
#[Out]#         [  5.55111512e-16,   5.55111512e-16,   5.55111512e-16,
#[Out]#            5.55111512e-16,   5.55111512e-16],
#[Out]#         [  5.55111512e-16,   5.55111512e-16,   5.55111512e-16,
#[Out]#            5.55111512e-16,   5.55111512e-16]],
#[Out]# 
#[Out]#        [[  6.66133815e-16,   6.66133815e-16,   6.66133815e-16,
#[Out]#            6.66133815e-16,   6.66133815e-16],
#[Out]#         [  6.66133815e-16,   6.66133815e-16,   6.66133815e-16,
#[Out]#            6.66133815e-16,   6.66133815e-16],
#[Out]#         [  6.66133815e-16,   6.66133815e-16,   6.66133815e-16,
#[Out]#            6.66133815e-16,   6.66133815e-16]],
#[Out]# 
#[Out]#        [[  5.55111512e-16,   5.55111512e-16,   5.55111512e-16,
#[Out]#            5.55111512e-16,   5.55111512e-16],
#[Out]#         [  5.55111512e-16,   5.55111512e-16,   5.55111512e-16,
#[Out]#            5.55111512e-16,   5.55111512e-16],
#[Out]#         [  5.55111512e-16,   5.55111512e-16,   5.55111512e-16,
#[Out]#            5.55111512e-16,   5.55111512e-16]],
#[Out]# 
#[Out]#        [[  4.44089210e-16,   4.44089210e-16,   4.44089210e-16,
#[Out]#            4.44089210e-16,   4.44089210e-16],
#[Out]#         [  4.44089210e-16,   4.44089210e-16,   4.44089210e-16,
#[Out]#            4.44089210e-16,   4.44089210e-16],
#[Out]#         [  4.44089210e-16,   4.44089210e-16,   4.44089210e-16,
#[Out]#            4.44089210e-16,   4.44089210e-16]],
#[Out]# 
#[Out]#        [[  6.66133815e-16,   6.66133815e-16,   6.66133815e-16,
#[Out]#            6.66133815e-16,   6.66133815e-16],
#[Out]#         [  6.66133815e-16,   6.66133815e-16,   6.66133815e-16,
#[Out]#            6.66133815e-16,   6.66133815e-16],
#[Out]#         [  6.66133815e-16,   6.66133815e-16,   6.66133815e-16,
#[Out]#            6.66133815e-16,   6.66133815e-16]],
#[Out]# 
#[Out]#        [[  6.66133815e-16,   6.66133815e-16,   6.66133815e-16,
#[Out]#            6.66133815e-16,   6.66133815e-16],
#[Out]#         [  6.66133815e-16,   6.66133815e-16,   6.66133815e-16,
#[Out]#            6.66133815e-16,   6.66133815e-16],
#[Out]#         [  6.66133815e-16,   6.66133815e-16,   6.66133815e-16,
#[Out]#            6.66133815e-16,   6.66133815e-16]],
#[Out]# 
#[Out]#        [[  7.77156117e-16,   7.77156117e-16,   7.77156117e-16,
#[Out]#            7.77156117e-16,   7.77156117e-16],
#[Out]#         [  7.77156117e-16,   7.77156117e-16,   7.77156117e-16,
#[Out]#            7.77156117e-16,   7.77156117e-16],
#[Out]#         [  7.77156117e-16,   7.77156117e-16,   7.77156117e-16,
#[Out]#            7.77156117e-16,   7.77156117e-16]],
#[Out]# 
#[Out]#        [[  6.66133815e-16,   6.66133815e-16,   6.66133815e-16,
#[Out]#            6.66133815e-16,   6.66133815e-16],
#[Out]#         [  6.66133815e-16,   6.66133815e-16,   6.66133815e-16,
#[Out]#            6.66133815e-16,   6.66133815e-16],
#[Out]#         [  6.66133815e-16,   6.66133815e-16,   6.66133815e-16,
#[Out]#            6.66133815e-16,   6.66133815e-16]],
#[Out]# 
#[Out]#        [[  6.66133815e-16,   6.66133815e-16,   6.66133815e-16,
#[Out]#            6.66133815e-16,   6.66133815e-16],
#[Out]#         [  6.66133815e-16,   6.66133815e-16,   6.66133815e-16,
#[Out]#            6.66133815e-16,   6.66133815e-16],
#[Out]#         [  6.66133815e-16,   6.66133815e-16,   6.66133815e-16,
#[Out]#            6.66133815e-16,   6.66133815e-16]],
#[Out]# 
#[Out]#        [[  7.77156117e-16,   7.77156117e-16,   7.77156117e-16,
#[Out]#            7.77156117e-16,   7.77156117e-16],
#[Out]#         [  7.77156117e-16,   7.77156117e-16,   7.77156117e-16,
#[Out]#            7.77156117e-16,   7.77156117e-16],
#[Out]#         [  7.77156117e-16,   7.77156117e-16,   7.77156117e-16,
#[Out]#            7.77156117e-16,   7.77156117e-16]],
#[Out]# 
#[Out]#        [[  8.88178420e-16,   8.88178420e-16,   8.88178420e-16,
#[Out]#            8.88178420e-16,   8.88178420e-16],
#[Out]#         [  8.88178420e-16,   8.88178420e-16,   8.88178420e-16,
#[Out]#            8.88178420e-16,   8.88178420e-16],
#[Out]#         [  8.88178420e-16,   8.88178420e-16,   8.88178420e-16,
#[Out]#            8.88178420e-16,   8.88178420e-16]],
#[Out]# 
#[Out]#        [[  9.99200722e-16,   9.99200722e-16,   9.99200722e-16,
#[Out]#            9.99200722e-16,   9.99200722e-16],
#[Out]#         [  9.99200722e-16,   9.99200722e-16,   9.99200722e-16,
#[Out]#            9.99200722e-16,   9.99200722e-16],
#[Out]#         [  9.99200722e-16,   9.99200722e-16,   9.99200722e-16,
#[Out]#            9.99200722e-16,   9.99200722e-16]],
#[Out]# 
#[Out]#        [[  9.99200722e-16,   9.99200722e-16,   9.99200722e-16,
#[Out]#            9.99200722e-16,   9.99200722e-16],
#[Out]#         [  9.99200722e-16,   9.99200722e-16,   9.99200722e-16,
#[Out]#            9.99200722e-16,   9.99200722e-16],
#[Out]#         [  9.99200722e-16,   9.99200722e-16,   9.99200722e-16,
#[Out]#            9.99200722e-16,   9.99200722e-16]],
#[Out]# 
#[Out]#        [[  1.11022302e-15,   1.11022302e-15,   1.11022302e-15,
#[Out]#            1.11022302e-15,   1.11022302e-15],
#[Out]#         [  1.11022302e-15,   1.11022302e-15,   1.11022302e-15,
#[Out]#            1.11022302e-15,   1.11022302e-15],
#[Out]#         [  1.11022302e-15,   1.11022302e-15,   1.11022302e-15,
#[Out]#            1.11022302e-15,   1.11022302e-15]],
#[Out]# 
#[Out]#        [[  1.22124533e-15,   1.22124533e-15,   1.22124533e-15,
#[Out]#            1.22124533e-15,   1.22124533e-15],
#[Out]#         [  1.22124533e-15,   1.22124533e-15,   1.22124533e-15,
#[Out]#            1.22124533e-15,   1.22124533e-15],
#[Out]#         [  1.22124533e-15,   1.22124533e-15,   1.22124533e-15,
#[Out]#            1.22124533e-15,   1.22124533e-15]],
#[Out]# 
#[Out]#        [[  1.22124533e-15,   1.22124533e-15,   1.22124533e-15,
#[Out]#            1.22124533e-15,   1.22124533e-15],
#[Out]#         [  1.22124533e-15,   1.22124533e-15,   1.22124533e-15,
#[Out]#            1.22124533e-15,   1.22124533e-15],
#[Out]#         [  1.22124533e-15,   1.22124533e-15,   1.22124533e-15,
#[Out]#            1.22124533e-15,   1.22124533e-15]],
#[Out]# 
#[Out]#        [[  1.22124533e-15,   1.22124533e-15,   1.22124533e-15,
#[Out]#            1.22124533e-15,   1.22124533e-15],
#[Out]#         [  1.22124533e-15,   1.22124533e-15,   1.22124533e-15,
#[Out]#            1.22124533e-15,   1.22124533e-15],
#[Out]#         [  1.22124533e-15,   1.22124533e-15,   1.22124533e-15,
#[Out]#            1.22124533e-15,   1.22124533e-15]],
#[Out]# 
#[Out]#        [[  1.44328993e-15,   1.44328993e-15,   1.44328993e-15,
#[Out]#            1.44328993e-15,   1.44328993e-15],
#[Out]#         [  1.44328993e-15,   1.44328993e-15,   1.44328993e-15,
#[Out]#            1.44328993e-15,   1.44328993e-15],
#[Out]#         [  1.44328993e-15,   1.44328993e-15,   1.44328993e-15,
#[Out]#            1.44328993e-15,   1.44328993e-15]],
#[Out]# 
#[Out]#        [[  1.33226763e-15,   1.33226763e-15,   1.33226763e-15,
#[Out]#            1.33226763e-15,   1.33226763e-15],
#[Out]#         [  1.33226763e-15,   1.33226763e-15,   1.33226763e-15,
#[Out]#            1.33226763e-15,   1.33226763e-15],
#[Out]#         [  1.33226763e-15,   1.33226763e-15,   1.33226763e-15,
#[Out]#            1.33226763e-15,   1.33226763e-15]],
#[Out]# 
#[Out]#        [[  1.44328993e-15,   1.44328993e-15,   1.44328993e-15,
#[Out]#            1.44328993e-15,   1.44328993e-15],
#[Out]#         [  1.44328993e-15,   1.44328993e-15,   1.44328993e-15,
#[Out]#            1.44328993e-15,   1.44328993e-15],
#[Out]#         [  1.44328993e-15,   1.44328993e-15,   1.44328993e-15,
#[Out]#            1.44328993e-15,   1.44328993e-15]],
#[Out]# 
#[Out]#        [[  1.66533454e-15,   1.66533454e-15,   1.66533454e-15,
#[Out]#            1.66533454e-15,   1.66533454e-15],
#[Out]#         [  1.66533454e-15,   1.66533454e-15,   1.66533454e-15,
#[Out]#            1.66533454e-15,   1.66533454e-15],
#[Out]#         [  1.66533454e-15,   1.66533454e-15,   1.66533454e-15,
#[Out]#            1.66533454e-15,   1.66533454e-15]],
#[Out]# 
#[Out]#        [[  1.66533454e-15,   1.66533454e-15,   1.66533454e-15,
#[Out]#            1.66533454e-15,   1.66533454e-15],
#[Out]#         [  1.66533454e-15,   1.66533454e-15,   1.66533454e-15,
#[Out]#            1.66533454e-15,   1.66533454e-15],
#[Out]#         [  1.66533454e-15,   1.66533454e-15,   1.66533454e-15,
#[Out]#            1.66533454e-15,   1.66533454e-15]],
#[Out]# 
#[Out]#        [[  1.99840144e-15,   1.99840144e-15,   1.99840144e-15,
#[Out]#            1.99840144e-15,   1.99840144e-15],
#[Out]#         [  1.99840144e-15,   1.99840144e-15,   1.99840144e-15,
#[Out]#            1.99840144e-15,   1.99840144e-15],
#[Out]#         [  1.99840144e-15,   1.99840144e-15,   1.99840144e-15,
#[Out]#            1.99840144e-15,   1.99840144e-15]],
#[Out]# 
#[Out]#        [[  1.99840144e-15,   1.99840144e-15,   1.99840144e-15,
#[Out]#            1.99840144e-15,   1.99840144e-15],
#[Out]#         [  1.99840144e-15,   1.99840144e-15,   1.99840144e-15,
#[Out]#            1.99840144e-15,   1.99840144e-15],
#[Out]#         [  1.99840144e-15,   1.99840144e-15,   1.99840144e-15,
#[Out]#            1.99840144e-15,   1.99840144e-15]],
#[Out]# 
#[Out]#        [[  2.22044605e-15,   2.22044605e-15,   2.22044605e-15,
#[Out]#            2.22044605e-15,   2.22044605e-15],
#[Out]#         [  2.22044605e-15,   2.22044605e-15,   2.22044605e-15,
#[Out]#            2.22044605e-15,   2.22044605e-15],
#[Out]#         [  2.22044605e-15,   2.22044605e-15,   2.22044605e-15,
#[Out]#            2.22044605e-15,   2.22044605e-15]],
#[Out]# 
#[Out]#        [[  2.44249065e-15,   2.44249065e-15,   2.44249065e-15,
#[Out]#            2.44249065e-15,   2.44249065e-15],
#[Out]#         [  2.44249065e-15,   2.44249065e-15,   2.44249065e-15,
#[Out]#            2.44249065e-15,   2.44249065e-15],
#[Out]#         [  2.44249065e-15,   2.44249065e-15,   2.44249065e-15,
#[Out]#            2.44249065e-15,   2.44249065e-15]],
#[Out]# 
#[Out]#        [[  2.66453526e-15,   2.66453526e-15,   2.66453526e-15,
#[Out]#            2.66453526e-15,   2.66453526e-15],
#[Out]#         [  2.66453526e-15,   2.66453526e-15,   2.66453526e-15,
#[Out]#            2.66453526e-15,   2.66453526e-15],
#[Out]#         [  2.66453526e-15,   2.66453526e-15,   2.66453526e-15,
#[Out]#            2.66453526e-15,   2.66453526e-15]],
#[Out]# 
#[Out]#        [[  2.77555756e-15,   2.77555756e-15,   2.77555756e-15,
#[Out]#            2.77555756e-15,   2.77555756e-15],
#[Out]#         [  2.77555756e-15,   2.77555756e-15,   2.77555756e-15,
#[Out]#            2.77555756e-15,   2.77555756e-15],
#[Out]#         [  2.77555756e-15,   2.77555756e-15,   2.77555756e-15,
#[Out]#            2.77555756e-15,   2.77555756e-15]],
#[Out]# 
#[Out]#        [[  2.99760217e-15,   2.99760217e-15,   2.99760217e-15,
#[Out]#            2.99760217e-15,   2.99760217e-15],
#[Out]#         [  2.99760217e-15,   2.99760217e-15,   2.99760217e-15,
#[Out]#            2.99760217e-15,   2.99760217e-15],
#[Out]#         [  2.99760217e-15,   2.99760217e-15,   2.99760217e-15,
#[Out]#            2.99760217e-15,   2.99760217e-15]],
#[Out]# 
#[Out]#        [[  3.10862447e-15,   3.10862447e-15,   3.10862447e-15,
#[Out]#            3.10862447e-15,   3.10862447e-15],
#[Out]#         [  3.10862447e-15,   3.10862447e-15,   3.10862447e-15,
#[Out]#            3.10862447e-15,   3.10862447e-15],
#[Out]#         [  3.10862447e-15,   3.10862447e-15,   3.10862447e-15,
#[Out]#            3.10862447e-15,   3.10862447e-15]],
#[Out]# 
#[Out]#        [[  3.44169138e-15,   3.44169138e-15,   3.44169138e-15,
#[Out]#            3.44169138e-15,   3.44169138e-15],
#[Out]#         [  3.44169138e-15,   3.44169138e-15,   3.44169138e-15,
#[Out]#            3.44169138e-15,   3.44169138e-15],
#[Out]#         [  3.44169138e-15,   3.44169138e-15,   3.44169138e-15,
#[Out]#            3.44169138e-15,   3.44169138e-15]]])
np.testing.assert_allclose(result_order3, 0)
np.testing.assert_array_almost_equal_nulp(result_order3, 0)
get_ipython().magic(u'pinfo np.testing.assert_array_almost_equal_nulp')
(result_order3, 0)
#[Out]# (array([[[ -4.44089210e-16,  -4.44089210e-16,  -4.44089210e-16,
#[Out]#            -4.44089210e-16,  -4.44089210e-16],
#[Out]#          [ -4.44089210e-16,  -4.44089210e-16,  -4.44089210e-16,
#[Out]#            -4.44089210e-16,  -4.44089210e-16],
#[Out]#          [ -4.44089210e-16,  -4.44089210e-16,  -4.44089210e-16,
#[Out]#            -4.44089210e-16,  -4.44089210e-16]],
#[Out]#  
#[Out]#         [[ -3.33066907e-16,  -3.33066907e-16,  -3.33066907e-16,
#[Out]#            -3.33066907e-16,  -3.33066907e-16],
#[Out]#          [ -3.33066907e-16,  -3.33066907e-16,  -3.33066907e-16,
#[Out]#            -3.33066907e-16,  -3.33066907e-16],
#[Out]#          [ -3.33066907e-16,  -3.33066907e-16,  -3.33066907e-16,
#[Out]#            -3.33066907e-16,  -3.33066907e-16]],
#[Out]#  
#[Out]#         [[ -2.22044605e-16,  -2.22044605e-16,  -2.22044605e-16,
#[Out]#            -2.22044605e-16,  -2.22044605e-16],
#[Out]#          [ -2.22044605e-16,  -2.22044605e-16,  -2.22044605e-16,
#[Out]#            -2.22044605e-16,  -2.22044605e-16],
#[Out]#          [ -2.22044605e-16,  -2.22044605e-16,  -2.22044605e-16,
#[Out]#            -2.22044605e-16,  -2.22044605e-16]],
#[Out]#  
#[Out]#         [[ -2.22044605e-16,  -2.22044605e-16,  -2.22044605e-16,
#[Out]#            -2.22044605e-16,  -2.22044605e-16],
#[Out]#          [ -2.22044605e-16,  -2.22044605e-16,  -2.22044605e-16,
#[Out]#            -2.22044605e-16,  -2.22044605e-16],
#[Out]#          [ -2.22044605e-16,  -2.22044605e-16,  -2.22044605e-16,
#[Out]#            -2.22044605e-16,  -2.22044605e-16]],
#[Out]#  
#[Out]#         [[ -1.11022302e-16,  -1.11022302e-16,  -1.11022302e-16,
#[Out]#            -1.11022302e-16,  -1.11022302e-16],
#[Out]#          [ -1.11022302e-16,  -1.11022302e-16,  -1.11022302e-16,
#[Out]#            -1.11022302e-16,  -1.11022302e-16],
#[Out]#          [ -1.11022302e-16,  -1.11022302e-16,  -1.11022302e-16,
#[Out]#            -1.11022302e-16,  -1.11022302e-16]],
#[Out]#  
#[Out]#         [[  0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
#[Out]#             0.00000000e+00,   0.00000000e+00],
#[Out]#          [  0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
#[Out]#             0.00000000e+00,   0.00000000e+00],
#[Out]#          [  0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
#[Out]#             0.00000000e+00,   0.00000000e+00]],
#[Out]#  
#[Out]#         [[  1.11022302e-16,   1.11022302e-16,   1.11022302e-16,
#[Out]#             1.11022302e-16,   1.11022302e-16],
#[Out]#          [  1.11022302e-16,   1.11022302e-16,   1.11022302e-16,
#[Out]#             1.11022302e-16,   1.11022302e-16],
#[Out]#          [  1.11022302e-16,   1.11022302e-16,   1.11022302e-16,
#[Out]#             1.11022302e-16,   1.11022302e-16]],
#[Out]#  
#[Out]#         [[  1.11022302e-16,   1.11022302e-16,   1.11022302e-16,
#[Out]#             1.11022302e-16,   1.11022302e-16],
#[Out]#          [  1.11022302e-16,   1.11022302e-16,   1.11022302e-16,
#[Out]#             1.11022302e-16,   1.11022302e-16],
#[Out]#          [  1.11022302e-16,   1.11022302e-16,   1.11022302e-16,
#[Out]#             1.11022302e-16,   1.11022302e-16]],
#[Out]#  
#[Out]#         [[  2.22044605e-16,   2.22044605e-16,   2.22044605e-16,
#[Out]#             2.22044605e-16,   2.22044605e-16],
#[Out]#          [  2.22044605e-16,   2.22044605e-16,   2.22044605e-16,
#[Out]#             2.22044605e-16,   2.22044605e-16],
#[Out]#          [  2.22044605e-16,   2.22044605e-16,   2.22044605e-16,
#[Out]#             2.22044605e-16,   2.22044605e-16]],
#[Out]#  
#[Out]#         [[  2.22044605e-16,   2.22044605e-16,   2.22044605e-16,
#[Out]#             2.22044605e-16,   2.22044605e-16],
#[Out]#          [  2.22044605e-16,   2.22044605e-16,   2.22044605e-16,
#[Out]#             2.22044605e-16,   2.22044605e-16],
#[Out]#          [  2.22044605e-16,   2.22044605e-16,   2.22044605e-16,
#[Out]#             2.22044605e-16,   2.22044605e-16]],
#[Out]#  
#[Out]#         [[  2.22044605e-16,   2.22044605e-16,   2.22044605e-16,
#[Out]#             2.22044605e-16,   2.22044605e-16],
#[Out]#          [  2.22044605e-16,   2.22044605e-16,   2.22044605e-16,
#[Out]#             2.22044605e-16,   2.22044605e-16],
#[Out]#          [  2.22044605e-16,   2.22044605e-16,   2.22044605e-16,
#[Out]#             2.22044605e-16,   2.22044605e-16]],
#[Out]#  
#[Out]#         [[  3.33066907e-16,   3.33066907e-16,   3.33066907e-16,
#[Out]#             3.33066907e-16,   3.33066907e-16],
#[Out]#          [  3.33066907e-16,   3.33066907e-16,   3.33066907e-16,
#[Out]#             3.33066907e-16,   3.33066907e-16],
#[Out]#          [  3.33066907e-16,   3.33066907e-16,   3.33066907e-16,
#[Out]#             3.33066907e-16,   3.33066907e-16]],
#[Out]#  
#[Out]#         [[  2.22044605e-16,   2.22044605e-16,   2.22044605e-16,
#[Out]#             2.22044605e-16,   2.22044605e-16],
#[Out]#          [  2.22044605e-16,   2.22044605e-16,   2.22044605e-16,
#[Out]#             2.22044605e-16,   2.22044605e-16],
#[Out]#          [  2.22044605e-16,   2.22044605e-16,   2.22044605e-16,
#[Out]#             2.22044605e-16,   2.22044605e-16]],
#[Out]#  
#[Out]#         [[  3.33066907e-16,   3.33066907e-16,   3.33066907e-16,
#[Out]#             3.33066907e-16,   3.33066907e-16],
#[Out]#          [  3.33066907e-16,   3.33066907e-16,   3.33066907e-16,
#[Out]#             3.33066907e-16,   3.33066907e-16],
#[Out]#          [  3.33066907e-16,   3.33066907e-16,   3.33066907e-16,
#[Out]#             3.33066907e-16,   3.33066907e-16]],
#[Out]#  
#[Out]#         [[  3.33066907e-16,   3.33066907e-16,   3.33066907e-16,
#[Out]#             3.33066907e-16,   3.33066907e-16],
#[Out]#          [  3.33066907e-16,   3.33066907e-16,   3.33066907e-16,
#[Out]#             3.33066907e-16,   3.33066907e-16],
#[Out]#          [  3.33066907e-16,   3.33066907e-16,   3.33066907e-16,
#[Out]#             3.33066907e-16,   3.33066907e-16]],
#[Out]#  
#[Out]#         [[  4.44089210e-16,   4.44089210e-16,   4.44089210e-16,
#[Out]#             4.44089210e-16,   4.44089210e-16],
#[Out]#          [  4.44089210e-16,   4.44089210e-16,   4.44089210e-16,
#[Out]#             4.44089210e-16,   4.44089210e-16],
#[Out]#          [  4.44089210e-16,   4.44089210e-16,   4.44089210e-16,
#[Out]#             4.44089210e-16,   4.44089210e-16]],
#[Out]#  
#[Out]#         [[  4.44089210e-16,   4.44089210e-16,   4.44089210e-16,
#[Out]#             4.44089210e-16,   4.44089210e-16],
#[Out]#          [  4.44089210e-16,   4.44089210e-16,   4.44089210e-16,
#[Out]#             4.44089210e-16,   4.44089210e-16],
#[Out]#          [  4.44089210e-16,   4.44089210e-16,   4.44089210e-16,
#[Out]#             4.44089210e-16,   4.44089210e-16]],
#[Out]#  
#[Out]#         [[  4.44089210e-16,   4.44089210e-16,   4.44089210e-16,
#[Out]#             4.44089210e-16,   4.44089210e-16],
#[Out]#          [  4.44089210e-16,   4.44089210e-16,   4.44089210e-16,
#[Out]#             4.44089210e-16,   4.44089210e-16],
#[Out]#          [  4.44089210e-16,   4.44089210e-16,   4.44089210e-16,
#[Out]#             4.44089210e-16,   4.44089210e-16]],
#[Out]#  
#[Out]#         [[  4.44089210e-16,   4.44089210e-16,   4.44089210e-16,
#[Out]#             4.44089210e-16,   4.44089210e-16],
#[Out]#          [  4.44089210e-16,   4.44089210e-16,   4.44089210e-16,
#[Out]#             4.44089210e-16,   4.44089210e-16],
#[Out]#          [  4.44089210e-16,   4.44089210e-16,   4.44089210e-16,
#[Out]#             4.44089210e-16,   4.44089210e-16]],
#[Out]#  
#[Out]#         [[  5.55111512e-16,   5.55111512e-16,   5.55111512e-16,
#[Out]#             5.55111512e-16,   5.55111512e-16],
#[Out]#          [  5.55111512e-16,   5.55111512e-16,   5.55111512e-16,
#[Out]#             5.55111512e-16,   5.55111512e-16],
#[Out]#          [  5.55111512e-16,   5.55111512e-16,   5.55111512e-16,
#[Out]#             5.55111512e-16,   5.55111512e-16]],
#[Out]#  
#[Out]#         [[  6.66133815e-16,   6.66133815e-16,   6.66133815e-16,
#[Out]#             6.66133815e-16,   6.66133815e-16],
#[Out]#          [  6.66133815e-16,   6.66133815e-16,   6.66133815e-16,
#[Out]#             6.66133815e-16,   6.66133815e-16],
#[Out]#          [  6.66133815e-16,   6.66133815e-16,   6.66133815e-16,
#[Out]#             6.66133815e-16,   6.66133815e-16]],
#[Out]#  
#[Out]#         [[  5.55111512e-16,   5.55111512e-16,   5.55111512e-16,
#[Out]#             5.55111512e-16,   5.55111512e-16],
#[Out]#          [  5.55111512e-16,   5.55111512e-16,   5.55111512e-16,
#[Out]#             5.55111512e-16,   5.55111512e-16],
#[Out]#          [  5.55111512e-16,   5.55111512e-16,   5.55111512e-16,
#[Out]#             5.55111512e-16,   5.55111512e-16]],
#[Out]#  
#[Out]#         [[  4.44089210e-16,   4.44089210e-16,   4.44089210e-16,
#[Out]#             4.44089210e-16,   4.44089210e-16],
#[Out]#          [  4.44089210e-16,   4.44089210e-16,   4.44089210e-16,
#[Out]#             4.44089210e-16,   4.44089210e-16],
#[Out]#          [  4.44089210e-16,   4.44089210e-16,   4.44089210e-16,
#[Out]#             4.44089210e-16,   4.44089210e-16]],
#[Out]#  
#[Out]#         [[  6.66133815e-16,   6.66133815e-16,   6.66133815e-16,
#[Out]#             6.66133815e-16,   6.66133815e-16],
#[Out]#          [  6.66133815e-16,   6.66133815e-16,   6.66133815e-16,
#[Out]#             6.66133815e-16,   6.66133815e-16],
#[Out]#          [  6.66133815e-16,   6.66133815e-16,   6.66133815e-16,
#[Out]#             6.66133815e-16,   6.66133815e-16]],
#[Out]#  
#[Out]#         [[  6.66133815e-16,   6.66133815e-16,   6.66133815e-16,
#[Out]#             6.66133815e-16,   6.66133815e-16],
#[Out]#          [  6.66133815e-16,   6.66133815e-16,   6.66133815e-16,
#[Out]#             6.66133815e-16,   6.66133815e-16],
#[Out]#          [  6.66133815e-16,   6.66133815e-16,   6.66133815e-16,
#[Out]#             6.66133815e-16,   6.66133815e-16]],
#[Out]#  
#[Out]#         [[  7.77156117e-16,   7.77156117e-16,   7.77156117e-16,
#[Out]#             7.77156117e-16,   7.77156117e-16],
#[Out]#          [  7.77156117e-16,   7.77156117e-16,   7.77156117e-16,
#[Out]#             7.77156117e-16,   7.77156117e-16],
#[Out]#          [  7.77156117e-16,   7.77156117e-16,   7.77156117e-16,
#[Out]#             7.77156117e-16,   7.77156117e-16]],
#[Out]#  
#[Out]#         [[  6.66133815e-16,   6.66133815e-16,   6.66133815e-16,
#[Out]#             6.66133815e-16,   6.66133815e-16],
#[Out]#          [  6.66133815e-16,   6.66133815e-16,   6.66133815e-16,
#[Out]#             6.66133815e-16,   6.66133815e-16],
#[Out]#          [  6.66133815e-16,   6.66133815e-16,   6.66133815e-16,
#[Out]#             6.66133815e-16,   6.66133815e-16]],
#[Out]#  
#[Out]#         [[  6.66133815e-16,   6.66133815e-16,   6.66133815e-16,
#[Out]#             6.66133815e-16,   6.66133815e-16],
#[Out]#          [  6.66133815e-16,   6.66133815e-16,   6.66133815e-16,
#[Out]#             6.66133815e-16,   6.66133815e-16],
#[Out]#          [  6.66133815e-16,   6.66133815e-16,   6.66133815e-16,
#[Out]#             6.66133815e-16,   6.66133815e-16]],
#[Out]#  
#[Out]#         [[  7.77156117e-16,   7.77156117e-16,   7.77156117e-16,
#[Out]#             7.77156117e-16,   7.77156117e-16],
#[Out]#          [  7.77156117e-16,   7.77156117e-16,   7.77156117e-16,
#[Out]#             7.77156117e-16,   7.77156117e-16],
#[Out]#          [  7.77156117e-16,   7.77156117e-16,   7.77156117e-16,
#[Out]#             7.77156117e-16,   7.77156117e-16]],
#[Out]#  
#[Out]#         [[  8.88178420e-16,   8.88178420e-16,   8.88178420e-16,
#[Out]#             8.88178420e-16,   8.88178420e-16],
#[Out]#          [  8.88178420e-16,   8.88178420e-16,   8.88178420e-16,
#[Out]#             8.88178420e-16,   8.88178420e-16],
#[Out]#          [  8.88178420e-16,   8.88178420e-16,   8.88178420e-16,
#[Out]#             8.88178420e-16,   8.88178420e-16]],
#[Out]#  
#[Out]#         [[  9.99200722e-16,   9.99200722e-16,   9.99200722e-16,
#[Out]#             9.99200722e-16,   9.99200722e-16],
#[Out]#          [  9.99200722e-16,   9.99200722e-16,   9.99200722e-16,
#[Out]#             9.99200722e-16,   9.99200722e-16],
#[Out]#          [  9.99200722e-16,   9.99200722e-16,   9.99200722e-16,
#[Out]#             9.99200722e-16,   9.99200722e-16]],
#[Out]#  
#[Out]#         [[  9.99200722e-16,   9.99200722e-16,   9.99200722e-16,
#[Out]#             9.99200722e-16,   9.99200722e-16],
#[Out]#          [  9.99200722e-16,   9.99200722e-16,   9.99200722e-16,
#[Out]#             9.99200722e-16,   9.99200722e-16],
#[Out]#          [  9.99200722e-16,   9.99200722e-16,   9.99200722e-16,
#[Out]#             9.99200722e-16,   9.99200722e-16]],
#[Out]#  
#[Out]#         [[  1.11022302e-15,   1.11022302e-15,   1.11022302e-15,
#[Out]#             1.11022302e-15,   1.11022302e-15],
#[Out]#          [  1.11022302e-15,   1.11022302e-15,   1.11022302e-15,
#[Out]#             1.11022302e-15,   1.11022302e-15],
#[Out]#          [  1.11022302e-15,   1.11022302e-15,   1.11022302e-15,
#[Out]#             1.11022302e-15,   1.11022302e-15]],
#[Out]#  
#[Out]#         [[  1.22124533e-15,   1.22124533e-15,   1.22124533e-15,
#[Out]#             1.22124533e-15,   1.22124533e-15],
#[Out]#          [  1.22124533e-15,   1.22124533e-15,   1.22124533e-15,
#[Out]#             1.22124533e-15,   1.22124533e-15],
#[Out]#          [  1.22124533e-15,   1.22124533e-15,   1.22124533e-15,
#[Out]#             1.22124533e-15,   1.22124533e-15]],
#[Out]#  
#[Out]#         [[  1.22124533e-15,   1.22124533e-15,   1.22124533e-15,
#[Out]#             1.22124533e-15,   1.22124533e-15],
#[Out]#          [  1.22124533e-15,   1.22124533e-15,   1.22124533e-15,
#[Out]#             1.22124533e-15,   1.22124533e-15],
#[Out]#          [  1.22124533e-15,   1.22124533e-15,   1.22124533e-15,
#[Out]#             1.22124533e-15,   1.22124533e-15]],
#[Out]#  
#[Out]#         [[  1.22124533e-15,   1.22124533e-15,   1.22124533e-15,
#[Out]#             1.22124533e-15,   1.22124533e-15],
#[Out]#          [  1.22124533e-15,   1.22124533e-15,   1.22124533e-15,
#[Out]#             1.22124533e-15,   1.22124533e-15],
#[Out]#          [  1.22124533e-15,   1.22124533e-15,   1.22124533e-15,
#[Out]#             1.22124533e-15,   1.22124533e-15]],
#[Out]#  
#[Out]#         [[  1.44328993e-15,   1.44328993e-15,   1.44328993e-15,
#[Out]#             1.44328993e-15,   1.44328993e-15],
#[Out]#          [  1.44328993e-15,   1.44328993e-15,   1.44328993e-15,
#[Out]#             1.44328993e-15,   1.44328993e-15],
#[Out]#          [  1.44328993e-15,   1.44328993e-15,   1.44328993e-15,
#[Out]#             1.44328993e-15,   1.44328993e-15]],
#[Out]#  
#[Out]#         [[  1.33226763e-15,   1.33226763e-15,   1.33226763e-15,
#[Out]#             1.33226763e-15,   1.33226763e-15],
#[Out]#          [  1.33226763e-15,   1.33226763e-15,   1.33226763e-15,
#[Out]#             1.33226763e-15,   1.33226763e-15],
#[Out]#          [  1.33226763e-15,   1.33226763e-15,   1.33226763e-15,
#[Out]#             1.33226763e-15,   1.33226763e-15]],
#[Out]#  
#[Out]#         [[  1.44328993e-15,   1.44328993e-15,   1.44328993e-15,
#[Out]#             1.44328993e-15,   1.44328993e-15],
#[Out]#          [  1.44328993e-15,   1.44328993e-15,   1.44328993e-15,
#[Out]#             1.44328993e-15,   1.44328993e-15],
#[Out]#          [  1.44328993e-15,   1.44328993e-15,   1.44328993e-15,
#[Out]#             1.44328993e-15,   1.44328993e-15]],
#[Out]#  
#[Out]#         [[  1.66533454e-15,   1.66533454e-15,   1.66533454e-15,
#[Out]#             1.66533454e-15,   1.66533454e-15],
#[Out]#          [  1.66533454e-15,   1.66533454e-15,   1.66533454e-15,
#[Out]#             1.66533454e-15,   1.66533454e-15],
#[Out]#          [  1.66533454e-15,   1.66533454e-15,   1.66533454e-15,
#[Out]#             1.66533454e-15,   1.66533454e-15]],
#[Out]#  
#[Out]#         [[  1.66533454e-15,   1.66533454e-15,   1.66533454e-15,
#[Out]#             1.66533454e-15,   1.66533454e-15],
#[Out]#          [  1.66533454e-15,   1.66533454e-15,   1.66533454e-15,
#[Out]#             1.66533454e-15,   1.66533454e-15],
#[Out]#          [  1.66533454e-15,   1.66533454e-15,   1.66533454e-15,
#[Out]#             1.66533454e-15,   1.66533454e-15]],
#[Out]#  
#[Out]#         [[  1.99840144e-15,   1.99840144e-15,   1.99840144e-15,
#[Out]#             1.99840144e-15,   1.99840144e-15],
#[Out]#          [  1.99840144e-15,   1.99840144e-15,   1.99840144e-15,
#[Out]#             1.99840144e-15,   1.99840144e-15],
#[Out]#          [  1.99840144e-15,   1.99840144e-15,   1.99840144e-15,
#[Out]#             1.99840144e-15,   1.99840144e-15]],
#[Out]#  
#[Out]#         [[  1.99840144e-15,   1.99840144e-15,   1.99840144e-15,
#[Out]#             1.99840144e-15,   1.99840144e-15],
#[Out]#          [  1.99840144e-15,   1.99840144e-15,   1.99840144e-15,
#[Out]#             1.99840144e-15,   1.99840144e-15],
#[Out]#          [  1.99840144e-15,   1.99840144e-15,   1.99840144e-15,
#[Out]#             1.99840144e-15,   1.99840144e-15]],
#[Out]#  
#[Out]#         [[  2.22044605e-15,   2.22044605e-15,   2.22044605e-15,
#[Out]#             2.22044605e-15,   2.22044605e-15],
#[Out]#          [  2.22044605e-15,   2.22044605e-15,   2.22044605e-15,
#[Out]#             2.22044605e-15,   2.22044605e-15],
#[Out]#          [  2.22044605e-15,   2.22044605e-15,   2.22044605e-15,
#[Out]#             2.22044605e-15,   2.22044605e-15]],
#[Out]#  
#[Out]#         [[  2.44249065e-15,   2.44249065e-15,   2.44249065e-15,
#[Out]#             2.44249065e-15,   2.44249065e-15],
#[Out]#          [  2.44249065e-15,   2.44249065e-15,   2.44249065e-15,
#[Out]#             2.44249065e-15,   2.44249065e-15],
#[Out]#          [  2.44249065e-15,   2.44249065e-15,   2.44249065e-15,
#[Out]#             2.44249065e-15,   2.44249065e-15]],
#[Out]#  
#[Out]#         [[  2.66453526e-15,   2.66453526e-15,   2.66453526e-15,
#[Out]#             2.66453526e-15,   2.66453526e-15],
#[Out]#          [  2.66453526e-15,   2.66453526e-15,   2.66453526e-15,
#[Out]#             2.66453526e-15,   2.66453526e-15],
#[Out]#          [  2.66453526e-15,   2.66453526e-15,   2.66453526e-15,
#[Out]#             2.66453526e-15,   2.66453526e-15]],
#[Out]#  
#[Out]#         [[  2.77555756e-15,   2.77555756e-15,   2.77555756e-15,
#[Out]#             2.77555756e-15,   2.77555756e-15],
#[Out]#          [  2.77555756e-15,   2.77555756e-15,   2.77555756e-15,
#[Out]#             2.77555756e-15,   2.77555756e-15],
#[Out]#          [  2.77555756e-15,   2.77555756e-15,   2.77555756e-15,
#[Out]#             2.77555756e-15,   2.77555756e-15]],
#[Out]#  
#[Out]#         [[  2.99760217e-15,   2.99760217e-15,   2.99760217e-15,
#[Out]#             2.99760217e-15,   2.99760217e-15],
#[Out]#          [  2.99760217e-15,   2.99760217e-15,   2.99760217e-15,
#[Out]#             2.99760217e-15,   2.99760217e-15],
#[Out]#          [  2.99760217e-15,   2.99760217e-15,   2.99760217e-15,
#[Out]#             2.99760217e-15,   2.99760217e-15]],
#[Out]#  
#[Out]#         [[  3.10862447e-15,   3.10862447e-15,   3.10862447e-15,
#[Out]#             3.10862447e-15,   3.10862447e-15],
#[Out]#          [  3.10862447e-15,   3.10862447e-15,   3.10862447e-15,
#[Out]#             3.10862447e-15,   3.10862447e-15],
#[Out]#          [  3.10862447e-15,   3.10862447e-15,   3.10862447e-15,
#[Out]#             3.10862447e-15,   3.10862447e-15]],
#[Out]#  
#[Out]#         [[  3.44169138e-15,   3.44169138e-15,   3.44169138e-15,
#[Out]#             3.44169138e-15,   3.44169138e-15],
#[Out]#          [  3.44169138e-15,   3.44169138e-15,   3.44169138e-15,
#[Out]#             3.44169138e-15,   3.44169138e-15],
#[Out]#          [  3.44169138e-15,   3.44169138e-15,   3.44169138e-15,
#[Out]#             3.44169138e-15,   3.44169138e-15]]]), 0)
np.testing.assert_array_almost_equal_nulp(x=result_order3, y=0, nulp=10)
np.testing.assert_array_almost_equal_nulp(x=result_order3, y=0*result_order3, nulp=10)
np.abs(result_order3).max()
#[Out]# 3.4416913763379853e-15
