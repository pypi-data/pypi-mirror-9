# -*- coding: utf-8 -*-
from max.MADMax import MADMaxDB
from max.decorators import MaxResponse
from max.decorators import requirePersonActor
from max.exceptions import ObjectNotFound
from max.oauth2 import oauth2
from max.rest.ResourceHandlers import JSONResourceRoot
from max.rest.utils import searchParams

from pyramid.httpexceptions import HTTPNoContent
from pyramid.view import view_config


@view_config(route_name='comments', request_method='GET', restricted='Manager')
@MaxResponse
@oauth2(['widgetcli'])
@requirePersonActor(force_own=False, exists=False)
def getGlobalComments(context, request):
    """
    """
    mmdb = MADMaxDB(context.db)
    is_head = request.method == 'HEAD'
    activities = mmdb.activity.search({'verb': 'comment'}, flatten=1, count=is_head, **searchParams(request))
    handler = JSONResourceRoot(activities, stats=is_head)
    return handler.buildResponse()


@view_config(route_name='context_comments', request_method='GET', restricted='Manager')
@MaxResponse
@oauth2(['widgetcli'])
@requirePersonActor(force_own=False, exists=False)
def getContextComments(context, request):
    """
    """
    mmdb = MADMaxDB(context.db)
    is_head = request.method == 'HEAD'
    chash = request.matchdict['hash']

    query = {
        'verb': 'comment',
        'object.inReplyTo.contexts': {
            '$in': [chash]
        }
    }

    comments = mmdb.activity.search(query, flatten=1, count=is_head, **searchParams(request))
    handler = JSONResourceRoot(comments, stats=is_head)
    return handler.buildResponse()


@view_config(route_name='comments', request_method='DELETE', restricted='Manager')
@MaxResponse
@oauth2(['widgetcli'])
@requirePersonActor(force_own=False, exists=False)
def deleteActivity(context, request):
    """
    """
    mmdb = MADMaxDB(context.db)
    activityid = request.matchdict.get('activity', None)
    commentid = request.matchdict.get('comment', None)
    try:
        found_activity = mmdb.activity[activityid]
    except:
        raise ObjectNotFound("There's no activity with id: %s" % activityid)

    comment = found_activity.get_comment(commentid)
    if not comment:
        raise ObjectNotFound("There's no comment with id: %s" % commentid)

    found_activity.delete_comment(commentid)
    return HTTPNoContent()
