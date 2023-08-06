pwf = get_workflow_for('Patch', ask_confirm=False)
outdated = pwf.state_by_name('outdated')
reviewed = pwf.state_by_name('reviewed')
pwf.add_transition(_('reopen/accept'), outdated, reviewed, ('managers', ))
