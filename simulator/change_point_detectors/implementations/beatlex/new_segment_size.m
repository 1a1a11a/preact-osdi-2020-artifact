function [best_S1, best_k] = new_segment_size(X, cur, models, Smin, Smax, max_dist)

num_models = length(models);
ave_costs = inf(Smax, num_models+1, Smax); % outer segment size, model, inner segment size
for S = Smin:Smax
    if cur + S >= size(X, 2)
        continue
    end
    for k = 1:num_models + 1
        if k <= num_models
            cur_model = models{k};
        else
            cur_model = X(:, cur : cur + S - 1);
        end
        Xcur = X(:, cur + S : min(size(X, 2), cur + S + Smax - 1));
        [~, dtw_mat, ~, ~] = dtw(cur_model, Xcur, max_dist);
        dtw_costs = dtw_mat(end, :);
        ave_costs(S, k, 1:size(Xcur, 2)) = dtw_costs ./ (1:size(Xcur, 2));
        ave_costs(S, k, 1:Smin) = inf;
    end
end

[~, best_idx] = nanmin(ave_costs(:));
[best_S1, best_k, ~] = ind2sub(size(ave_costs), best_idx);

end