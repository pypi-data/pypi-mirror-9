import requests
import clearbit

class Resource(dict):
    endpoint = ''

    @classmethod
    def new(cls, item):
        if isinstance(item, list):
            return (cls(rec) for rec in item)
        else:
            return cls(item)

    @classmethod
    def get(cls, url, **options):
        params = options.get('params', {})
        key = options.get('key', clearbit.key)
        endpoint = cls.endpoint + url

        if 'stream' in options:
            endpoint = endpoint.replace('.', '-stream.', 1)

        response = requests.get(endpoint, params=params, auth=(key, ''))

        if response.status_code == 200:
            return cls.new(response.json())
        if response.status_code == 202:
            return cls({ 'pending': True })
        elif response.status_code == requests.codes.not_found:
            return None
        else:
            response.raise_for_status()

    @classmethod
    def post(cls, url, **options):
        params = options.get('params', {})
        key = options.get('key', clearbit.key)
        endpoint = cls.endpoint + url

        response = requests.post(endpoint, params=params, auth=(key, ''))
        response.raise_for_status()

        return response

    @classmethod
    def delete(cls, url, **options):
        key = options.get('key', clearbit.key)
        endpoint = cls.endpoint + url

        response = requests.delete(endpoint, auth=(key, ''))
        response.raise_for_status()

        return response
