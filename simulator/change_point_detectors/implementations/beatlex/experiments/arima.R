args=(commandArgs(TRUE)) #args: alg, numpredict
library(forecast)
setwd('~/Desktop/bryan-papers/heart/code')
X = read.csv('../temp/arima_in.txt', header=F, stringsAsFactors=F)$V1
X = as.numeric(X)
time = system.time(mod <- auto.arima(ts(X)))[3]
f = forecast(mod, h=numpredict)
summary(mod)
write.table(f$mean, '../temp/arima_out.txt', row.names=F, col.names=F)
write.table(time, '../temp/arima_time.txt', row.names=F, col.names=F)