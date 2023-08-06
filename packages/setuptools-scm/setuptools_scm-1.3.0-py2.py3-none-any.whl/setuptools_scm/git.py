from .utils import do, do_ex
from .version import meta

FILES_COMMAND = 'git ls-files'


def parse(root):
    rev_node, _, ret = do_ex('git rev-parse --verify --quiet HEAD', root)
    if ret:
        return meta('0.0')
    rev_node = rev_node[:7]
    out, err, ret = do_ex('git describe --dirty --tags --long', root)
    if '-' not in out and '.' not in out:
        revs = do('git rev-list HEAD', root)
        count = revs.count('\n')
        if ret:
            out = rev_node
        return meta('0.0', distance=count + 1, node=out)
    if ret:
        return
    dirty = out.endswith('-dirty')
    if dirty:
        out = out.rsplit('-', 1)[0]

    tag, number, node = out.rsplit('-', 2)
    number = int(number)
    if number:
        return meta(tag, distance=number, node=node, dirty=dirty)
    else:
        return meta(tag, dirty=dirty, node=node)
