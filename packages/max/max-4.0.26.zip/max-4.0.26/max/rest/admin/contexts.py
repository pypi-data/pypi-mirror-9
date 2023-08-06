# -*- coding: utf-8 -*-
from max import DEFAULT_CONTEXT_PERMISSIONS_PERMANENCY
from max.MADMax import MADMaxCollection
from max.MADMax import MADMaxDB
from max.decorators import MaxResponse
from max.decorators import requirePersonActor
from max.exceptions import InvalidPermission
from max.exceptions import ObjectNotFound
from max.exceptions import Unauthorized
from max.exceptions import ValidationError
from max.models import Context
from max.oauth2 import oauth2
from max.rest.ResourceHandlers import JSONResourceEntity
from max.rest.ResourceHandlers import JSONResourceRoot
from max.rest.utils import extractPostData
from max.rest.utils import searchParams

from pyramid.httpexceptions import HTTPNoContent
from pyramid.view import view_config


@view_config(route_name='contexts', request_method='GET', restricted='Manager')
@MaxResponse
@oauth2(['widgetcli'])
def getContexts(context, request):
    """
    """
    mmdb = MADMaxDB(context.db)
    found_contexts = mmdb.contexts.search({}, flatten=1, **searchParams(request))
    handler = JSONResourceRoot(found_contexts)
    return handler.buildResponse()


@view_config(route_name='context', request_method='DELETE', restricted='Manager')
@MaxResponse
@oauth2(['widgetcli'])
def DeleteContext(context, request):
    """
    """
    mmdb = MADMaxDB(context.db)
    chash = request.matchdict.get('hash', None)
    found_contexts = mmdb.contexts.getItemsByhash(chash)

    if not found_contexts:
        raise ObjectNotFound("There's no context matching this url hash: %s" % chash)

    ctx = found_contexts[0]
    ctx.removeUserSubscriptions()
    ctx.removeActivities(logical=True)
    ctx.delete()
    return HTTPNoContent()


@view_config(route_name='context', request_method='GET', restricted='Manager')
@MaxResponse
@oauth2(['widgetcli'])
def getContext(context, request):
    """
        /contexts/{hash}

        [RESTRICTED] Return a context by its hash.
    """
    mmdb = MADMaxDB(context.db)
    chash = request.matchdict.get('hash', None)
    found_context = mmdb.contexts.getItemsByhash(chash)

    if not found_context:
        raise ObjectNotFound("There's no context matching this url hash: %s" % chash)

    handler = JSONResourceEntity(found_context[0].getInfo())
    return handler.buildResponse()


@view_config(route_name='contexts', request_method='POST', restricted='Manager')
@MaxResponse
@oauth2(['widgetcli'])
def addContext(context, request):
    """
        /contexts

        Adds a context.
    """
    request.actor = None

    # Initialize a Context object from the request
    newcontext = Context()
    newcontext.fromRequest(request)

    # If we have the _id setted, then the object already existed in the DB,
    # otherwise, proceed to insert it into the DB
    # In both cases, respond with the JSON of the object and the appropiate
    # HTTP Status Code

    if newcontext.get('_id'):
        # Already Exists
        code = 200
    else:
        # New context
        code = 201
        contextid = newcontext.insert()
        newcontext['_id'] = contextid

    handler = JSONResourceEntity(newcontext.flatten(), status_code=code)
    return handler.buildResponse()


@view_config(route_name='context', request_method='PUT', restricted='Manager')
@MaxResponse
@requirePersonActor(force_own=False, exists=True)
@oauth2(['widgetcli'])
def ModifyContext(context, request):
    """
        /contexts/{hash}

        Modify the given context.
    """
    chash = request.matchdict['hash']
    contexts = MADMaxCollection(context.db.contexts)
    maxcontext = contexts.getItemsByhash(chash)
    if maxcontext:
        maxcontext = maxcontext[0]
    else:
        raise ObjectNotFound('Unknown context: %s' % chash)

    properties = maxcontext.getMutablePropertiesFromRequest(request)
    maxcontext.modifyContext(properties)
    maxcontext.updateUsersSubscriptions()
    maxcontext.updateContextActivities()
    handler = JSONResourceEntity(maxcontext.flatten())
    return handler.buildResponse()


@view_config(route_name='context_user_permission', request_method='PUT', restricted='Manager')
@MaxResponse
@oauth2(['widgetcli'])
@requirePersonActor(force_own=False)
def grantPermissionOnContext(context, request):
    """ [RESTRICTED]
    """
    permission = request.matchdict.get('permission', None)
    if permission not in ['read', 'write', 'subscribe', 'invite', 'delete', 'flag']:
        raise InvalidPermission("There's not any permission named '%s'" % permission)

    chash = request.matchdict.get('hash', None)
    subscription = None
    pointer = 0
    while subscription is None and pointer < len(request.actor.subscribedTo):
        if request.actor.subscribedTo[pointer]['hash'] == chash:
            subscription = request.actor.subscribedTo[pointer]
        pointer += 1

    if not subscription:
        raise Unauthorized("You can't set permissions on a context where the user is not subscribed")

    # If we reach here, we are subscribed to a context and ready to set the permission

    if permission in subscription.get('_grants', []):
        # Already have the permission grant
        code = 200
    else:
        # Assign the permission
        code = 201
        subscription = request.actor.grantPermission(
            subscription,
            permission,
            permanent=request.params.get('permanent', DEFAULT_CONTEXT_PERMISSIONS_PERMANENCY))

    handler = JSONResourceEntity(subscription, status_code=code)
    return handler.buildResponse()


@view_config(route_name='context_user_permission', request_method='DELETE', restricted='Manager')
@MaxResponse
@oauth2(['widgetcli'])
@requirePersonActor(force_own=False)
def revokePermissionOnContext(context, request):
    """ [RESTRICTED]
    """
    permission = request.matchdict.get('permission', None)
    if permission not in ['read', 'write', 'subscribe', 'invite', 'flag']:
        raise InvalidPermission("There's not any permission named '%s'" % permission)

    chash = request.matchdict.get('hash', None)
    subscription = None
    pointer = 0
    while subscription is None and pointer < len(request.actor.subscribedTo):
        if request.actor.subscribedTo[pointer]['hash'] == chash:
            subscription = request.actor.subscribedTo[pointer]
        pointer += 1

    if not subscription:
        raise Unauthorized("You can't remove permissions on a context where you are not subscribed")

    # If we reach here, we are subscribed to a context and ready to remove the permission

    code = 200
    if permission in subscription.get('_vetos', []):
        code = 200
        # Alredy vetted
    else:
        # We have the permission, let's delete it
        subscription = request.actor.revokePermission(
            subscription,
            permission,
            permanent=request.params.get('permanent', DEFAULT_CONTEXT_PERMISSIONS_PERMANENCY))
        code = 201
    handler = JSONResourceEntity(subscription, status_code=code)
    return handler.buildResponse()


@view_config(route_name='context_user_permissions_defaults', request_method='POST', restricted='Manager')
@MaxResponse
@oauth2(['widgetcli'])
@requirePersonActor(force_own=False)
def resetPermissionsOnContext(context, request):
    """ [RESTRICTED]
    """
    chash = request.matchdict.get('hash', None)
    subscription = None
    pointer = 0
    while subscription is None and pointer < len(request.actor.subscribedTo):
        if request.actor.subscribedTo[pointer]['hash'] == chash:
            subscription = request.actor.subscribedTo[pointer]
        pointer += 1

    if not subscription:
        raise Unauthorized("You can't set permissions on a context where the user is not subscribed")

    # If we reach here, we are subscribed to a context and ready to reset the permissions

    contexts = MADMaxCollection(context.db.contexts)
    maxcontext = contexts.getItemsByhash(chash)[0]
    subscription = request.actor.reset_permissions(subscription, maxcontext)
    handler = JSONResourceEntity(subscription, status_code=200)
    return handler.buildResponse()


@view_config(route_name='context_subscriptions', request_method='GET', restricted='Manager')
@MaxResponse
@oauth2(['widgetcli'])
def getContextSubscriptions(context, request):
    """
    """
    chash = request.matchdict['hash']
    mmdb = MADMaxDB(context.db)
    found_users = mmdb.users.search({"subscribedTo.hash": chash}, flatten=1, show_fields=["username", "subscribedTo"], **searchParams(request))

    for user in found_users:
        subscription = user['subscribedTo'][0]
        del user['subscribedTo']
        user['permissions'] = subscription.pop('permissions')
        user['vetos'] = subscription.pop('vetos', [])
        user['grants'] = subscription.pop('grants', [])

    handler = JSONResourceRoot(found_users)
    return handler.buildResponse()


@view_config(route_name='context_tags', request_method='GET', restricted='Manager')
@MaxResponse
@oauth2(['widgetcli'])
def getContextTags(context, request):
    """
    """
    chash = request.matchdict['hash']
    contexts = MADMaxCollection(context.db.contexts, query_key='hash')
    context = contexts[chash]
    handler = JSONResourceRoot(context.tags)
    return handler.buildResponse()


@view_config(route_name='context_tags', request_method='DELETE', restricted='Manager')
@MaxResponse
@oauth2(['widgetcli'])
def clearContextTags(context, request):
    """
    """
    chash = request.matchdict['hash']
    contexts = MADMaxCollection(context.db.contexts, query_key='hash')
    context = contexts[chash]
    context.tags = []
    context.save()
    context.updateContextActivities(force_update=True)
    context.updateUsersSubscriptions(force_update=True)
    handler = JSONResourceRoot([])
    return handler.buildResponse()


@view_config(route_name='context_tags', request_method='PUT', restricted='Manager')
@MaxResponse
@oauth2(['widgetcli'])
def updateContextTags(context, request):
    """
    """
    chash = request.matchdict['hash']
    tags = extractPostData(request)

    # Validate tags is a list of strings
    valid_tags = isinstance(tags, list)
    if valid_tags:
        valid_tags = False not in [isinstance(tag, (str, unicode)) for tag in tags]
    if not valid_tags:
        raise ValidationError("Sorry, We're expecting a list of strings...")

    contexts = MADMaxCollection(context.db.contexts, query_key='hash')
    context = contexts[chash]
    context.tags.extend(tags)
    context.tags = list(set(context.tags))
    context.save()
    context.updateContextActivities(force_update=True)
    context.updateUsersSubscriptions(force_update=True)
    handler = JSONResourceRoot(context.tags)
    return handler.buildResponse()


@view_config(route_name='context_tag', request_method='DELETE', restricted='Manager')
@MaxResponse
@oauth2(['widgetcli'])
def removeContextTag(context, request):
    """
    """
    chash = request.matchdict['hash']
    tag = request.matchdict['tag']
    contexts = MADMaxCollection(context.db.contexts, query_key='hash')
    context = contexts[chash]

    try:
        context.tags.remove(tag)
    except ValueError:
        raise ObjectNotFound('This context has no tag "{}"'.format(tag))

    context.save()
    context.updateContextActivities(force_update=True)
    context.updateUsersSubscriptions(force_update=True)
    return HTTPNoContent()


@view_config(route_name='context_push_tokens', request_method='GET', restricted='Manager')
@MaxResponse
@oauth2(['widgetcli'])
def getPushTokensForContext(context, request):
    """
         /contexts/{hash}/tokens
         Return all relevant tokens for a given context
    """

    cid = request.matchdict['hash']
    contexts = MADMaxCollection(context.db.contexts, query_key='hash')
    ctxt = contexts[cid]

    users = ctxt.subscribedUsers()

    result = []
    for user in users:
        for idevice in user.get('iosDevices', []):
            result.append(dict(token=idevice, platform='iOS', username=user.get('username')))
        for adevice in user.get('androidDevices', []):
            result.append(dict(token=adevice, platform='android', username=user.get('username')))

    handler = JSONResourceRoot(result)
    return handler.buildResponse()
