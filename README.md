# Description

This module is a simple 2D dictionary wrapper used to create an excel like table in python.

# Usage

```python
from vtable import VTable

column_headers = ['row_headers_column', 'A', 'B', 'C']
row_headers = ['1', '2', '3']

table = VTable(column_headers, row_headers)
table.fill_column('A', 'FILLED')
print table.export('\t')

table['B', '2'] = 'C'
print table.export('\t')
print table['B', '2']  # prints 'C'
```

# Drawbacks

Row headers must be unique just like column headers in SQL

# To Do

* Allow multiple row headers
* Add loading of flat files

# Installation

* Clone the repository to your local machine
* `pip install -e /path/to/local/folder/vtable`