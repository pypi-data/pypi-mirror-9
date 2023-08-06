#! /usr/env/python

"""
fracture_grid: creates and returns a 2D grid with randomly generated fractures.
The grid contains the value 1 where fractures (one cell wide) exist, and
0 elsewhere. The idea is to use this for simulations based on weathering and
erosion of, and/or flow within, fracture networks.

The entry point is the function:
    
    make_frac_grid(frac_spacing, numrows=50, numcols=50, model_grid=None)
    
If called with a Landlab RasterModelGrid, the function returns the fracture
grid as a node array. Otherwise, it returns a numrows x numcols Numpy array.

Potential improvements:
    - Add doctests
    - Fractures could be defined by links rather than nodes (i.e., return a
        link array with a code indicating whether the link crosses a fracture
        or not)
    - Fractures could have a finite length rather than extending all the way
        across the grid
    - Use of starting position along either x or y axis makes fracture net
        somewhat asymmetric. One would need a different algorithm to make it
        fully (statistically) symmetric.
        
Created: September 2013 by Greg Tucker
Last significant modification: August 2014 GT
"""

from numpy import *
from numpy.random import *
import random
import pylab as plt


def calculate_fracture_starting_position(numrows, numcols):
    """
    Chooses a random starting position along the x or y axis (random choice).
    
    Parameters
    ----------
    numrows, numcols : int
        Number of rows and columns in the grid
        
    Returns
    -------
    x, y : int
        Fracture starting coordinates
    """
    if random.randint(0, 1)==0:
        x = 0
        y = random.randint(0, numrows-1)
    else:
        x = random.randint(0, numcols-1)        
        y = 0
    return x, y
    
    
def calculate_fracture_orientation(x, y):
    """
    Chooses a random orientation for the fracture.
    
    Parameters
    ----------
    x, y : int
        Starting coordinates (one of which should be zero)
        
    Returns
    -------
    ang : float
        Fracture angle relative to horizontal
        
    Notes
    -----
    If the fracture starts along the bottom of the grid (y=0), then the angle
    will be between 45 and 135 degrees from horizontal (counter-clockwise).
    Otherwise, it will be between -45 and 45 degrees.
    """
    ang = (pi/2)*rand()
    if y==0:
        ang += pi/4
    else:
        ang -= pi/4

    return ang

    
def calculate_fracture_step_sizes(startx, starty, ang):
    """
    Calculates the sizes of steps dx and dy to be used when "drawing" the
    fracture onto the grid.
    
    Parameters
    ----------
    startx, starty : int
        Starting grid coordinates
    ang : float
        Fracture angle relative to horizontal (radians)
        
    Returns
    -------
    dx, dy : float
        Step sizes in x and y directions. One will always be unity, and the 
    other will always be <1.
    """
    if startx==0:  # frac starts on left side
        dx = 1
        dy = tan(ang)
    else:  # frac starts on bottom side
        dy = 1
        dx = -tan(ang-pi/2)
        
    return dx, dy
    
    
def trace_fracture_through_grid(m, x0, y0, dx, dy):
    """
    Creates a "fracture" in a 2D grid, m, by setting cell values to unity along
    the trace of the fracture (i.e., "drawing" a line throuh the grid).
    
    Parameters
    ----------
    m : 2D Numpy array
        Array that represents the grid
    x0, y0 : int
        Starting grid coordinates for fracture
    dx, dy : float
        Step sizes in x and y directions
        
    Returns
    -------
    None, but changes contents of m
    """
    x = x0
    y = y0
    
    while round(x)<size(m, 1) and round(y)<size(m, 0) \
            and round(x)>=0 and round(y)>=0:
        m[round(y),round(x)] = 1
        x += dx
        y += dy


def make_frac_grid(frac_spacing, numrows=50, numcols=50, model_grid=None):
    """
    Creates and returns a grid containing a network of random fractures, which
    are represented as 1's embedded in a grid of 0's.
    
    Parameters
    ----------
    frac_spacing : int
        Average spacing of fractures (in grid cells)
    (optional) numrows, numcols : int 
        Number of rows and columns in grid (if model_grid parameter is given,
        uses values from the model grid instead)
    (optional) model_grid : Landlab RasterModelGrid object
        RasterModelGrid to use for grid size
        
    Returns
    -------
    m : Numpy array
        Array containing fracture grid, represented as 0's (matrix) and 1's
        (fractures). If model_grid parameter is given, returns a 1D array
        corresponding to a node-based array in the model grid. Otherwise,
        returns a 2D array with dimensions given by numrows, numcols.
    """
    # Make an initial grid of all zeros. If user specified a model grid,
    # use that. Otherwise, use the given dimensions.
    if model_grid is not None:
        numrows = model_grid.number_of_node_rows
        numcols = model_grid.number_of_node_columns
    m = zeros((numrows,numcols))
    
    # Add fractures to grid
    nfracs = (numrows+numcols)/frac_spacing
    for i in range(nfracs):
        
        x, y = calculate_fracture_starting_position(numrows, numcols)
        ang = calculate_fracture_orientation(x, y)
        dx, dy = calculate_fracture_step_sizes(x, y, ang)
    
        #print 'startx=',x,'starty=',y,'ang=',180*ang/pi,'dx=',dx,'dy=',dy
    
        trace_fracture_through_grid(m, x, y, dx, dy)
    
    # If we have a model_grid, flatten the frac grid so it's equivalent to
    # a node array.
    if model_grid is not None:
        #print 'FROG!'
        m.shape = (m.shape[0]*m.shape[1])

    return m
            
    
def test_fracture_grid():
    """
    Test routine that generates and displays a fracture grid.

    Parameters
    ----------
    (none)
    
    Returns
    -------
    (none)
    """
    # User-defined parameters
    N = 100
    frac_spacing = 8
    
    frac_grid = make_frac_grid(frac_spacing, N, N)
    
    plt.figure()
    plt.imshow(frac_grid)
    plt.show()
        
    # Version with model grid
    from landlab import RasterModelGrid
    rmg = RasterModelGrid(40, 50, 1.0)
    frac_grid = make_frac_grid(frac_spacing, model_grid=rmg)
    fg_raster = rmg.node_vector_to_raster(frac_grid)
    
    plt.figure()
    plt.imshow(fg_raster)
    plt.show()
            
