#This is a temporary fork of the original Bernhard to support some custom events that are NOT generic. You shouldn't use this fork and should use the original bernahrd version from banjiewen. Hopefully I will introduce generic events handling at some point, and merge back the work into the original repo.

# Bernhard

A simple Python client for [Riemann](http://github.com/aphyr/riemann). Usage:

```python
import bernhard

c = bernhard.Client()
c.send({'host': 'myhost.foobar.com', 'service': 'myservice', 'metric': 12})
q = c.query('true')
```

## Installing

```bash
pip install bernhard
```

You may encounter issues with the `protobuf` dependency; if so, just run `pip
install protobuf` manually, then `pip install bernhard`.

