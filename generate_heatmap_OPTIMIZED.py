import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.figure as fig
import datetime as dt
import scipy.ndimage as ndi
from mpl_toolkits.basemap import Basemap
from scipy import misc
from matplotlib.colors import LinearSegmentedColormap
from copy import copy, deepcopy

# generate a map of the 'undocking' (blue) and 're-docking' (red) events in the 
# citibike system as a function of time

# define a grid-density gaussian filter algorithm
# adapted from: http://stackoverflow.com/questions/6652671/efficient-method-of-calculating-density-of-irregularly-spaced-points\

# return the gaussian filtered data for a given current_img
def grid_density_gaussian_filter_img(current_img, radius):
		r = radius
		return ndi.gaussian_filter(current_img, (r,r)) #apply gaussian filter to the image and return the ndimage

def decay_img(current_img): # go through and bring all image data closer to zero
		for index,value in np.ndenumerate( current_img ):
			if value > 0:
				current_img[index] -= 1
			if value < 0:
				current_img[index] += 1
		return current_img
			
# add 'positive_data' and subtract 'negative data' to previous_img and return a new image with those values
def iterate_image(previous_img, x0, y0, x1, y1, w, h, positive_data, negative_data):
		imgw = previous_img.shape[0]
		imgh = previous_img.shape[1]
		new_img = copy(previous_img)
		kx = (imgw - 1) / (x1 - x0)
		ky = (imgh - 1) / (y1 - y0)
		for x, y in positive_data:
				ix = int((x - x0) * kx) 
				iy = int((y - y0) * ky)
				if 0 <= ix < imgw and 0 <= iy < imgh:
					new_img[iy][ix] += 1
		for x, y in negative_data:
				ix = int((x - x0) * kx)
				iy = int((y - y0) * ky)
				if 0 <= ix < imgw and 0 <= iy < imgh:
					new_img[iy][ix] -= 1
		return new_img

#----------------------------------------------------- CONSTANTS -----------------------------------
# the path to the citibike data
data_path = '2013-07-CitiBikeTripData.csv'

# time increment stuff
number_of_days = 3 # the number of days worth of data that should be used in the visualization
time_increment = 5 # the amount of time (minutes) by which we step forward each frame of the animation
time_window_size = 10 # the size of the time window we look at each frame

#boundary values for the map
lon0 = -74.0417
lon1 = -73.8982
lat0 = 40.6851
lat1 = 40.7721

# size and filter constants for the image
image_width = 200
image_height = 200
gaussian_filter_radius = 3
#---------------------------------------------------------------------------------------------------


# ++++++++++++++++++++++++create a custom colormap to overlay on the map++++++++++++++++++++++++++++
bwr_cmap = plt.get_cmap('bwr')
cdict_new = bwr_cmap._segmentdata.copy()
cdict_new['alpha'] = ((0.0, 1.0, 1.0),
                #   (0.25,1.0, 1.0),
                   (0.6, 0.4, 0.0),
                #   (0.75,1.0, 1.0),
                   (1.0, 1.0, 1.0))
blue_red1 = LinearSegmentedColormap('BlueRed1', cdict_new)
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

## Instantiate the Basemap - all subsequent images will be applied directly to the map. 
m = Basemap(llcrnrlon=lon0, llcrnrlat=lat0, urcrnrlon=lon1, urcrnrlat=lat1, resolution='l', lat_0=lat0, lon_0=lon0)
# grab the openstreetmaps image
osm_image = misc.imread('map.png')
#plot it onto the map
m.imshow(osm_image, extent=[lon0, lat0, lon1, lat1], origin='upper', aspect='auto')
##

## READ THE DATA: 
# read in the undocking data
undocking_dataframe = pd.read_csv('2013-07-CitiBikeTripData.csv', usecols=[1,5,6], index_col=0, parse_dates=True)
#read in the docking datax
docking_dataframe_unsorted = pd.read_csv('2013-07-CitiBikeTripData.csv', usecols=[2,9,10], index_col=0, parse_dates=True)
docking_dataframe = docking_dataframe_unsorted.sort_index()

# find the first timestamp
initial_start_date_undocking = undocking_dataframe.index[0]

# ims will hold the series of images that make up the animation
ims = []
# determine the number of frames in the animation
num_frames = number_of_days*24*60/time_increment
#animation function: this is called sequentially
for i in range(num_frames):
	# find the indices of the next time windows for undocking events
	next_start_date_undocking_index = undocking_dataframe.index.searchsorted( initial_start_date_undocking + dt.timedelta(minutes=time_increment*i) )
	next_end_date_undocking_index = undocking_dataframe.index.searchsorted( initial_start_date_undocking + dt.timedelta(minutes=(time_window_size + time_increment*i) ) )
	# grab the next time windows for undocking events
	next_start_date_undocking = undocking_dataframe.index[next_start_date_undocking_index]
	next_end_date_undocking = undocking_dataframe.index[next_end_date_undocking_index]
	
	# find the indices of the next time windows for re-docking events
	next_start_date_docking_index = docking_dataframe.index.searchsorted( next_start_date_undocking )
	next_end_date_docking_index = docking_dataframe.index.searchsorted( next_end_date_undocking )
	# grab the next time windows for undocking events
	next_start_date_docking = docking_dataframe.index[next_start_date_docking_index]
	next_end_date_docking = docking_dataframe.index[next_end_date_docking_index]
	
	# get the next few undocking events
	next_data_undocking = undocking_dataframe[next_start_date_undocking:next_end_date_undocking]
	x_udata = next_data_undocking['start station longitude']
	y_udata = next_data_undocking['start station latitude']
	x_undocking, y_undocking = m(x_udata,y_udata)
	
	# get the next few docking events
	next_data_docking = docking_dataframe[next_start_date_docking:next_end_date_docking]
	x_ddata = next_data_docking['end station longitude']
	y_ddata = next_data_docking['end station latitude']
	x_docking, y_docking = m(x_ddata,y_ddata)	
	
	# get the new heatmap image
	if i == 0:
		new_heatmap_image = np.zeros((image_width, image_height))
	else:
		new_heatmap_image = iterate_image(heatmap_image, lon0, lat0, lon1, lat1, image_width, image_height, zip(x_docking,y_docking), zip(x_undocking,y_undocking))
	
	if i % 100 == 0:
	 new_heatmap_image = decay_img(new_heatmap_image)
		
	# generate the z dimension with the newlt iterated image
	z_dimension = grid_density_gaussian_filter_img(new_heatmap_image, gaussian_filter_radius)
	
	#reset the heatmap_image variable
	heatmap_image = new_heatmap_image
	
	# produce the im from this data
	heatmap_im = m.imshow(z_dimension , origin='lower', extent=[lon0, lat0, lon1, lat1], alpha=.4, vmin=-1, vmax=1, cmap=blue_red1, aspect='auto')
	# find the text string for displaying time/date
	current_date = initial_start_date_undocking + dt.timedelta(minutes=time_increment*i)
	current_date_string = current_date.strftime('%I:%M%p on %a %b %d')
	current_date_plotted = plt.text(-73.9509, 40.6909, current_date_string, fontsize=14)
	# append it to the array of drawn images
	ims.append([current_date_plotted,heatmap_im])

# set the figure size
plt.gcf().set_size_inches(15.0, 12.0)
plt.gcf().subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=None, hspace=None

# run the animation	
anim = animation.ArtistAnimation(plt.gcf(), ims, interval=50, blit=True, repeat=True)

#plot all of these points
plt.show()

	

