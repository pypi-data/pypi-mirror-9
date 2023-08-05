# Digital Ocean PYthon wrapper that Sucks Less

Inspired by https://github.com/ahmontero/dop and https://github.com/devo-ps/dopy

## Installation

```
pip install dopysl
```

## Getting Started

Credentials for DigitalOcean API should be passed in environment variables.
There is API v1 and v2.

If you want to use APIv2, you need to find out the api token from https://cloud.digitalocean.com/settings/applications and you shoud set it as envvar:

```sh
export DO_API_TOKEN=...
```

If you still want to use APIv1 you need to define client ID and API key. **!!!Beware, API key for v1 is different than API token for v2 !!!**. Find it out from https://cloud.digitalocean.com/api_access and set it as:

```sh
export DO_CLIENT_ID=...
export DO_API_KEY=...
```

## Usage

You have to call the dopysl.init() first to authenticate.

To list all the droplets:

```python
import dopysl
dopysl.init()
print dopysl.all_active_droplets()
```

alternatively more prettily:

```python
import dopysl
import json

pp = lambda chunk: json.dumps(chunk, sort_keys=True, indent=4)

dopysl.init()
pp(dopysl.all_active_droplets())
```

If you use APIv2 you can use strings instead of id for regions, sizes, etc.
i.e. you can do

```python
dopysl.init()
dopysl.new_droplet('new_vm', '512mb', 'lamp', 'ams2')
```

If you use APIv1 you first need to get ID of those.

# Methods

The methods of the DoManager are self explanatory; ex.

```
dopysl.init()
dopysl.all_active_droplets()
dopysl.show_droplet('12345')
dopysl.destroy_droplet('12345')
dopysl.call_regions()
dopysl.call_images()
dopysl.call_ssh_keys()
dopysl.sizes()
dopysl.all_domains()
dopysl.new_droplet('new_droplet', 66, 1601, 1)
```

The methods for v.2 API are similar, the only difference
is using names instead of IDs for domains and slugs for
sizes, images and datacenters; ex.

```
dopysl.init()
dopysl.show_domain('exapmle.com')
dopysl.new_droplet('new_droplet', '512mb', 'lamp', 'ams2')
```

More in https://github.com/t0mk/dopysl/blob/master/dopysl/__init__.py
