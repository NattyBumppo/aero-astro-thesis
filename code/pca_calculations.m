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

% Normalize data
standard_data_matrix = data_matrix - repmat(mean(data_matrix, 2), 1, size(data_matrix, 2));
standard_data_matrix = standard_data_matrix ./ repmat(std(standard_data_matrix, 0, 2), 1, size(data_matrix, 2));

% Clean up bad values
standard_data_matrix(isnan(standard_data_matrix)) = 0;
standard_data_matrix(isinf(standard_data_matrix)) = 0;

% Take the singular value decomposition of the covariance of the
% measurements
[U, S, V] = svd(standard_data_matrix);

% Plot the singular values
figure(4);
subplot(2,1,1);
plot(diag(S) / sum(diag(S)),'ko');
title('Singular Values of Raw Telemetry Test Data (non-log)');
ylabel('Magnitude');
xlabel('Order');

subplot(2,1,2);
semilogy(diag(S) / sum(diag(S)),'ko');
title('Singular Values of Raw Telemetry Test Data (log)');
ylabel('Magnitude');
xlabel('Order');

% Plot the principal modes of the system
%%%%%%%%%%%%%%%%%%

% Reduce to single-dimensional movement
reduced_S = zeros(size(S));
reduced_S(1:29,1:29) = S(1:29,1:29);

% Reconstruct using the reduced SVD
reduced_dynamics = U*reduced_S*V';