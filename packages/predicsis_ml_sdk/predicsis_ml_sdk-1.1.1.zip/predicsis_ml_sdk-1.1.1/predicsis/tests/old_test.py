# coding: utf-8
#!/usr/bin/env python
#
# Copyright 2014-2015 PredicSis
from api import PredicSisAPI
''' Typical workflow '''
api = PredicSisAPI(token="be047cc75842e8cd6d10c8a8a961311a328528c2e16b3bf6076da1c825efe649", debug=1, url="https://api.stagedicsis.net/")
dataset_id = api.create_dataset("C:/Users/PC/Documents/projekty/use casy/datasets/and/data.dat", header=True)
print("******* " + dataset_id + " *******")
dictionary_id = api.create_dictionary(dataset_id)
print("******* " + dictionary_id + " *******")
target_var_id = api.edit_dictionary(dictionary_id, "Label")
print("******* " + target_var_id + " *******")
model_id = api.create_model(dataset_id, target_var_id)
print("******* " + model_id + " *******")
#scoreset_id = api.create_score(dictionary_id, model_id, '340.93433 5.327099 1.685518 9.881241 19.6133 8.322316 69.26095 13.585038 155.31125 2276.3384 23250.264 1 417105.9 417105.9 139800.83 1.95442708E10 116.147514 1.8148049 2.681506 6.4654155 12.717999 6.205488 38.508083 7.468458 43.524803 1383.0907 8572.303 1 277654.7 277654.7 92579.28 8.570923E9 319.6355 4.9943047 2.9879637 7.8067365 19.6133 6.000171 36.002056 13.265827 155.5757 1918.2577 21309.826 1 323089.2 323089.2 111859.11 1.25124598E10 39598.67 618.72925 195.76872 1147.6816 2278.036 966.61633 934347.1 1577.8684 18039.016 264391.03 2700460.2 1 4.8445812E7 4.8445812E7 1.6237518E7 2.63656986E14 37124.867 580.07605 857.1045 2066.5764 4065.124 1983.4943 3934249.8 2387.1843 13912.072 442084.88 2740012.5 1 8.8748304E7 8.8748304E7 2.9591624E7 8.7566424E14 108974.71 1702.7299 1018.69934 2661.5845 6686.847 2045.6643 4184742.5 4522.776 53041.098 653999.9 7265251.0 1 1.10152184E8 1.10152184E8 3.8136608E7 1.45440088E15', "yes")
scoreset_ids = api.create_score(dictionary_id, model_id, "C:/Users/PC/Documents/projekty/use casy/datasets/and/data.dat", header=True)
print("******* " + scoreset_ids[0] + " / " + scoreset_ids[1] + " *******")
print(api.retrieve_scores(scoreset_ids))
''' Additional reports '''
report_id = api.create_uni_unsuper_report(dataset_id, dictionary_id)
#print(api.retrieve_report(report_id))
report_id = api.create_uni_super_report(dataset_id, dictionary_id, target_var_id)
#print(api.retrieve_report(report_id))
report_id = api.create_model_eval_report(dataset_id, dictionary_id, model_id, "yes")
#print(api.retrieve_report(report_id))
''' Cleaning everything '''
api.delete_all()