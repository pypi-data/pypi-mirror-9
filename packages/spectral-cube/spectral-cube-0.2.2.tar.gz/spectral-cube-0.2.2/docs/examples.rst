
CASA <1>: import spectral_cube
CASA <2>: cube = spectral_cube.SpectralCube.read('SgrB2_a_03_7M.H2CS303-202.image')
CASA <3>: cube.spectral_axis
Out [3]: <Quantity [  1.03074575e+11,  1.03074231e+11,  1.03073888e+11, ... ] Hz>
CASA <4>: cube
  Out[4]:
SpectralCube with shape=(250, 216, 216) and unit=Jy / beam:
 n_x: 216  type_x: RA---SIN  unit_x: deg
 n_y: 216  type_y: DEC--SIN  unit_y: deg
 n_s: 250  type_s: FREQ      unit_s: Hz
CASA <5>: vcube
  Out[5]:
SpectralCube with shape=(250, 216, 216):
 n_x: 216  type_x: RA---SIN  unit_x: deg
 n_y: 216  type_y: DEC--SIN  unit_y: deg
 n_s: 250  type_s: VRAD      unit_s: m / s
CASA <6>: from astropy import units as u
CASA <7>: vcube = cube.with_spectral_unit(u.km/u.s,
...                                       velocity_convention='radio',
...                                       rest_value=103.04045*u.GHz)
CASA <8>: vcube
  Out[8]:
SpectralCube with shape=(250, 216, 216) and unit=Jy / beam:
 n_x: 216  type_x: RA---SIN  unit_x: deg
 n_y: 216  type_y: DEC--SIN  unit_y: deg
 n_s: 250  type_s: VRAD      unit_s: m / s
CASA <9>: vcube.spectral_axis 
Out [9]: <Quantity [ -99.28522114, -98.28522019, ..., 149.71501567] km / s>
CASA <10>: vcube.spectral_slab(-10*u.km/u.s,10*u.km/u.s).moment0(axis=0)
  Out[10]:
<Projection [[ 0., 0., 0.,...,  0., 0., 0.], ... ] Jy km / (beam s)>

Visualization:

.to_yt
.to_glue
.to_pvextractor

import h5py
import yt
import spectral_cube
cube = spectral_cube.SpectralCube.read('SgrB2_a_03_7M.H2CS303-202.image')
from astropy import units as u
vcube = cube.with_spectral_unit(u.km/u.s,
                                velocity_convention='radio',
                                rest_value=103.04045*u.GHz)
vcube[:,:,125].quicklook()
vcube[:,125,125].quicklook()
