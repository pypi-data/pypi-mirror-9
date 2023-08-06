# core Python imports
import datetime
import logging
import operator


# django imports
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import utc
from django.db.models import Q


# local app imports
from djhcup_staging.models import StagingBatch, StagingQueue, StagingTable, ImportBatch, File
from djhcup_staging.utils import misc


# start a logger
default_logger = logging.getLogger('default')


# constants
STAGING_CONVERSIONS = [
    dict(cat_out='CHARGES', req_in=['CHARGES_SOURCE']),
    dict(cat_out='PR', req_in=['CORE_SOURCE']),
    dict(cat_out='DX', req_in=['CORE_SOURCE']),
    dict(cat_out='UFLAGS',
         req_in=[
            'CORE_SOURCE',
            'CHARGES',
            'PR',
        ]),
    dict(cat_out='CORE_PROCESSED',
         req_in=[
            'CORE_SOURCE',
        ],
         opt_in=[
            'AHALINK_SOURCE',
            'UFLAGS',
            'DX_PR_GRPS_SOURCE',
            'SEVERITY_SOURCE',
            'CORE_SOURCE',
            'DAYSTOEVENT_SOURCE',
        ]),
]

CAT_IN_TO_ATTR = {
    'AHALINK_SOURCE': 'aha_input',
    'CHARGES_SOURCE': 'stg_input',
    'DX_PR_GRPS_SOURCE': 'dx_pr_grps_input',
    'SEVERITY_SOURCE': 'severity_input',
    'CORE_SOURCE': 'stg_input',
    'DAYSTOEVENT_SOURCE': 'dte_input',
    'CHARGES': 'charges_input',
    'PR': 'pr_input',
    'UFLAGS': 'uflag_input',
}

DATA_SOURCE_PARENTS = [
    'SID',
    'SEDD',
    'SASD',
    'PUDF'
]


def unprocessed_batches(conversions=STAGING_CONVERSIONS,
                        cat_to_attr=CAT_IN_TO_ATTR,
                        allowable_ds_parents=DATA_SOURCE_PARENTS):
    """
    Creates batches for unprocessed files, including batches with
    changed input availability.
    """
    now = datetime.datetime.utcnow().replace(tzinfo=utc).strftime("%Y%m%d%H%M%S")
    b = StagingBatch(name='Unprocessed, circa {now}'.format(now=now), description='Conversions include...')
    b.save()

    states = misc.states()
    years = misc.years()
    for ds in allowable_ds_parents:
        # throw a pre-check in here to see if there are any tables at all with this ds as parent?
        # might save some time on chunking through SEDD/SASD for now
        ds_ct = StagingTable.objects \
            .filter(imported_via__file__file_type__source__parent__abbreviation=ds) \
            .count()
        if ds_ct > 0:
            default_logger.info("Found one or more StagingTable objects with traceable heredity to parent data source with abbreviation {ds}. Proceeding...".format(ds=ds))
            for con in conversions:
                req_in = con['req_in']
                cat_out = con['cat_out']
                description = '\n{ds} {inputs} to {cat_out}.' \
                    .format(ds=ds, inputs=req_in, cat_out=cat_out, now=now)
                b.description = b.description + description
                b.save()
                #b = StagingBatch(name=name, description=description)
                #b.save()
                for st in states:
                    for yr in years:
                        # instantiate, but do not save/add to batch til end
                        stg_q = StagingQueue(category=cat_out)
                        
                        reqs = []
                        for reqd in req_in:
                            attr = cat_to_attr[reqd]
                            
                            b.log("reqd looking for {st} {yr} {cat}".format(st=st, yr=yr, cat=reqd),
                                        level='DEBUG')
                                
                            reqd_qs = StagingTable.objects \
                                .filter(category=reqd, wip=False) \
                                .order_by('-created_at')
                        
                            b.log("reqd_qs is {qs}".format(qs=reqd_qs),
                                        level='DEBUG')
                            
                            if st.lower() == 'tx':
                                reqd_lst = filter(
                                    lambda x: st.lower() + '_' + str(yr) in x.name and
                                    x.data_source.parent is not None and
                                    x.data_source.parent.abbreviation == ds,
                                    reqd_qs
                                )
                            else:
                                reqd_lst = filter(
                                    lambda x: x.state==st and
                                    x.year==yr and
                                    x.data_source.parent is not None and
                                    x.data_source.parent.abbreviation == ds,
                                    reqd_qs
                                )
                            
                            if len(reqd_lst) > 0:
                                #print "reqd found some matching {attr}".format(attr=attr)
                                i = reqd_lst[0]
                                try:
                                    if getattr(stg_q, attr) != None:
                                        # unable to add a second time if already not None
                                        # should emit a logger error about this
                                        #print "{stg_q}.{attr} value is not None ({val})" \
                                            #.format(stg_q=stg_q, attr=attr, val=getattr(stg_q, attr))
                                        reqs.append(False)
                                    else:
                                        b.log("{stg_q}.{attr} value is None and didn't freak out" \
                                            .format(stg_q=stg_q, attr=attr),
                                            level='DEBUG')
                                        setattr(stg_q, attr, i)
                                        b.log("{stg_q}.{attr} set to {i}" \
                                            .format(stg_q=stg_q, attr=attr, i=i),
                                            level='DEBUG')
                                        reqs.append(reqd)
                                except ObjectDoesNotExist:
                                    if reqd == req_in[0]:
                                        stg_q.stg_input = i
                                        
                                    else:
                                        b.log("Setting {stg}.{attr} to {i}".format(stg=stg_q, attr=attr, i=i),
                                            level='DEBUG')
                                        setattr(stg_q, attr, i)
                                    reqs.append(reqd)
                            else:
                                reqs.append(False)
                        
                        opts = []
                        if 'opt_in' in con:
                            opt_in = con['opt_in']
                            for opt in opt_in:
                                attr = cat_to_attr[opt]
                                
                                b.log("opt looking for {st} {yr} {cat}".format(st=st, yr=yr, cat=opt),
                                    level='DEBUG')
                                
                                opt_qs = StagingTable.objects \
                                    .filter(category=opt, wip=False) \
                                    .order_by('-created_at')
                                
                                opt_lst = filter(
                                    lambda x: x.state==st and
                                    x.year==yr and
                                    x.data_source.parent is not None and
                                    x.data_source.parent.abbreviation == ds,
                                    opt_qs)
                                
                                if len(opt_lst) > 0:
                                    b.log("opt found some matching {attr}".format(attr=attr),
                                        level='DEBUG')
                                    i = opt_lst[0]
                                    if getattr(stg_q, attr) == None:
                                        setattr(stg_q, attr, i)
                                        opts.append(opt)
                                    else:
                                        # unable to add a second time if already not None
                                        # should emit a logger error about this
                                        opts.append(False)
                                else:
                                    opts.append(False)
                        
                        b.log("reqs is {reqs}".format(reqs=reqs),
                            level='DEBUG')
                        if any(x==False for x in reqs):
                            b.log("One or more required components of this conversion ({ds} {state} {year} {cat}) are unavailable." \
                                .format(ds=ds, state=st, year=yr, cat=cat_out), level='DEBUG')
                        
                        else:
                            # check for completed StagingQueue built matching cat_out and state-year already
                            # I know this variable name implies this should be querying StagingTable objects.
                            # It should not.
                            # Ideally it would and then do some reverse lookup stuff on related StagingQueue objects,
                            # but everytime I try to do that I eff it up. So this is what we have.
                            st_tbl_qs = StagingQueue.objects \
                                .filter(category=cat_out, complete__isnull=False,
                                        stg_output__isnull=False, void=False)
                            
                            # NB reqs and opts are already based on what is available to build a
                            # StagingTable at this time. Therefore, they can be safely joined with
                            # operator.and_ rather than operator.or_ (ie "is there anything out
                            # there that matches ALL of the available required and available
                            # optional inputs?")
                            # TODO: totally should move this shit to some kind of function or
                            # StagingTable method. It's gross to have it out here and not at all
                            # DRY when something similar is needed to deprecate tables down the
                            # line.
                            reqd_predicates = [('%s__isnull' % CAT_IN_TO_ATTR[x], False) for x in reqs if x is not False]
                            opt_predicates = [('%s__isnull' % CAT_IN_TO_ATTR[x], False) for x in opts if x is not False]
                            equiv_q_lst = [Q(x) for x in reqd_predicates + opt_predicates]
                            equivalent_qs = st_tbl_qs.filter(reduce(operator.and_, equiv_q_lst))
                            
                            equivalent_lst = filter(lambda x: x.stg_input.state==st and x.stg_input.year==yr, equivalent_qs)
                            equivalent_ct = len(equivalent_lst)
                            
                            # while we're here, make sure it isn't in the queryset for this batch as well
                            inb_st_tbl_qs = StagingQueue.objects \
                                .filter(category=cat_out, batch=b)
                            
                            # prepare a Q object dynamically, based on whether each possible input is used
                            # e.g., if aha_input is used, will build a Q required that aha_input__isnull=False
                            reqd_predicates = [('%s__isnull' % CAT_IN_TO_ATTR[x], False) for x in reqs if x is not False]
                            opt_predicates = [('%s__isnull' % CAT_IN_TO_ATTR[x], False) for x in opts if x is not False]
                            inb_q_lst = [Q(x) for x in reqd_predicates + opt_predicates]
                            inb_qs = inb_st_tbl_qs.filter(reduce(operator.and_, inb_q_lst))
                            
                            inb_lst = filter(lambda x: x.stg_input.state==st and x.stg_input.year==yr, inb_qs)
                            inb_ct = len(inb_lst)
                            
                            if equivalent_ct == 0 and inb_ct == 0:
                                msg = "There are no StagingTable or StagingQueue objects for {state} {year} {category} with an equivalent constellation of inputs compared to those now available."
                                b.log(msg.format(state=st, year=yr, category=cat_out))
                                stg_q.batch = b
                                stg_q.save()
                                b.log("Saved StagingQueue {pk} for {state} {year} {category}." \
                                    .format(pk=stg_q.pk, state=st, year=yr, category=cat_out))
                            
                            elif inb_ct > 0:
                                msg = "There are no StagingTable objects for {state} {year} {category} with the constellation of inputs now available, but one is in the batch already."
                                b.log(msg.format(state=st, year=yr, category=cat_out))
                            
                            elif equivalent_ct > 0:
                                msg = "There are already one or more StagingTable objects for {state} {year} {category} with the constellation of inputs now available."
                                b.log(msg.format(state=st, year=yr, category=cat_out))
                                #print reqs
                                #print opts
                                #print equiv_q_lst
                                #print equivalent_qs
                                #print equivalent_qs.query
                                #print equivalent_lst
                                # if replacing, delete old ones?
                                # OR!
                                # Set up a model to hold deprecation queues. Would have attributes like
                                # st_q, superceded_by, a timestamp of when that happened/was noticed,
                                # and a boolean for whether the old one has been dropped.
                                # that could be pruned manually on a periodic basis, or whatevs.
                                # would probably need to review dependencies/parent-child tbl relations
                                # RESULT: This is done during the execution of the batch, not during
                                # the contemplation and enqueuing phase.
                                
        else:
            default_logger.info("Found no StagingTable objects with traceable heredity to parent data source with abbreviation {ds}. Therefore, the entire data source family was skipped.".format(ds=ds))
    
    set_length = len(b.stagingqueue_set.all())
    
    if set_length == 0:
        b.log('Found no out-of-date conversions for StagingBatch {pk}. The batch will be marked as void.' \
            .format(pk=b.pk))
        b.void = True
        b.save()
    else:
        b.log('Created StagingBatch {pk} with {length} files'.format(pk=b.pk, length=set_length))
    
    return b


def unimported_batch():
    """
    Creates an ImportBatch object for discovered files that have not
    yet been imported to StagingTable objects.
    """
    now = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")

    name = 'Non-imported {now}' \
        .format(now=now)

    description = 'Non-imported files as of {now}' \
        .format(now=now)

    b = ImportBatch(name=name, description=description)
    b.save()

    fqs = File.objects.filter(
        Q(file_type__content_type='CONTENTWH') | Q(file_type__content_type='CONTENTNH',loadfile__isnull=False)
        ).exclude(state__abbreviation='TX') # these are special

    fqs = fqs.order_by('state__abbreviation', 'year', '-file_type__compression')

    # add each if one matching state-year is not already in there
    for f in fqs:
        # look for other matches that cover this already
        st = f.state
        yr = f.year
        ds = f.file_type.source
        
        # either in the database
        st_tbl_qs = StagingTable.objects.filter(
            imported_via__file__state=st,
            imported_via__file__year=yr,
            imported_via__file__file_type__source=ds
        )
        
        # or in the queue set itself
        q_qs = File.objects.filter(
            state=st,
            year=yr,
            file_type__source=ds,
            importqueue__batch=b
        )
        
        if len(st_tbl_qs) == 0 and len(q_qs) == 0:
            b.importqueue_set.create(file=f)
    
    return b
