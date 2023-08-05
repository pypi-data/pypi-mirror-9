/*
 *  :organization: Logilab
 *  :copyright: 2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
 *  :contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
 */


/* this function is called on to add activity from inlined form
 *
 * It calls the [add|eid]_activity method on the jsoncontroller and [re]load
 * only the view for the added or edited activity
 */

function addActivity(eid, parentcreated, context) {
    validateForm(
	'has_activityForm' + eid, null,
	function(result, formid, cbargs) {
	    if (parentcreated) {
		// reload the whole section
		reloadCtxComponentsSection(context, result[2].eid, eid);
	    } else {
		// only reload the activity component
		reload('vcreview_activitysection' + eid, 'vcreview.activitysection',
		       'ctxcomponents', null, eid);
	    };
	});
}

$(function () {
    /* mark task as done */
    $(document).on('click', '.vcreview_task .task_is_done', function (evt) {
        var $mynode = $(evt.currentTarget),
            $parentnode = $mynode.parents('.vcreview_task'),
            eid = $parentnode.data('eid'),
            d = asyncRemoteExec('vcreview_change_state', eid);
        d.addCallback(function () {
            $('.vcreview_task[data-eid=' + eid + ']').each(function () {
                var params = ajaxFuncArgs('render', null, 'views', 'vcreview.task-view', eid);
                $(this).loadxhtml(AJAX_BASE_URL, params, null, 'swap');
            });
        });
        return false;
    });
});

