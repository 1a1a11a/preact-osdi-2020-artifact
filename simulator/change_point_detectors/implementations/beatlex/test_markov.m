clear all; clc;
v = [1 1 2];
v2 = [v v v v v 2];

m = init_markov(2);
for i=1:length(v2)
    m = update_markov(m, v2(1:i));
end

for ord=0:2
    fprintf('FOR ORDER %d\n', ord);
    mk = m.maps{ord+1}.keys; mv = m.maps{ord+1}.values;
    for i=1:length(mk)
        fprintf('%s: %d\n', mk{i}, mv{i});
    end
end
fprintf('FINISHED TRAINING\n');

v3 = v2;
for iter_idx=1:5
    fprintf('PREDICTION ITERATION %d\n', iter_idx);
    fprintf('%s\n', num2str(v3));
    best_char = predict_markov(m, v3);
    v3 = [v3 best_char];
end