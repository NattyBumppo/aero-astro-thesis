import csv
from sets import Set
import datetime
import json
import sys
import numpy as np

telem_filename = 'telem.csv'
timecurve_json_filename = 'timecurve_test_dummy_data.json'
dataset_name = 'PFM2 User Test Data'

# Gets a "distance" between two arrays of values
def get_distance(arr1, arr2):
    # print "diffing:"
    # print "1: %s" % arr1
    # print "2: %s" % arr2

    return np.linalg.norm(arr1 - arr2)

# Take an array, and "standardizes" it by subtracting the mean then
# dividing by the standard deviation
def standardize(arr):
    # print "Working on array: %s" % str(arr)
    mean = np.mean(arr)
    stddev = np.std(arr)

    if stddev == 0:
        return arr
    else:
        # print "Mean: %s" % str(mean)
        # print "Std dev: %s" % str(stddev)
        # print "Returning %s" % str((arr - mean) / stddev)

        return (arr - mean) / stddev

with open(telem_filename, 'rb') as csvfile:
    csv_reader = csv.reader(csvfile)

    channel_names = Set()

    # First, just grab the channel names
    for row in csv_reader:
        # Parse out data
        channel_name = row[0]

        channel_names.add(channel_name)

    # Now, make channel_names a list to ensure the ordering doesn't change
    channel_names = list(channel_names)

    print "Collected names of %s distinct data channels." % len(channel_names)
    # for channel_name in channel_names:
    #     print channel_name

# Initialize this value so it'll be global
earliest_time_struct = None

with open(telem_filename, 'rb') as csvfile:
    csv_reader = csv.reader(csvfile)    

    # Now that we have channel names, let's make data entries for the entire state
    # of the system at each second interval. Let's start by ingesting all of
    # the data and then looking it by the timestamps.
    data_points = []
    for row in csv_reader:
        channel_name = row[0]
        value = row[1]
        timestamp = row[2]
        fault_level = row[3]

        # We won't worry about ingesting the fault_level for this
        # (we might use it later...)
        data_points.append((timestamp, channel_name, value))

    print "Processed data for %s data points." % len(data_points)
    print
    
    # Sort time points
    data_points = sorted(data_points, key=lambda x: x[0])
    
    print "Extracted and sorted data points by time. See below for a few examples:"
    print data_points[0]
    print data_points[1]
    print data_points[2]
    print '...'
    print data_points[-3]
    print data_points[-2]
    print data_points[-1]
    print

    # Now, let's coalesce points into buckets to reduce their size
    earliest_time = data_points[0][0]
    earliest_time_struct = datetime.datetime.strptime(earliest_time, "%m/%d/%Y %H:%M:%S") 

    latest_time = data_points[-1][0]
    latest_time_struct = datetime.datetime.strptime(latest_time, "%m/%d/%Y %H:%M:%S")

    # Calculate difference and make buckets
    timespan = latest_time_struct - earliest_time_struct
    timespan_seconds = timespan.total_seconds()
    print "Total elapsed seconds of data:", timespan_seconds
    print

    # Divide up timespan into interval seconds-sized buckets
    time_bucket_size = 5
    time_bucket_data = {}

    for floor in xrange(0, int(timespan_seconds)+1, time_bucket_size):
        # Initialize with an empty dictionary mapping channel names to a list of data values
        time_bucket_data[floor] = {channel_name: [] for channel_name in channel_names}

    # Now we'll go through all of the data points and dump them into the buckets
    for data_point in data_points:
        time_string = data_point[0]
        time_struct = datetime.datetime.strptime(time_string, "%m/%d/%Y %H:%M:%S") 
        timestamp_seconds = (time_struct - earliest_time_struct).total_seconds()
        bucketed_timestamp = int(timestamp_seconds - timestamp_seconds % time_bucket_size)

        # Now, add a value for the channel name in this timestamp bucket
        channel_name = data_point[1]
        value = float(data_point[2])

        time_bucket_data[bucketed_timestamp][channel_name].append(value)

    # Now, go through and coalesce (average) all data
    for time_bucket_floor in xrange(0, int(timespan_seconds)+1, time_bucket_size):
        for channel_name in (time_bucket_data[time_bucket_floor].keys()):
            # Replace each list of values with the average of the values
            values = time_bucket_data[time_bucket_floor][channel_name]
            if len(values) > 0:
                # print "setting ", time_bucket_data[time_bucket_floor][channel_name]
                time_bucket_data[time_bucket_floor][channel_name] = float(sum(values)) / float(len(values))
            else:
                # No values... take the value for the previous timestep, if there is one
                if time_bucket_floor != 0:
                    time_bucket_data[time_bucket_floor][channel_name] = time_bucket_data[time_bucket_floor - time_bucket_size][channel_name]
                else:
                    # Otherwise, just zero out the data
                    time_bucket_data[time_bucket_floor][channel_name] = 0.0

    # Now, time_bucket_data contains all of the averaged, bucketed data. This is great!!
    # Let's start treating this data as matrix data, so we can do some numerical things
    # to it. First, let's make an n x t matrix, where n is the number of data channels,
    # and t is the number of timesteps.

    num_channels = len(channel_names)
    data_matrix_initialized = False

    # We'll make each timestamp into a column vector
    for time_bucket_floor in time_bucket_data.keys():
        data_vector = np.empty((num_channels, 1))

        # We'll iterate using the channel name list so we're always using the same channel ordering
        for i, channel_name in enumerate(channel_names):
            # print 'i:', i
            # print 'channel_name:', channel_name
            # print 'time_bucket_floor:', time_bucket_floor
            # print 'time_bucket_data[time_bucket_floor][channel_name]:', time_bucket_data[time_bucket_floor][channel_name]
            data_vector[i, 0] = time_bucket_data[time_bucket_floor][channel_name]

        # Now that we've filled up a vector, let's append it to the data matrix
        if not data_matrix_initialized:
            data_matrix = data_vector
            data_matrix_initialized = True
        else:
            # print "data_vector size: %s" % str(data_vector.shape)
            # print "data_matrix size: %s" % str(data_matrix.shape)
            data_matrix = np.hstack((data_matrix, data_vector))

    print "Combined all data into a giant matrix."
    print "Size of assembled data matrix: %s" % str(data_matrix.shape)
    print "First few values of %s from data matrix:" % channel_names[0]
    print str(data_matrix[0,:5])
    print

    # Finally, we need to normalize using the mean and variance of each row,
    # in order to be able to calculate "distances" in an unbiased way
    standardized_data_matrix = np.apply_along_axis(standardize, 1, data_matrix)

    print "Standardardized data matrix."
    print "Size of assembled data matrix: %s" % str(standardized_data_matrix.shape)
    print "First few values of %s from data matrix:" % channel_names[0]
    print str(standardized_data_matrix[0,:5])
    print

    # print str(data_matrix[0,:])
    # print str(np.mean(data_matrix[0,:]))
    # print str(np.std(data_matrix[0,:]))
    # print str(standardized_data_matrix[0,:])

    # Now we've standardardized the data matrix! Heck yeah!
    # For our last trick, we'll make a symmetric distance matrix (where
    # the value at n x m shows the "distance" between column n and column m)
    num_timesteps = standardized_data_matrix.shape[1]
    distance_matrix = np.empty((num_timesteps, num_timesteps))

    for (col_num, row_num), value in np.ndenumerate(distance_matrix):
        # print 'Trying to fill in spot at row %s, col %s' % (row_num, col_num)
        distance_matrix[row_num, col_num] = get_distance(standardized_data_matrix[:, row_num], standardized_data_matrix[:, col_num])

    # Now, we're done generating our distance matrix
    print "Distance matrix generated. Here's a snippet:"
    print str(distance_matrix[:5, :5])
    print

    # Let's dump this out into a .json file for timecurve conversion
    json_dict = {}
    json_dict['distancematrix'] = distance_matrix.tolist()

    times = [str(earliest_time_struct + datetime.timedelta(seconds=t)) for t in sorted(time_bucket_data.keys())]

    json_dict['data'] = [{'name': dataset_name, 'timelabels': times}]

    # Finally, write the .json file
    with open(timecurve_json_filename, 'w') as outfile:
        json.dump(json_dict, outfile)
        print "Outputted time curve data to .json file (%s)" % timecurve_json_filename