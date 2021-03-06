% Initial cleanup
close all;
clear;
clc;

% Load bucketed telemetry data
data_matrix = csvread('one_second_bucketed_telem_output.csv');
channel_count = size(data_matrix,1);
timestep_count = size(data_matrix,2);

% Size of the window in which to calculate the correlation
corr_window = 15;

% Matrices to hold changing PCC, Tau, and Rho correlations over time
pcc_corr_over_time = zeros(channel_count^2, timestep_count - corr_window + 1);
tau_corr_over_time = zeros(channel_count^2, timestep_count - corr_window + 1);
rho_corr_over_time = zeros(channel_count^2, timestep_count - corr_window + 1);

% Let's generate correlation data at each time step. We'll advance at
% the rate of one second per step, and we'll look back to get the
% instantaneous correlation based on the last corr_window measurements. This means
% we'll start at corr_window seconds in.
disp('Calculating correlation data for each time step:');
for step = corr_window:timestep_count,
   disp(step);
   % Generate a slice of the data matrix using the last corr_window measurements
   data_matrix_slice = data_matrix(:, step-corr_window+1:step);
   
   % Generate Pearson correlation coefficient
    corr_mx_pcc = corr(data_matrix_slice', 'type', 'Pearson');
    % Generate Kendall's tau
    corr_mx_tau = corr(data_matrix_slice', 'type', 'Kendall');
    % Generate Spearman's rho
    corr_mx_rho = corr(data_matrix_slice', 'type', 'Spearman');
    
    % Unroll each of the correlation matrices and put into a matrix
    pcc_corr_over_time(:, step-corr_window+1) = reshape(corr_mx_pcc, [], 1);
    tau_corr_over_time(:, step-corr_window+1) = reshape(corr_mx_tau, [], 1);
    rho_corr_over_time(:, step-corr_window+1) = reshape(corr_mx_rho, [], 1);
end

% Anything that had a standard deviation of 0 will have a NaN correlation,
% which screws us up. Let's replace NaN correlations with 0.
pcc_corr_over_time(isnan(pcc_corr_over_time)) = 0;
tau_corr_over_time(isnan(tau_corr_over_time)) = 0;
rho_corr_over_time(isnan(rho_corr_over_time)) = 0;

% Square correlation values to make them stand out more (preserve signs)
pcc_corr_over_time = (pcc_corr_over_time.^2) .* sign(pcc_corr_over_time);
tau_corr_over_time = (tau_corr_over_time.^2) .* sign(tau_corr_over_time);
rho_corr_over_time = (rho_corr_over_time.^2) .* sign(rho_corr_over_time);

% Create distance matrices for time points
pcc_distance_matrix = zeros(timestep_count - corr_window + 1);
tau_distance_matrix = zeros(timestep_count - corr_window + 1);
rho_distance_matrix = zeros(timestep_count - corr_window + 1);

disp('Calculating distance matrices:');

% Now, we'll fill in these distance matrices
for i = 1:timestep_count - corr_window + 1,
    for j = 1:timestep_count - corr_window + 1,
        % Fill in the cell of each of the distance matrices at (i, j)
        pcc_distance = norm(pcc_corr_over_time(:, i) - pcc_corr_over_time(:, j));
        tau_distance = norm(tau_corr_over_time(:, i) - tau_corr_over_time(:, j));
        rho_distance = norm(rho_corr_over_time(:, i) - rho_corr_over_time(:, j));
        
        pcc_distance_matrix(i, j) = pcc_distance;
        tau_distance_matrix(i, j) = tau_distance;
        rho_distance_matrix(i, j) = rho_distance;
    end
    disp(i);
end

% These distance matrices will be used to generate .csv files, which we'll
% load in Python and use to generate our file .csv files.
pcc_distance_matrix_file = 'pcc_distance_matrix.csv';
tau_distance_matrix_file = 'tau_distance_matrix.csv';
rho_distance_matrix_file = 'rho_distance_matrix.csv';

% Write files
csvwrite(pcc_distance_matrix_file, pcc_distance_matrix);
csvwrite(tau_distance_matrix_file, tau_distance_matrix);
csvwrite(rho_distance_matrix_file, rho_distance_matrix);