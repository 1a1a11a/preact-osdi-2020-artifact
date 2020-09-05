function [Xp,time] = forecast_arima(X, pred_len)

dlmwrite('../temp/arima_in.txt',X');
cmd = sprintf('/usr/local/bin/R CMD BATCH "--args numpredict=%d" arima.R arima.out', pred_len);
system(cmd);
Xp = dlmread('../temp/arima_out.txt')';
time = dlmread('../temp/arima_time.txt');
assert(length(Xp) == pred_len);
delete ../temp/*.txt