# -*- coding: utf-8 -*-
from max import AUTHORS_SEARCH_MAX_QUERIES_LIMIT
from max import LAST_AUTHORS_LIMIT
from max.MADMax import MADMaxDB
from max.decorators import MaxResponse
from max.decorators import requirePersonActor
from max.exceptions import ObjectNotFound
from max.exceptions import Unauthorized
from max.oauth2 import oauth2
from max.rest.ResourceHandlers import JSONResourceEntity
from max.rest.ResourceHandlers import JSONResourceRoot
from max.rest.utils import downloadTwitterUserImage
from max.rest.utils import flatten
from max.rest.utils import searchParams
from max.rest.sorting import sorted_query

from pyramid.httpexceptions import HTTPNotImplemented
from pyramid.response import Response
from pyramid.view import view_config

import os
import time


@view_config(route_name='public_contexts', request_method='GET')
@MaxResponse
@oauth2(['widgetcli'])
@requirePersonActor(force_own=False)
def getPublicContexts(context, request):
    """
        /contexts/public

        Return a list of public-subscribable contexts
    """
    mmdb = MADMaxDB(context.db)
    found_contexts = mmdb.contexts.search({'permissions.subscribe': 'public'}, **searchParams(request))

    handler = JSONResourceRoot(flatten(found_contexts, squash=['owner', 'creator', 'published']))
    return handler.buildResponse()


@view_config(route_name='context_activities_authors', request_method='GET')
@MaxResponse
@oauth2(['widgetcli'])
@requirePersonActor(force_own=False)
def getContextAuthors(context, request):
    """
        /contexts/{hash}/activities/authors
    """
    chash = request.matchdict['hash']
    mmdb = MADMaxDB(context.db)
    actor = request.actor
    author_limit = int(request.params.get('limit', LAST_AUTHORS_LIMIT))

    is_subscribed = chash in [subscription['hash'] for subscription in actor.subscribedTo]
    if not is_subscribed:
        raise Unauthorized("You're not allowed to access this context")

    query = {}
    query['contexts.hash'] = chash
    query['verb'] = 'post'
    # Include only visible activity, this includes activity with visible=True
    # and activity WITHOUT the visible field
    query['visible'] = {'$ne': False}

    still_has_activities = True

    # Save full author object to construct de response
    # and a separate username field to make the uniquefication easier
    distinct_authors = []
    distinct_usernames = []

    activities = []
    before = None
    queries = 0

    while len(distinct_usernames) < author_limit and still_has_activities and queries <= AUTHORS_SEARCH_MAX_QUERIES_LIMIT:
        if not activities:
            extra = {'before': before} if before else {}
            activities = sorted_query(request, mmdb.activity, query, **extra)
            queries += 1
            still_has_activities = len(activities) > 0
        if still_has_activities:
            activity = activities.pop(0)
            before = activity._id
            if activity.actor['username'] not in distinct_usernames:
                distinct_authors.append(activity.actor)
                distinct_usernames.append(activity.actor['username'])
    handler = JSONResourceRoot(distinct_authors)
    return handler.buildResponse()


@view_config(route_name='context', request_method='GET')
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

    handler = JSONResourceEntity(found_context[0].flatten())
    return handler.buildResponse()


@view_config(route_name='context_avatar', request_method='GET')
@MaxResponse
def getContextAvatar(context, request):
    """
        /contexts/{hash}/avatar

        Return the context's avatar. To the date, this is only implemented to
        work integrated with Twitter.
    """
    chash = request.matchdict['hash']
    AVATAR_FOLDER = request.registry.settings.get('avatar_folder')
    context_image_filename = '%s/%s.png' % (AVATAR_FOLDER, chash)

    if not os.path.exists(context_image_filename):
        mmdb = MADMaxDB(context.db)
        found_context = mmdb.contexts.getItemsByhash(chash)
        if len(found_context) > 0:
            twitter_username = found_context[0]['twitterUsername']
            downloadTwitterUserImage(twitter_username, context_image_filename)
        else:
            raise ObjectNotFound("There's no context with hash %s" % chash)

    if os.path.exists(context_image_filename):
        # Calculate time since last download and set if we have to redownload or not
        modification_time = os.path.getmtime(context_image_filename)
        hours_since_last_modification = (time.time() - modification_time) / 60 / 60
        if hours_since_last_modification > 3:
            mmdb = MADMaxDB(context.db)
            found_context = mmdb.contexts.getItemsByhash(chash)
            twitter_username = found_context[0]['twitterUsername']
            downloadTwitterUserImage(twitter_username, context_image_filename)
    else:
        context_image_filename = '%s/missing.png' % (AVATAR_FOLDER)

    data = open(context_image_filename).read()
    image = Response(data, status_int=200)
    image.content_type = 'image/png'
    return image


@view_config(route_name='context', request_method='DELETE')
@MaxResponse
@oauth2(['widgetcli'])
def DeleteContext(context, request):
    """
    """
    return HTTPNotImplemented  # pragma: no cover
