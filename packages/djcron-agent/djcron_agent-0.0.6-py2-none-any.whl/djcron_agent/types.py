from collections import namedtuple


Host = namedtuple('Host', ('fqdn', ))
Output = namedtuple('Output', ('rc', 'stdout', 'stderr'))
Timestamp = namedtuple('Timestamp', ('start', 'end'))

Result = namedtuple('Result', ('host', 'output', 'timestamp'))
