args=(commandArgs(TRUE)) #args: numpredict
library(forecast)
setwd('~/Desktop/bryan-papers/heart/code')
X = read.csv('../temp/tbats_in.txt', header=F, stringsAsFactors=F)$V1
X = as.numeric(X)
time = system.time(mod <- tbats(ts(X)))[3]
f = forecast(mod, h=numpredict)
summary(mod)
write.table(f$mean, '../temp/tbats_out.txt', row.names=F, col.names=F)
write.table(time, '../temp/tbats_time.txt', row.names=F, col.names=F)