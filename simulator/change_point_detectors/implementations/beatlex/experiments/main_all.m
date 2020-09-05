fclose('all'); close all; clear all; clc; 

addpath keogh
addpath distinguishable_colors/

dats = dir('../data/MIMIC2/mitdb/*.dat');
% dats = dir('../data/MIMIC2/mitdb/104.dat');
num_seq = length(dats);

T = 5000;
Smin = 150;
Smax = 500;
max_dist = 350;
verbosity = 0;

method_names = {'BEATLEX', 'HMM', 'AUTOPLAIT'};
num_methods = length(method_names);

seq_names = cell(1, num_seq);
nmi_scores = nan(num_methods, num_seq);
ari_scores = nan(num_methods, num_seq);
 
for seq_idx=1:num_seq
    fname = dats(seq_idx).name;
    fnum = fname(1:length(fname)-4);
    fprintf('PROCESSING DATA FILE %s\n', fnum);
    seq_names{seq_idx} = fnum;

%     M = dlmread(sprintf('../data/MIMIC2/mitdb_txt/%s.txt', fnum));
%     save(sprintf('../data/MIMIC2/mitdb_txt/%s', fnum), 'M');
    load(sprintf('../data/MIMIC2/mitdb_txt/%s', fnum));

    annot_info_file = fopen('../data/MIMIC2/annotation_info.txt');
    annot_info = textscan(annot_info_file, '%s %s','Delimiter',',');
    beat_chars = annot_info{1};
    beat_desc = annot_info{2};
    beat_cols = distinguishable_colors(length(beat_chars));

    annot_file = fopen(sprintf('../data/MIMIC2/mitdb/%s.fqrs', fnum));
    annot_dat = textscan(annot_file, '%s %d %s %d %d %d %s');
    annot_sub = ismember(annot_dat{3}, beat_chars) & annot_dat{2} < T;
    annot_type = annot_dat{3}(annot_sub);
    annot_times = double(annot_dat{2}(annot_sub));
    annot_times = annot_times(annot_times < T);
    annot_starts = annot_times(1:end-1);
    annot_ends = annot_times(2:end)-1;
    X = M(annot_starts(1):annot_ends(end), 2)';
    offset = annot_starts(1) - 1;
    annot_starts = annot_starts - offset;
    annot_ends = annot_ends - offset;

    T2 = length(X);
    true_clusters = nan(1, T2);
    for i=1:length(annot_starts)
        true_clusters(annot_starts(i) : annot_ends(i)) = find(strcmp(annot_type(i), beat_chars));
    end
    T3 = T2 - 500;
    true_clusters = true_clusters(1:T3);
    if all(true_clusters == true_clusters(1))
        continue
    end

    [models, starts, ends, idx] = summarize_seq(X, Smin, Smax, max_dist, verbosity);

    beatles_clusters = nan(1, T2);
    for i=1:length(starts)
        beatles_clusters(starts(i) : ends(i)) = idx(i);
    end
    autoplait_clusters = run_autoplait(X, fnum);
    
    [~, ~, ~, ~, ~, ~, ~, hmm_clusters] = learn_hmm(X, length(unique(true_clusters)));
    
    method_clusters = {beatles_clusters, hmm_clusters, autoplait_clusters};
    
    for method_idx = 1:num_methods
        fprintf('METHOD: %s\n', method_names{method_idx});
        cur_clusters = method_clusters{method_idx}(1:T3);
        crosstab(cur_clusters, true_clusters)
        nmi_scores(method_idx, seq_idx) = nmi(true_clusters, cur_clusters);
        ari_scores(method_idx, seq_idx) = RandIndex(true_clusters, cur_clusters);
        fprintf('NMI: %.3f, ARI: %.3f\n', ari_scores(method_idx, seq_idx), nmi_scores(method_idx, seq_idx));
    end
    
    figure('Units', 'pixels', 'Position', [600 100 700 700]);  hold on;
    subplot(2,1,1); 
    title(sprintf('Ground truth: signal %s',fnum));
    plot_truth(X, annot_starts, annot_ends, ends(end), annot_type, beat_chars, beat_desc, beat_cols);
    subplot(2,1,2); 
    title(sprintf('NMI: %.3f, ARI: %.3f\n', nmi_scores(1, seq_idx), ari_scores(1, seq_idx)));
    plot_clustering(X, starts, ends, idx);
    printpdf(gcf, sprintf('../plots/clustering_eval/%s.pdf', fnum));
end
%%
good = ~isnan(nmi_scores(1,:));
nmi_scores = nmi_scores(:, good); 
ari_scores = ari_scores(:, good); 
seq_names = seq_names(good);
seq_printnames = cellfun(@(x) ['s' x], seq_names, 'UniformOutput', false);
if sum(good) > 0
    fprintf('NMI:\n');
    array2table(nmi_scores, 'RowNames', method_names, 'VariableNames', seq_printnames)
    fprintf('ARI:\n');
    array2table(ari_scores, 'RowNames', method_names, 'VariableNames', seq_printnames)
    
    fprintf('MEAN SCORES: \n\n');
    array2table([mean(nmi_scores, 2) mean(ari_scores, 2)], 'RowNames', method_names, 'VariableNames', {'NMI', 'ARI'})
end

%%
metric_names = {'NMI', 'ARI'};
all_scores = {nmi_scores, ari_scores};
col = distinguishable_colors(num_methods);
for metric_idx=1:length(metric_names)
    
    cur_errs = all_scores{metric_idx};
    mean_errs = mean(cur_errs, 2);
    std_errs = std(cur_errs, [], 2);

    addpath terrorbar
    figure('Position', [0 0 500 500]); hold on;
    ebarwid = [4.1 1.9 1.3];
    for i=1:num_methods
        bar(i, mean_errs(i), 'FaceColor', col(i,:));
        t = terrorbar(i, mean_errs(i), std_errs(i)/sqrt(size(cur_errs, 2)), ebarwid(i), 'centi');
        set(t,'LineWidth',3,'Color','k');
    end
    ylabel(sprintf('Labelling accuracy (%s)', metric_names{metric_idx}));
    set(gca,'XTick', 1:num_methods, 'XTickLabel', method_names);
    % set(gca,'YTick', [0:1]);
    set(gcf, 'PaperPositionMode', 'auto');
    set(findall(gcf,'Type','Axes'),'FontSize',20);
    set(findall(gcf,'Type','Text'),'FontSize',26);
    set(findall(gcf,'Type','Legend'),'FontSize',22);
    printpdf(gcf, sprintf('../plots/clustering_err/cluster_bar_%s.pdf', metric_names{metric_idx}));
    hold off;
end