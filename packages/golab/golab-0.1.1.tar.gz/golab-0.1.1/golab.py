__all__ = ["__version__", "Client"]
__version__ = "0.1.0"

import collections
import json

import memcache


class Client(object):
    __slots__ = ["connection"]

    def __init__(self, host="127.0.0.1", port=11222):
        self.connection = memcache.Client(["%s:%s" % (host, port)])

    def get_user_variants(self, exp_ids, user_id):
        keys = ['%s:%s' % (exp_id, user_id) for exp_id in exp_ids]
        data = self.connection.get_multi(keys)
        results = {}

        for key, value in data.iteritems():
            exp_id, _, _ = key.partition(":")
            results[exp_id] = value

        return results

    def get_user_variant(self, exp_id, user_id):
        key = '%s:%s' % (exp_id, user_id)
        return self.connection.get(key)

    def convert_user(self, exp_id, user_id):
        key = '%s:%s' % (exp_id, user_id)
        return self.connection.incr(key)

    def add_new_experiment(self, data):
        data = json.dumps(data)
        return self.connection.add("1", data)

    def update_experiment(self, exp_id, data):
        data = json.dumps(data)
        return self.connection.replace(exp_id, data)

    def get_experiment(self, exp_id):
        data = self.connection.get("experiment:%s" % (exp_id, ))
        if data:
            return json.loads(data)
        return None

    def get_active_experiments(self):
        data = self.connection.get("experiment:active")
        results = {}
        if data:
            data = json.loads(data)
            for exp in data:
                results[int(exp['id'])] = exp
        return results

    def get_all_experiments(self):
        data = self.connection.get("experiment:*")
        results = {}
        if data:
            data = json.loads(data)
            for exp in data:
                results[int(exp['id'])] = exp
        return results

    def deactivate_experiment(self, exp_id):
        return self.connection.delete(exp_id)

    def activate_experiment(self, exp_id):
        return self.connection.touch(exp_id)

    def get_active_experiment_stats(self):
        data = self.connection.get_stats()
        results = collections.defaultdict(lambda: collections.defaultdict(dict))
        for server, stats in data:
            for key, value in stats.iteritems():
                key, exp_id, bucket_id = key.split(".")
                results[int(exp_id)][int(bucket_id)][key] = value
        return results

    def get_experiment_stats(self, exp_id):
        data = self.connection.get_stats(str(exp_id))
        results = collections.defaultdict(dict)
        for server, stats in data:
            for key, value in stats.iteritems():
                key, exp_id, bucket_id = key.split(".")
                results[int(bucket_id)][int(key)] = value
        return results
