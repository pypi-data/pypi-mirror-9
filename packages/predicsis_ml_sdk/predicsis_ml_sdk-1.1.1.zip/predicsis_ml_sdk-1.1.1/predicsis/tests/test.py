# coding: utf-8
#!/usr/bin/env python
#
# Copyright 2014-2015 PredicSis

import predicsis
predicsis.api_token="be047cc75842e8cd6d10c8a8a961311a328528c2e16b3bf6076da1c825efe649"
predicsis.api_url="https://api.stagedicsis.net/"
predicsis.lvl_debug = 3
predicsis.api_client.verify_ssl_certs = False
#predicsis.api_client.ssl_certs_path = 'C:/Users/PC/Documents/projekty/tools/stagedicsis.net.crt'
#proj = predicsis.Project.create(title="My project")
#print proj.title
#print predicsis.Project.retrieve_all()
#print predicsis.Project.retrieve(proj.id)
dat = predicsis.Dataset.create(name='My dataset',file='C:/Users/PC/Documents/projekty/use casy/datasets/and/data.dat',header=True,separator='\t')
#dat = predicsis.Dataset.create(name='My dataset',file='C:/Users/PC/Desktop/Clothing_Store2.txt',header=True,separator=',')
print dat.name
job_id = dat.job_ids[0]
job = predicsis.Job.retrieve(job_id)
print job.status
dat.update(name="New name", puap='fdsqfqfsq')
dat.save()
print dat.name
dat = predicsis.Dataset.retrieve(dat.id)
print dat.name
dico = predicsis.Dictionary.create(name = "My new dico", dataset_id = dat.id)
print dico.description
#dat = predicsis.Dataset.retrieve(dat.id)
dico.update(description = "don't know")
dico.save()
dico = predicsis.Dictionary.retrieve(dico.id)
print dico.description
#dat = predicsis.Dataset.retrieve(dat.id)

target = predicsis.Target.create(target_var="Label",dictionary_id=dico.id)
print target.modalities

dat = predicsis.Dataset.retrieve(dat.id)

model = predicsis.Model.create(dataset_id = dat.id, variable_id = target.variable_id)
print model.model_variables

scoresets = predicsis.Scoreset.create(name="My scores",dictionary_id = dico.id, model_id = model.id, data = 'C:/Users/PC/Documents/projekty/use casy/datasets/and/data.dat', header=True,separator='\t', file_name='out.txt', papa='papa')
#scoresets = predicsis.Scoreset.create(name="My scores",dictionary_id = dico.id, model_id = model.id, data = 'C:/Users/PC/Desktop/Clothing_Store2.txt', header=True,separator=',', file_name='out.txt', papa='papa')
print predicsis.Scoreset.result(scoresets)

r1 = predicsis.Report.create(type = "univariate_unsupervised", dataset_id = dat.id, dictionary_id = dico.id)
print r1.id
r2 = predicsis.Report.create(type = "univariate_supervised", dataset_id = dat.id, dictionary_id = dico.id, variable_id = target.variable_id)
print r2.id
r3 = predicsis.Report.create(type = "classifier_evaluation", variable_id = target.variable_id, dataset_id = dat.id, dictionary_id = dico.id, model_id = model.id, main_modality="yes")
print r3.id

dat.delete()
try:
    dat = predicsis.Dataset.retrieve(dat.id)
    print dat.name
except predicsis.error.PredicSisError:
    print 'ok'
try:
    dico = predicsis.Dictionary.create()
except predicsis.error.PredicSisError:
    print 'ok'
predicsis.Project.delete_all()
predicsis.Dataset.delete_all()
predicsis.Dictionary.delete_all()
predicsis.Target.delete_all()
predicsis.Report.delete_all()

#import predicsis
#predicsis.api_token="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
#predicsis.api_token="be047cc75842e8cd6d10c8a8a961311a328528c2e16b3bf6076da1c825efe649"
#predicsis.api_url="https://api.stagedicsis.net/"
#predicsis.lvl_debug = 2
#predicsis.api_client.verify_ssl_certs = False
#dataset = predicsis.Dataset.create(file='C:/Users/PC/Documents/projekty/use casy/datasets/and/data.dat',name='My Iris',header=True,separator='\t')
#dictionary = predicsis.Dictionary.create(name = "My new dico", dataset_id = dataset.id)
#target = predicsis.Target.create(target_var = "Label", dictionary_id = dictionary.id)
#model = predicsis.Model.create(dataset_id = dataset.id, target_id = target.variable_id)
#scoresets = predicsis.Scoreset.create(dictionary_id = dictionary.id, model_id = model.id, data = 'C:/Users/PC/Documents/projekty/use casy/datasets/and/data.dat', header=True,separator='\t', name='Iris scored', file_name='iris_out.txt')
#print predicsis.Scoreset.result(scoresets)