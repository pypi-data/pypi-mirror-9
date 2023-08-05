# coding: utf-8
#!/usr/bin/env python
#
# Copyright 2014-2015 PredicSis

import predicsis
predicsis.api_token="be047cc75842e8cd6d10c8a8a961311a328528c2e16b3bf6076da1c825efe649"
predicsis.api_url="https://api.stagedicsis.net/"
#predicsis.api_url="http://192.168.1.10:3001/"
#predicsis.api_token="931a60168acec8ac6e3c2a0c54d5c7c79cd5122d1584a74bebff44b675ad83f9"
predicsis.lvl_debug = 3
dataset = predicsis.Dataset.create(file='C:/Users/PC/Desktop/tactill_tab2.csv',name='Mixpanel',header=False,separator='\t')
dictionary = predicsis.Dictionary.create(name = 'Mixpanel dico', dataset_id = dataset.id)
target = predicsis.Target.create(target_var = 55, dictionary_id = dictionary.id, unused_vars=[30])
model = predicsis.Model.create(dataset_id = dataset.id, variable_id = target.variable_id)
report = predicsis.Report.create(type='classifier_evaluation', dictionary_id=dictionary.id, dataset_id=dataset.id, model_id=model.id, main_modality='True', variable_id=target.variable_id)
print report
#scoresets = predicsis.Scoreset.create(dictionary_id = dictionary.id, model_id = model.id, data = 'C:/Users/PC/Desktop/protoDataMart_au_mois.csv', header=True,separator=',', name='Mixpanel scored', file_name='mixpanel_out.txt')
#print predicsis.Scoreset.result(scoresets)