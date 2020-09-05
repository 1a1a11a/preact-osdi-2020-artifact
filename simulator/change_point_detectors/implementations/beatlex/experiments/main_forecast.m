fclose('all'); close all; clearvars; clc; 

addpath keogh
addpath distinguishable_colors/

method_names = {'BEATLEX', 'ARIMA', 'TBATS'};
num_methods = length(method_names);

dats = dir('../data/MIMIC2/mitdb/*.dat');
num_data = length(dats);

metric_names = {'RMSE', 'DTW'};
all_errs = nan(length(metric_names), num_data, num_methods);

T = 5000;
signal_freq = 360;

Smin = 150;
Smax = 500;
max_dist = 200;
pred_len = 1000;
% verbosity = (num_data == 1);
verbosity = 0;

[beat_chars, beat_desc] = load_mitdb_info();
beat_cols = distinguishable_colors(length(beat_chars));
all_fnums = cell(1, num_data);

for data_idx=1:num_data

    fname = dats(data_idx).name;
    fnum = fname(1:length(fname)-4);
    all_fnums{data_idx} = fnum;
    
    load(sprintf('../data/MIMIC2/mitdb_txt/%s', fnum));
    Xe = M(Xe_annot_times(1) : Xe_annot_times(1) + T, 2)';
    
    X = Xe(1 : end-pred_len);
    Xp_true = Xe(length(X)+1 : end);
    
    [Xp_beatles, idx, starts, ends, p_idx, p_starts, p_ends, ~] = forecast_seq(X, pred_len, Smin, Smax, max_dist, verbosity);
    %%
%     arima_fname = sprintf('../temp/arima_saved/%s.mat', fnum);
%     tbats_fname = sprintf('../temp/tbats_saved/%s.mat', fnum);
%     load(arima_fname);
%     load(tbats_fname);
    Xp_arima = forecast_arima(X, pred_len);
    Xp_tbats = forecast_tbats(X, pred_len);
%     save(arima_fname, 'Xp_arima');
%     save(tbats_fname, 'Xp_tbats');
    
    
    preds = {Xp_beatles, Xp_arima, Xp_tbats};
    s = (1:500); 
    for method_idx=1:num_methods
        all_errs(1, data_idx, method_idx) = sqrt(mean(Xp_true(s) - preds{method_idx}(s)).^2);
        all_errs(2, data_idx, method_idx) = dtw(Xp_true(s), preds{method_idx}(s), 300);
    end

%     plot_forecast(X, Xe, Xe_annot_starts, Xe_annot_ends, Xe_annot_type, beat_chars, beat_desc, beat_cols, signal_freq, fnum, ...
%         Xp_beatles, idx, starts, ends, p_idx, p_starts, p_ends);
end

%%
save('../output/forecast_errs.mat', 'all_errs', 'metric_names');

for metric_idx = 1:length(metric_names)
    cur_errs = reshape(all_errs(metric_idx,:,:), num_data, num_methods);
    fprintf('METRIC: %s\n', metric_names{metric_idx});
    array2table(cur_errs, 'RowNames', all_fnums, 'VariableNames', method_names)
    mean_errs = mean(cur_errs, 1);
    fprintf('MEAN:\n');
    array2table(mean_errs, 'VariableNames', method_names)
end

%%
for metric_idx=1:length(metric_names)
    
    cur_errs = reshape(all_errs(metric_idx,:,:), num_data, num_methods);
    mean_errs = mean(cur_errs, 1);
    std_errs = std(cur_errs, 1);

    figure('Units', 'pixels', 'Position', [100 100 500 500]); hold on;
    col = distinguishable_colors(num_methods);
    mymarkers = {'x','o','^'};
    lwd = [4 1 1];
    for method_idx = 1:num_methods
        plot(cur_errs(:,method_idx), 'x', 'Color', col(method_idx,:), 'Marker', mymarkers{method_idx}, ...
            'MarkerFaceColor', col(method_idx,:) , 'MarkerSize', 12, 'LineWidth', lwd(method_idx));
    end
    legend(method_names);
    set(gca, 'XTick', 1:num_data, 'XTickLabels', all_fnums);
    set(gca,'XTickLabelRotation',90)
    ylabel(sprintf('Forecast error (%s)', metric_names{metric_idx}));
    xlabel('ECG Sequence ID');
    xt = get(gca, 'XTick');
    set(gca, 'FontSize', 9);
    set(gcf, 'PaperPositionMode', 'auto');
    % set(findall(gcf,'Type','Axes'),'FontSize',18);
    set(findall(gcf,'Type','Text'),'FontSize',24);
    set(findall(gcf,'Type','Legend'),'FontSize',20);
    printpdf(gcf, sprintf('../plots/forecast_err/forecast_allerr_%s.pdf', metric_names{metric_idx}));
    hold off;
    

    addpath terrorbar
    figure('Position', [0 0 500 500]); hold on;
    ebarwid = [4.1 1.9 1.3];
    for i=1:num_methods
        bar(i, mean_errs(i), 'FaceColor', col(i,:));
        t = terrorbar(i, mean_errs(i), std_errs(i)/sqrt(num_data), ebarwid(i), 'centi');
        set(t,'LineWidth',3,'Color','k');
    end
    ylabel(sprintf('Forecast error (%s)', metric_names{metric_idx}));
    set(gca,'XTick', 1:num_methods, 'XTickLabel', method_names);
    % set(gca,'YTick', [0:1]);
    set(gcf, 'PaperPositionMode', 'auto');
    set(findall(gcf,'Type','Axes'),'FontSize',20);
    set(findall(gcf,'Type','Text'),'FontSize',24);
    set(findall(gcf,'Type','Legend'),'FontSize',20);
    printpdf(gcf, sprintf('../plots/forecast_err/forecast_bar_%s.pdf', metric_names{metric_idx}));
    hold off;
end