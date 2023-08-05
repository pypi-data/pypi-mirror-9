# coding: utf-8
#!/usr/bin/env python
#
# Copyright 2014-2015 PredicSis

import predicsis
predicsis.api_token="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
dataset = predicsis.Dataset.create(file='./Iris.dat',name='My Iris',header=True,separator='\t')
dictionary = predicsis.Dictionary.create(name = "My new dico", dataset_id = dataset.id)
target = predicsis.Target.create(target_var = "Class", dictionary_id = dictionary.id)
model = predicsis.Model.create(dataset_id = dataset.id, variable_id = target.variable_id)
scoresets = predicsis.Scoreset.create(dictionary_id = dictionary.id, model_id = model.id, data = './Iris.dat', header=True,separator='\t', name='Iris scored', file_name='iris_out.txt')
print predicsis.Scoreset.result(scoresets)