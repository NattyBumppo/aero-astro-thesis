% Initial cleanup
close all;
clear;
clc;

% Make a random matrix of data channel values
channel_count = 6;
time_slots = 8;
channel_data_rand = rand(channel_count, time_slots);

% Make purposefully interesting channel data
channel1_data = [0 10 101 102 0 10 101 400];
channel2_data = 4 * ones(1, 8) + rand(1, 8)*0.5;
channel3_data = 6 * ones(1, 8) + rand(1, 8)*0.3;
channel4_data = [1.2 2.3 3.4 4.4 4.5 3.5 2.2 1.1];
channel5_data = -[10 20 30 40 40 30 20 10];
channel6_data = [1 2 500 2000 1 100 200 201];

channel_data = [channel1_data; channel2_data; channel3_data; channel4_data; channel5_data; channel6_data];

% Generate Pearson correlation coefficient
corr_mx_pcc = corr(channel_data', 'type', 'Pearson');
% Generate Kendall's tau
corr_mx_tau = corr(channel_data', 'type', 'Kendall');
% Generate Spearman's rho
corr_mx_rho = corr(channel_data', 'type', 'Spearman');

% Make a colormap to color the grids (from blue to white to red)
Rs = [linspace(0.0, 1.0, 16) linspace(1.0, 1.0, 16)];
Gs = [linspace(0.0, 1.0, 16) linspace(1.0, 0.0, 16)];
Bs = [linspace(1.0, 1.0, 16) linspace(1.0, 0.0, 16)];
map = [Rs' Gs' Bs'];

% Plot PCC
figure(1)
imagesc(corr_mx_pcc);
colormap(map);
colorbar;
title('PCC Correlation Map Example');
xlabel('Data Channels');
ylabel('Data Channels');

% Plot tau
figure(2)
imagesc(corr_mx_tau);
colormap(map);
colorbar;
title('Kendall''s Tau Correlation Map Example');
xlabel('Data Channels');
ylabel('Data Channels');

% Plot rho
figure(3)
imagesc(corr_mx_rho);
colormap(map);
colorbar;
title('Spearman''s Rho Correlation Map Example');
xlabel('Data Channels');
ylabel('Data Channels');