function plot_forecast(X, Xe, Xe_annot_starts, Xe_annot_ends, Xe_annot_type, beat_chars, beat_desc, beat_cols, signal_freq, fnum, Xp, idx, starts, ends, p_idx, p_starts, p_ends)

figure('Units', 'pixels', 'Position', [600 100 700 700]);  hold on;
subplot(2,1,1); 
title(sprintf('Ground truth: signal %s',fnum));
plot_truth(Xe, Xe_annot_starts, Xe_annot_ends, Xe_annot_ends(end), Xe_annot_type, beat_chars, beat_desc, beat_cols);
line([length(X)/signal_freq length(X)/signal_freq], get(gca, 'ylim'), 'Color', 'black', 'LineWidth', 3, 'LineStyle', '--');
%     xlim([0, length(X_ext) / signal_freq]);
subplot(2,1,2);
hold on;
times = (1:length(X)) / signal_freq;
cols = distinguishable_colors(max(idx));
for i=1:length(idx)
    plot(times(starts(i):ends(i)), Xe(starts(i):ends(i)), 'LineWidth', 3, 'Color', cols(idx(i),:)); 
end
for x1 = starts / signal_freq
  line([x1 x1], get(gca, 'ylim'));
end
ylabel('ECG Signal (\muV)');
xlabel('Time (s)');

line([length(X)/signal_freq length(X)/signal_freq], get(gca, 'ylim'), 'Color', 'black', 'LineWidth', 3, 'LineStyle', '--');

XXp = [X Xp];
times = (1:length(XXp)) / signal_freq;
cols = distinguishable_colors(max(p_idx));
for i=1:length(p_idx)
    plot(times(p_starts(i):p_ends(i)), XXp(p_starts(i):p_ends(i)), 'LineWidth', 3, 'Color', cols(p_idx(i),:)); 
end
for x1 = p_starts(2:end) / signal_freq
  line([x1 x1], get(gca, 'ylim'));
end
xlim([0 p_ends(end) / signal_freq]);

set(findall(gcf,'Type','Axes'),'FontSize',18);
set(findall(gcf,'Type','Text'),'FontSize',24);
set(findall(gcf,'Type','Legend'),'FontSize',18);
set(gcf, 'PaperPositionMode', 'auto');
printpdf(gcf, sprintf('../plots/forecast/%s.pdf', fnum));
