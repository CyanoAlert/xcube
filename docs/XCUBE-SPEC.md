# xcube Specification

Version: 0.1 draft

Date: 31.05.2018

Author: Norman

--------------------------------------

## Motivation

Multivariate coregistration, extraction, comparison, and analysis of 
Earth observation data is difficult for many users when data is 
provided at different spatio-temporal resolutions.


## High-level requirements


xcube data 

* SHALL be time series of gridded, geo-spatial, geo-physical variables  
* SHALL use a common, equidistant, global or regional geo-spatial grid
* SHALL shall be easy to read, write, process, generate
* SHALL conform to the requirements of analysis ready data (ARD)
* SHALL be compatible with existing tools and APIs
* SHALL conform to standards or common practices
* SHALL be Cloud ready (TBD...)

ARD links:

* http://ceos.org/ard/
* https://landsat.usgs.gov/ard
* https://medium.com/planet-stories/analysis-ready-data-defined-5694f6f48815
 

## xcube Schemas

### Basic Schema

* Attributes metadata convention 
  * SHALL be CF >= 1.6 
  * SHOULD adhere to THREDDS data server catalogue metadata 
* Dimensions: 
  * SHALL be at least `time`, `bnds`, and MAY be any others.
  * SHALL all be greater than zero, but `bnds` must always be two. 
* Temporal coordinate variables: 
  * SHALL provide time coordinates for given time index.
  * MAY be non-equidistant or equidistant. 
  * `time[time]` SHALL provide observation or average time of *cell centers*. 
  * `time_bnds[time, bnds]` SHALL provide observation or integration time of *cell boundaries*. 
  * Attributes: 
    * Temporal coordinate variables MUST have `units`, `standard_name`, and any others.
    * `standard_name` MUST be `"time"`, `units` MUST have format `"<deltatime> since <datetime>"` 
       where `datetime` must have ISO-format. `calendar` may be given, if not,
      `"gregorian"` is assumed.
* Spatial coordinate variables
  * SHALL provide spatial coordinates for given spatial index.
  * SHALL be equidistant in either angular or metric units 
* Cube variables: 
  * SHALL provide *cube cells* with the dimensions as index.
  * SHALL have shape 
    * `[time, ..., lat, lon]` (see WGS84 schema) or 
    * `[time, ..., y, x]` (see Generic schema) 
  * MAY have extra dimensions, e.g. `layer` (of the atmosphere), `band` (of a spectrum).


### WGS84 Schema (extends Basic)

* Dimensions:
  * SHALL be at least `time`, `lat`, `lon`, `bnds`, and MAY be any others. 
* Spatial coordinate variables: 
  * SHALL use WGS84 (EPSG:4326) CRS.
  * SHALL have `lat[lat]` that provides observation or average latitude of *cell centers*
    with attributes: `standard_name="latitude"` `units="degrees north"`.
  * SHALL have `lon[lon]` that provides observation or average longitude of *cell centers* 
    with attributes: `standard_name="longitude"` and `units="degrees east"` 
  * SHOULD HAVE `lat_bnds[lat, bnds]`, `lon_bnds[lon, bnds]`: provide geodetic observation or integration coordinates of *cell boundaries*. 
* Cube variables: 
  * SHALL have shape `[time, ..., lat, lon]`. 

### Generic Schema (extends Basic)

* Dimensions: `time`, `y`, `x`, `bnds`, and any others. 
  * SHALL be at least `time`, `y`, `x`, `bnds`, and MAY be any others. 
* Spatial coordinate variables: 
  * Any spatial grid and CRS.
  * `y[y]`, `x[x]`: provide spatial observation or average coordinates of *cell centers*.
    *  Attributes: `standard_name`, `units`, other units describe the CRS / projections, see CF.
  * `y_bnds[y, bnds]`, `x_bnds[x, bnds]`: provide spatial observation or integration coordinates of *cell boundaries*.
  * MAY have `lat[y,x]`: latitude of *cell centers*. 
    *  Attributes: `standard_name="latitude"`, `units="degrees north"`.
  * `lon[y,x]`: longitude of *cell centers*. 
    *  Attributes: `standard_name="longitude"`, `units="degrees east"`.
* Cube variables: 
  * MUST have shape `[time, ..., y, x]`. 



## xcube Processing Levels


### Level-2C 

* Generated from Level-2 Earth Observation data
* Spatially resampled to common grid
  * Typically resampled at original resolution
  * May be down-sampled: aggregation/integration
  * May be upsampled: interpolation
* No temporal aggregation/integration
* Temporally non-equidistant

### Level-3

* Generated from Level-2C xcubes
* No spatial processing
* Temporally equidistant
* Temporally integrated/aggregated

## Further ideas 

* Multi-resolution xcubes: embed cube pyramids in xcube at different spatial resolutions.
  Usages: fast image tile server, multi-resolution analysis (e.g. feature detection, algal blooms)
* Multi-chunks xcubes: embed differently chunked cubes in an xcube.
  Usages: fast time-series analyses.   

Provide a Python API based on xarray addressing the following operations

* Merge
* Combine
* Fill gaps
* Match-up
* Extract where
* Subset

## Implementation Hints

For multiple regional cubes that "belong together" (e.g. one project)
use common resolutions and regions that snap on a Fixed Earth grid, which has been
been defined with respect to ideal tile / chunk sizes. 

Chunking of data has a very high impact on processing performance:

* If xcubes are served by a tile map server, tile sizes shall be aligned with chunk sizes
* xcube spatial image size shall be integer divisible by chunk sizes 

