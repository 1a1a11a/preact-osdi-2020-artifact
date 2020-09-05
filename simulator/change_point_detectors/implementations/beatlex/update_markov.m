function m = update_markov(m, v)
for ord=0:m.maxord
    if length(v) > ord
        if all(v(end) ~= m.chars)
            m.chars = [m.chars v(end)];
        end
        seq = num2str(v(end-ord:end));
        if ~isKey(m.maps{ord+1},seq)
            m.maps{ord+1}(seq) = 0;
        end
        m.maps{ord+1}(seq) = m.maps{ord+1}(seq) + 1;
    end
end
end