from cubicweb import Binary

etypelist = ['Plan'] + [i.type for i in schema['Plan'].specialized_by()]

add_cubes(('signedrequest', 'file'))

add_attribute('Recipe', 'script', commit=False)
rql('SET X script "#to be updated" WHERE X is Recipe, X script NULL')
sync_schema_props_perms(schema['Recipe'].rdef('name'))

for etype in etypelist:
    print "add script on", etype
    add_attribute(etype, 'script', commit=False)
    # we shouldn't have any, but just in case...
    rql('SET X script "unknown" WHERE X is %s, X script NULL' % etype)
commit()

drop_entity_type('RecipeStep')
drop_entity_type('RecipeTransition')
drop_entity_type('NarvalConditionExpression')
drop_entity_type('RecipeTransitionCondition')
drop_entity_type('RecipeStepInput')
drop_entity_type('RecipeStepOutput')

for rtype in ('in_recipe', 'start_step', 'end_step', 'in_steps',
              'in_error_steps', 'out_steps', 'conditions', 'takes_input',
              'generates_output', 'matches_condition'):
    if rtype not in fsschema:
        drop_relation_type(rtype)

# create the workflow for Plan and attach it to derivated entity types
if not rql('Any X, WF WHERE X name "Plan", WF workflow_of X'):
    make_workflowable('Plan')

    wf = add_workflow(u'Plan execution status workflow', 'Plan')

    ready = wf.add_state(_('ready'), initial=True)
    running = wf.add_state(_('running'))
    done = wf.add_state(_('done'))
    error = wf.add_state(_('error'),
            description=_('The execution of the Plan has been terminated (due to unexpected error)'))
    killed = wf.add_state(_('killed'),
            description=_('The execution of the Plan has been terminated (due to resource exhaustion)'))
    wf.add_transition(_('start'), ready, running, requiredgroups=('narval', 'managers'))
    wf.add_transition(_('end'), running, done, requiredgroups=('narval', 'managers'))
    wf.add_transition(_('fail'), running, error, requiredgroups=('narval', 'managers'))
    wf.add_transition(_('kill'), running, killed, requiredgroups=('narval', 'managers'))

    # attach the workflow to all derived entity types
    rql('SET WF workflow_of TE, TE default_workflow WF WHERE P default_workflow WF, '
        'P name "Plan", TE specializes P, P is CWEType')
    commit(ask_confirm=True)


# Ensure workflow status:
for etype in etypelist:
    print "Managing %s workflow" % etype
    # remove Plan (and derived CWETypes) that are in "running" state:
    # these are zombies
    rql('DELETE %s P WHERE P execution_status "running"' % etype)

    # for each TestExecution...
    te_eids = rql('DISTINCT Any X WHERE '
                  'X is %s, '
                  'NOT X in_state S' % etype)
    print "Setting %s %s in 'ready' state" % (len(te_eids), etype)
    # set it in correct initial state
    for (eid,) in te_eids:
        session.entity_from_eid(eid).cw_adapt_to('IWorkflowable').set_initial_state('ready')
    commit()
    # fire all necessary transitions
    print "Setting TestExecution states in correct state"
    to_update=[]
    for (eid,) in te_eids:
        te = session.entity_from_eid(eid)
        if te.execution_status == 'ready':
            continue

        tri = te.cw_adapt_to('IWorkflowable').fire_transition('start')
        if te.starttime:
            to_update.append((tri.eid, te.starttime))

        if te.execution_status == 'done':
            tri = te.cw_adapt_to('IWorkflowable').fire_transition('end')
        elif te.execution_status == 'killed':
            tri = te.cw_adapt_to('IWorkflowable').fire_transition('kill')
        else:
            tri = te.cw_adapt_to('IWorkflowable').fire_transition('fail')
        if te.endtime:
            to_update.append((tri.eid, te.endtime))

    # set correct timestamps
    for eid, date in to_update:
        rql('SET TI creation_date %(date)s WHERE TI eid %(eid)s',
            {'date': date, 'eid': eid})
    commit()


install_custom_sql_scripts('narval')

log_list = []

if confirm('Upgrade all execution_logs to file objects (if you say no here, execution logs will be lost)?'):
    # first create the File entities with
    from cubicweb.predicates import is_instance
    from cubicweb.entities.adapters import IFTIndexableAdapter
    class NoIndexFileIndexableAdapter(IFTIndexableAdapter):
        __select__ = is_instance('File')
        def get_words(self):
            return {}
    obj = NoIndexFileIndexableAdapter
    session.vreg.register(obj)
    registered = getattr(obj, '__registered__', None)
    if registered:
        for registry in obj.__registries__:
            registered(session.vreg[registry])
    try:
        for i, (eid,) in enumerate(rql('Any X WHERE X is_instance_of Plan, NOT X execution_log NULL')):
            data = rql('Any F WHERE X execution_log F, X eid %(eid)s', {'eid': eid})[0][0]
            rset = rql('INSERT File F: F data_name "execution_log.txt", F data %(data)s, '
                       'F data_encoding "utf-8", F data_format "text/plain"',
                       {'data': Binary(data.encode('utf-8')), 'eid': eid})

            log_list.append((eid, rset[0][0]))
            if not i%1000:
                print i, "..."
                commit(ask_confirm=False)
                print "OK"
        commit(ask_confirm=False)
    finally:
        session.vreg.unregister(obj)

for etype in etypelist:
    drop_attribute(etype, 'execution_log')
for etype in etypelist:
    add_relation_definition(etype, 'execution_log', 'File')

sync_schema_props_perms('execution_log')

# transform attribute to file
for plan_eid, log_file_eid in log_list:
        rql('SET X execution_log Y WHERE X eid %(x)s, Y eid %(y)s',
                {'x': plan_eid, 'y': log_file_eid})

commit()

for etype in etypelist:
    drop_attribute(etype, 'execution_status')
    drop_attribute(etype, 'starttime')
    drop_attribute(etype, 'endtime')
    drop_attribute(etype, 'arguments')
