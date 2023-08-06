
from cubicweb.predicates import is_instance, is_in_state
from cubicweb.sobjects.notification import StatusChangeMixIn, NotificationView
from cubes.nosylist.sobjects import NosyListRecipientsFinder
from cubes.task import hooks as task
from cubes.vcreview.site_cubicweb import COMPONENT_CONTEXT

MAX_PATCH_SIZE = 100 << 10 # 100 Ko


class NosyListPatchRecipientsFinder(NosyListRecipientsFinder):
    """Recipient finder of Patches.

    Merge users in the patch nosy list with those of the associated repository.

    This recipient finder is implemented instead of using a nosy list
    propagation rule to avoid useless (and costly) propagations when a user
    subscribes to a project with a "big" set of patches.
    """
    __select__ = is_instance('Patch')

    def recipients(self):
        recipients = set(super(NosyListPatchRecipientsFinder, self).recipients())
        patch_eid = self.cw_rset[self.cw_row or 0][self.cw_col or 0]
        rset = self._cw.execute('Any X WHERE P eid %(p)s, P patch_revision R,'
                                ' R from_repository X', {'p': patch_eid})
        repo_finder = self._cw.vreg['components'].select(
            'recipients_finder', self._cw, rset=rset, row=0, col=0)
        recipients.update(set(repo_finder.recipients()))
        return list(recipients)


class PatchAddedView(NotificationView):
    """Notification view for new patches."""
    __regid__ = 'notif_after_add_entity'
    __select__ = is_instance('Patch')
    msgid_timestamp = False
    content = """url: %(url)s

%(content)s
"""

    def subject(self):
        entity = self.cw_rset.get_entity(0, 0)
        return self._cw._(u'[%(repo)s] new patch: %(patch)s') % {
            'repo': entity.repository.dc_title(),
            'patch': entity.dc_title()}

    def context(self, **kwargs):
        entity = self.cw_rset.get_entity(0, 0)
        patch = entity.email_export(size=MAX_PATCH_SIZE)
        return super(PatchAddedView, self).context(content=patch, **kwargs)


class PatchStatusChangeView(StatusChangeMixIn, NotificationView):
    __select__ = is_instance('Patch') & is_in_state('pending-review',
                                                    'in-progress',
                                                    'reviewed',
                                                    'applied',
                                                    'rejected')

    content = StatusChangeMixIn.content + '''
%(reviewer)s

%(patch)s
'''

    def subject(self):
        entity = self.cw_rset.get_entity(0, 0)
        return self._cw._(u'[%(repo)s] patch %(state)s: %(patch)s') % {
            'repo': entity.repository.dc_title(),
            'patch': entity.dc_title(),
            'state': self._cw.__(self._kwargs['current_state'])}

    def context(self, **kwargs):
        context = super(PatchStatusChangeView, self).context(**kwargs)
        entity = self.cw_rset.get_entity(0, 0)
        tasks = []
        for task in self._cw.execute(
            u'Any T,TT ORDERBY TCD DESC '
            'WHERE T in_state TS, TS name "todo" '
            'WITH T,TT,TCD BEING ('
            '(Any T,TT,TCD WHERE '
            'X has_activity T, T title TT, T creation_date TCD, X eid %(x)s)'
            ' UNION '
            '(Any T,TT,TCD WHERE '
            'X patch_revision RE, IP point_of RE, IP has_activity T, '
            'T title TT, T creation_date TCD, X eid %(x)s)'
            ')', {'x': entity.eid}).entities():
            tasks.append(task.dc_title())
        if tasks:
            context['comment'] += '\n\n%s\n\n- %s' % (
                self._cw._('remaining tasks:'), '\n- '.join(tasks))
        else:
            context['comment'] += '\n\n%s' % self._cw._('(No recorded task)')

        context['patch'] = ''
        if self._kwargs['current_state'] == 'pending-review':
            patch = entity.email_export(size=MAX_PATCH_SIZE)
            context['patch'] = patch

        if entity.patch_reviewer:
            context['reviewer'] = self._cw._('reviewer: ') + ', '.join([user.dc_title() for user in entity.patch_reviewer])
        else:
            context['reviewer'] = self._cw._('reviewer: ')

        return context


class TaskAddedView(task.TaskAddedView):
    """get notified from new tasks"""
    __select__ = is_instance('Task')
    content_attr = 'description'

    def subject(self):
        entity = self.cw_rset.get_entity(0, 0)
        patch = entity.activity_of
        if not patch:
            return super(TaskAddedView, self).subject()
        if patch.__regid__ == 'InsertionPoint':
            patch = patch.parent.reverse_patch_revision
            if not patch:
                return super(TaskAddedView, self).subject()
            patch = patch[0]
        return self._cw._(u'[%(repo)s] patch task: %(patch)s - %(task)s') % {
            'repo': patch.repository.dc_title(),
            'patch': patch.dc_title(),
            'task': entity.dc_title()}

    def context(self, **kwargs):
        kwargs = super(TaskAddedView, self).context(**kwargs)
        task = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        concerned = task.activity_of
        if concerned:
            # build a URL for the task either in the context of an
            # InsertionPoint or directly using the related Patch.
            if concerned.cw_etype == 'InsertionPoint':
                revision = concerned.parent
                fragment = '#{ctx}{eid}'.format(ctx=COMPONENT_CONTEXT,
                                                eid=concerned.eid)
                url = revision.absolute_url(__secure__=True) + fragment
            else:
                # This should be a Patch.
                url = concerned.absolute_url(__secure__=True)
            kwargs['url'] = url
        return kwargs


class ReviewerSetNotificationView(NotificationView):
    __regid__ = 'vcreview.notifications.reviewer-set'
    __select__ = is_instance('Patch')
    content = _('''
You have been assigned for review of patch %(title)s

url: %(url)s

%(patch)s
''')
    def recipients(self):
        reviewer = self.cw_extra_kwargs['user']
        email = reviewer.cw_adapt_to('IEmailable').get_email()
        if email:
            return [(email, reviewer.property_value('ui.language'))]
        return []

    def subject(self):
        patch = self.cw_rset.get_entity(0, 0)
        return self._cw._('[%(repo)s] patch assigned: %(patch)s') % {
            'app': self._cw.vreg.config.appid,
            'repo': patch.repository.dc_title(),
            'patch': patch.dc_title()}

    def context(self, **kwargs):
        context = super(ReviewerSetNotificationView, self).context(**kwargs)
        entity = self.cw_rset.get_entity(0, 0)
        patch = entity.email_export(size=MAX_PATCH_SIZE)
        context['patch'] = patch
        return context


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, (TaskAddedView,))
    vreg.register_and_replace(TaskAddedView, task.TaskAddedView)
