function m = init_markov(maxord)
m.maxord = maxord;
for i=0:maxord
    m.maps{i+1} = containers.Map;
end
m.chars = [];
end