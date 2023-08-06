# A10 Networks LBaaS Driver

A10 github repos:

- [a10-openstack-lbaas](https://github.com/a10networks/a10-openstack-lbaas) - OpenStack LBaaS driver, 
identical to the files that are currently merged into Juno.  Also supports Icehouse.  Pypi package 
'a10-openstack-lbaas'.
- [a10-openstack-lbaas, havana branch](https://github.com/a10networks/a10-openstack-lbaas/tree/havana) - OpenStack 
LBaaS driver, for the Havana release.  Pypi package 'a10-openstack-lbaas-havana'.
- [a10-neutron-lbaas](https://github.com/a10networks/a10-neutron-lbaas) - Middleware sitting between the 
openstack driver and our API client, mapping openstack constructs to A10's AxAPI.
- [acos-client](https://github.com/a10networks/acos-client) - AxAPI client used by A10's OpenStack driver.
- [neutron-thirdparty-ci](https://github.com/a10networks/neutron-thirdparty-ci) - Scripts used by 
our Jenkins/Zuul/Devstack-Gate setup, used to test every openstack code review submission against 
A10 appliances and our drivers.
- [a10_lbaas_driver](https://github.com/a10networks/a10_lbaas_driver) - An older revision of A10's 
LBaaS driver; no longer supported.

## Installation

To use this driver, you must:

1. Install the [a10-neutron-lbaas](https://github.com/a10networks/a10-neutron-lbaas) module. 
(E.g.: 'pip install a10-neutron-lbaas')
- Create a driver config file, a [sample](#example-config-file) of which is given below.
- Enable it in `neutron.conf`
- Restart neutron-server

### Configuration file:

Create a configuration file with a list of A10 appliances, similar to the
file below, located at: `/etc/neutron/services/loadbalancer/a10networks/config.py`.

Or you can override that directory by setting the environment
variable `A10_CONFIG_DIR`.

#### Example config file:

```python
devices = {
    "ax1": {
        "name": "ax1",
        "host": "10.10.100.20",
        "port": 443,
        "protocol": "https",
        "username": "admin",
        "password": "a10",
        "status": True,
        "autosnat": False,
        "api_version": "2.1",
        "v_method": "LSI",
        "max_instance": 5000,
        "use_float": False,
        "method": "hash"
    },
    "ax4": {
        "host": "10.10.100.23",
        "username": "admin",
        "password": "a10",
    },
}
```

## Third-party CI Information

If you encounter any problems, contact A10 at:

* [a10-openstack-ci@a10networks.com](mailto: a10-openstack-ci@a10networks.com)
* Doug Wiegley directly via IRC (dougwig)

## Contributing

1. Fork it ( http://github.com/a10networks/a10-openstack-lbaas/fork )
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create new Pull Request
