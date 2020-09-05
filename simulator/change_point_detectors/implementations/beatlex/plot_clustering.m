function plot_clustering(Xs, starts, ends, idx, savepath)
hold on;
signal_freq = 360;
times = (1:length(Xs)) / signal_freq;
cols = distinguishable_colors(max(idx));
% figure('Units', 'pixels', 'Position', [100 100 1100 300]); hold on;
% plot(1:Ts, Xs, 'ko','MarkerSize',2); hold on;
for i=1:length(idx)
    plot(times(starts(i):ends(i)), Xs(starts(i):ends(i)), 'LineWidth', 3, 'Color', cols(idx(i),:)); 
end
% scatter(1:Ts, Xs, 50, cols, 'filled');
for x1 = starts / signal_freq
  line([x1 x1], get(gca, 'ylim'));
end
ylabel('ECG Signal (Volts)');
xlabel('Time (s)');
yl = ylim;
xlim([0 ends(end) / signal_freq]);
ylim([yl(1), yl(2)+200]);
set(findall(gcf,'Type','Axes'),'FontSize',18);
set(findall(gcf,'Type','Text'),'FontSize',24);
set(findall(gcf,'Type','Legend'),'FontSize',18);
set(gcf, 'PaperPositionMode', 'auto');
if nargin == 5
    printpdf(gcf, savepath);
end
end