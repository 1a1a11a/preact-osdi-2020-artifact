function [beat_chars, beat_desc] = load_mitdb_info()
annot_info_file = fopen('../data/MIMIC2/annotation_info.txt');
annot_info = textscan(annot_info_file, '%s %s','Delimiter',',');
beat_chars = annot_info{1};
beat_desc = annot_info{2};
end