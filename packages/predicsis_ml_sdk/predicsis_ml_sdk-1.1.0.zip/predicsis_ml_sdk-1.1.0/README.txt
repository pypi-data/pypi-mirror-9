===========================
PredicSis ML SDK for Python
===========================

This SDK provides the bindings for PredicSis REST API in Python. 
Typical usage often looks like this::

	#!/usr/bin/env python
	
	# Import the PredicSisAPI object
	import predicsis
	
	# Initiate the API with your token
	predicsis.api_token="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
	
	# Workflow from uploading a dataset to scores
	dataset = predicsis.Dataset.create(file='./Iris.dat',name='My Iris',header=True,separator='\t')
	dictionary = predicsis.Dictionary.create(name = 'My new dico', dataset_id = dataset.id)
	target = predicsis.Target.create(target_var = 'Class', dictionary_id = dictionary.id)
	model = predicsis.Model.create(dataset_id = dataset.id, variable_id = target.variable_id)
	scoresets = predicsis.Scoreset.create(dictionary_id = dictionary.id, model_id = model.id, data = './Iris.dat', header=True,separator='\t', name='Iris scored', file_name='iris_out.txt')
	print predicsis.Scoreset.result(scoresets)
