function Xp = forecast_ar(X, pred_len, ord)

data = iddata(X',[]);
m = ar(data, ord);
X_forecast = forecast(m, data, pred_len);
Xp = X_forecast.y';