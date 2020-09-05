function plot_truth(X, starts, ends, Tlim, annot_type, beat_chars, beat_desc, beat_cols, savepath)
linestyle = {'-','--'};
hold on;
signal_freq = 360;
num_seg = length(starts);
times = (1:size(X, 2)) / signal_freq;
annot_idx = nan(1, num_seg);
legend_plots = {};
legend_descs = {};
for i=1:num_seg
    annot_idx(i) = find(strcmp(annot_type(i), beat_chars));
    for j=1:size(X, 1)
        h = plot(times(starts(i):ends(i)), X(j, starts(i):ends(i)), 'LineStyle', linestyle{j}, 'LineWidth', 3, 'Color', beat_cols(annot_idx(i),:));
    end
    cur_desc = beat_desc(annot_idx(i));
    if sum(strcmp(cur_desc, legend_descs)) == 0
        legend_plots = [legend_plots h];
        legend_descs = [legend_descs cur_desc];
    end
end
xlim([0, Tlim / signal_freq]);
yl = ylim;
ylim([yl(1), yl(2)+120]);
for i=1:num_seg
    t1 = starts(i) / signal_freq;
    line([t1 t1], get(gca, 'ylim'), 'Color', [.6 .6 .6], 'LineWidth', 1);
%     text(t1+.1, min(X) + .95*(max(X) - min(X)), annot_type{i});
end
ylabel('ECG Signal (\muV)', 'FontSize', 24);
xlabel('Time (s)', 'FontSize', 24);
legend(legend_plots, legend_descs);
set(findall(gcf,'Type','Axes'),'FontSize',18);
set(findall(gcf,'Type','Text'),'FontSize',24);
set(findall(gcf,'Type','Legend'),'FontSize',18);
set(gcf, 'PaperPositionMode', 'auto');
if nargin == 9
    printpdf(gcf, savepath);
end
end