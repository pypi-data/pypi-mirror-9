channelstream
=============

This is **experimental code** based on gevent-websocket.

Basic usage::

    YOUR_PYTHON_ENV/bin/channelstream - filename.ini


You can also see simple pyramid/angularjs demo included, open your browser and point it to following url::

    http://127.0.0.1:8000/demo

**To run the demo you will need to have the `requests` package installed in your environment**

Possible config options for the server::

    YOUR_PYTHON_ENV/bin/channelstream -h


The server can also be configured via ini files, example::

    [channelstream]
    debug = 0
    port = 8000
    demo_app_url = http://127.0.0.1
    secret = YOURSECRET
    admin_secret = YOURADMINSECRET
    allow_posting_from = 127.0.0.1,
                         x.x.x.x,
                         y.y.y.y,



** USAGE **

Refer to channelstream/wsgi_views/demo.py for example usage.

** Security model **

To send information client interacts only with your normal www application.
Your app handled authentication and processing messages from client, then passed
them as signed message to channelstream server for broadcast.

socketio client -> webapp -> REST call to socket server -> broadcast to other client

This model is easy to implement, secure, easy to scale and allows all kind of
languages/apps/work queues to interact with socket server.

All messages need to be signed with a HMAC of destination endpoint ::

    import requests
    from itsdangerous import TimestampSigner
    signer = TimestampSigner(request.registry.settings['secret'])
    sig_for_server = signer.sign('/connect')
    secret_headers = {'x-channelstream-secret': sig_for_server,
                      'x-channelstream-endpoint': endpoint,
                      'Content-Type': 'application/json'}
    response = requests.post(url, data=json.dumps(payload),
                             headers=secret_headers).json()

The function accepts endpoint in form of '/messages' if you want to send a message
 to users. This will be validated on socketio server side.



Data format and endpoints
=========================

/connect?secret=YOURSECRET
--------------------------

expects a json request in form of::

    { "user": YOUR_username,
      "conn_id": CUSTOM_UNIQUE_UID_OF_CONNECTION, # for example uuid.uuid4()
    "channels": [ "CHAN_NAME1", "CHAN_NAMEX" ]
    }
   
where channels is a list of channels this connection/user should be subscribed to.

/info?secret=YOURSECRET
--------------------------

expects a json request in form of::

    { 
    "channels": [ "CHAN_NAME1", "CHAN_NAMEX" ]
    }
   
where channels is a list of channels you want information about.
If channel list is empty server will return full list of all channels and their
information.

/disconnect
--------------------------

expects a json request in form of::

    { "conn_id": CONN_ID}

marks specific connection to be garbage collected

/message?secret=YOURSECRET
--------------------------

expects a json request in form of::

    {
    "channel": "CHAN_NAME", #optional
    "pm_users": [username1,username2], #optional
    "user": "NAME_OF_POSTER",
    "message": MSG_PAYLOAD
    }

When just channel is present message is public to all connections subscribed 
to the channel. When channel & pm_users is a private message is sent 
to connections subscribed to this specific channel. 
If only pm_users is present a private message is sent to all connections that are
owned by pm_users.  

/subscribe?secret=YOURSECRET
----------------------------

expects a json request in form of::

    { "channels": [ "CHAN_NAME1", "CHAN_NAMEX" ], "conn_id": "CONNECTION_ID"}


/user_status?secret=YOURSECRET
----------------------------

expects a json request in form of::

    { "user": username, "status":STATUS_ID_INT}


Responses to js client
----------------------

Responses to client are in form of **list** containing **objects**:

examples:

**new message** ::

    {
    "date": "2011-09-15T11:36:18.471862",
    "message": MSG_PAYLOAD,
    "type": "message",
    "user": "NAME_OF_POSTER",
    "channel": "CHAN_NAME"
    }

**presence info** ::

    {
    "date": "2011-09-15T11:43:47.434905",
    "message": null,
    "type": "join",
    "user": "NAME_OF_POSTER",
    "channel": "CHAN_NAME"
    }


Installation and Setup
======================

Obtain source from github and do::

    python setup.py develop
