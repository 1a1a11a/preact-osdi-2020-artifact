function mi = mutual_information(a,b)
tab = crosstab(a, b);
m = sum(tab(:));
p_row = sum(tab, 1) / m;
p_col = sum(tab, 2) / m;
mi = (tab/m) .* log((tab/m) ./ (p_col * p_row));

end