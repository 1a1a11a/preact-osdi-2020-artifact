function [Xe, Xe_annot_type, Xe_annot_starts, Xe_annot_ends] = load_mitdb(fnum, beat_chars, segstart, segend, dims)

fprintf('PROCESSING DATA FILE %s\n', fnum);
load(sprintf('../data/MIMIC2/mitdb_txt/%s', fnum));

annot_file = fopen(sprintf('../data/MIMIC2/mitdb/%s.fqrs', fnum));
annot_dat = textscan(annot_file, '%s %d %s %d %d %d %s');

annot_sub = ismember(annot_dat{3}, beat_chars);
annot_times = double(annot_dat{2}(annot_sub));
annot_type = annot_dat{3}(annot_sub);

Xe_annot_times = annot_times(segstart:segend);

Xe = M(Xe_annot_times(1) : Xe_annot_times(end), dims)';

Xe_annot_type = annot_type(segstart:segend-1);
Xe_annot_times = Xe_annot_times - Xe_annot_times(1) + 1;

Xe_annot_starts = Xe_annot_times(1:end-1);
Xe_annot_ends = Xe_annot_times(2:end)-1;

end