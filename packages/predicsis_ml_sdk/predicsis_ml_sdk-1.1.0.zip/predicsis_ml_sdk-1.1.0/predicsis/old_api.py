import sys
import pprint
import json
import requests
from xml.dom import minidom

class PredicSisAPI(object):
    
    """ Initializes the prediction object """
    def __init__ (self, token="", storage=".", url="https://api.predicsis.com/", debug=1):
        self.token = token
        self.storage = storage
        self.url = url; 
        self.debug = debug
        requests.packages.urllib3.disable_warnings()
    
    """ Setting the token outside the init """
    def set_token(self, token):
        self.token = token    
                
    # Generic GET on the API
    def _simple_get(self, resource):
        headers = {'Accept': 'application/json', 'Authorization': 'Bearer ' + self.token}
        response = requests.get(self.url + resource, verify=False, headers=headers)
        if (self.debug >= 2):
            print 'GET['+self.url + resource+'] return status : ' + str(response.status_code)
        if (self.debug >= 3):
            print json.dumps(response.json(), indent=4)
        return response.json()
 
    # Generic POST on the API
    def _simple_post(self, resource, payload):
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': 'Bearer ' + self.token}
        response = requests.post(self.url + resource, verify=False, headers=headers, data=json.dumps(payload))
        if (self.debug >= 2):
            print 'POST['+self.url + resource+ ' (' + str(payload) +')] return status : ' + str(response.status_code)
        if (self.debug >= 3):
            print json.dumps(response.json(), indent=4)
        return response.json()
 
    # Generic POST on the API
    def _simple_patch(self, resource, payload):
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': 'Bearer ' + self.token}
        response = requests.patch(self.url + resource, verify=False, headers=headers, data=json.dumps(payload))
        if (self.debug >= 2):
            print 'PATCH['+self.url + resource+ ' (' + str(payload) +')] return status : ' + str(response.status_code)
        if (self.debug >= 3):
            print json.dumps(response.json(), indent=4)
        return response.json()
 
    # Generic DELETE on the API
    def _simple_delete(self, resource):
        headers = {'Accept': 'application/json', 'Authorization': 'Bearer ' + self.token}
        url = self.url + resource
        response = requests.delete(url, verify=False, headers=headers)
        if (self.debug >= 2):
            print 'DELETE['+self.url + resource+ '] return status : ' + str(response.status_code)
    
    """ Retrieving a job """
    def retrieve_job(self, job_id):
        if (self.debug >= 1):
            print 'Retrieving a job..'
        response = self._simple_get('jobs/' + job_id)
        return response
    
    """ Creating a dataset """
    def create_dataset(self, file, header=False, separator='\t'):
        if (self.debug >= 1):
            print 'Getting credentials..'
        credentials = self._simple_get('sources/credentials/s3') 
        payload = {
            'Content-Type':'multipart/form-data',
            'success_action_status':'201',
            'acl':'private',
            'policy':credentials['credentials']['policy'],
            'AWSAccessKeyId':credentials['credentials']['aws_access_key_id'],
            'signature':credentials['credentials']['signature'],
            'key':credentials['credentials']['key']
        }
        if (self.debug >= 1):
            print 'Uploading a file..'
        files = {'file': open(file,'rb')} 
        response = requests.post(credentials['credentials']['s3_endpoint'], data=payload, files=files)
        if (self.debug >= 2):
            print 'Status: ' + str(response.status_code) 
        xmlResponse = minidom.parseString(response.text)
        if (self.debug >= 3):
            print xmlResponse.toprettyxml(indent="\t")
        keyList = xmlResponse.getElementsByTagName('Key')
        if (self.debug >= 1):
            print 'Creating a source..'
        payload = {'source': {'name': file, 'key': keyList[0].firstChild.data}}
        response = self._simple_post('sources', payload)
        sid = response['source']['id']
        if (self.debug >= 1):
            print 'Creating a dataset..'
        payload = {'dataset' : {'name': file, 'header':header, 'separator':separator, 'source_ids':[sid]}}
        response = self._simple_post('datasets', payload)
        jid = response['dataset']['job_ids'][0]
        status = 'pending'
        job = self.retrieve_job(jid)
        status = job['job']['status']
        while ((status != 'completed') and (status != 'failed')):
            job = self.retrieve_job(jid)
            status = job['job']['status']
        if status == 'failed':
            raise Exception("Job failed! (job_id: " + job['job']['id'] + ")")
        dataset_id = response['dataset']['id'] 
        return dataset_id
    
    """ Retrieving a dataset """
    def retrieve_dataset(self, dataset_id):
        if (self.debug >= 1):
            print 'Retrieving a dataset..'
        response = self._simple_get('datasets/' + dataset_id)
        return response
    
    """ Retrieving a source """
    def retrieve_source(self, source_id):
        if (self.debug >= 1):
            print 'Retrieving a source..'
        response = self._simple_get('sources/' + source_id)
        return response
    
    """ Creating a dictionary """
    def create_dictionary(self, dataset_id):
        if (self.debug >= 1):
            print 'Creating a dictionary..'
        payload = {'dictionary' : {'name':"Dico_"+dataset_id, 'dataset_id':dataset_id }}
        dico = self._simple_post('dictionaries', payload)
        dictionary_id = dico['dictionary']['id']
        jid = dico['dictionary']['job_ids'][0]
        status = 'pending'
        job = self.retrieve_job(jid)
        status = job['job']['status']
        while ((status != 'completed') and (status != 'failed')):
            job = self.retrieve_job(jid)
            status = job['job']['status']
        if status == 'failed':
            raise Exception("Job failed! (job_id: " + job['job']['id'] + ")")
        return dictionary_id
    
    """ Edit a dictionary """
    def edit_dictionary(self, dictionary_id, target_var, unused_vars={}):
        if (self.debug >= 1):
            print 'Retrieving variables..'
        target_id = -1
        unused_ids = []
        dico = self._simple_get('dictionaries/' + str(dictionary_id))
        dataset_id = dico['dictionary']['dataset_id']
        variables = self._simple_get('dictionaries/' + str(dictionary_id) + '/variables')
        i = 1
        for var in variables['variables']:
            if type(target_var).__name__ == "str":
                if var['name'] == target_var:
                    target_id = var['id']
            elif type(target_var).__name__ == "int":
                if i == target_var:
                    target_id = var['id']
            if var['name'] in unused_vars:
                unused_ids.append(var['id'])
            elif i in unused_vars:
                unused_ids.append(var['id'])
            i+=1
        if target_id == -1:
            raise Exception("Your target variable doesn't exist in the dataset.")
        if (self.debug >= 1):
            print 'Creating a set of modalities..'
        payload = {"modalities_set" : {"variable_id":target_id, "dataset_id":dataset_id }}
        modalities = self._simple_post('modalities_sets', payload)
        for unused_id in unused_ids:
            payload = {"variable" : {"use": false }}
            response = self._simple_patch('dictionaries/' + dictionary_id + "/variables/" + unused_id, payload)
        jid = modalities['modalities_set']['job_ids'][0]
        status = 'pending'
        job = self.retrieve_job(jid)
        status = job['job']['status']
        while ((status != 'completed') and (status != 'failed')):
            job = self.retrieve_job(jid)
            status = job['job']['status']
        if status == 'failed':
            raise Exception("Job failed! (job_id: " + job['job']['id'] + ")")
        return target_id
    
    """ Retrieving a variable """
    def retrieve_variable(self, dictionary_id, variable_id):
        if (self.debug >= 1):
            print 'Retrieving a variable..'
        response = self._simple_get('dictionaries/' + dictionary_id + "/variables/" + variable_id)
        return response
    
    """ Retrieving a modalities set """
    def retrieve_modalities_set(self, modalities_set_id):
        if (self.debug >= 1):
            print 'Retrieving a set of modalities..'
        response = self._simple_get('modalities_sets/' + modalities_set_id)
        return response
    
    """ Retrieving a dictionary """
    def retrieve_dictionary(self, dictionary_id):
        if (self.debug >= 1):
            print 'Retrieving a dictionary..'
        response = self._simple_get('dictionaries/' + dictionary_id)
        return response
    
    """ Creating a model """
    def create_model(self, dataset_id, target_var_id):
        if (self.debug >= 1):
            print 'Creating a set of preparation rules..'
        payload = {'preparation_rules_set' : {'variable_id':target_var_id, 'dataset_id':dataset_id }}
        prs = self._simple_post('preparation_rules_sets', payload)
        prs_id = prs['preparation_rules_set']['id']
        jid = prs['preparation_rules_set']['job_ids'][0]
        status = 'pending'
        job = self.retrieve_job(jid)
        status = job['job']['status']
        while ((status != 'completed') and (status != 'failed')):
            job = self.retrieve_job(jid)
            status = job['job']['status']
        if status == 'failed':
            raise Exception("Job failed! (job_id: " + job['job']['id'] + ")")
        if (self.debug >= 1):
            print 'Creating a model..'
        payload = {'model' : {'type':'classifier', 'preparation_rules_set_id':prs_id }}
        model = self._simple_post('models', payload)
        model_id = model['model']['id']
        jid = model['model']['job_ids'][0]
        status = 'pending'
        job = self.retrieve_job(jid)
        status = job['job']['status']
        while ((status != 'completed') and (status != 'failed')):
            job = self.retrieve_job(jid)
            status = job['job']['status']
        if status == 'failed':
            raise Exception("Job failed! (job_id: " + job['job']['id'] + ")")
        return model_id
    
    """ Retrieving a preparation rules set """
    def retrieve_preparation_rules_set(self, preparation_rules_set_id):
        if (self.debug >= 1):
            print 'Retrieving a set of preparation rules..'
        response = self._simple_get('preparation_rules_sets/' + preparation_rules_set_id)
        return response
    
    """ Retrieving a model """
    def retrieve_model(self, model_id):
        if (self.debug >= 1):
            print 'Retrieving a model..'
        response = self._simple_get('models/' + model_id)
        return response
    
    """ Creating a score """
    def create_score(self, dictionary_id, model_id, data, header=False, separator='\t'):
        response = self.retrieve_model(model_id)
        prs_id = response['model']['preparation_rules_set_id']
        response = self.retrieve_preparation_rules_set(prs_id)
        var_id = response['preparation_rules_set']['variable_id']
        response = self.retrieve_variable(dictionary_id, var_id)
        modalities_set_id = response['variable']['modalities_set_ids'][0]
        response = self.retrieve_modalities_set(modalities_set_id)
        modalities = response['modalities_set']['modalities']
        if (self.debug >= 1):
            print 'Preparing data..'
        dataset_id = -1
        file_name = ""
        try:
            open(data,'rb')
            file_name=data
            dataset_id = self.create_dataset(data, header, separator)
        except IOError:
            file_name = self.storage + '/tmp.dat'
            f = open(file_name,'w')
            f.write(data)
            f.close()
            dataset_id = self.create_dataset(file_name, headers, separators)
        if dataset_id == -1:
            raise Exception("Error creating your test dataset")
        scoreset_ids = []
        for modality in modalities:
            payload = {'dataset' : {'name':'Scores', 'header':header, 'separator':separator, 'classifier_id':model_id, 'dataset_id':dataset_id, 'modalities_set_id':modalities_set_id, "main_modality":modality, 'data_file': { 'filename':file_name } }}
            scoreset = self._simple_post('datasets', payload)
            scoreset_id = scoreset['dataset']['id']
            jid = scoreset['dataset']['job_ids'][0]
            status = 'pending'
            job = self.retrieve_job(jid)
            status = job['job']['status']
            while ((status != 'completed') and (status != 'failed')):
                job = self.retrieve_job(jid)
                status = job['job']['status']
            if status == 'failed':
                raise Exception("Job failed! (job_id: " + job['job']['id'] + ")")
            scoreset_ids.append(scoreset_id)
        return scoreset_ids
    
    """ Retrieving a scoreset """
    def retrieve_scoreset(self, scoreset_id):
        if (self.debug >= 1):
            print 'Retrieving a scoreset..'
        response = self._simple_get('datasets/' + scoreset_id)
        return response
    
    """ Retrieving scores """
    def retrieve_scores(self, scoreset_ids):
        lines = []
        first = True
        for scoreset_id in scoreset_ids:
            response = self.retrieve_scoreset(scoreset_id)
            url = response['dataset']['data_file']['url']
            those_lines = requests.get(url).text.split("\n")
            i = 0
            for l in those_lines:
                if first:
                    lines.append(l)
                else:
                    lines[i] += '\t' + l
                i+=1
            first = False
        return "\n".join(lines)
    
    """ Creating an univariate unsupervised report """
    def create_uni_unsuper_report(self, dataset_id, dictionary_id):
        if (self.debug >= 1):
            print 'Creating a report..'
        payload = {'report' : {'type':'univariate_unsupervised', 'dataset_id':dataset_id, 'dictionary_id':dictionary_id }}
        response = self._simple_post('reports', payload)
        jid = response['report']['job_ids'][0]
        status = 'pending'
        job = self.retrieve_job(jid)
        status = job['job']['status']
        while ((status != 'completed') and (status != 'failed')):
            job = self.retrieve_job(jid)
            status = job['job']['status']
        if status == 'failed':
            raise Exception("Job failed! (job_id: " + job['job']['id'] + ")")
        return response['report']['id']
    
    """ Creating an univariate supervised report """
    def create_uni_super_report(self, dataset_id, dictionary_id, variable_id):
        if (self.debug >= 1):
            print 'Creating a report..'
        payload = {'report' : {'type':'univariate_supervised', 'dataset_id':dataset_id, 'dictionary_id':dictionary_id, 'variable_id':variable_id }}
        response = self._simple_post('reports', payload)
        jid = response['report']['job_ids'][0]
        status = 'pending'
        job = self.retrieve_job(jid)
        status = job['job']['status']
        while ((status != 'completed') and (status != 'failed')):
            job = self.retrieve_job(jid)
            status = job['job']['status']
        if status == 'failed':
            raise Exception("Job failed! (job_id: " + job['job']['id'] + ")")
        return response['report']['id']
    
    
    """ Creating a model evaluation report """
    def create_model_eval_report(self, dataset_id, dictionary_id, model_id, target_modality):
        if (self.debug >= 1):
            print 'Creating a report..'
        response = self.retrieve_model(model_id)
        prs_id = response['model']['preparation_rules_set_id']
        response = self.retrieve_preparation_rules_set(prs_id)
        var_id = response['preparation_rules_set']['variable_id']
        response = self.retrieve_variable(dictionary_id, var_id)
        modalities_set_id = response['variable']['modalities_set_ids'][0]
        payload = {'report' : {'type':'classifier_evaluation', 'dataset_id':dataset_id, 'classifier_id':model_id, 'modalities_set_id':modalities_set_id, 'main_modality':target_modality }}
        response = self._simple_post('reports', payload)
        jid = response['report']['job_ids'][0]
        status = 'pending'
        job = self.retrieve_job(jid)
        status = job['job']['status']
        while ((status != 'completed') and (status != 'failed')):
            job = self.retrieve_job(jid)
            status = job['job']['status']
        if status == 'failed':
            raise Exception("Job failed! (job_id: " + job['job']['id'] + ")")
        return response['report']['id']
    
    """ Retrieving a report """
    def retrieve_report(self, report_id):
        if (self.debug >= 1):
            print 'Retrieving a report..'
        response = self._simple_get('reports/' + report_id)
        return response
        
    """ Cleaning up the created stuff """
    def delete_all(self):
        if (self.debug >= 1):
            print 'Deleting everything..';
        response = self._simple_get('models')
        for model in response['models']:
            self._simple_delete('models/' + model['id'])
        response = self._simple_get('preparation_rules_sets')
        for prs in response['preparation_rules_sets']:
            self._simple_delete('preparation_rules_sets/' + prs['id'])
        response = self._simple_get('reports')
        for report in response['reports']:
            self._simple_delete('reports/' + report['id'])
        response = self._simple_get('dictionaries')
        for dico in response['dictionaries']:
            self._simple_delete('dictionaries/' + dico['id'])
        response = self._simple_get('modalities_sets')
        for mset in response['modalities_sets']:
            self._simple_delete('modalities_sets/' + mset['id'])
        response = self._simple_get('datasets')
        for dset in response['datasets']:
            self._simple_delete('datasets/' + dset['id'])
        response = self._simple_get('sources')
        for src in response['sources']:
            self._simple_delete('sources/' + src['id'])
