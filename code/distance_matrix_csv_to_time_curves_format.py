import csv
import json
import datetime
import sys
import numpy as np

pcc_distance_matrix = 'pcc_distance_matrix.csv'
tau_distance_matrix = 'tau_distance_matrix.csv'
rho_distance_matrix = 'rho_distance_matrix.csv'
pcc_timecurve_json_filename = 'pcc_timecurve_from_distance_matrix.json'
tau_timecurve_json_filename = 'tau_timecurve_from_distance_matrix.json'
rho_timecurve_json_filename = 'rho_timecurve_from_distance_matrix.json'
pcc_name = 'PFM2 User Test Data (PCC Correlations)'
tau_name = 'PFM2 User Test Data (Kendall\'s Tau Correlations)'
rho_name = 'PFM2 User Test Data (Spearman\'s Rho Correlations)'

pcc_distance_matrix_simpler = 'pcc_distance_matrix_simpler.csv'
tau_distance_matrix_simpler = 'tau_distance_matrix_simpler.csv'
rho_distance_matrix_simpler = 'rho_distance_matrix_simpler.csv'
pcc_timecurve_json_filename_simpler = 'pcc_timecurve_from_distance_matrix_simpler.json'
tau_timecurve_json_filename_simpler = 'tau_timecurve_from_distance_matrix_simpler.json'
rho_timecurve_json_filename_simpler = 'rho_timecurve_from_distance_matrix_simpler.json'
pcc_name_simpler = 'PFM2 User Test Data (PCC Correlations, Simplified)'
tau_name_simpler = 'PFM2 User Test Data (Kendall\'s Tau Correlations, Simplified)'
rho_name_simpler = 'PFM2 User Test Data (Spearman\'s Rho Correlations, Simplified)'

pcc_distance_matrix_averaged = 'pcc_distance_matrix_averaged.csv'
tau_distance_matrix_averaged = 'tau_distance_matrix_averaged.csv'
rho_distance_matrix_averaged = 'rho_distance_matrix_averaged.csv'
pcc_timecurve_json_filename_averaged = 'pcc_timecurve_from_distance_matrix_averaged.json'
tau_timecurve_json_filename_averaged = 'tau_timecurve_from_distance_matrix_averaged.json'
rho_timecurve_json_filename_averaged = 'rho_timecurve_from_distance_matrix_averaged.json'
pcc_name_averaged = 'PFM2 User Test Data (PCC Correlations, Averaged in 5-Second Chunks)'
tau_name_averaged = 'PFM2 User Test Data (Kendall\'s Tau Correlations, Averaged in 5-Second Chunks)'
rho_name_averaged = 'PFM2 User Test Data (Spearman\'s Rho Correlations, Averaged in 5-Second Chunks)'

# Let's dump these out into a .json file for timecurve conversion
for input_distance_matrix_filename, output_json_filename, dataset_name in ((pcc_distance_matrix, pcc_timecurve_json_filename, pcc_name),
        (tau_distance_matrix, tau_timecurve_json_filename, tau_name),
        (rho_distance_matrix, rho_timecurve_json_filename, rho_name),
        (pcc_distance_matrix_simpler, pcc_timecurve_json_filename_simpler, pcc_name_simpler),
        (tau_distance_matrix_simpler, tau_timecurve_json_filename_simpler, tau_name_simpler),
        (rho_distance_matrix_simpler, rho_timecurve_json_filename_simpler, rho_name_simpler),
        (pcc_distance_matrix_averaged, pcc_timecurve_json_filename_averaged, pcc_name_averaged),
        (tau_distance_matrix_averaged, tau_timecurve_json_filename_averaged, tau_name_averaged),
        (rho_distance_matrix_averaged, rho_timecurve_json_filename_averaged, rho_name_averaged)):        
    # Load distance matrix from .csv file
    reader = csv.reader(open(input_distance_matrix_filename,"rb"),delimiter=',')
    distance_matrix = list(reader)
    print 'Loaded %s by %s matrix from %s' % (len(distance_matrix), len(distance_matrix[0]), input_distance_matrix_filename)
    # Convert to numpy matrix of floats
    distance_matrix = np.array(distance_matrix).astype('float')

    num_timesteps = distance_matrix.shape[0]

    json_dict = {}
    json_dict['distancematrix'] = distance_matrix.tolist()

    earliest_time = '02/28/2016 20:20:20'

    earliest_time_struct = datetime.datetime.strptime(earliest_time, "%m/%d/%Y %H:%M:%S") 

    times = [str(earliest_time_struct + datetime.timedelta(seconds=t)) for t in range(num_timesteps)]

    json_dict['data'] = [{'name': dataset_name, 'timelabels': times}]

    # Finally, write the .json file
    with open(output_json_filename, 'w') as outfile:
        json.dump(json_dict, outfile)
        print "Outputted time curve data to .json file (%s)" % output_json_filename