import json, glob, os, numpy as np, datetime, shutil

class JsonParser():
    def __init__(self, folder : str):
        """
        JSonParser will save the recordings of the experiment as json files
        folder : the location where the json will be saved, it will be created if it does not exist
        cont : if set to False and the parameter folder is an existing directory, then previous recordings will be erased. If set to True, new recordings will be appended to existing ones
        """
        self.folder = folder
        self.power_metric_filename = self.folder + '/power_metrics.json'
        self.exp_metric_filename = self.folder + '/results_exp.json'
        if not os.path.isdir(self.folder):
            os.makedirs(self.folder)
        self.model_card_file = os.path.join(self.folder,'model_summary.json')

    def erase(self):
        shutil.rmtree(self.folder)
        os.makedirs(self.folder)

    def save_model_card(self, model_card):
        print('saving model', self.model_card_file)
        json.dump(model_card, open(self.model_card_file, 'w'))

    def save_power_metrics(self, metrics):
        power_metric_fileout = open(self.power_metric_filename,'a')
        today_str = datetime.datetime.now().__str__()
        data = { 'date': today_str, 'metrics': metrics }
        json_str = json.dumps(data)
        power_metric_fileout.write(json_str+'\n')

    def save_exp_metrics(self, metrics):
        exp_metric_fileout = open(self.exp_metric_filename,'a')
        today_str = datetime.datetime.now().__str__()
        data = { 'date': today_str, 'metrics': metrics }
        json_str = json.dumps(data)
        exp_metric_fileout.write(json_str+'\n')

    def get_model_card(self, folder):
        assert os.path.isfile(self.model_card_file)
        return json.load(open(self.model_card_file))

    def load_cpu_metrics(self):
        if os.path.isfile(self.power_metric_filename):
            metrics = {}
            for line in open(self.power_metric_filename):
                result = json.loads(line)
                date = datetime.datetime.fromisoformat(result['date'])
                if 'cpu' in result['metrics']:
                    for k, v in result['metrics']['cpu'].items():
                        if isinstance(v, dict):
                            v = sum(v.values())
                        if k not in metrics:
                            metrics[k] = {'dates':[], 'values':[]}
                        metrics[k]['dates'].append(date)
                        metrics[k]['values'].append(v)
            if len(metrics) == 0:
                return None
            return metrics

    def load_gpu_metrics(self):
        if os.path.isfile(self.power_metric_filename):
            metrics = {} #Streaming Processor / Shared Processor sm
            for line in open(self.power_metric_filename):
                result = json.loads(line)
                if 'gpu' in result['metrics']:
                    date = datetime.datetime.fromisoformat(result['date'])
                    for k in ['nvidia_estimated_attributable_power_draw', 'nvidia_estimated_attributable_power_draw']:
                        v = result['metrics']['gpu'][k]
                        if k not in metrics:
                            metrics[k] = {'dates':[], 'values':[]}
                        metrics[k]['dates'].append(date)
                        metrics[k]['values'].append(v)
            if len(metrics) == 0:
                return None
            return metrics

    def load_exp_metrics(self):
        if os.path.isfile(self.exp_metric_filename):
            results = json.load(open(self.exp_metric_filename))
            for result in results:
                date = datetime.datetime.fromisoformat(result['end_training_epoch'])
                for k in result:
                    if k == 'end_training_epoch':
                        continue
                    if k not in metrics:
                        self.metrics[k] = {'dates':[], 'values':[]}
                    metrics[k]['dates'].append(date)
                    metrics[k]['values'].append(result[k])


    def load_metrics(self):
        cpu_metrics = self.load_cpu_metrics()
        gpu_metrics = self.load_gpu_metrics()
        exp_metrics = self.load_exp_metrics()
        return cpu_metrics, gpu_metrics, exp_metrics