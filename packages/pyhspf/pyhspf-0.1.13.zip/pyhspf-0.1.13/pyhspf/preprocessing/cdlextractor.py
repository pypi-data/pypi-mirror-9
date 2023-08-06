# cdlextractor.py
#
# David J. Lampert, PhD, PE
#
# last updated: 10/12/2014
#
# Calculates the land use data from a raster file within each of the shapes
# in a shapefile.

import os, pickle, csv, zipfile, itertools, gdal, osr, numpy

from urllib          import request
from shapefile       import Reader
from PIL             import Image, ImageDraw
from matplotlib      import pyplot, patches, path, colors, ticker

from .rasterutils import get_pixel
from .rasterutils import get_raster
from .rasterutils import get_raster_table
from .rasterutils import get_raster_in_poly

class CDLExtractor:
    """A class to download and extract data from the Cropland Data Layer for
     a given state and period of years."""

    def __init__(self,
                 destination,
                 website = 'http://nassgeodata.gmu.edu/nass_data_cache/byfips',
                 ):

        self.destination = destination  # location of the raw CDL files
        self.website     = website      # web address of the CDL
        self.state       = None         # 2-character state abbreviation
        self.years       = []           # years with data
        self.categories  = None         # land use category key-value
        self.landuse     = {}           # dictionary of results
        self.order       = None         # aggregate data

        # make the destination directory if needed

        if not os.path.isdir(destination):

            print('destination directory for CDL data does not exist\n')

            try: 

                print('creating destination directory for CDL data\n')
                os.mkdir(destination)

            except:

                print('error, unable to create destination directory\n')
                raise

        # state codes

        self.statecodes = {
            'AL': '01',
            'AK': '02',
            'AZ': '04',
            'AR': '05',
            'CA': '06',
            'CO': '08',
            'CT': '09',
            'DC': '11',
            'DE': '10',
            'FL': '12',
            'GA': '13',
            'ID': '16',
            'IL': '17',
            'IN': '18',
            'IA': '19',
            'KS': '20',
            'KY': '21',
            'LA': '22',
            'ME': '23',
            'MD': '24',
            'MA': '25',
            'MI': '26',
            'MN': '27',
            'MS': '28',
            'MO': '29',
            'MT': '30',
            'NE': '31',
            'NV': '32',
            'NH': '33',
            'NJ': '34',
            'NM': '35',
            'NY': '36',
            'NC': '37',
            'ND': '38',
            'OH': '39',
            'OK': '40',
            'OR': '41',
            'PA': '42',
            'RI': '44',
            'SC': '45',
            'SD': '46',
            'TN': '47',
            'TX': '48',
            'UT': '49',
            'VT': '50',
            'VA': '51',
            'WA': '53',
            'WV': '54',
            'WI': '55',
            'WY': '56',
            }

    def is_number(self, s):
        """Test if the string is a number."""

        try: float(s) 
        except ValueError: return False
        return True

    def shape_to_mask(self, shape, width = 1000):
        """Converts a shapefile into a raster mask."""
        
        # separate the x and y values for the shape

        xs, ys = zip(*shape)

        x0 = min(xs)
        y0 = min(ys)

        # calculate the pixel height

        height = math.ceil((max(ys) - min(ys)) / (max(xs) - min(xs)) * width)

        # calculate the width and height of a pixel

        w = (max(xs) - min(xs)) / width
        h = (max(ys) - min(ys)) / height

        # convert points of the polygon to pixels

        pixel_polygon = [(get_pixel(x, x0, w), get_pixel(y, y0, h))
                         for x, y in zip(xs, ys)]

        # make a PIL image with the appropriate dimensions to use as a mask 

        rasterpoly = Image.new('L', (width, height), 1)
        rasterize  = ImageDraw.Draw(rasterpoly)

        # rasterize the polygon

        rasterize.polygon(pixel_polygon, 0)

        # convert the PIL array to numpy boolean to use as a mask

        mask = 1 - numpy.array(rasterpoly)

        return mask

    def poly_to_cdf(self, poly, n = 1000, dim = 'x'):
        """
        Determines the cumulative distribution function of the area of the 
        polygon (assumed to be made up of a list of points) in the chosen 
        dimension for "n" values.
        """

        # convert the points to xs and ys

        xs, ys = zip(*poly)

        if dim == 'x':

            # convert the points to a mask array of ones (in) and zeros (out)
        
            mask = shape_to_mask(poly, width = n)

            # get the total number of pixels in the shape

            tot = mask.sum()

            # iterate from left to right or top to bottom and get the fraction
            # inside as a function of x or y

            x0 = min(xs)
            delx = (max(xs) - min(xs)) / n
            xrange = [x0 + delx * i for i in range(n + 1)]
            fractions = [column.sum() / tot for column in mask.transpose()]

            cdf = [0]
            for f in fractions: cdf.append(cdf[-1] + f)

            return xrange, cdf

        elif dim == 'y':
            mask = shape_to_mask(poly, width = 1)

        else:
            print('error, unknown coordinate dimension, please specify x or y.')
            raise

    def report(self, 
               n, 
               block, 
               size,
               ):
        """Private method to report the status of the file download."""

        if n % 100 == 0:
            it = block * n / 10**6, size / 10**6
            print('{:.1f} MB of {:.1f} MB transferred'.format(*it))

    def download_data(self, 
                      state,
                      years,
                      ):

        self.state = state

        for year in years:

            # compressed filename on the CDL server

            webfile = 'CDL_{}_{}.zip'.format(year, self.statecodes[state])

            # path to compressed filename locally

            compressed = '{}/{}'.format(self.destination, webfile)

            # url to file on CDL server

            url = '{}/{}'.format(self.website, webfile)

            # download the compressed file if needed

            its = year, state
            if not os.path.isfile(compressed):

                print('downloading compressed file for {} {} '.format(*its) +
                      'from {}\n'.format(url))
                
                try: 

                    request.urlretrieve(url, compressed, self.report)

                except:

                    print('unable to download CDL data')
                    print('double-check that data are available for the ' +
                          'requested year')
                    return
                    
                print('')

            else: 

                print('compressed file for {} {} exists'.format(*its))

            # decompress the files

            its = self.destination, year, self.statecodes[state]
            decompressed = '{}/CDL_{}_{}.tif'.format(*its)
            if not os.path.isfile(decompressed):

                print('decompressing {} archive\n'.format(compressed))
                f = zipfile.ZipFile(compressed)
                f.extractall(self.destination)

            # keep track of all the years where the source files exist

            self.years.append(year)

    def extract_bbox(self,
                     bbox,
                     directory,
                     verbose = True,
                     ):
        """Extracts NASS CDL data from the source file for the bounding box."""
        
        # get the extents

        xmin, ymin, xmax, ymax = bbox

        # somwhat hack way to figure out the UTM

        UTM = int(numpy.floor((0.5 * xmin + 0.5 * xmax + 180) / 6) + 1)

        # extract the values for each year

        for year in self.years:

            its = self.destination, year, self.statecodes[self.state]
            decompressed = '{}/CDL_{}_{}.tif'.format(*its)
            output       = '{}/{}landuse.tif'.format(directory, year)

            # get the values of the raster and the origin

            values, corner = get_raster_table(decompressed, bbox, 'uint8')

            # get the source, source reference, and the source band

            source = gdal.Open(decompressed)
            source_band = source.GetRasterBand(1)

            # set the transform to the new origin

            transform = source.GetGeoTransform()
            transform = (corner[0], transform[1], transform[2], corner[1],
                         transform[4], transform[1])

            # get a driver and set the projection and georeference

            driver = gdal.GetDriverByName('GTiff')

            destination = driver.Create(output, 
                                        len(values[0]), 
                                        len(values), 
                                        1, 
                                        gdal.GDT_Byte)
            destination.SetGeoTransform(transform)
            destination.SetProjection(source.GetProjection())

            # set the metadata and get the destination band

            destination.SetMetadata(source.GetMetadata())
            destination_band = destination.GetRasterBand(1)

            # copy the pertinent attributes to the band

            destination_band.WriteArray(values, 0, 0)
            destination_band.SetColorTable(source_band.GetColorTable().Clone())

            # transform the projection from WGS 1984 to NAD 1983 
            # (needs to be done)

            # close up the files

            source      = None
            destination = None

        if verbose: print('successfully extracted cropland data to new file\n')

    def extract_shapefile(self, 
                          shapefile,
                          directory,
                          space = 0.05,
                          ):
        """Extracts the cropland data for the bounding box of the shapefile."""

        if not os.path.isdir(directory): 
            print('error, specified output directory does not exist\n')
            raise

        r = Reader(shapefile)

        xmin, ymin, xmax, ymax = r.bbox

        # adjust to make the map just larger than the extents

        xmin, xmax = xmin - space * (xmax - xmin), xmax + space * (xmax - xmin)
        ymin, ymax = ymin - space * (ymax - ymin), ymax + space * (ymax - ymin)

        self.extract_bbox((xmin, ymin, xmax, ymax), directory)

    def read_aggregatefile(self, aggregatefile):

        with open(aggregatefile, 'r') as csvfile:
            reader = csv.reader(csvfile)
            rows = [row for row in reader][1:]

        # the columns in the aggregate file should be:
        #
        # raster uint8 code
        # CDL land use category
        # HSPF land use category (to allow grouping)
        # RGB "red" value (for plotting)
        # RGB "green" value (for plotting)
        # RGB "blue" value (for plotting)

        columns = [column for column in zip(*rows)]

        self.categories = {int(i):c  for i,c in zip(columns[0], columns[1])}
        self.groups     = {int(i):g  for i,g in zip(columns[0], columns[2])}
        self.reds       = {i:int(r)  for i,r in zip(columns[2], columns[3])}
        self.greens     = {i:int(g)  for i,g in zip(columns[2], columns[4])}
        self.blues      = {i:int(b)  for i,b in zip(columns[2], columns[5])}

        # make and preserve a unique, ordered list of the groups

        seen = set()
        self.order = [i for i in columns[2] if not (i in seen or seen.add(i))]

    def calculate_landuse(self, 
                          rasterfile,
                          shapefile, 
                          aggregatefile, 
                          attribute,
                          csvfile = None,
                          ):
        """
        Calculates the land use for the given year for the "attribute" 
        feature attribute in the polygon shapefile using the aggregate 
        mapping provided in the "aggregatefile."
        """

        for f in rasterfile, shapefile + '.shp', aggregatefile:
            if not os.path.isfile(f):
                print('error, {} does not exist'.format(f))
                raise

        # read the aggregate file

        self.read_aggregatefile(aggregatefile)

        # open the shapefile

        sf = Reader(shapefile, shapeType = 5)

        attributes = [f[0] for f in sf.fields]

        try:    index = attributes.index(attribute) - 1
        except: 
            print('error: attribute ' +
                  '{} is not in the shapefile fields'.format(attribute))
            raise

        # iterate through the shapes, get the fractions and save them

        for i in range(len(sf.records())):

            points = numpy.array(sf.shape(i).points)
            record = sf.record(i)

            k = record[index]

            # store the results

            self.landuse[k] = {r:0 for r in self.order}

            try:

                values, origin = get_raster_in_poly(rasterfile, points, 
                                                    verbose = False)
                values = values.flatten()
                values = values[values.nonzero()]

                tot_pixels = len(values)

                # count the number of pixels of each land use type
                                   
                for v in numpy.unique(values):

                    # find all the indices for each pixel value

                    pixels = numpy.argwhere(values == v)
                    
                    # normalize by the total # of pixels

                    f = len(values[pixels]) / tot_pixels
                    
                    # add the landuse to the aggregated value

                    self.landuse[k][self.groups[v]] += f
    
            # work around for small shapes
            
            except: self.landuse[k][self.groups[0]] = 1

        if csvfile is not None:  self.make_csv(attribute, csvfile)

        return self.landuse

    def make_csv(self, attribute, output):

        with open(output, 'w', newline = '') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Catchment Land Use Fractions'])
            writer.writerow([''])

            row = [attribute] + self.order
            writer.writerow(row)

            for k,d in self.landuse.items():
                row = [k] + [d[r] for r in self.order]
                writer.writerow(row)

    def make_patch(self, points, facecolor, edgecolor = 'Black', width = 1, 
                   alpha = None, hatch = None, label = None):
        """Uses a list or array of points to generate a matplotlib patch."""

        vertices = [(point[0], point[1]) for point in points]
        vertices.append((points[0][0], points[0][1]))

        codes     = [path.Path.LINETO for i in range(len(points) + 1)]
        codes[0]  = path.Path.MOVETO

        patch = patches.PathPatch(path.Path(vertices, codes), 
                                  facecolor = facecolor,
                                  edgecolor = edgecolor, 
                                  lw = width, 
                                  hatch = hatch,
                                  alpha = alpha, 
                                  label = label)

        return patch

    def plot_landuse(self,
                     landuse,
                     catchments,
                     attribute,
                     output = None, 
                     datatype = 'raw', 
                     overwrite = False,
                     pixels = 1000,
                     border = 0.02,
                     lw = 0.5,
                     show = False,
                     verbose = True, 
                     vverbose = False
                     ):
        """
        Makes a plot of the landuse of a catchment shapefile on top of a
        raster landuse file.
        """

        if self.order is None:
            print('error: no aggregate file information specified')
            raise Exception

        if verbose: print('generating land use plot\n')

        # make the figure

        fig = pyplot.figure()
        subplot = fig.add_subplot(111, aspect = 'equal')
        subplot.tick_params(axis = 'both', which = 'major', labelsize = 11)

        # add the title

        if datatype == 'results': title = 'Land Use Fractions'
        else:                     title = 'Raw Land Use Data'

        subplot.set_title(title, size = 14)

        # open the shapefile and get the bounding box

        s = Reader(catchments, shapeType = 5)

        xmin, ymin, xmax, ymax = s.bbox

        # get the index of the field for the attribute matching

        index = [f[0] for f in s.fields].index(attribute) - 1

        # set up a custom colormap using the rgbs supplied in the aggregate file

        color_table = [(self.reds[g] / 255, self.greens[g] / 255, 
                        self.blues[g] / 255) for g in self.order]
            
        cmap = colors.ListedColormap(color_table)
        
        # provide the cutoff boundaries for the mapping of values to the table

        bounds = [i-0.5 for i in range(len(self.order)+1)]

        # create a norm to map the bounds to the colors

        norm = colors.BoundaryNorm(bounds, cmap.N)

        # get the pixel width and origin

        w = (xmax - xmin) / pixels

        # calculate the image array height and the height of a pixel

        height = int(numpy.ceil((ymax - ymin) / (xmax - xmin)) * pixels)
        h = (ymax - ymin) / height

        # set up the image array

        image_array = numpy.zeros((height, pixels), dtype = 'uint8')

        # get the land use fraction for each category

        if datatype == 'results': 

            # iterate through the shapes and make patches

            for i in range(len(s.records())):
                comid = s.record(i)[index]
                points = numpy.array(s.shape(i).points)

                # convert the shape to pixel coordinates

                pixel_polygon = [(get_pixel(x, xmin, w), get_pixel(y, ymin, h))
                                 for x, y in points]

                # make a PIL image to use as a mask 

                rasterpoly = Image.new('L', (pixels, height), 1)
                rasterize  = ImageDraw.Draw(rasterpoly)

                # rasterize the polygon

                rasterize.polygon(pixel_polygon, 0)

                # convert the PIL array to numpy boolean to use as a mask

                mask = 1 - numpy.array(rasterpoly)

                # get the total number of pixels in the shape

                tot = mask.sum()

                # iterate from left to right and get the fraction of the total 
                # area inside the shape as a function of x (takes into account 
                # the depth)

                fractions = [column.sum() / tot for column in mask.transpose()]
                area_cdf  = [sum(fractions[:i+1]) 
                             for i in range(len(fractions))]

                # convert the land use fractions into a land use cdf

                fractions = [self.landuse[comid][g] for g in self.order]
                land_cdf = [sum(fractions[:i+1]) for i in range(len(fractions))]

                # use the area cdf to determine the break points for the land 
                # use patches. note this array does not account for the masking 
                # of the patch. thus there are n+1 vertical bands. the first 
                # and last are the "empty" (first in the aggregate file). in 
                # between the break points are determined from the area cdf.

                color_array = numpy.zeros(len(mask[0]), dtype = 'uint8')

                # find the break point for each band by looping through the land
                # ues cdf and filling from left to right

                i = 0
                for p, n in zip(land_cdf, range(len(self.order))):

                    # move from left to right nuntil the area_cdf exceeds 
                    # the land area cdf

                    while area_cdf[i] <= p: 
                        color_array[i] = n
                        if i < len(area_cdf) - 1: i += 1
                        else: break

                # multiply the color band array by the mask to get the img

                sub_img = mask * color_array

                # add the new mask to the watershed image

                image_array = image_array + sub_img

                # add a patch for the shape boundary

                subplot.add_patch(self.make_patch(points, (1,0,0,0), width=lw))

            # show the bands

            bbox = s.bbox[0], s.bbox[2], s.bbox[1], s.bbox[3]
            im = subplot.imshow(image_array, extent = bbox, 
                                origin = 'upper left', 
                                interpolation = 'nearest', 
                                cmap = cmap, norm = norm)

            # adjust the plot bounding box 

            xmin, xmax = xmin-border * (xmax-xmin), xmax + border * (xmax-xmin)
            ymin, ymax = ymin-border * (ymax-ymin), ymax + border * (ymax-ymin)

        else:

            # adjust the plot bounding box 

            xmin, xmax = xmin-border * (xmax-xmin), xmax + border * (xmax-xmin)
            ymin, ymax = ymin-border * (ymax-ymin), ymax + border * (ymax-ymin)

            # pixel width in latitude

            pw = (xmax - xmin) / pixels

            # calculate the image height in pixels

            ny = int(numpy.ceil((ymax - ymin) / (xmax - xmin) * pixels))

            # note the height of pixels = width of pixels
            # and image width in pixels is "pixels"

            xs = numpy.array([xmin + (i + 0.5) * pw for i in range(pixels)])
            ys = numpy.array([ymin + (i + 0.5) * pw for i in range(ny)])

            # set up an array of values for the image

            zs = numpy.zeros((ny, pixels))

            for i in range(len(ys)):
                ps = [(x, ys[i]) for x in xs]
                zs[i, :] = numpy.array(get_raster(landuse, ps, quiet = True))

            zs = zs.astype(int)

            tot = zs.size

            for v in numpy.unique(zs):
                group = self.groups[v]
                i = self.order.index(group)
                zs[numpy.where(zs == v)] = i
                
            # plot the grid

            im = subplot.imshow(zs,
                                interpolation = 'nearest',
                                origin = 'upper left',
                                extent = [xmin, xmax, ymin, ymax], 
                                norm = norm, 
                                cmap = cmap,
                                )

            # add patch for the shape boundary

            for shape in s.shapes():
                points = numpy.array(shape.points)
                subplot.add_patch(self.make_patch(points, (1,0,0,0), width=0.5))

        # add the legend using a dummy box to make patches for the legend

        dummybox = [[0,0], [0,1], [1,1], [1,0], [0,0]]
        handles, labels = [], []
        for group, color in zip(self.order[1:], color_table[1:]):
            p = self.make_patch(dummybox, facecolor = color, width = 0)
            handles.append(subplot.add_patch(p))
            labels.append(group)

        leg = subplot.legend(handles, labels, bbox_to_anchor = (1.0, 0.5), 
                             loc = 'center left', title = 'Land Use Categories')
        legtext = leg.get_texts()
        pyplot.setp(legtext, fontsize = 10)
        subplot.set_position([0.125, 0.1, 0.6, 0.8])

        # add the labels and set the limits

        subplot.set_xlabel('Longitude, Decimal Degrees', size = 13)
        subplot.set_ylabel('Latitude, Decimal Degrees',  size = 13)

        subplot.set_xlim([xmin, xmax])
        subplot.set_ylim([ymin, ymax])

        subplot.xaxis.set_major_locator(ticker.MaxNLocator(8))
        subplot.yaxis.set_major_locator(ticker.MaxNLocator(8))

        subplot.xaxis.set_major_formatter(ticker.FormatStrFormatter('%.2f'))
        subplot.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.2f'))

        # show it

        if output is not None: pyplot.savefig(output)
        if show: pyplot.show()

        pyplot.clf()
        pyplot.close()
