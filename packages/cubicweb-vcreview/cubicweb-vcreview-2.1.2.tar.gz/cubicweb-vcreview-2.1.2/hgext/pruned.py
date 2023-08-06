import mercurial.revset, mercurial.obsolete
#from mercurial.i18n import _

def _is_pruned(repo, node):
    repo = repo.unfiltered()
    succmarkers = repo.obsstore.successors
    toproceed = set([node])
    seen = set(toproceed)
    while toproceed:
        current = toproceed.pop()
        if current not in succmarkers:
            return False
        for m in succmarkers.get(current, ()):
            for s in m[1]:
                if s not in seen:
                    seen.add(s)
                    toproceed.add(s)
    return True

def pruned(repo, subset, x):
#    mercurial.revset.getargs(x, 0, 0, _('unknown_successor takes no argument'))
    mercurial.revset.getargs(x, 0, 0, 'unknown_successor takes no argument')
    return subset.filter(lambda node: _is_pruned(repo, repo[node].node()))

def extsetup(ui):
    if mercurial.obsolete._enabled:
        mercurial.revset.symbols['pruned'] = pruned
