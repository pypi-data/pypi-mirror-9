# -*- coding: utf-8 -*-

__version__ = '0.0.3'
__license__ = 'MIT'


import inspect
import json
import os
import requests

API_ENDPOINT = 'https://api.digitalocean.com'

DO_API_CREDENTIALS = """
Credentials for DigitalOcean API should be passed in environment variables.
There is API v1 and v2.
If you use APIv2 you can use strings instead of id for regions, sizes, etc.
i.e. you can do

Manager().new_droplet('new_vm', '512mb', 'lamp', 'ams2')

If you use APIv1 you first need to get ID of those.

If you want to use APIv2, you need to find out the api token from:
https://cloud.digitalocean.com/settings/applications

and you shoud set it as envvar:
export DO_API_TOKEN=...

If you still want to use APIv1 you need to define client ID and API key.
!!! API key for v1 is different than API token for v2 !!!
Find it out from:
https://cloud.digitalocean.com/api_accessA

And set it as:
export DO_CLIENT_ID=...
export DO_API_KEY=...
"""


def usage():
    print DO_API_CREDENTIALS
    sys.exit(1)

class DoError(RuntimeError):
    pass

class DoManager(object):

    def __init__(self, client_id, api_key, api_version=1):
        self.api_endpoint = API_ENDPOINT
        self.client_id = client_id
        self.api_key = api_key
        self.api_version = int(api_version)

        if self.api_version == 2:
            self.api_endpoint += '/v2'

    def all_active_droplets(self):
        json_out = self.request('/droplets/')
        return json_out['droplets']

    def new_droplet(self, name, size_id, image_id, region_id,
            ssh_keys, virtio=False, private_networking=False,
            backups_enabled=False):
        if self.api_version == 2:
            params = {
                'name': name,
                'size': size_id,
                'image': image_id,
                'region': region_id,
                'virtio': virtio,
                'private_networking': private_networking,
                'backups_enabled': backups_enabled,
            }
            if not isinstance(ssh_keys, list):
                ssh_keys = [ssh_keys]
            params['ssh_keys'] = ssh_keys
            json_out = self.request('/droplets', params=params, method='POST')
        else:
            params = {
                'name': name,
                'size_id': size_id,
                'image_id': image_id,
                'region_id': region_id,
                'virtio': virtio,
                'private_networking': private_networking,
                'backups_enabled': backups_enabled,
            }
            if ssh_key_ids:
                params['ssh_key_ids'] = ssh_key_ids

            json_out = self.request('/droplets/new', params=params)
        return json_out['droplet']

    def show_droplet(self, id):
        json_out = self.request('/droplets/%s' % id)
        return json_out['droplet']

    def droplet_v2_action(self, id, type, params={}):
        params = {
            'type': type
        }
        json_out = self.request('/droplets/%s/actions' % id, params=params, method='POST')
        return json_out

    def reboot_droplet(self, id):
        if self.api_version == 2:
            json_out = self.droplet_v2_action(id, 'reboot')
        else:
            json_out = self.request('/droplets/%s/reboot/' % id)
        json_out.pop('status', None)
        return json_out

    def power_cycle_droplet(self, id):
        if self.api_version == 2:
            json_out = self.droplet_v2_action(id, 'power_cycle')
        else:
            json_out = self.request('/droplets/%s/power_cycle/' % id)
        json_out.pop('status', None)
        return json_out

    def shutdown_droplet(self, id):
        if self.api_version == 2:
            json_out = self.droplet_v2_action(id, 'shutdown')
        else:
            json_out = self.request('/droplets/%s/shutdown/' % id)
        json_out.pop('status', None)
        return json_out

    def power_off_droplet(self, id):
        if self.api_version == 2:
            json_out = self.droplet_v2_action(id, 'power_off')
        else:
            json_out = self.request('/droplets/%s/power_off/' % id)
        json_out.pop('status', None)
        return json_out

    def power_on_droplet(self, id):
        if self.api_version == 2:
            json_out = self.droplet_v2_action(id, 'power_on')
        else:
            json_out = self.request('/droplets/%s/power_on/' % id)
        json_out.pop('status', None)
        return json_out

    def password_reset_droplet(self, id):
        if self.api_version == 2:
            json_out = self.droplet_v2_action(id, 'password_reset')
        else:
            json_out = self.request('/droplets/%s/password_reset/' % id)
        json_out.pop('status', None)
        return json_out

    def resize_droplet(self, id, size_id):
        if self.api_version == 2:
            params = {'size': size_id}
            json_out = self.droplet_v2_action(id, 'resize', params)
        else:
            params = {'size_id': size_id}
            json_out = self.request('/droplets/%s/resize/' % id, params)
        json_out.pop('status', None)
        return json_out

    def snapshot_droplet(self, id, name):
        params = {'name': name}
        if self.api_version == 2:
            json_out = self.droplet_v2_action(id, 'snapshot', params)
        else:
            json_out = self.request('/droplets/%s/snapshot/' % id, params)
        json_out.pop('status', None)
        return json_out

    def restore_droplet(self, id, image_id):
        if self.api_version == 2:
            params = {'image': image_id}
            json_out = self.droplet_v2_action(id, 'restore', params)
        else:
            params = {'image_id': image_id}
            json_out = self.request('/droplets/%s/restore/' % id, params)
        json_out.pop('status', None)
        return json_out

    def rebuild_droplet(self, id, image_id):
        if self.api_version == 2:
            params = {'image': image_id}
            json_out = self.droplet_v2_action(id, 'rebuild', params)
        else:
            params = {'image_id': image_id}
            json_out = self.request('/droplets/%s/rebuild/' % id, params)
        json_out.pop('status', None)
        return json_out

    def enable_backups_droplet(self, id):
        if self.api_version == 2:
            json_out = self.droplet_v2_action(id, 'enable_backups')
        else:
            json_out = self.request('/droplets/%s/enable_backups/' % id)
        json_out.pop('status', None)
        return json_out

    def disable_backups_droplet(self, id):
        if self.api_version == 2:
            json_out = self.droplet_v2_action(id, 'disable_backups')
        else:
            json_out = self.request('/droplets/%s/disable_backups/' % id)
        json_out.pop('status', None)
        return json_out

    def rename_droplet(self, id, name):
        params = {'name': name}
        if self.api_version == 2:
            json_out = self.droplet_v2_action(id, 'rename', params)
        else:
            json_out = self.request('/droplets/%s/rename/' % id, params)
        json_out.pop('status', None)
        return json_out

    def destroy_droplet(self, id, scrub_data=True):
        if self.api_version == 2:
            json_out = self.request('/droplets/%s' % id, method='DELETE')
        else:
            params = {'scrub_data': '1' if scrub_data else '0'}
            json_out = self.request('/droplets/%s/destroy/' % id, params)
        json_out.pop('status', None)
        return json_out

#regions==========================================
    def all_regions(self):
        json_out = self.request('/regions/')
        return json_out['regions']

#images==========================================
    def all_images(self, filter='global'):
        params = {'filter': filter}
        json_out = self.request('/images/', params)
        return json_out['images']

    def image_v2_action(self, id, type, params={}):
        params = {
            'type': type
        }
        json_out = self.request('/images/%s/actions' % id, params=params, method='POST')
        return json_out

    def show_image(self, image_id):
        params= {'image_id': image_id}
        json_out = self.request('/images/%s' % image_id)
        return json_out['image']

    def destroy_image(self, image_id):
        if self.api_version == 2:
            self.request('/images/%s' % id, method='DELETE')
        else:
            self.request('/images/%s/destroy' % image_id)
        return True

    def transfer_image(self, image_id, region_id):
        if self.api_version == 2:
            params = {'region': region_id}
            json_out = self.image_v2_action(id, 'transfer', params)
        else:
            params = {'region_id': region_id}
            json_out = self.request('/images/%s/transfer' % image_id, params)
        json_out.pop('status', None)
        return json_out

#ssh_keys=========================================
    def all_ssh_keys(self):
        if self.api_version == 2:
            json_out = self.request('/account/keys')
        else:
            json_out = self.request('/ssh_keys/')
        return json_out['ssh_keys']

    def new_ssh_key(self, name, pub_key):
        if self.api_version == 2:
            params = {'name': name, 'public_key': pub_key}
            json_out = self.request('/account/keys', params, method='POST')
        else:
            params = {'name': name, 'ssh_pub_key': pub_key}
            json_out = self.request('/ssh_keys/new/', params)
        return json_out['ssh_key']

    def show_ssh_key(self, key_id):
        if self.api_version == 2:
            json_out = self.request('/account/keys/%s/' % key_id)
        else:
            json_out = self.request('/ssh_keys/%s/' % key_id)
        return json_out['ssh_key']

    def edit_ssh_key(self, key_id, name, pub_key):
        if self.api_version == 2:
            params = {'name': name} # v2 API doesn't allow to change key body now
            json_out = self.request('/account/keys/%s/' % key_id, params, method='PUT')
        else:
            params = {'name': name, 'ssh_pub_key': pub_key}  # the doc needs to be improved
            json_out = self.request('/ssh_keys/%s/edit/' % key_id, params)
        return json_out['ssh_key']

    def destroy_ssh_key(self, key_id):
        if self.api_version == 2:
            self.request('/account/keys/%s' % key_id, method='DELETE')
        else:
            self.request('/ssh_keys/%s/destroy/' % key_id)
        return True

#sizes============================================
    def sizes(self):
        json_out = self.request('/sizes/')
        return json_out['sizes']

#domains==========================================
    def all_domains(self):
        json_out = self.request('/domains/')
        return json_out['domains']

    def new_domain(self, name, ip):
        params = {
                'name': name,
                'ip_address': ip
            }
        if self.api_version == 2:
            json_out = self.request('/domains', params=params, method='POST')
        else:
            json_out = self.request('/domains/new/', params)
        return json_out['domain']

    def show_domain(self, domain_id):
        json_out = self.request('/domains/%s/' % domain_id)
        return json_out['domain']

    def destroy_domain(self, domain_id):
        if self.api_version == 2:
            self.request('/domains/%s' % domain_id, method='DELETE')
        else:
            self.request('/domains/%s/destroy/' % domain_id)
        return True

    def all_domain_records(self, domain_id):
        json_out = self.request('/domains/%s/records/' % domain_id)
        if self.api_version == 2:
            return json_out['domain_records']
        return json_out['records']

    def new_domain_record(self, domain_id, record_type, data, name=None, priority=None, port=None, weight=None):
        params = {'data': data}

        if self.api_version == 2:
            params['type'] = record_type
        else:
            params['record_type'] = record_type

        if name: params['name'] = name
        if priority: params['priority'] = priority
        if port: params['port'] = port
        if weight: params['weight'] = weight

        if self.api_version == 2:
            json_out = self.request('/domains/%s/records/' % domain_id, params, method='POST')
        else:
            json_out = self.request('/domains/%s/records/new/' % domain_id, params)
        return json_out['record']

    def show_domain_record(self, domain_id, record_id):
        json_out = self.request('/domains/%s/records/%s' % (domain_id, record_id))
        if self.api_version == 2:
            return json_out['domain_record']
        return json_out['record']

    def edit_domain_record(self, domain_id, record_id, record_type, data, name=None, priority=None, port=None, weight=None):
        if self.api_version == 2:
            params['name'] = name # API v.2 allows only record name change
            json_out = self.request('/domains/%s/records/%s' % (domain_id, record_id), params, method=PUT)
            return json_out['domain_record']

        params = {
                'record_type': record_type,
                'data': data,
            }

        if name: params['name'] = name
        if priority: params['priority'] = priority
        if port: params['port'] = port
        if weight: params['weight'] = weight
        json_out = self.request('/domains/%s/records/%s/edit/' % (domain_id, record_id), params)
        return json_out['record']

    def destroy_domain_record(self, domain_id, record_id):
        if self.api_version == 2:
            self.request('/domains/%s/records/%s' % (domain_id, record_id), method='DELETE')
        else:
            self.request('/domains/%s/records/%s/destroy/' % (domain_id, record_id))
        return True

#events(actions in v2 API)========================
    def show_all_actions(self):
        if self.api_version == 2:
            json_out = self.request('/actions')
            return json_out['actions']
        return False # API v.1 haven't this functionality

    def show_action(self, action_id):
        if self.api_version == 2:
            json_out = self.request('/actions/%s' % event_id)
            return json_out['action']
        return show_event(self,action_id)

    def show_event(self, event_id):
        if self.api_version == 2:
            return show_action(self,event_id)
        json_out = self.request('/events/%s' % event_id)
        return json_out['event']

#low_level========================================
    def request(self, path, params={}, method='GET'):
        if not path.startswith('/'):
            path = '/'+path
        url = self.api_endpoint+path
        if self.api_version == 2:
            headers = { 'Authorization': "Bearer %s" % self.api_key }
            headers['Content-Type'] = 'application/json_out'
            resp = self.request_v2(url, params=params, headers=headers, method=method)
        else:
            params['client_id'] = self.client_id
            params['api_key'] = self.api_key
            resp = self.request_v1(url, params, method=method)

        return resp

    def request_v1(self, url, params={}, method='GET'):
        try:
            resp = requests.get(url, params=params, timeout=60)
            json_out = resp.json()
        except ValueError:  # requests.models.json.JSONDecodeError
            raise ValueError("The API server doesn't respond with a valid json_out")
        except requests.RequestException as e:  # errors from requests
            raise RuntimeError(e)

        if resp.status_code != requests.codes.ok:
            if json_out:
                if 'error_message' in json_out:
                    raise DoError(json_out['error_message'])
                elif 'message' in json_out:
                    raise DoError(json_out['message'])
            # The JSON reponse is bad, so raise an exception with the HTTP status
            resp.raise_for_status()
        if json_out.get('status') != 'OK':
            raise DoError(json_out['error_message'])

        return json_out

    def request_v2(self, url, headers={}, params={}, method='GET'):
        params = json.dumps(params)
        try:
            if method == 'POST':
                resp = requests.post(url, params=params, headers=headers, timeout=60)
                json_out = resp.json()
            elif method == 'DELETE':
                resp = requests.delete(url, headers=headers, timeout=60)
                json_out = { 'status': resp.status_code }
            elif method == 'PUT':
                resp = requests.put(url, headers=headers, params=params, timeout=60)
                json_out = resp.json()
            elif method == 'GET':
                resp = requests.get(url, headers=headers, params=params, timeout=60)
                json_out = resp.json()
            else:
                raise DoError('Unsupported method %s' % method)

        except ValueError:  # requests.models.json.JSONDecodeError
            raise ValueError("The API server doesn't respond with a valid json_out")
        except requests.RequestException as e:  # errors from requests
            raise RuntimeError(e)

        if resp.status_code != requests.codes.ok:
            if json_out:
                if 'error_message' in json_out:
                    raise DoError(json_out['error_message'])
                elif 'message' in json_out:
                    raise DoError(json_out['message'])
            # The JSON reponse is bad, so raise an exception with the HTTP status
            resp.raise_for_status()

        if json_out.get('id') == 'not_found':
            raise DoError(json_out['message'])

        return json_out


class Proxy(object):
    _manager = None
    def __new__(cls, *args, **kwargs):
        if not cls._manager:
            if os.environ.get('DO_API_TOKEN'):
                api_token = os.environ.get('DO_API_TOKEN')
                cls._manager = DoManager(None, api_token, 2)
            else:
                # we assume APIv1
                client_id = os.environ.get('DO_CLIENT_ID') or usage()
                api_key = os.environ.get('DO_API_KEY') or usage()
                cls._manager = DoManager(client_id, api_key, 1)
        return cls._manager


def init():
    """ checks if credentials are present and initalizes the module """
    manager = Proxy()

    current_module = __import__(__name__)
    # Following registers all the methods of DoManager to current namespace
    # so that we can call straight list
    # dopysl.init()
    # dopysl.all_active_droplets()
    for name, method in inspect.getmembers(manager, inspect.ismethod):
        if name != "__init__":
            setattr(current_module, name, method)



