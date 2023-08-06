# -*- coding: utf-8 -*-


class Formats(object):

    culprit = "`Culprit- {filepath}>{lineno}>{exception}`"

    title = "{exception} - {filename}::{method_name}"

    body = """
Following exception occurred:

```python
{stack_trace}
```
"""
    locals_format = """
Locals:
```python
{locals_data}
```

"""

    request_data = """
Request Data:

```python
{request_data}
```
"""
