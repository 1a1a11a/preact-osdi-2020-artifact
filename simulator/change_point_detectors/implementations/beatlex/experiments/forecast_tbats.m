function [Xp,time] = forecast_tbats(X, pred_len)

dlmwrite('../temp/tbats_in.txt',X');
cmd = sprintf('/usr/local/bin/R CMD BATCH ''--args numpredict=%d'' tbats.R tbats.out', pred_len);
system(cmd);
Xp = dlmread('../temp/tbats_out.txt')';
time = dlmread('../temp/tbats_time.txt');
delete ../temp/*.txt
assert(length(Xp) == pred_len);