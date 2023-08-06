#! /usr/bin/env python

import numpy

from landlab.grid.base import ModelGrid, CORE_NODE, BAD_INDEX_VALUE
from scipy.spatial import Voronoi

def simple_poly_area(x, y):
    """Calculates and returns the area of a 2-D simple polygon.
    
    Input vertices must be in sequence (clockwise or counterclockwise). *x*
    and *y* are arrays that give the x- and y-axis coordinates of the
    polygon's vertices.

    Parameters
    ----------
    x : ndarray
        x-coordinates of of polygon vertices.
    y : ndarray
        y-coordinates of of polygon vertices.

    Returns
    -------
    out : float
        Area of the polygon

    Examples
    --------
    >>> import numpy as np
    >>> from landlab.grid.voronoi import simple_poly_area
    >>> x = np.array([3., 1., 1., 3.])
    >>> y = np.array([1.5, 1.5, 0.5, 0.5])
    >>> simple_poly_area(x, y)
    2.0

    If the input coordinate arrays are 2D, calculate the area of each polygon.
    Note that when used in this mode, all polygons must have the same
    number of vertices, and polygon vertices are listed column-by-column.

    >>> x = np.array([[ 3.,  1.,  1.,  3.],
    ...               [-2., -2., -1., -1.]]).T
    >>> y = np.array([[1.5, 1.5, 0.5, 0.5],
    ...               [ 0.,  1.,  2.,  0.]]).T
    >>> simple_poly_area(x, y)
    array([ 2. ,  1.5])
    """
    # For short arrays (less than about 100 elements) it seems that the
    # Python sum is faster than the numpy sum. Likewise for the Python
    # built-in abs.
    return .5 * abs(sum(x[:-1] * y[1:] - x[1:] * y[:-1]) +
                    x[-1] * y[0] - x[0] * y[-1])


def calculate_link_lengths(pts, link_from, link_to):
    """Calculates and returns length of links between nodes.

    Parameters
    ----------
    pts : Nx2 numpy array containing (x,y) values
    link_from : 1D numpy array containing index numbers of nodes at starting
                point ("from") of links
    link_to : 1D numpy array containing index numbers of nodes at ending point
              ("to") of links
                      
    Returns
    -------
    out : ndarray
        1D numpy array containing horizontal length of each link
    
    Examples
    --------
    >>> import numpy as np
    >>> from landlab.grid.voronoi import calculate_link_lengths
    >>> pts = np.array([[0.,0.],[3.,0.],[3.,4.]]) # 3:4:5 triangle
    >>> lfrom = np.array([0,1,2])
    >>> lto = np.array([1,2,0])
    >>> calculate_link_lengths(pts, lfrom, lto)
    array([ 3.,  4.,  5.])
    """
    dx = pts[link_to, 0] - pts[link_from, 0]
    dy = pts[link_to, 1] - pts[link_from, 1]
    link_length = numpy.sqrt(dx * dx + dy * dy)
    return link_length
    
    
class VoronoiDelaunayGrid(ModelGrid):
    """
    This inherited class implements an unstructured grid in which cells are
    Voronoi polygons and nodes are connected by a Delaunay triangulation. Uses
    scipy.spatial module to build the triangulation.
    
    Examples
    --------
    >>> from numpy.random import rand
    >>> from landlab.grid import VoronoiDelaunayGrid
    >>> x, y = rand(25), rand(25)
    >>> vmg = VoronoiDelaunayGrid(x, y)  # node_x_coords, node_y_coords
    >>> vmg.number_of_nodes
    25
    """
    def __init__(self, x=None, y=None, reorient_links=True, **kwds):
        """Create a Voronoi Delaunay grid from a set of points.

        Create an unstructured grid from points whose coordinates are given
        by the arrays *x*, *y*.

        Parameters
        ----------
        x : array_like
            x-coordinate of points
        y : array_like
            y-coordinate of points

        Returns
        -------
        VoronoiDelaunayGrid
            A newly-created grid.

        Examples
        --------
        >>> from numpy.random import rand
        >>> from landlab.grid import VoronoiDelaunayGrid
        >>> x, y = rand(25), rand(25)
        >>> vmg = VoronoiDelaunayGrid(x, y)  # node_x_coords, node_y_coords
        >>> vmg.number_of_nodes
        25
        """
        if (x is not None) and (y is not None):
            self._initialize(x, y, reorient_links)
        super(VoronoiDelaunayGrid, self).__init__(**kwds)
        
    def _initialize(self, x, y, reorient_links=False):
        """
        Creates an unstructured grid around the given (x,y) points.
        """
        
        assert type(x)==numpy.ndarray, 'x must be a numpy array'
        assert type(y)==numpy.ndarray, 'y must be a numpy array'
        assert len(x)==len(y), 'x and y arrays must have the same size'
        
        # Make a copy of the points in a 2D array (useful for calls to geometry
        # routines, but takes extra memory space).
        pts = numpy.zeros((len(x), 2))
        pts[:,0] = x
        pts[:,1] = y
        self.pts = pts
        
        # NODES AND CELLS: Set up information pertaining to nodes and cells:
        #   - number of nodes
        #   - node x, y coordinates
        #   - default boundary status 
        #   - interior and boundary nodes
        #   - nodes associated with each cell and active cell
        #   - cells and active cells associated with each node 
        #     (or BAD_VALUE_INDEX if none)
        #
        # Assumptions we make here:
        #   - all interior (non-perimeter) nodes have cells (this should be 
        #       guaranteed in a Delaunay triangulation, but there may be 
        #       special cases)
        #   - all cells are active (later we'll build a mechanism for the user
        #       specify a subset of cells as active)
        #
        self._num_nodes = len(x)
        #print x, y
        self._node_x = x
        self._node_y = y
        [self.node_status, self._core_nodes, self._boundary_nodes] = \
                self.find_perimeter_nodes(pts)
        self._num_active_nodes = self.number_of_nodes
        self._num_core_nodes = len(self.core_nodes)
        self._num_cells = len(self.core_nodes)
        self._num_active_cells = self.number_of_cells
        [self.node_cell, self.cell_node] = self.setup_node_cell_connectivity(
            self.node_status, self.number_of_cells)
        self.node_activecell = self.node_cell
        self.activecell_node = self.cell_node

        # ACTIVE CELLS: Construct Voronoi diagram and calculate surface area of
        # each active cell.
        vor = Voronoi(pts)
        self.vor = vor
        self.active_cell_areas = numpy.zeros(self.number_of_active_cells)
        for node in self.activecell_node:
            xv = vor.vertices[vor.regions[vor.point_region[node]],0]
            yv = vor.vertices[vor.regions[vor.point_region[node]],1]
            self.active_cell_areas[self.node_activecell[node]] = simple_poly_area(xv, yv)
        
        # LINKS: Construct Delaunay triangulation and construct lists of link
        # "from" and "to" nodes.
        (self.link_fromnode,
         self.link_tonode,
         self.active_links_ids,
         self.face_width) = self.create_links_and_faces_from_voronoi_diagram(vor)
        
        # Optionally re-orient links so that they all point within upper-right
        # semicircle
        if reorient_links:
            self.reorient_links_upper_right()

        #[self.link_fromnode, self.link_tonode, self.active_links, self.face_width] \
        #        = self.create_links_and_faces_from_voronoi_diagram(vor)
        self._num_links = len(self.link_fromnode)
        self._num_faces = self._num_links # temporary: to be done right!
                    
        # LINKS: Calculate link lengths
        self._link_length = calculate_link_lengths(pts, self.link_fromnode,
                                                  self.link_tonode)
                                                       
        # LINKS: inlink and outlink matrices
        self._setup_inlink_and_outlink_matrices()
        
        # ACTIVE LINKS: Create list of active links, as well as "from" and "to"
        # nodes of active links.
        self._reset_list_of_active_links()

        # LINKS: set up link unit vectors and node unit-vector sums
        self._make_link_unit_vectors()

        # LINKS: ID of corresponding face, if any
        self.link_face = (numpy.zeros(self.number_of_links, dtype=int) +
                          BAD_INDEX_VALUE)  # make the list
        face_id = 0
        for link in self.active_links:
            self.link_face[link] = face_id
            face_id += 1
            
    @property
    def number_of_patches(self):
        """Number of patches.
        Returns the number of patches over the grid.
        """
        try:
            return self._number_of_patches
        except AttributeError:
            self.create_patches_from_delaunay_diagram(self.pts, self.vor)
            return self._number_of_patches
            
    @property
    def patch_nodes(self):
        """patch_nodes
        Returns the four nodes at the corners of each patch in a regular grid.
        """
        try:
            return self._patch_nodes
        except AttributeError:
            self.create_patches_from_delaunay_diagram(self.pts, self.vor)
            return self._patch_nodes

    def node_patches(self, nodata=-1):
        """node_patches()
        (This is a placeholder method until improved using jagged array 
        operations.)
        Returns a (N,max_voronoi_polygon_sides) array of the patches associated 
        with each node in the grid.
        The patches are returned in id order, with any null or nonexistent 
        patches recorded after the ids of existing faces.
        The nodata argument allows control of the array value used to indicate
        nodata. It defaults to -1, but other options are 'nan' and 'bad_value'.
        Note that this method returns a *masked* array, with the normal provisos
        that integer indexing with a masked array removes the mask.
        """
        if nodata==-1: #fiddle needed to ensure we set the nodata value properly if we've called patches elsewhere
            try:
                return self._node_patches
            except AttributeError:
                self.create_patches_from_delaunay_diagram(self.pts, self.vor, nodata)        
                return self._node_patches
        else:
            try:
                self.set_bad_value
            except:
                self.create_patches_from_delaunay_diagram(self.pts, self.vor, nodata)  
                self.set_bad_value=True      
                return self._node_patches
            else:
                return self._node_patches
            

    def find_perimeter_nodes(self, pts):
        """
        Uses a convex hull to locate the perimeter nodes of the Voronoi grid,
        then sets them as fixed value boundary nodes.
        It then sets/updates the various relevant node lists held by the grid, 
        and returns *node_status*, *core_nodes*, *boundary_nodes*.
        """
    
        # Calculate the convex hull for the set of points
        from scipy.spatial import ConvexHull
        hull = ConvexHull(pts, qhull_options='Qc') # see below why we use 'Qt'
        
        # The ConvexHull object lists the edges that form the hull. We need to
        # get from this list of edges the unique set of nodes. To do this, we
        # first flatten the list of vertices that make up all the hull edges 
        # ("simplices"), so it becomes a 1D array. With that, we can use the set()
        # function to turn the array into a set, which removes duplicate vertices.
        # Then we turn it back into an array, which now contains the set of IDs for
        # the nodes that make up the convex hull.
        #   The next thing to worry about is the fact that the mesh perimeter 
        # might contain nodes that are co-planar (that is, co-linear in our 2D 
        # world). For example, if you make a set of staggered points for a
        # hexagonal lattice using make_hex_points(), there will be some 
        # co-linear points along the perimeter. The ones of these that don't 
        # form convex corners won't be included in convex_hull_nodes, but they
        # are nonetheless part of the perimeter and need to be included in
        # the list of boundary_nodes. To deal with this, we pass the 'Qt'
        # option to ConvexHull, which makes it generate a list of coplanar
        # points. We include these in our set of boundary nodes.
        convex_hull_nodes = numpy.array(list(set(hull.simplices.flatten())))
        coplanar_nodes = hull.coplanar[:,0]
        boundary_nodes = numpy.concatenate((convex_hull_nodes, coplanar_nodes))
    
        # Now we'll create the "node_status" array, which contains the code
        # indicating whether the node is interior and active (=0) or a
        # boundary (=1). This means that all perimeter (convex hull) nodes are
        # initially flagged as boundary code 1. An application might wish to change
        # this so that, for example, some boundaries are inactive.
        node_status = numpy.zeros(len(pts[:,0]), dtype=numpy.int8)
        node_status[boundary_nodes] = 1
        
        # It's also useful to have a list of interior nodes
        core_nodes = numpy.where(node_status==0)[0]
        
        #save the arrays and update the properties
        self.node_status = node_status
        self._num_active_nodes = node_status.size
        self._num_core_nodes = len(core_nodes)
        self._num_core_cells = len(core_nodes)
        self.core_cells = numpy.arange(len(core_nodes))
        self.node_corecell = numpy.empty(node_status.size)
        self.node_corecell.fill(BAD_INDEX_VALUE)
        self.node_corecell[core_nodes] = self.core_cells
        self.active_cells = numpy.arange(node_status.size)
        self.cell_node = core_nodes
        self.activecell_node = core_nodes
        self.corecell_node = core_nodes
        self._boundary_nodes = boundary_nodes
        
        # Return the results
        return node_status, core_nodes, boundary_nodes

    @staticmethod
    def setup_node_cell_connectivity(node_status, ncells):
        """Setup node connectivity

        Creates and returns the following arrays:
        1. For each node, the ID of the corresponding cell, or
           BAD_INDEX_VALUE if the node has no cell.
        2. For each cell, the ID of the corresponding node.
            
        Parameters
        ----------
        node_status : ndarray of ints
            1D array containing the boundary status code for each node.
        ncells : ndarray of ints
            Number of cells (must equal the number of occurrences of CORE_NODE
            in node_status).
                    
        Examples
        --------
        >>> import numpy as np
        >>> from landlab.grid import VoronoiDelaunayGrid, BAD_INDEX_VALUE
        >>> ns = np.array([1, 0, 0, 1, 0])  # 3 interior, 2 boundary nodes
        >>> [node_cell, cell_node] = VoronoiDelaunayGrid.setup_node_cell_connectivity(ns, 3)
        >>> node_cell[1:3]
        array([0, 1])
        >>> node_cell[0] == BAD_INDEX_VALUE
        True
        >>> cell_node
        array([1, 2, 4])
        """
        assert ncells==numpy.count_nonzero(node_status==CORE_NODE), \
               'ncells must equal number of CORE_NODE values in node_status'

        cell = 0
        node_cell = numpy.ones(len(node_status), dtype=int)*BAD_INDEX_VALUE
        cell_node = numpy.zeros(ncells, dtype=int)
        for node in range(len(node_cell)):
            if node_status[node] == CORE_NODE:
                node_cell[node] = cell
                cell_node[cell] = node
                cell += 1
                
        #save the arrays
        #self.node_cell = node_cell
        #self.cell_node = cell_node
        
        return node_cell, cell_node
        
    @staticmethod
    def create_links_from_triangulation(tri):
        """
        From a Delaunay Triangulation of a set of points, contained in a
        scipy.spatial.Delaunay object "tri", creates and returns:
            1) a numpy array containing the ID of the "from" node for each link
            2) a numpy array containing the ID of the "to" node for each link
            3) the number of links in the triangulation
        
        Examples
        --------
        >>> from scipy.spatial import Delaunay
        >>> import numpy as np
        >>> from landlab.grid import VoronoiDelaunayGrid
        >>> pts = np.array([[ 0., 0.], [ 1., 0.], [ 1., 0.87],
        ...                 [-0.5, 0.87], [ 0.5, 0.87], [ 0., 1.73],
        ...                 [ 1., 1.73]])
        >>> dt = Delaunay(pts)
        >>> [myfrom,myto,nl] = VoronoiDelaunayGrid.create_links_from_triangulation(dt)
        >>> print myfrom, myto, nl # doctest: +SKIP
        [5 3 4 6 4 3 0 4 1 1 2 6] [3 4 5 5 6 0 4 1 0 2 4 2] 12
        """
    
        # Calculate how many links there will be and create the arrays.
        #
        # The number of links equals 3 times the number of triangles minus
        # half the number of shared links. Finding out the number of shared links
        # is easy: for every shared link, there is an entry in the tri.neighbors
        # array that is > -1 (indicating that the triangle has a neighbor opposite
        # a given vertex; in other words, two triangles are sharing an edge).
        #
        num_shared_links = numpy.count_nonzero(tri.neighbors>-1)
        num_links = 3*tri.nsimplex - num_shared_links/2
        link_fromnode = numpy.zeros(num_links, dtype=int)
        link_tonode = numpy.zeros(num_links, dtype=int)
        
        # Sweep through the list of triangles, assigning "from" and "to" nodes to
        # the list of links.
        #
        # The basic algorithm works as follows. For each triangle, we will add its
        # 3 edges as links. However, we have to make sure that each shared edge
        # is added only once. To do this, we keep track of whether or not each
        # triangle has been processed yet using a boolean array called "tridone".
        # When we look at a given triangle, we check each vertex in turn. If there
        # is no neighboring triangle opposite that vertex, then we need to add the
        # corresponding edge. If there is a neighboring triangle but we haven't
        # processed it yet, we also need to add the edge. If neither condition is
        # true, then this edge has already been added, so we skip it.
        link_id = 0
        tridone = numpy.zeros(tri.nsimplex, dtype=bool)    
        for t in range(tri.nsimplex):  # loop over triangles
            for i in range(0, 3):       # loop over vertices & neighbors
                if tri.neighbors[t,i] == -1 or not tridone[tri.neighbors[t,i]]:
                    link_fromnode[link_id] = tri.simplices[t,numpy.mod(i+1,3)]
                    link_tonode[link_id] = tri.simplices[t,numpy.mod(i+2,3)]
                    link_id += 1
            tridone[t] = True
        
        #save the results
        #self.link_fromnode = link_fromnode
        #self.link_tonode = link_tonode
        #self._num_links = num_links
    
        # Return the results
        return link_fromnode, link_tonode, num_links
    
    @staticmethod
    def is_valid_voronoi_ridge(vor, n):
        
        SUSPICIOUSLY_BIG = 40000000.0
        return vor.ridge_vertices[n][0]!=-1 and vor.ridge_vertices[n][1]!=-1 \
                and numpy.amax(numpy.abs(vor.vertices[vor.ridge_vertices[n]]))<SUSPICIOUSLY_BIG

    @staticmethod
    def create_links_and_faces_from_voronoi_diagram(vor):
        """
        From a Voronoi diagram object created by scipy.spatial.Voronoi(),
        builds and returns:
        1. Arrays of link "from" and "to" nodes
        2. Array of link IDs for each active link
        3. Array containing with of each face
        
        Parameters
        ----------
        vor : scipy.spatial.Voronoi
            Voronoi object initialized with the grid nodes.

        Returns
        -------
        out : tuple of ndarrays
            - link_fromnode = "from" node for each link (len=num_links)
            - link_tonode   = "to" node for each link (len=num_links)
            - active_links  = link ID for each active link (len=num_active_links)
            - face_width    = width of each face (len=num_active_links

        Examples
        --------
        >>> import numpy as np
        >>> from landlab.grid import VoronoiDelaunayGrid
        >>> pts = np.array([[ 0., 0.],[  1., 0.],[  1.5, 0.87],[-0.5, 0.87],[ 0.5, 0.87],[  0., 1.73],[  1., 1.73]])
        >>> from scipy.spatial import Voronoi
        >>> vor = Voronoi(pts)
        >>> [fr,to,al,fw] = VoronoiDelaunayGrid.create_links_and_faces_from_voronoi_diagram(vor)
        >>> fr
        array([0, 0, 0, 1, 1, 3, 3, 6, 6, 6, 4, 4])
        >>> to
        array([3, 1, 4, 2, 4, 4, 5, 4, 2, 5, 2, 5])
        >>> al
        array([ 2,  4,  5,  7, 10, 11])
        >>> fw
        array([ 0.57669199,  0.57669199,  0.575973  ,  0.57836419,  0.575973  , 0.57836419])
        """
        # Each Voronoi "ridge" corresponds to a link. The Voronoi object has an
        # attribute ridge_points that contains the IDs of the nodes on either
        # side (including ridges that have one of their endpoints undefined).
        # So, we set the number of links equal to the number of ridges.
        num_links = len(vor.ridge_points)
        
        # Create the arrays for link from and to nodes
        link_fromnode = -numpy.ones(num_links, dtype=int)
        link_tonode = -numpy.ones(num_links, dtype=int)
        
        # Ridges along the perimeter of the grid will have one of their 
        # endpoints undefined. The endpoints of each ridge are contained in
        # vor.ridge_vertices, and an undefined vertex is flagged with -1.
        # Ridges with both vertices defined correspond to faces and active 
        # links, while ridges with an undefined vertex correspond to inactive
        # links. So, to find the number of active links, we subtract from the
        # total number of links the number of occurrences of an undefined
        # vertex.
        num_active_links = num_links \
                    - numpy.count_nonzero(numpy.array(vor.ridge_vertices)==-1)
        #print 'num_links=', num_links,'num_active_links=',num_active_links
        
        # Create arrays for active links and width of faces (which are Voronoi
        # ridges).
        active_links = -numpy.ones(num_active_links, dtype=int)
        face_width = -numpy.ones(num_active_links)
    
        # Loop through the list of ridges. For each ridge, there is a link, and
        # its "from" and "to" nodes are the associated "points". In addition, if
        # the ridge endpoints are defined, we have a face and an active link,
        # so we add them to our arrays as well.
        j = 0
        for i in range(num_links):
            link_fromnode[i] = vor.ridge_points[i,0]
            link_tonode[i] = vor.ridge_points[i,1]
            face_corner1 = vor.ridge_vertices[i][0]
            face_corner2 = vor.ridge_vertices[i][1]
            if VoronoiDelaunayGrid.is_valid_voronoi_ridge(vor, i):  # means it's a valid face
                dx = vor.vertices[face_corner2,0]-vor.vertices[face_corner1,0]
                dy = vor.vertices[face_corner2,1]-vor.vertices[face_corner1,1]
                face_width[j] = numpy.sqrt(dx*dx+dy*dy)
                if abs(face_width[j])>=40000.0:
                    print 'link',i,'from',link_fromnode[i],'to',link_tonode[i],'has face width',face_width[j]
                    print vor.ridge_vertices[i]
                    print vor.vertices[vor.ridge_vertices[i]]
                    from scipy.spatial import voronoi_plot_2d
                    voronoi_plot_2d(vor)
                assert face_width[j] < 40000., 'face width must be less than earth circumference!'
                active_links[j] = i
                j += 1
        #print 'active links:',active_links
        #print 'vor ridge points:',vor.ridge_points
        
        #save the data
        #self.link_fromnode = link_fromnode
        #self.link_tonode = link_tonode
        #self.active_link_ids = active_links
        #self._face_widths = face_width
        #self._num_faces = face_width.size
        #self._num_active_links = active_links.size
        
        return link_fromnode, link_tonode, active_links, face_width
        
    
    def reorient_links_upper_right(self):
        """
        Reorients links so that all point within the upper-right semi-circle.
        
        Notes
        -----
        "Upper right semi-circle" means that the angle of the link with respect
        to the vertical (measured clockwise) falls between -45 and +135. More
        precisely, if :math:`\theta' is the angle, :math:`-45 \ge \theta < 135`.
        For example, the link could point up and left as much as -45, but not -46.
        It could point down and right as much as 134.9999, but not 135. It will
        never point down and left, or up-but-mostly-left, or 
        right-but-mostly-down.
        
        Examples
        --------
        >>> from landlab.grid import HexModelGrid
        >>> hg = HexModelGrid(3, 2, 1., reorient_links=True)
        >>> hg.link_fromnode
        array([3, 3, 2, 0, 3, 1, 4, 5, 2, 0, 0, 1])
        >>> hg.link_tonode
        array([6, 5, 3, 3, 4, 3, 6, 6, 5, 2, 1, 4])
        """
        
        # Calculate the horizontal (dx) and vertical (dy) link offsets
        link_dx = self.node_x[self.link_tonode] - self.node_x[self.link_fromnode]
        link_dy = self.node_y[self.link_tonode] - self.node_y[self.link_fromnode]
        
        # Calculate the angle, clockwise, with respect to vertical, then rotate
        # by 45 degrees counter-clockwise (by adding pi/4)
        link_angle = numpy.arctan2(link_dx, link_dy) + numpy.pi/4
        
        # The range of values should be -180 to +180 degrees (but in radians).
        # It won't be after the above operation, because angles that were 
        # > 135 degrees will now have values > 180. To correct this, we subtract
        # 360 (i.e., 2 pi radians) from those that are > 180 (i.e., > pi radians).
        link_angle -= 2*numpy.pi*(link_angle>=numpy.pi)
        
        # Find locations where the angle is negative; these are the ones we
        # want to flip
        (flip_locs, ) = numpy.where(link_angle<0.)
        
        # If there are any flip locations, proceed to switch their fromnodes and
        # tonodes; otherwise, we're done
        if len(flip_locs)>0:
            
            # Temporarily story the fromnode for these
            fromnode_temp = self.link_fromnode[flip_locs]
            
            # The fromnodes now become the tonodes, and vice versa
            self.link_fromnode[flip_locs] = self.link_tonode[flip_locs]
            self.link_tonode[flip_locs] = fromnode_temp
            
    def create_patches_from_delaunay_diagram(self, pts, vor, nodata=-1):
        """
        Uses a delaunay diagram drawn from the provided points to
        generate an array of patches and patch-node-link connectivity.
        Returns ...
        DEJH, 10/3/14
        """
        from scipy.spatial import Delaunay
        tri = Delaunay(pts)
        assert numpy.array_equal(tri.points, vor.points)
        
        if nodata==-1:
            pass
        elif nodata=='bad_value':
            nodata=BAD_INDEX_VALUE
        elif nodata=='nan':
            nodata=numpy.nan
        else:
            raise ValueError('Do not recognise nodata value!')
        
        self._patch_nodes = tri.simplices
        self._number_of_patches = tri.simplices.shape[0]
        max_dimension = 0
        #need to build a squared off, masked array of the node_patches
        #the max number of patches for a node in the grid is the max sides of
        #the side-iest voronoi region.
        for i in xrange(len(vor.regions)):
            if len(vor.regions[i])>max_dimension:
                max_dimension=len(vor.regions[i])
        _node_patches = numpy.empty((self.number_of_nodes, max_dimension), dtype=int)
        _node_patches.fill(nodata)
        for i in xrange(self.number_of_nodes):
            if not self.is_boundary(i, boundary_flag=4): #don't include closed nodes
                patches_with_node = numpy.argwhere(numpy.equal(self._patch_nodes,i))[:,0]
                _node_patches[i,:patches_with_node.size] = patches_with_node[:]
        #mask it
        self._node_patches = numpy.ma.array(_node_patches, mask=numpy.equal(_node_patches, -1))
