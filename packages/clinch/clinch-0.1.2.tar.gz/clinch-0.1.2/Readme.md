Clinch
======

*easy command-line parsing for Python 3*

[![Build Status](https://travis-ci.org/enaeseth/clinch.svg?branch=master)](https://travis-ci.org/enaeseth/clinch)

```python
from clinch import application, arg

git = application('a stupid content tracker')

@git.command('Add things')
def add(all: arg('-A', '--all', action='store_true',
                 help='really make things match'),
        paths: arg('paths', nargs='*')):
    print('all?', ('yes' if all else 'no'))
    print('paths:', ', '.join(paths))

@git.command('Commit changes')
def commit(all: arg('-a', '--all',
                    help='include all modifications and deletions'),
           message: arg('-m', '--message', help='the commit message'),
           verbose: arg('-v', '--verbose', help='show diff in message editor')):
    pass

if __name__ == '__main__':
    git.run()
```
