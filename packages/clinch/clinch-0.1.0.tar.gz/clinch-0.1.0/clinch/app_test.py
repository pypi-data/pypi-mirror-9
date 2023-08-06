import shlex

import pytest

from clinch import application, arg

git = application('git', description='a stupid content tracker')

@git.command('Add things')
def add(all: arg('-A', '--all', action='store_true',
                 help='really make things match'),
        paths: arg('paths', nargs='*')):
    return (add, all, paths)

@git.command('Commit changes')
def commit(all: arg('-a', '--all', action='store_true',
                    help='include all modifications and deletions'),
           message: arg('-m', '--message', help='the commit message'),
           verbose: arg('-v', '--verbose', action='store_true',
                        help='show diff in message editor')):
    return (commit, all, message, verbose)

def test_app():
    assert git.name == 'git'

def test_run():
    def run(cmdline):
        return git.run(shlex.split(cmdline))

    assert run('add') == (add, False, [])
    assert run('add -A') == (add, True, [])
    assert run('add foo bar') == (add, False, ['foo', 'bar'])

    assert run('commit') == (commit, False, None, False)
    assert run('commit -a') == (commit, True, None, False)
    assert run('commit -m "hey there"') == (commit, False, 'hey there', False)
    assert run('commit -av') == (commit, True, None, True)

    with pytest.raises(SystemExit):
        run('lol')

def test_run_sys_argv(monkeypatch):
    monkeypatch.setattr('sys.argv', ['git', 'commit', '-a'])
    assert git.run() == (commit, True, None, False)

def test_repr():
    assert repr(git) == '<Application git>'

if __name__ == '__main__':
    git.run()
