#Citibike_Heatmap

##A python project for creating an animated heap map of historical NYC CitiBike data.

[Citibike](https://www.citibikenyc.com/) is NYC's new(ish) and very popular bike share program. Citibike customers can take a bike from any station, and leave it at any other station. It's natural to assume that after some time, certain areas of the city will end up with a high density of bikes, and others areas will have few bikes. Moreover, this relative density is likely to fluctuate in both space and time.

This project is an attempt to visualize the approximate density of available bikes throughout the day, using Citibike's own system data available at: http://citibikenyc.com/system-data

###Technical Details:

This project uses the [wonderful Pandas data analysis library](http://pandas.pydata.org/) for data cleaning, formatting and analysis. To visualize the movement of Citibikes, it builds a [Matplotlib](http://matplotlib.org/) figure. To assist in the creation of the heatmap, I used [Numpy](http://www.numpy.org/) and some techniques borrowed from [this StackOverflow question](http://stackoverflow.com/questions/6652671/efficient-method-of-calculating-density-of-irregularly-spaced-points). 

###Please visit [this iPython notebook](http://nbviewer.ipython.org/github/beneverson/Citibike_Heatmap/blob/master/Citibike-Heatmap.ipynb) for a more in-depth look at this project.

