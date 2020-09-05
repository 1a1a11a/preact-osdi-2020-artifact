function plot_models(models, idx)
addpath subaxis;
hold on; 
signal_freq = 360;
cols = distinguishable_colors(size(models,2));
starts = cumsum([0 cellfun(@length, models)] + 100);
tot_len = starts(end);
linestyle = {'-','--'};
sub = [];
all_len = cellfun(@length, models);
len_frac = all_len ./ max(all_len);
for k=1:length(models)
    for j=1:size(models{k}, 1)
        times = (1:size(models{k},2)) / signal_freq;
        sub(length(sub)+1) = subaxis(length(models), 1, k, 'sv', 0.01, 'paddingleft', .1);
        p = plot(times(1:size(models{k},2)), models{k}(j,:), 'LineWidth',3, 'Color', cols(k,:), 'LineStyle', linestyle{j}); box off;
        pos = get(gca,'Position');
        set(gca,'Position',[pos(1)+.35 pos(2) (pos(3)-.3)*len_frac(k) pos(4)]);
        set(gca,'Visible','off')
    end
    model_percent = 100 * mean(idx == k);
    text(0, .5, sprintf('%.0f%%', model_percent), 'FontSize', 24, 'units', 'normalized', 'HorizontalAlignment', 'right');
    
    xlim([0 max(times)]);
    set(gca,'xtick',[]);
    set(gca,'ytick',[]);
    set(gca,'Linewidth',1.5);
end
% linkaxes(sub, 'x');
set(gcf, 'PaperPositionMode', 'auto');
end