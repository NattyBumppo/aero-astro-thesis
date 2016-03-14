% Initial cleanup
close all;
clear;
clc;

% Generate random channels
mean1 = 20;
stddev1 = 2;

mean2 = 50;
stddev2 = 3;

mean3 = 75;
stddev3 = 3;

y1 = stddev1*randn(100,1) + mean1;
y2 = stddev2*randn(100,1) + mean2;
y3 = stddev3*randn(100,1) + mean3;

y2(60:70) = y2(60:70) - 15;

t = 1:100;

% Now, plot!
figure(1);
hold on;
plot(t, y1, 'g');
plot(t, y2, 'r');
plot(t, y3, 'b');
xlabel('Time (s)');
ylabel('Data Channel Value');

