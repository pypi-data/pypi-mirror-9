# Docker registry ufile driver

This is a [docker-registry backend driver](https://github.com/dotcloud/docker-registry/tree/master/depends/docker-registry-core) based on the [UFile](http://www.ucloud.cn/product/ufile_main/) key-value storage.

[![PyPI version][pypi-image]][pypi-url]
[![Build Status][travis-image]][travis-url]
[![Coverage Status]()]()
![Downloads]()
## Usage

Assuming you have a working docker-registry

`pip install docker-registry-driver-ufile`

Edit your configuration so that `storage` reads `ufile`.


## Options

You may add any of the following to your main docker-registry configuration to further configure it.

1. `ufile_baseurl`: your ufile bucket url, like `http://your-bucket.ufile.ucloud.cn` (scheme included), you should use internal url like `http://your-bucket.ufile.cn-north-03.ucloud.cn` if possible
1. `ufile_public_key`: ucloud public key
1. `ufile_private_key`: ucloud private key
1. `ufile_retries`: total retries if an http request fails (default 3)
1. `ufile_retry_interval`: if a http request fails, wait several seconds before trying again (default 1)
1. `ufile_timeout`: seconds to wait for the operation complete (default 60)

Example:

```yaml
ufile:
      <<: *common
      storage: ufile
      ufile_baseurl: http://your-bucket.ufile.ucloud.cn
      ufile_public_key: your-ucloud-public-key
      ufile_private_key: your-ucloud-private-key
      ufile_retries: 3
      ufile_retry_interval: 1
      ufile_timeout: 60
```

## Developer setup

Clone this.

Setup test environment:

```
pip install tox
```

Start the test `ufile`:

```
tox
```

You are ready to hack.
In order to verify what you did is ok, just run `tox`.

This will run the tests provided by [`docker-registry-core`](https://github.com/dotcloud/docker-registry/tree/master/depends/docker-registry-core)


## License

This is licensed under the Apache license.
Most of the code here comes from docker-registry, under an Apache license as well.

[pypi-url]:
[pypi-image]:

[travis-url]:
[travis-image]:
