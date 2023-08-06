from matplotlib import pyplot as plt
import numpy as np
from sklearn.decomposition import PCA
from shapely.geometry import MultiPolygon, Polygon, Point
from shapely import geometry
from scipy.sparse import lil_matrix, issparse
from itertools import product
import sima
from descartes import PolygonPatch
from skimage.measure import find_contours
from scipy import ndimage


class AxonROI(object):

    def __init__(self, name, imsize, points=np.array([]), mask=np.array([]),polyPoints=None ):
        self._name = name
        self._imsize = imsize
        self.well_formed = True
        self.count = 0

        if polyPoints is not None:
            self.points = np.array([list(pts) for pts in polyPoints.exterior.coords]).astype(int)
            self.simplify
        elif len(points) > 0:
            self.points = points
        elif len(mask) > 0:
            self.points = self.extractPoints(mask)
            #self.points = mask2poly(mask)


    @property
    def poly(self):
        try:
            self._ploy
        except AttributeError:
            self._poly = geometry.Polygon(self.points)

        return self._poly

    @property
    def mask(self):
        try:
            self._mask
        except AttributeError:
            self._mask = poly2mask(self.poly,self._imsize)
        return self._mask

    def addToCount(self):
        try:
            self.count
        except AttributeError:
            self.count = 0

        self.count = self.count+1

    def addPoint(self, point):
        self.points = self.points.append()


    def plotROI(self, fig, closed=True, linewidth=1, color=None):
        plt.figure(fig.number)

        if color is not None:
            return plt.plot(np.append(self.points[:,0], self.points[0,0]), np.append(self.points[:,1], self.points[0,1]),linewidth=linewidth,color=color)

        elif closed:
            return plt.plot(np.append(self.points[:,0], self.points[0,0]), np.append(self.points[:,1], self.points[0,1]),linewidth=linewidth)
        else:
            return plt.plot(self.points[:,0], self.points[:,1],linewidth=linewidth)


    def flipPoly(self):
        for point in self.points:
            point[1] = self._imsize[0]-point[1]
        

    def plotPoly(self,ax,color=None):
        BLUE = '#6699cc'
        GREEN = '#66cc99'
        RED = '#cc9966'

        if color == None:
            color = BLUE

        patch = PolygonPatch(self.poly, fc=color, ec=color, alpha=0.5, zorder=1)    
        ax.add_patch(patch)


    def simplify(self):
        diffpoints = np.diff(self.points,axis=0)
        slopes = 1.0*diffpoints[:,1]/diffpoints[:,0]
        indexes = np.where(np.diff(np.nan_to_num(slopes)) < 1)[0] +1
        indexes = np.insert(indexes,0,0)
        indexes = np.append(indexes,self.points.shape[0]-1)
        self.points = self.points[indexes]


    def downsample(self, n):
        self.points = self.points[::n,:]

    def segments(self,p):
        return zip(p, p[1:] + [p[0]])

    def area(self):
        return 0.5 * abs(sum(x0*y1 - x1*y0 for ((x0, y0), (x1, y1)) in self.segments(self.points)))

    def length(self):
        return np.sum(np.sum((self.points[1:,:]-self.points[0:-1,:])**2,axis=1)**0.5)

    def orientation(self, showPlot=False):
        pca = PCA(n_components=2)
        pca.fit(self.points)
        
        if showPlot:
            plt.figure()
            normPts = 1.0*self.points/np.max(self.points)
            normPts[:,0] = normPts[:,0]-np.min(normPts[:,0])
            normPts[:,1] = normPts[:,1]-np.min(normPts[:,1])

            plt.plot(np.append(0,pca.components_[0,0]),np.append(0,pca.components_[0,1]),'r')
            plt.plot(normPts[:,0],normPts[:,1])
            plt.show()

        return ((pca.components_[0,1]/pca.components_[0,0]), pca.explained_variance_ratio_)

    def extractPoints(self,mask):
        frame = mask.copy()
          
        frame[frame>0]=1
        check = frame[:-2,:-2]+frame[1:-1,:-2]+frame[2:,:-2]+frame[:-2,1:-1]+frame[2:,1:-1]+frame[:-2:,2:]+frame[1:-1,2:]+frame[2:,2:]
        z = np.zeros(frame.shape)
        z[1:-1,1:-1] = check;


        b = []
        rows,cols = np.where(z>0)
        p = [cols[0],rows[0]]
        base = p

        radius = 3
        x=np.roll(np.array(list(p[0]+range(-3,3))+[p[0]+3]*(2*3+1)+list(p[0]+range(-3,3)[::-1]) +[p[0]-(3+1)]*(2*3+1)),-2)
        y=np.roll(np.array([p[1]-3]*(2*3)+list(p[1]+range(-3,3))+[p[1]+3]*(2*3+1)+list(p[1]+range(-3,(3+1))[::-1])),-3)
            
        limit = 1500
        tmpRad = False
        for i in range(limit):
            b.append(p)
            #x=np.roll(np.array(list(p[0]+range(-3,3))+[p[0]+3]*(2*3+1)+list(p[0]+range(-3,3)[::-1]) +[p[0]-(3+1)]*(2*3+1)),-2)
            #y=np.roll(np.array([p[1]-3]*(2*3)+list(p[1]+range(-3,3))+[p[1]+3]*(2*3+1)+list(p[1]+range(-3,(3+1))[::-1])),-3)
            x=np.roll(np.array(list(p[0]+range(-radius,radius))+[p[0]+radius]*(2*radius+1)+list(p[0]+range(-radius,radius)[::-1]) +[p[0]-(radius+1)]*(2*radius+1)),-2)
            y=np.roll(np.array([p[1]-radius]*(2*radius)+list(p[1]+range(-radius,radius))+[p[1]+radius]*(2*radius+1)+list(p[1]+range(-radius,(radius+1))[::-1])),-radius)
    
            x[x<0]=0
            y[y<0]=0
            x[x>=z.shape[1]] = z.shape[1]-1
            y[y>=z.shape[0]] = z.shape[0]-1
            
            vals = z[y,x]

            if len(np.where(np.roll(vals,1) == 0)[0]) == 0 or len(np.where(vals>0)[0]) == 0:
                print "confusion failure"
                self.well_formed = False
                return np.array(b)

            idx = np.intersect1d(np.where(vals>0)[0], np.where(np.roll(vals,1) == 0)[0])[0]
            p = [x[idx],y[idx]]

            """
            if tmpRad:
                a = np.array(b)
                plt.imshow(z)
                plt.plot(a[:,0],a[:,1],'o')
                plt.plot(p[0],p[1],'o',color='g')
                plt.show()
            """

            if ((p[0]-base[0])**2+(p[1]-base[1])**2)**0.5 < radius:
                print "well formed ROI"
                return np.array(b)

            if p in b:
                print "possible duplicate entry...", radius
                """
                a = np.array(b)
                plt.imshow(z)
                plt.plot(a[:,0],a[:,1],'o')
                plt.plot(p[0],p[1],'o',color='g')
                plt.show()
               
                """
                
                if radius > 5:
                    radius = 3
                    z = ndimage.gaussian_filter(z, sigma=1)

                    b = []
                    rows,cols = np.where(z>0)
                    p = [cols[0],rows[0]]
                    base = p
                    tmpRad = False


                else:
                    radius = radius+1
                    tmpRad = True
                    p = b[-3]
                    del b[-1]
                    del b[-1]
                    del b[-1]
    

                #return np.array(b)
                
            elif tmpRad:
                tmpRad = False
                radius = 3

            

        

        if i == limit-1:
            print "terminal failure"
            self.well_formed = False
            return np.array(b)


    def distanceTo(self, roi, showPlot=False, secondCheck=False):
        dist = np.Inf
        minpt = None
        minx = 0
        miny = 0
        x1,y1 = self.points[0,:]
        for x2,y2 in self.points[1:,:]:

            for x3,y3 in roi.points:
                px,py = x2-x1,y2-y1
                u = ((x3-x1)*px + (x3-y1)*py)/float(px*px+py*py)
        
                if u > 1:
                    u = 1
                elif u < 0:
                    u = 0

                x = x1+u*px
                y = y1+u*py
            
                dx = x-x3
                dy = y-y3

                newDist = dx*dx+dy*dy

                if newDist < dist:
                    minx = x
                    miny = y
                    dist = newDist
                    minpt = (x3,y3)
                    
            (x1,y1) = (x2,y2)

        x = minx
        y = miny

        if showPlot:
            plt.plot(np.append(minpt[0],x),np.append(minpt[1],y))
        
        if not secondCheck:
            dist = min(dist,roi.distanceTo(self,showPlot=showPlot,secondCheck=True))

        return dist


    def merge(self,roi):
        """
        dists = np.array([[(x2-x1)**2 + (y2-y1)**2 for x2,y2 in roi.points] for x1,y1 in self.points])
        minDists = np.min(dists,axis=1)

        b1 = np.min(minDists)
        b2 = np.min(minDists[minDists>b1])

        row = np.array(np.where(dists==b1)).flatten()[0]
        col =  np.array(np.where(dists==b1)).flatten()[1]
        
        angleChecks = [[1,1],[1,-1],[-1,1],[-1,-1]]
        orthoChecks = [[0,0],[0,1],[0,-1],[1,0],[-1,0]]

        #import pudb; pudb.set_trace()
        
        #checkall = [[dists[arow,acol]+ dists[(arow+acheck[0],acol+acheck[1])] for acheck in angleChecks] for (arow+row,acol+col) in orthoChecks]
        #import pudb; pudb.set_trace()

        adj = np.roll(roi.points,col,axis=0)
        adj = adj[::-1]
        self.points = np.insert(self.points,[row+1]*(adj.shape[0]),adj,axis=0)
        """
        dists = []
        p=[0,0]
        dists.append( (self.points[p[0],0]-roi.points[p[1],0])**2 + (self.points[p[0],1]-roi.points[p[1],1])**2)
        p=[-1,-1]
        dists.append((self.points[p[0],0]-roi.points[p[1],0])**2 + (self.points[p[0],1]-roi.points[p[1],1])**2)
        p=[-1,0]
        dists.append((self.points[p[0],0]-roi.points[p[1],0])**2 + (self.points[p[0],1]-roi.points[p[1],1])**2)
        p=[0,-1]
        dists.append((self.points[p[0],0]-roi.points[p[1],0])**2 + (self.points[p[0],1]-roi.points[p[1],1])**2)
        

        if dists[2]+dists[3] > dists[0]+dists[1]:
            roi.points = roi.points[::-1]

        self.points = np.append(roi.points,self.points,axis=0)


def mask2poly(mask, threshold=0.5):
    """Takes a mask and returns a MultiPolygon

    Parameters
    ----------
    mask : array
        Sparse or dense array to identify polygon contours within.
    threshold : float, optional
        Threshold value used to separate points in and out of resulting
        polygons. 0.5 will partition a boolean mask, for an arbitrary value
        binary mask choose the midpoint of the low and high values.

    Output
    ------
    MultiPolygon
        Returns a MultiPolygon of all masked regions.

    """

    if issparse(mask):
        mask = np.array(mask.astype('byte').todense())

    if (mask != 0).sum() == 0:
        raise Exception('Empty mask cannot be converted to polygons.')

    # Add an empty row and column around the mask to make sure edge masks
    # are correctly determined
    expanded_dims = (mask.shape[0] + 2, mask.shape[1] + 2)
    expanded_mask = np.zeros(expanded_dims, dtype=float)
    expanded_mask[1:mask.shape[0] + 1, 1:mask.shape[1] + 1] = mask

    verts = find_contours(expanded_mask.T, threshold)

    # Subtract off 1 to shift coords back to their real space,
    # but also add 0.5 to move the coordinates back to the corners,
    # so net subtract 0.5 from every coordinate
    verts = [np.subtract(x, 0.5).tolist() for x in verts]

    return _reformat_polygons(verts)



def poly2mask(polygons, im_size):
    """ ----- Copied from Sima.ROI -----
    
    Converts polygons to a sparse binary mask.

    >>> poly1 = [[0,0], [0,1], [1,1], [1,0]]
    >>> poly2 = [[0,1], [0,2], [2,2], [2,1]]
    >>> mask = poly2mask([poly1, poly2], (3, 3))
    >>> mask.todense()
    matrix([[ True, False, False],
            [ True,  True, False],
            [False, False, False]], dtype=bool)

    Parameters
    ----------
    polygons : sequence of coordinates or sequence of Polygons
        A sequence of polygons where each is either a sequence of (x,y)
        coordinate pairs, an Nx2 numpy array, or a Polygon object.
    im_size : tuple
        Final size of the resulting mask

    Output
    ------
    mask
        A sparse binary mask of the points contained within the polygons.

    """

    polygons = _reformat_polygons(polygons)
    mask = np.zeros(im_size, dtype=bool)
    for poly in polygons:
        x_min, y_min, x_max, y_max = poly.bounds

        # Shift all points by 0.5 to move coordinates to corner of pixel
        shifted_poly = Polygon(np.array(poly.exterior.coords)+0.5)

        points = [Point(x, y) for x, y in
                  product(np.arange(int(x_min), np.ceil(x_max)),
                          np.arange(int(y_min), np.ceil(y_max)))]
        points_in_poly = filter(shifted_poly.contains, points)
        for point in points_in_poly:
            x = int(point.x)
            y = int(point.y)
            if 0 <= y < im_size[0] and 0 <= x < im_size[1]:
                mask[y, x] = True
    return mask
    #return lil_matrix(mask)


def _reformat_polygons(polygons):
    """Convert polygons to a MulitPolygon

    Accepts one or more sequence of 2-element sequences (sequence of coords) or
    Polygon objects

    Parameters
    ----------
    polygons : sequence of coordinates or sequence of Polygons
        Polygon(s) to be converted to a MulitPolygon

    Returns
    -------
    MulitPolygon

    """
    if isinstance(polygons, MultiPolygon):
        return polygons
    if isinstance(polygons, Polygon):
        polygons = [polygons]
    elif isinstance(polygons[0], Polygon):
        pass
    else:
        # We got some sort of sequence of sequences, ensure it has the
        # correct depth and convert to Polygon objects
        try:
            Polygon(polygons[0])
        except (TypeError, AssertionError):
            polygons = [polygons]
        new_polygons = []
        for poly in polygons:
            # Polygon.simplify with tolerance=0 will return the exact same
            # polygon with co-linear points removed
            new_polygons.append(Polygon(poly).simplify(tolerance=0))
        polygons = new_polygons
    return MultiPolygon(polygons)
