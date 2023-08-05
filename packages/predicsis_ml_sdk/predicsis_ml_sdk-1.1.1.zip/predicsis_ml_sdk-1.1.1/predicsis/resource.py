from predicsis.api_client import APIClient
from predicsis.error import PredicSisError
from collections import namedtuple
import predicsis
import json
import datetime
from xml.dom import minidom
import time

class APIResource(dict):
    
    def __init__(self, obj):
        for k, v in obj.iteritems():
            if isinstance(v, dict):
                setattr(self, k, APIResource(v))
            else:
                setattr(self, k, v)
                
    def __getitem__(self, val):
        return self.__dict__[val]
    
    def __repr__(self):
        return '{%s}' % str(', '.join('"%s": %s' % (k, repr(v).replace("'","\"").replace("u\"","\"").replace("False","false").replace("True","true").replace("None","null")) for (k, v) in self.__dict__.iteritems()))
        
    @classmethod
    def res_name(cls):
        if cls.__name__ == 'APIResource':
            raise NotImplementedError('APIResource is an abstract class.')
        return cls.__name__.lower()
    
    @classmethod
    def res_url(cls):
        return cls.res_name() + 's'
    
    @classmethod
    def retrieve(cls, id):
        predicsis.log('Retrieving: ' + cls.res_name() + '..', 1)
        json_data = APIClient.request('get', cls.res_url() + '/' + id)
        j = json_data[cls.res_name()]
        return cls(j)
    
    @classmethod
    def retrieve_all(cls):
        predicsis.log('Retrieving all: ' + cls.res_name() + '..', 1)
        json_data = APIClient.request('get', cls.res_url())
        j = json_data[cls.res_url().split('/')[-1]]
        return [cls(i) for i in j]
    
    @classmethod
    def parse_post_data(cls, data):
        post_data = '{"' + cls.res_name() + '":{'
        for key, value in data.iteritems():
            if (type(value).__name__ == "str" or type(value).__name__ == "unicode") and not value=='true' and not value=='false':
                post_data += '"' + key +'":"' + value + '",'
            else:
                post_data += '"' + key +'":' + str(value).replace("'", "\"").replace("False","false").replace("True","true").replace("None","null") + ','
        if post_data.endswith(','):
            post_data = post_data[0:-1]
        post_data += '}}'
        return post_data
    
class CreatableAPIResource(APIResource):
    @classmethod
    def create(cls, **data):
        if validate('c', cls.__name__, data) < 0:
            raise PredicSisError("Validation failed!")
        predicsis.log('Creating: ' + cls.res_name() + '..', 1)
        post_data = cls.parse_post_data(data)
        json_data = APIClient.request('post', cls.res_url(), post_data)
        j = json_data[cls.res_name()]
        try:
            jid = j['job_ids'][0]
            status = 'pending'
            job = Job.retrieve(jid)
            status = job.status
            while ((status != 'completed') and (status != 'failed')):
                job = Job.retrieve(jid)
                status = job.status
                if status == 'failed':
                    raise PredicSisError("Job failed! (job_id: " + job.id + ")")
                #time.sleep(1)
            return cls.retrieve(j['id'])
        except KeyError:
            return cls(j)
        except IndexError:
            raise PredicSisError("Job launching failed. Report this bug to support@predicsis.com");

class UpdatableAPIResource(APIResource):
    to_update = {}
    
    def update(self, **data):
        if validate('u', self.__class__.__name__, data) >= 0:
            for key, value in data.iteritems():
                self.to_update[key] = value
        
    def save(self):
        predicsis.log('Updating: ' + self.__class__.res_name() + '..', 1)
        post_data = self.__class__.parse_post_data(self.to_update)
        json_data = APIClient.request('patch', self.__class__.res_url() + '/' + self.id, post_data)
        j = json_data[self.__class__.res_name()]
        try:
            jid = j['job_ids'][0]
            status = 'pending'
            job = Job.retrieve(jid)
            status = job.status
            while ((status != 'completed') and (status != 'failed')):
                job = Job.retrieve(jid)
                status = job.status
                if status == 'failed':
                    raise PredicSisError("Job failed! (job_id: " + job.id + ")")
                #time.sleep(1)
            json_data = APIClient.request('get', self.res_url() + '/' + self.id)
            obj = json_data[self.res_name()]
            for k, v in obj.iteritems():
                if isinstance(v, dict):
                    setattr(self, k, APIResource(v))
                else:
                    setattr(self, k, v)
        except KeyError:
            json_data = APIClient.request('get', self.res_url() + '/' + self.id)
            obj = json_data[self.res_name()]
            for k, v in obj.iteritems():
                if isinstance(v, dict):
                    setattr(self, k, APIResource(v))
                else:
                    setattr(self, k, v)
        except IndexError:
            raise PredicSisError("Job launching failed. Report this bug to support@predicsis.com");
        
    def reset(self):
        self.to_update = {}

class DeletableAPIResource(APIResource):
    @classmethod
    def delete_all(cls):
        objs = cls.retrieve_all()
        for obj in objs:
            obj.delete()
            
    def delete(self):
        predicsis.log('Deleting: ' + self.__class__.res_name() + '..', 1)
        APIClient.request('delete', self.__class__.res_url() + '/' + self.id)
        
class Job(DeletableAPIResource):
    pass
    
class Project(CreatableAPIResource, DeletableAPIResource):
    pass

class Credentials(CreatableAPIResource):    
    @classmethod
    def res_url(cls):
        return 'sources/credentials'
    
class Source(CreatableAPIResource, DeletableAPIResource):
    pass
    
class DatasetAPI(CreatableAPIResource, DeletableAPIResource):
    @classmethod
    def res_name(cls):
        return 'dataset'
    
class Dataset(CreatableAPIResource, UpdatableAPIResource, DeletableAPIResource):
    @classmethod
    def create(cls, **data):
        if validate('c', cls.__name__, data) < 0:
            raise PredicSisError("Validation failed!")
        credentials = Credentials.retrieve('s3')
        payload = {
            'Content-Type':'multipart/form-data',
            'success_action_status':'201',
            'acl':'private',
            'policy':credentials.policy,
            'AWSAccessKeyId':credentials.aws_access_key_id,
            'signature':credentials.signature,
            'key':credentials.key
        }
        predicsis.log('Uploading a file..', 1)
        files = {'file': open(data.get('file'),'rb')}
        response = APIClient.request_full(method='post', url=credentials.s3_endpoint, headers=[],post_data=payload, files=files)
        if not response[1] == 201:
            raise PredicSisError('Upload failed by Amazon - retry.')
        xmlResponse = minidom.parseString(response[0])
        keyList = xmlResponse.getElementsByTagName('Key')
        predicsis.log('Creating: dataset..', 1)
        source = Source.create(name=data.get('file'), key=str(keyList[0].firstChild.data))
        sid = str(source.id)
        if data.get('header') == None or data.get('separator') == None:
            if not (data.get('header') == None and data.get('separator') == None):
                predicsis.log('Either both separator and header should be set, or both should be left unset. The set parameter is skipped.', 0)
            dapi = DatasetAPI.create(name=data.get('name'), source_ids=[sid])
        else:
            dapi = DatasetAPI.create(name=data.get('name'), header=str(data.get('header')).lower(), separator=data.get('separator').encode('string_escape'), source_ids=[sid])
        for i in range(0,len(dapi.preview)):
            dapi.preview[i] = '...not available in the SDK...'#dapi.preview[i].replace('"','*')#
        return cls(json.loads(str(dapi)))
    
    def delete(self):
        predicsis.log('Deleting: ' + self.__class__.res_name() + '..', 1)
        APIClient.request('delete', self.__class__.res_url() + '/' + self.id)
        for id in self.source_ids:
            APIClient.request('delete', 'sources/' + id)
            
class Dictionary(CreatableAPIResource, UpdatableAPIResource, DeletableAPIResource):        
    @classmethod
    def res_url(cls):
        return 'dictionaries'
    
class Variable(UpdatableAPIResource):
    dic_id = ''
    
    @classmethod
    def res_url(cls):
        return 'dictionaries/' + cls.dic_id + '/' + cls.res_name() + 's'
    
class ModalitiesSet(CreatableAPIResource, DeletableAPIResource):
    @classmethod
    def res_name(cls):
        return 'modalities_set'
    
            
class Target(CreatableAPIResource, DeletableAPIResource):         
    @classmethod
    def res_name(cls):
        return 'modalities_set'
    
    @classmethod
    def create(cls, **data):
        if validate('c', cls.__name__, data) < 0:
            raise PredicSisError("Validation failed!")
        predicsis.log('Retrieving: variables..', 1)
        target_id = -1
        unused_ids = []
        dico = Dictionary.retrieve(data.get('dictionary_id'))
        dataset_id = dico.dataset_id
        Variable.dic_id = data.get('dictionary_id')
        variables = Variable.retrieve_all()
        i = 1
        for var in variables:
            if type(data.get('target_var')).__name__ == "str":
                if var.name == data.get('target_var'):
                    target_id = var.id
                    if not var.type == 'categorical':
                        predicsis.log("Your variable is not detected as categorical - changing it manually.",0)
                        var.update(type = 'categorical')
                        var.save()
            elif type(data.get('target_var')).__name__ == "int":
                if i == data.get('target_var'):
                    target_id = var.id
                    if not var.type == 'categorical':
                        predicsis.log("Your variable is not detected as categorical - changing it manually.",0)
                        var.update(type = 'categorical')
                        var.save()
            if not data.get('unused_vars') == None:
                if var.name in data.get('unused_vars'):
                    var.update(use = False)
                    var.save()
                elif i in data.get('unused_vars'):
                    var.update(use = False)
                    var.save()
            i+=1
        if target_id == -1:
            raise PredicSisError("Your target variable doesn't exist in the dataset.")
        predicsis.log('Creating: target..', 1)
        modal = ModalitiesSet.create(variable_id = target_id, dataset_id = dataset_id)
        return cls(json.loads(str(modal)))
    
class PreparationRules(CreatableAPIResource, UpdatableAPIResource, DeletableAPIResource):        
    @classmethod
    def res_name(cls):
        return 'preparation_rules_set'
    
class Classifier(CreatableAPIResource):  
    @classmethod
    def res_name(cls):
        return 'model'

class Model(CreatableAPIResource):
    @classmethod
    def create(cls, **data):
        if validate('c', cls.__name__, data) < 0:
            raise PredicSisError("Validation failed!")
        prs = PreparationRules.create(variable_id = data.get('variable_id'), dataset_id = data.get('dataset_id'))
        if data.get('name') == None:
            clasif = Classifier.create(type='classifier',preparation_rules_set_id=prs.id)
        else:
            clasif = Classifier.create(type='classifier',preparation_rules_set_id=prs.id, name=data.get('name'))
        return cls(json.loads(str(clasif)))

class Scoreset(CreatableAPIResource, UpdatableAPIResource, DeletableAPIResource):
    @classmethod
    def res_name(cls):
        return 'dataset'
    
    @classmethod
    def create(cls, **data):
        if validate('c', cls.__name__, data) < 0:
            raise PredicSisError("Validation failed!")
        response = Model.retrieve(data.get('model_id'))
        prs_id = response.preparation_rules_set_id
        response = PreparationRules.retrieve(prs_id)
        var_id = response.variable_id
        Variable.dictionary_id = data.get('dictionary_id')
        response = Variable.retrieve(var_id)
        modalities_set_id = response.modalities_set_ids[0]
        response = ModalitiesSet.retrieve(modalities_set_id)
        modalities = response.modalities
        predicsis.log('Preparing data..', 1)
        dataset_id = -1
        file_name = ""
        try:
            open(data.get('data'),'rb')
            if data.get('header') == None or data.get('separator') == None:
                if not (data.get('header') == None and data.get('separator') == None):
                    predicsis.log('Either both separator and header should be set, or both should be left unset. The set parameter is skipped.', 0)
                dataset_id = Dataset.create(file=data.get('data'), name = data.get('name')).id
            else:
                dataset_id = Dataset.create(file=data.get('data'), header=data.get('header'), separator=data.get('separator'), name = data.get('name')).id
        except IOError:
            f = open(file_name,'w')
            f.write(data)
            f.close()
            if data.get('header') == None or data.get('separator') == None:
                if not (data.get('header') == None and data.get('separator') == None):
                    predicsis.log('Either both separator and header should be set, or both should be left unset. The set parameter is skipped.', 0)
                dataset_id = Dataset.create(file=file_name, name = data.get('name')).id
            else:
                dataset_id = Dataset.create(file=file_name, header=data.get('header'), separator=data.get('separator'), name = data.get('name')).id
        if dataset_id == -1:
            raise PredicSisError("Error creating your test dataset")
        scoresets = []
        for modality in modalities:
            if data.get('header') == None or data.get('separator') == None:
                if not (data.get('header') == None and data.get('separator') == None):
                    predicsis.log('Either both separator and header should be set, or both should be left unset. The set parameter is skipped.', 0)
                dataset = DatasetAPI.create(name=data.get('name'), classifier_id=data.get('model_id'), dataset_id=dataset_id, modalities_set_id=modalities_set_id, main_modality=modality, data_file = { "filename": data.get('file_name')})
            else:
                dataset = DatasetAPI.create(name=data.get('name'), header=str(data.get('header')).lower(), separator=data.get('separator').encode('string_escape'), classifier_id=data.get('model_id'), dataset_id=dataset_id, modalities_set_id=modalities_set_id, main_modality=modality, data_file = { "filename": data.get('file_name')})
            scoreset = cls(json.loads(str(dataset)))
            scoresets.append(scoreset)
        return scoresets
    
    @classmethod
    def result(cls, scoresets):
        lines = []
        first = True
        for scoreset in scoresets:
            url = scoreset.data_file.url
            those_lines = APIClient.request_direct(url).text.split("\n")
            i = 0
            for l in those_lines:
                if first:
                    lines.append(l)
                else:
                    lines[i] += '\t' + l
                i+=1
            first = False
        return "\n".join(lines)
    
    @classmethod
    def delete_all(cls):
        pass

class ReportAPI(CreatableAPIResource, UpdatableAPIResource, DeletableAPIResource):
    @classmethod
    def res_name(cls):
        return 'report'

class Report(CreatableAPIResource, UpdatableAPIResource, DeletableAPIResource):
    @classmethod
    def create(cls, **data):
        if validate('c', cls.__name__, data) < 0:
            raise PredicSisError("Validation failed!")
        type = data.get('type')
        if type == 'univariate_unsupervised':
            rep = ReportAPI.create(type=data.get('type'), dataset_id = data.get('dataset_id'), dictionary_id = data.get('dictionary_id'))
            return cls(json.loads(str(rep)))
        elif type == 'univariate_supervised':
            rep = ReportAPI.create(type=data.get('type'), dataset_id = data.get('dataset_id'), dictionary_id = data.get('dictionary_id'), variable_id = data.get('variable_id'))
            return cls(json.loads(str(rep)))
        elif type == 'classifier_evaluation':
            Variable.dictionary_id = data.get('dictionary_id')
            response = Variable.retrieve(data.get('variable_id'))
            modalities_set_id = response.modalities_set_ids[0]
            rep = ReportAPI.create(type=data.get('type'), dataset_id = data.get('dataset_id'), modalities_set_id=modalities_set_id, classifier_id = data.get('model_id'), main_modality=data.get('main_modality'))
            return cls(json.loads(str(rep)))

def validate(act, obj, data):
    cmandatory = {
        'dataset' : ['file', 'name'],
        'dictionary' : ['name'],
        'target' : ['target_var', 'dictionary_id'],
        'model' : ['variable_id', 'dataset_id'],
        'scoreset' : ['name', 'model_id', 'dictionary_id', 'data', 'file_name'],
        'report1' : ['type', 'dictionary_id', 'dataset_id'],
        'report2' : ['type', 'dictionary_id', 'dataset_id', 'variable_id'],
        'report3' : ['type', 'dictionary_id', 'dataset_id', 'model_id', 'main_modality', 'variable_id']
    }
    coptional = {
        'dataset' : ['header', 'separator', 'file_name'],
        'dictionary' : ['description', 'dataset_id'],
        'target' : ['unused_vars'],
        'model' : ['name'],
        'scoreset' : ['header', 'separator'],
        'report1' : ['title'],
        'report2' : ['title'],
        'report3' : ['title']
    }
    uoptional = {
        'dataset' : ['name', 'header', 'separator'],
        'dictionary' : ['name', 'description'],
        'scoreset' : ['name', 'header', 'separator'],
        'report' : ['title']
    }
    if not obj.lower() in coptional.keys() + uoptional.keys():
        predicsis.log('Unvalidated object [' + obj + ']', 1)
        return 0
    if act == 'c':
        predicsis.log('Parameters: mandatory'+ str(cmandatory.get(obj.lower())) + ', optional' + str(coptional.get(obj.lower())) + ', passed' + str(data.keys()), 3)
        if obj == 'Report':
            if data.get('type') == None:
                predicsis.log('Missing parameter to create [Report]: type')
                return -1
            if data.get('type') == 'univariate_unsupervised':
                obj = 'Report1'
            elif data.get('type') == 'univariate_supervised':
                obj = 'Report2'
            elif data.get('type') == 'classifier_evaluation':
                obj = 'Report3'
        if not all(x in data.keys() for x in cmandatory.get(obj.lower())):
            predicsis.log('Missing parameters to create [' + obj + ']: ' + str([item for item in cmandatory.get(obj.lower()) if item not in data.keys()]), -1)
            return -1
    if act == 'c':
        list = [item for item in data.keys() if item not in (coptional.get(obj.lower()) + cmandatory.get(obj.lower()))]
        if len(list) > 0:
            predicsis.log('Unnecessary parameters to create [' + obj + ']: ' + str(list), 0)
            return 0
    if act == 'u':
        predicsis.log('Parameters: optional' + str(uoptional.get(obj.lower())) + ', passed' + str(data.keys()), 3)
        list = [item for item in data.keys() if item not in uoptional.get(obj.lower())]
        if len(list) > 0:
            predicsis.log('Unnecessary parameters to update [' + obj + ']: ' + str(list), 0)
            return 0
    return 1
