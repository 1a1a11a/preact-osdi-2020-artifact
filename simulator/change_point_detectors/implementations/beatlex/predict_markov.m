function best_char = predict_markov(m, v)
nchar = length(m.chars);
for ord=m.maxord:-1:0
%     fprintf('for order %d\n', ord);
    scores = zeros(1, nchar);
    context = v(length(v)-ord+1:end);
    for i=1:nchar
        seq = num2str([context m.chars(i)]);
        if isKey(m.maps{ord+1},seq)
            scores(i) = m.maps{ord+1}(seq);
        end
    end
%     fprintf('scores: %s\n', num2str(scores));
    if ~all(scores == 0)
        [~, best_i] = max(scores);
        best_char = m.chars(best_i);
        break
    end
%     fprintf('ALL ZERO: DROPPING TO LEVEL %d\n', ord-1);
end
end
    