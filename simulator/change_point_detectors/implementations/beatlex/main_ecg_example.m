fclose('all'); close all; clearvars; clc; 
addpath util;
addpath util/distinguishable_colors;
addpath util/subaxis;

% [Smin, Smax, max_dist] = tune_hyperparams(X)

signal_freq = 1;
Smin = 30;
Smax = 90;
maxdist = 30;
pred_len = 15;
verbosity = 0;

Xe = csvread('data/seagate_4tb/seagate_4tb_3_month.csv')';
X = Xe(1 : end-pred_len);
Xp_true = Xe(length(X)+1 : end);

[Xp, idx, starts, ends, p_idx, p_starts, p_ends, models] = forecast_seq(X, pred_len, Smin, Smax, maxdist, verbosity);

%% PLOT INPUT

figure('Units', 'pixels', 'Position', [200 400 700 300]);  hold on;
times = (1:size(X, 2)) / signal_freq;
plot(times, X, 'LineWidth', 3, 'Color', 'black');
ylabel('ECG Signal (\muV)', 'FontSize', 24);
xlabel('Time (s)', 'FontSize', 24);
set(findall(gcf,'Type','Axes'),'FontSize',18);
set(findall(gcf,'Type','Text'),'FontSize',24);
set(findall(gcf,'Type','Legend'),'FontSize',18);
printpdf(gcf,'plots/ecg_input.pdf');

%% PLOT OUTPUT

figure('Units', 'pixels', 'Position', [100 100 100 500]);  hold on;
plot_models(models, idx);
printpdf(gcf,'plots/ecg_models.pdf');

%%

% Segmentation + labelling plot
figure('Units', 'pixels', 'Position', [200 0 700 300]);  hold on;
hold on;
times = (1:length(X)) / signal_freq;
cols = distinguishable_colors(max(idx));
for i=1:length(idx)
    plot(times(starts(i):ends(i)), Xe(starts(i):ends(i)), 'LineWidth', 3, 'Color', cols(idx(i),:)); 
end
ylabel('AFR (%)');
xlabel('Time (days)');
XXp = [X Xp];
times = (1:length(XXp)) / signal_freq;
cols = distinguishable_colors(max(p_idx));
for i=1:length(p_idx)
    plot(times(p_starts(i):p_ends(i)), XXp(p_starts(i):p_ends(i)), 'LineWidth', 3, 'Color', cols(p_idx(i),:)); 
end
xlim([0 p_ends(end) / signal_freq]);
set(findall(gcf,'Type','Axes'),'FontSize',18);
set(findall(gcf,'Type','Text'),'FontSize',24);
set(findall(gcf,'Type','Legend'),'FontSize',18);

% vertical lines
for x1 = starts / signal_freq
  line([x1 x1], get(gca, 'ylim'), 'Color', [.6 .6 .6], 'LineWidth', .7, 'LineStyle', '--');
end
for x1 = p_starts(2:end) / signal_freq
  line([x1 x1], get(gca, 'ylim'), 'Color', [.6 .6 .6], 'LineWidth', .7, 'LineStyle', '--');
end
line([length(X)/signal_freq length(X)/signal_freq], get(gca, 'ylim'), 'Color', 'black', 'LineWidth', 3, 'LineStyle', '--');
printpdf(gcf,'plots/seagate_4tb_3_month_prediction.pdf');

