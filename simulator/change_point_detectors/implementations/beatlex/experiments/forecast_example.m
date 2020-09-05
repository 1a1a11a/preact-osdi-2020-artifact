fclose('all'); close all; clear all; clc; 

cd ~/Desktop/bryan-papers/heart/code
addpath keogh
addpath distinguishable_colors/

dats = dir('../data/MIMIC2/mitdb/221.dat');
num_seq = length(dats);

% 221
segstart = 161;
segend = 186;
% segstart = 1;
% segend = 20;
signal_freq = 360;

Smin = 150;
Smax = 400;
max_dist = 300;
pred_len = 1000;
verbosity = 0;

data_idx = 1;

fname = dats(data_idx).name;
fnum = fname(1:length(fname)-4);

[beat_chars, beat_desc] = load_mitdb_info();
beat_cols = distinguishable_colors(length(beat_chars));
[Xe, Xe_annot_type, Xe_annot_starts, Xe_annot_ends] = load_mitdb(fnum, beat_chars, segstart, segend, 2:3);

X = Xe(:, 1 : end-pred_len);
Xp_true = Xe(:, size(X,2)+1 : end);

[Xp, idx, starts, ends, p_idx, p_starts, p_ends] = forecast_seq(X, pred_len, Smin, Smax, max_dist, verbosity);
    %%
    
figure('Units', 'pixels', 'Position', [600 100 700 700]);  hold on;

subplot(2,1,1); 

title('Ground truth labelling');
plot_truth(Xe, Xe_annot_starts, Xe_annot_ends, Xe_annot_ends(end), Xe_annot_type, beat_chars, beat_desc, beat_cols);
line([size(X,2)/signal_freq size(X,2)/signal_freq], get(gca, 'ylim'), 'Color', 'black', 'LineWidth', 3, 'LineStyle', '--');
%     xlim([0, length(X_ext) / signal_freq]);

subplot(2,1,2);
hold on;
title('BEATLES labelling and forecast');
linestyle = {'-','--'};
times = (1:size(X, 2)) / signal_freq;
cols = distinguishable_colors(max(idx));
for i=1:length(idx)
    for j=1:size(X, 1)
        plot(times(starts(i):ends(i)), X(j, starts(i):ends(i)), 'LineStyle', linestyle{j}, 'LineWidth', 3, 'Color', cols(idx(i),:)); 
    end
end
ylabel('ECG Signal (\muV)');
xlabel('Time (s)');


signal_freq = 360;
times = (1:size(Xp,2)+size(X, 2)) / signal_freq;
cols = distinguishable_colors(max(p_idx));
XXp = [X Xp];
for i=1:length(p_idx)
    for j=1:size(X, 1)
        plot(times(p_starts(i):p_ends(i)), XXp(j, p_starts(i):p_ends(i)), 'LineStyle', linestyle{j}, 'LineWidth', 3, 'Color', cols(p_idx(i),:)); 
    end
end
xlim([0 p_ends(end) / signal_freq]);
yl = ylim;
ylim([yl(1), yl(2)+120]);
for x1 = starts / signal_freq
  line([x1 x1], get(gca, 'ylim'));
end
line([size(X, 2)/signal_freq size(X, 2)/signal_freq], get(gca, 'ylim'), 'Color', 'black', 'LineWidth', 3, 'LineStyle', '--');
for x1 = p_starts(2:end) / signal_freq
  line([x1 x1], get(gca, 'ylim'));
end

set(findall(gcf,'Type','Axes'),'FontSize',18);
set(findall(gcf,'Type','Text'),'FontSize',24);
set(findall(gcf,'Type','Legend'),'FontSize',18);
set(gcf, 'PaperPositionMode', 'auto');
printpdf(gcf, '../plots/forecast_example.pdf');

% end