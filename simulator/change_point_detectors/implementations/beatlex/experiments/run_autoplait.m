function clust = run_autoplait(X, fnum)

cd autoplait
dlmwrite('_dat/X',X');
system('sh demo.sh');
segfiles = dir('_out/dat_tmp/dat1/segment*');

clust = nan(length(X), 1);
nseg = length(segfiles) - 1;
for seg_idx = 1:nseg
    fname = sprintf('_out/dat_tmp/dat1/segment.%d', seg_idx - 1);
    dat = dlmread(fname) + 1;
    for i=1:size(dat, 1)
        clust(dat(i,1) : dat(i,2)) = seg_idx;
    end
end
assert(length(clust) == length(X));
assert(all(~isnan(clust)));
cd ..
end