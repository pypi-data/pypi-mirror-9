"""
A set of stateless functions that can be used to complete various steps of an
OAuth handshake or to identify a MediaWiki user.
:Example:
    .. code-block:: python

        from mwoauth import ConsumerToken, initiate, complete, identify
        from six.moves import input # For compatibility between python 2 and 3

        # Consruct a "consumer" from the key/secret provided by MediaWiki
        import config
        consumer_token = ConsumerToken(config.consumer_key, config.consumer_secret)
        mw_uri = "https://en.wikipedia.org/w/index.php"

        # Step 1: Initialize -- ask MediaWiki for a temporary key/secret for user
        redirect, request_token = initiate(mw_uri, consumer_token)

        # Step 2: Authorize -- send user to MediaWiki to confirm authorization
        print("Point your browser to: %s" % redirect) #
        response_qs = input("Response query string: ")

        # Step 3: Complete -- obtain authorized key/secret for "resource owner"
        access_token = complete(mw_uri, consumer_token, request_token, response_qs)
        print(str(access_token))

        # Step 4: Identify -- (optional) get identifying information about the user
        identity = identify(mw_uri, consumer_token, access_token)
        print("Identified as {username}.".format(**identity))
"""
import re
import time

import requests

import jwt
from six import b, text_type, PY3
from six.moves.urllib.parse import urlencode, urlparse, parse_qs
from requests_oauthlib import OAuth1
from .tokens import RequestToken, AccessToken


def force_unicode(val):
    if type(val) == text_type:
        return val
    else:
        if PY3:
            return str(val, "unicode-escape")
        else:
            return unicode(val, "unicode-escape")


def initiate(mw_uri, consumer_token):
    """
    Initiates an oauth handshake with MediaWik.

    :Parameters:
        mw_uri : `str`
            The base URI of the MediaWiki installation.  Note that the URI
            should end in ``"index.php"``.
        consumer_token : :class:`~mwoauth.ConsumerToken`
            A token representing you, the consumer.  Provided by MediaWiki via
            ``Special:OAuthConsumerRegistration``.

    :Returns:
        A `tuple` of two values:

        * a MediaWiki URL to direct the user to
        * a :class:`~mwoauth.RequestToken` representing a request for access


    """
    auth = OAuth1(consumer_token.key,
                  client_secret=consumer_token.secret,
                  callback_uri='oob')

    r = requests.post(url=mw_uri,
                      params={'title': "Special:OAuth/initiate"},
                      auth=auth)

    credentials = parse_qs(r.content)

    if credentials is None or credentials == {}:
        raise Exception("Expected x-www-form-urlencoded response from " +
                        "MediaWiki, but got something else: " +
                        "{0}".format(repr(r.content)))

    elif b('oauth_token') not in credentials or \
         b('oauth_token_secret') not in credentials:

        raise Exception("MediaWiki response lacks token information: "
                        "{0}".format(repr(credentials)))

    else:

        request_token = RequestToken(
            credentials.get(b('oauth_token'))[0],
            credentials.get(b('oauth_token_secret'))[0]
        )

    return (
        mw_uri + "?" + urlencode({'title': "Special:OAuth/authorize",
                                  'oauth_token': request_token.key,
                                  'oauth_consumer_key': consumer_token.key}),
        request_token
    )


def complete(mw_uri, consumer_token, request_token, response_qs):
    """
    Completes an OAuth handshake with MediaWiki by exchanging an

    :Parameters:
        mw_uri : `str`
            The base URI of the MediaWiki installation.  Note that the URI
            should end in ``"index.php"``.
        consumer_token : :class:`~mwoauth.ConsumerToken`
            A key/secret pair representing you, the consumer.
        request_token : :class:`~mwoauth.RequestToken`
            A temporary token representing the user.  Returned by
            `initiate()`.
        response_qs : `bytes`
            The query string of the URL that MediaWiki forwards the user back
            after authorization.

    :Returns:
        An `AccessToken` containing an authorized key/secret pair that
        can be stored and used by you.
    """

    callback_data = parse_qs(b(response_qs))

    if callback_data is None or callback_data == {}:
        raise Exception("Expected URL query string containing, but got " +
                        "something else instead: {0}".format(str(response_qs)))

    elif b('oauth_token') not in callback_data or \
         b('oauth_verifier') not in callback_data:

        raise Exception("Query string lacks token information: "
                        "{0}".format(repr(callback_data)))

    else:
        # Check if the query string references the right temp resource owner key
        request_token_key = callback_data.get(b("oauth_token"))[0]
        # Get the verifier token
        verifier = callback_data.get(b("oauth_verifier"))[0]

    if not request_token.key == request_token_key:
        raise Exception("Unexpect request token key " +
                        "{0}, expected {1}.".format(request_token_key,
                                                    request_token.key))

    # Construct a new auth with the verifier
    auth = OAuth1(consumer_token.key,
                  client_secret=consumer_token.secret,
                  resource_owner_key=request_token.key,
                  resource_owner_secret=request_token.secret,
                  verifier=verifier)

    # Send the verifier and ask for an authorized resource owner key/secret
    r = requests.post(url=mw_uri,
                      params={'title': "Special:OAuth/token"},
                      auth=auth)

    # Parse response and construct an authorized resource owner
    credentials = parse_qs(r.content)

    if credentials is None:
        raise Exception("Expected x-www-form-urlencoded response, " +
                        "but got some else instead: {0}".format(r.content))

    access_token = AccessToken(
        credentials.get(b('oauth_token'))[0],
        credentials.get(b('oauth_token_secret'))[0]
    )

    return access_token


def identify(mw_uri, consumer_token, access_token, leeway=10.0):
    """
    Gather's identifying information about a user via an authorized token.

    :Parameters:
        mw_uri : `str`
            The base URI of the MediaWiki installation.  Note that the URI
            should end in ``"index.php"``.
        consumer_token : :class:`~mwoauth.ConsumerToken`
            A token representing you, the consumer.
        access_token : :class:`~mwoauth.AccessToken`
            A token representing an authorized user.  Obtained from `complete()`
        leeway : `int` | `float`
            The number of seconds of leeway to account for when examining a
            tokens "issued at" timestamp.

    :Returns:
        A dictionary containing identity information.
    """

    # Construct an OAuth auth
    auth = OAuth1(consumer_token.key,
                  client_secret=consumer_token.secret,
                  resource_owner_key=access_token.key,
                  resource_owner_secret=access_token.secret)

    # Request the identity using auth
    r = requests.post(url=mw_uri,
                      params={'title': "Special:OAuth/identify"},
                      auth=auth)

    # Decode json & stuff
    try:
        identity, signing_input, header, signature = jwt.load(r.content)
    except jwt.DecodeError as e:
        raise Exception("An error occurred while trying to read json " +
                        "content: {0}".format(e))

    # Ensure no downgrade in authentication
    if not header['alg'] == "HS256":
        raise Exception("Unexpected algorithm used for authentication " +
                        "{0}, expected {1}".format("HS256", header['alg']))

    # Check signature
    try:
        jwt.verify_signature(identity, signing_input, header, signature,
                             consumer_token.secret, False)
    except jwt.DecodeError as e:
        raise Exception("Could not verify the jwt signature: {0}".format(e))

    # Verify the issuer is who we expect (server sends $wgCanonicalServer)
    issuer = urlparse(identity['iss']).netloc
    expected_domain = urlparse(mw_uri).netloc
    if not issuer == expected_domain:
        raise Exception("Unexpected issuer " +
                        "{0}, expected {1}".format(issuer, expected_domain))

    # Verify we are the intended audience of this response
    audience = identity['aud']
    if not audience == consumer_token.key:
        raise Exception("Unexpected audience " +
                        "{0}, expected {1}".format(audience, expected_domain))

    now = time.time()

    # Check that the identity was issued in the past.
    issued_at = float(identity['iat'])
    if not now >= (issued_at - leeway):
        raise Exception("Identity issued {0} ".format(issued_at - now) +
                        "seconds in the future!")

    # Check that the identity has not yet expired
    expiration = float(identity['exp'])
    if not now <= expiration:
        raise Exception("Identity expired {0} ".format(expiration - now) +
                        "seconds ago!")

    # Verify that the nonce matches our request one,
    # to avoid a replay attack
    authorization_header = force_unicode(r.request.headers['Authorization'])
    request_nonce = re.search(r'oauth_nonce="(.*?)"',
                              authorization_header).group(1)
    if identity['nonce'] != request_nonce:
        raise Exception('Replay attack detected: {0} != {1}'.format(
            identity['nonce'], request_nonce))

    return identity
