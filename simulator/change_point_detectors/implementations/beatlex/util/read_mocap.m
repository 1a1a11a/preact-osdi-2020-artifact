function M = read_mocap(fcode)
matpath = sprintf('../data/mocap/%s.mat', fcode);
if exist(matpath, 'file')
    load(matpath)
else
    path = sprintf('../data/mocap/%s.amc', fcode);
    M = amc_to_matrix(path);
    chosen_idx = [16 9 26 22]; % indices of lhumerus rhumerus lfemur rfemur
    locations = [1 7 10 13 16 19 22 25 27 30 31 32 34 35 37 39 42 43 44 46 47 49 52 53 55 56 59 60 62];
    chosen_locations = locations(chosen_idx);
    M = M(:, chosen_locations)';
    save(sprintf('../data/mocap/%s.mat', fcode), 'M');
end
end
