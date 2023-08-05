IBM MQ Light Python module
==========================

MQ Light is designed to allow applications to exchange discrete pieces of
information in the form of messages. This might sound a lot like TCP/IP
networking, and MQ Light does use TCP/IP under the covers, but MQ Light takes
away much of the complexity and provides a higher level set of abstractions to
build your applications with.

This python module provides the high-level API by which you can interact
with the MQ Light runtime.

See https://developer.ibm.com/messaging/mq-light/ for more details.
Getting Started
---------------

Usage
^^^^^

.. code:: python

    import mqlight


Then create some instances of the client object to send and receive messages:

.. code:: python

    recv_client = mqlight.Client('amqp://localhost')

    topic_pattern = 'public'
    def subscribe(err):
        recv_client.subscribe(topic_pattern)
    def messages(data, delivery, options):
        print 'Recv: ', data
    recv_client.add_listener(mqlight.STARTED, subscribe)
    recv_client.add_listener(mqlight.MESSAGE, message)

    send_client = mqlight.Client('amqp://localhost')

    topic = 'public'
    def send(err):
        def sent(err, data):
            send_client.stop()
        send_client.send(topic, 'Hello World!', sent)
    send_client.add_listener(mqlight.STARTED, send)


API
---
mqlight.Client(``service``, [``client_id``], [``security_options``], [``callback``])
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Creates an MQ Light client instance in ``starting`` state

* `service` - (str, list, function) a string containing
     the URL for the service to connect to, or alternatively a list
     containing a list of URLs to attempt to connect to in turn, or
     alternatively an async function which will be expected to supply the
     service URL(s) to a callback function that will be passed to it whenever
     it is called (in the form ``function(err, service)``). User names and
     passwords may be embedded into the URL (e.g. ``amqp://user:pass@host``).
* `client_id` - (str, default: ``AUTO_[0-9a-f]{7}``) a unique identifier for
     this client. A maximum of one instance of the client (as identified by the
     value of this property) can be connected the an MQ Light server at a given
     point in time. If another instance of the same client connects, then the
     previously connected instance will be disconnected. This is reported, to
     the first client, as a ``ReplacedError`` being emitted as an error event
     and the client transitioning into ``stopped`` state. If the id property is
     not a valid client identifier (e.g. it contains a colon, it is too long,
     or it contains some other forbidden character) then the function will
     throw an ``InvalidArgumentError``
* ``security_options`` - (dict) options for the client. Properties include:

  *  **``property_user``**, (str) (optional), user name for authentication.
     Alternatively, the user name may be embedded in the URL passed via the
     service property. If you choose to specify a user name via this property
     and also embed a user name in the URL passed via the surface argument then
     all the user names must match otherwise an ``InvalidArgumentError`` will be
     thrown.  User names and passwords must be specified together (or not at
     all). If you specify just the user property but no password property an
     ``InvalidArgumentError`` will be thrown.
  *  **``property_password``**, (str) (optional), password for authentication.
     Alternatively, user name may be embedded in the URL passed via the service
     property.
  *  **``ssl_trust_certificate``**, (str) (optional), SSL trust certificate to
     use when authentication is required for the MQ Light server. Only used when
     service specifies the amqps scheme.
  *  **``ssl_verify_name``**, (bool, default: True) (optional), whether or not
     to additionally check the MQ Light server's common name in the certificate
     matches the actual server's DNS name. Only used when the
     ssl_trust_certificate option is specified.
* ``callback`` - (function) (optional) callback that is invoked (indicating
  success) if the client attains ``started`` state, or invoked (indicating
  failure) if the client enters ``stopped`` state before attaining ``started``
  state. The callback function is supplied two arguments, the first being an
  ``Error`` object that is set to ``None`` to indicate success.  The second
  is the instance of ``client``, returned by ``mqlight.Client``, that the
  callback relates to.

Returns a ``Client`` object representing the client instance.

mqlight.Client.start([`callback`])
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Prepares the client to send and/or receive messages from the server. As clients
are created in ``starting`` state, this method need only be called if an
instance of the client has been stopped using the ``mqlight.Client.stop``
method.

* ``callback`` - (function) (optional) callback to be notified when the client
  has either: transitioned into ``started`` state; or has entered ``stopped``
  state before it can transition into ``started`` state. The callback function
  will be invoked with a ``StoppedError`` as its argument if the client
  transitions into stopped state before it attains ``started state`` - which can
  happen as a result of calling the ``client.stop`` method.
mqlight.Client.stop([callback])
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Stops the client from sending and/or receiving messages from the server. The
client will automatically unsubscribe from all of the destinations that it is
subscribed to. Any system resources used by the client will be freed.

* ``callback`` - (function) (optional) callback to be notified when the client
  has transitioned into ``stopped`` state.
mqlight.Client.send(``topic``, ``data``, [``options``], [``callback``])
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Sends the value, specified via the ``data`` argument to the specified topic.
str and lst values will be sent and received as-is.

* ``topic`` - (str) the topic to which the message will be sent.
  A topic can contain any character in the Unicode character set.
* ``data`` - (str, lst) the message body to be sent
* ``options`` - (dict) (optional) additional options for the send operation.
  Supported options are:

  *  **qos**, (int) (optional) The quality of service to use when sending the
     message. 0 is used to denote at most once (the default) and 1 is used for
     at least once. If a value which is not 0 and not 1 is specified then this
     method will throw a ``RangeError``
  *  **ttl**, (int) (optional) A time to live value for the message in
     seconds. MQ Light will endeavour to discard, without delivering, any
     copy of the message that has not been delivered within its time to live
     period. The default time to live is 604800 seconds (7 days).
     The value supplied for this argument must be greater than zero and finite,
     otherwise a ``RangeError`` will be thrown when this method is called.
* ``callback`` - (function) The callback argument is optional if the qos
  property of the options argument is omitted or set to 0 (at most once). If
  the qos property is set to 1 (at least once) then the callback argument is
  required and a ``InvalidArgumentError`` is thrown if it is omitted. The
  callback will be notified when the send operation completes and is passed the
  following arguments:

  *  **error**, (Error) an error object if the callback is being invoked to
     indicate that the send call failed. If the send call completes successfully
     then the value ``None`` is supplied for this argument.
  *  **topic**, (str) the ``topic`` argument supplied to the corresponding
     send method call.
  *  **data**, (dict) the ``data`` argument supplied to the corresponding
     send method call.
  *  **options**, (dict) the ``options`` argument supplied to the corresponding
     send method call.

Returns ``True`` if this message was sent, or is the next to be sent.

Returns ``False`` if the message was queued in user memory, due to either a
backlog of messages, or because the client was not in a connected state.
When the backlog of messages is cleared, the ``drain`` event will be emitted.
mqlight.Client.subscribe(``topic_pattern``, [``share``], [``options``], [``callback``])
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Subscribes the client to a destination, based on the supplied ``topic_pattern``
and ``share`` arguments. The client throw a ``SubscribedError`` if a call is
made to ``client.subscribe(...)`` and the client is already associated with the
destination (as determined by the pattern and share arguments). It will throw
a ``StoppedError`` if the client has not been started prior to calling this
function.

The ``topic_pattern`` argument is matched against the ``topic`` that messages
are sent to, allowing the messaging service to determine whether a particular
message will be delivered to a particular destination, and hence the
subscribing client.

* ``topic_pattern`` - (str) used to match against the ``topic`` specified when a
  message is sent to the messaging service. A pattern can contain any character
  in the Unicode character set, with ``#`` representing a multilevel wildcard
  and ``+`` a single level wildcard as described
  `here
  <https://developer.ibm.com/messaging/mq-light/wildcard-topicpatterns/>`_).
  .
* ``share`` - (str) (optional) name for creating or joining a shared
  destination for which messages are anycast between connected subscribers. If
  omitted defaults to a private destination (e.g. messages can only be received
  by a specific instance of the client).
* ``options`` - (dict) (optional) additional options for the subscribe
  operation. Supported options are:

  * **auto_confirm**, (bool) (optional) When set to True (the default) the
    client will automatically confirm delivery of messages when all of the
    listeners registered for the client's ``message`` event have returned.
    When set to ``False``, application code is responsible for confirming the
    delivery of messages using the ``confirm_delivery`` method, passed via
    the ``delivery`` argument of the listener registered for ``message``
    events. ``auto_confirm`` is only applicable when the ``qos`` property is
    set to 1.  The ``qos`` property is described later.
  * **credit**, (int) The maximum number of unconfirmed messages a client
    can have before the server will stop sending new messages to the client
    and require that it confirms some of the outstanding message deliveries in
    order to receive more messages.  The default for this property is 1024. If
    specified the value will be coerced to a ``int`` and must be finite
    and >= 0, otherwise a ``RangeError`` will be thrown.
  * **qos**, (int) The quality of service to use for delivering messages to
    the subscription.  Valid values are: 0 to denote at most once (the
    default), and 1 for at least once. A ``RangeError`` will be thrown for
    other value.
  * **ttl**, (int) A time-to-live value, in seconds, that is applied
    to the destination that the client is subscribed to. If specified the
    value will be coerced to a ``int``, which must be finite and >= 0,
    otherwise a ``RangeError`` will be thrown. This value will replace any
    previous value, if the destination already exists. Time to live starts
    counting down when there are no instances of a client subscribed to a
    destination.  It is reset each time a new instance of the client
    subscribes to the destination. If time to live counts down to zero then MQ
    Light will delete the destination by discarding any messages held at the
    destination and not accruing any new messages. The default value for this
    property is 0 - which means the destination will be deleted as soon as
    there are no clients subscribed to it.
* ``callback`` - (function) (optional) callback to be notified when the
  subscribe operation completes. The ``callback`` function is passed the
  following arguments:

  * **error**, (Error) an error object if the callback is being invoked to
    indicate that the subscribe call failed. If the subscribe call completes
    successfully then the value ``None`` is supplied for this argument.
  * **topic_pattern**, (str) the ``topic_pattern`` argument supplied to the
    corresponding subscribe method call.
  * **share**, (str) the ``share`` argument supplied to the corresponding
    subscribe method call (or ``None`` if this parameter was not specified).

Returns the ``Client`` object that the subscribe was called on. ``message``
events will be emitted when messages arrive.
mqlight.Client.unsubscribe(``topicPattern``, ``[share]``, ``[options]``, ``[callback]``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Stops the flow of messages from a destination to this client. The client's
message callback will not longer be driven when messages arrive, that match the
pattern associated with the destination. Messages may still be stored at the
destination if it has a non-zero time to live value or is shared and is
subscribed to by other clients instances. If the client is not subscribed to a
subscription, as identified by the pattern (and optional) share arguments then
this method will throw a ``UnsubscribedError``.  The pattern and share arguments
will be coerced to type ``str``.  The pattern argument must be present
otherwise this method will throw a ``TypeError``.

* ``topic_pattern`` - (str) Matched against the ``topic_pattern`` specified on
  the ``mqlight.Client.subscribe`` call to determine which destination the
  client will unsubscribed from.
* ``share`` - (str) (optional) Matched against the ``share`` specified on the
  ``mqlight.Client.subscribe`` call to determine which destination the client
  will unsubscribed from.
* ``options`` - (dict) (optional) Properties that determine the behaviour of the
  unsubscribe operation:

  *  **ttl**, (int) (optional) Sets the destination's time to live as part of
     the unsubscribe operation. The default (when this property is not
     specified) is not to change the destination's time to live. When specified
     the only valid value for this property is 0.
* ``callback`` - (function) (optional) callback to be notified when the
  unsubscribe operation completes. The ``callback`` function is passed the
  following arguments:

  *  **error**, (Error) an error object if the callback is being invoked to
     indicate that the unsubscribe call failed. If the unsubscribe call
     completes successfully then the value ``None`` is supplied for this
     argument.
  *  **topic_pattern**, (str) the ``topic_pattern`` argument supplied to the
     corresponding unsubscribe method call.
  *  **share**, (str) the ``share`` argument supplied to the corresponding
     unsubscribe method call (or ``None`` if this parameter was not
     specified).
mqlight.Client.get_id()
^^^^^^^^^^^^^^^^^^^^^^^

Returns the identifier associated with the client. This will either be what
was passed in on the ``Client()`` call or an auto-generated id.

mqlight.Client.get_service()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Returns the URL of the server to which the client is currently connected
to, or ``None`` if not connected.

mqlight.Client.get_state()
^^^^^^^^^^^^^^^^^^^^^^^^^^

Returns the current state of the client, which will be one of:
'starting', 'started', 'stopping', 'stopped', or 'retrying'.
Event: 'message'
^^^^^^^^^^^^^^^^

Emitted when a message is delivered from a destination matching one of the
client's subscriptions.

- ``data`` - (str, lst) the message body.
- ``delivery`` - (dict) additional information about why the event was emitted.
  Properties include:

  -  **message**, (dict) additional information about the message. Properties
     include:

    -  **topic**, (str, function) the topic that the message was sent to.
    -  **confirm_delivery**, (function) A method that can be used to confirm
       (settle) the delivery of a at least once quality of service (qos:1)
       message. This method does not expect any arguments. This property will
       only be present if the message was delivered due to a subscribe call
       that specified both ``qos: 1`` and ``auto_confirm: False`` options.
    -  **ttl**, (int) the remaining time to live period for this message in
       seconds. This is calculated by subtracting the time the message
       spends at an MQ Light destination from the time to live value specified
       when the message is sent to MQ Light.

  -  **destination**, (dict) collects together the values that the client
       specified when it subscribed to the destination from which the message
       was received.

    -  **topic_pattern**, (str) the topic specified when the client
        subscribed to the destination from which the message was received.
    -  **share**, (str) the share name specified when the client subscribed
       to the destination from which the message was received. This property
       will not be present if the client subscribed to a private destination.

Event: 'started'
^^^^^^^^^^^^^^^^

This event is emitted when a client attains ``started`` state by successfully
establishing a connection to the MQ Light server. The client is ready to send
messages. The client is also ready to receive messages by subscribing to topic
patterns.

Event: 'stopped'
^^^^^^^^^^^^^^^^

This event is emitted when a client attains ``stopped`` state as a result of the
``mqlight.Client.stop`` method being invoked. In this state the client will not
receive messages, and attempting to send messages or subscribe to topic patterns
will result in an error being thrown from the respective method call.

Event: 'error'
^^^^^^^^^^^^^^

Emitted when an error is detected that prevents or interrupts a client's
connection to the messaging server. The client will automatically try to
reestablish connectivity unless either successful or the client is stopped by a
call to the ``mqlight.Client.stop`` method. ``error`` events will periodically
be emitted for each unsuccessful attempt the client makes to reestablish
connectivity to the MQ Light server.

* ``error`` (Error) the error.

Event: 'restarted'
^^^^^^^^^^^^^^^^^^

This event is emitted when the client has reestablished connectivity to the MQ
Light server. The client will automatically re-subscribe to any destinations
that it was subscribed to prior to losing connectivity. Any send or subscribe
requests made while the client was not connected to the MQ Light server will
also be automatically forwarded when connectivity is reestablished.

Event: 'drain'
^^^^^^^^^^^^^^

Emitted to indicate that the client has flushed any buffered messages to the
network. This event can be used in conjunction with the value returned by the
``mqlight.Client.send`` method to efficiently send messages without buffering a
large number of messages in memory allocated by the client.
Errors
------

Error: InvalidArgumentError
^^^^^^^^^^^^^^^^^^^^^^^^^^^

This is a subtype of ``Error`` defined by the MQ Light client. It is considered
a programming error. The underlying cause for this error are the parameter
values passed into a method. Typically ``InvalidArgumentError`` is thrown
directly from a method where ``TypeError`` and ``RangeError`` do not adequately
describe the problem (e.g., you specified a client id that contains a colon).
``InvalidArgumentError`` may also arrive asynchronously if, for example, the
server rejects a value supplied by the client (e.g. a message time to live
value which exceeds the maximum value that the server will permit).

Error: NetworkError
^^^^^^^^^^^^^^^^^^^

This is a subtype of ``Error`` defined by the MQ Light client. It is considered
an operational error. ``NetworkError`` is passed to an application if the
client cannot establish a network connection to the MQ Light server, or if an
established connection is broken.

Error: RangeError
^^^^^^^^^^^^^^^^^

This is a subtype of ``Error`` defined by the MQ Light client. It is considered
a programming error. The MQ Light client throws ``RangeError`` from a method
when a numeric value falls outside the range accepted by the client.

Error: ReplacedError
^^^^^^^^^^^^^^^^^^^^

This is a subtype of ``Error`` defined by the MQ Light client. It is considered
an operational error. ``ReplacedError`` is thrown to signify that an instance
of the client has been replaced by another instance that connected specifying
the exact same client id. Applications should react to ``ReplacedError`` by
ending as any other course of action is likely to cause two (or more) instances
of the application to loop replacing each other.

Error: SecurityError
^^^^^^^^^^^^^^^^^^^^

This is a subtype of ``Error`` defined by the MQ Light client. It is considered
an operational error. ``SecurityError`` is thrown when an operation fails due
to a security related problem. Examples include:

* The client specifies an incorrect user/password combination.
* The client specifies a user / password but the server is not configured to
  require a user / password.
* The client is configured to use an SSL / TLS certificate to establish the
  identity of the server - but cannot.
* etc.

Error: StoppedError
^^^^^^^^^^^^^^^^^^^

This is a subtype of ``Error`` defined by the MQ Light client. It is considered
a programming error - but is unusual in that, in some circumstances, a client
may reasonably expect to receive ``StoppedError`` as a result of its actions
and would typically not be altered to avoid this condition occurring.
``StoppedError`` is thrown by methods which require connectivity to the server
(e.g. send, subscribe) when they are invoked while the client is in stopping or
stopped states. ``StoppedError`` is also supplied to the callbacks and supplied
to methods which require connectivity to the server, when the client
transitions into stopped state before it can perform the action. It is this
latter case where applications may reasonably be written to expect
``StoppedError``.

Error: SubscribedError
^^^^^^^^^^^^^^^^^^^^^^

This is a subtype of ``Error`` defined by the MQ Light client. It is considered
a programming error. ``SubscribedError`` is thrown from the
``client.subscribe(...)`` method call when a request is made to subscribe to a
destination that the client is already subscribed to.

Error: TypeError
^^^^^^^^^^^^^^^^

This is a built-in subtype of ``Error``. It is considered a programming error.
The MQ Light client throws ``TypeError`` if the type of a method argument
cannot be coerced to the type expected by the client code. For example
specifying a numeric constant instead of a function. ``TypeError`` is also used
when a required parameter is omitted (the justification being that the argument
is assigned a value of undefined - which isn't the type that the client is
expecting).

Error: UnsubscribedError
^^^^^^^^^^^^^^^^^^^^^^^^

This is a subtype of ``Error`` defined by the MQ Light client. It is considered
a programming error. ``UnsubscribedError`` is thrown from the
``client.unsubscribe(...)`` method call when a request is made to unsubscribe
from a destination that the client is not subscribed to.
## Client state machine

Each instance of a client (as returned from `mqlight.createClient(...)` is
backed by the following state machine:

![Diagram of a state machine](state-machine.gif)

Each of the states shown in the state machine diagram corresponds to the values
stored i the `mqlight.Client.state` property, with the exception of `retrying1`
and `retrying2` which are collapsed into a single `retrying` value. While in the
`retrying` state the client will wait for up approximately 60 seconds (based on
an exponential backoff algorithm) before attempting to transition into a new
state.

Each line shown in the state machine diagram represents a possible way in which
the client can transition between states. The lines are labelled with
information about the transitions, which includes:
1. The function calls that can cause the transition to occur:
  * `start()` corresponds to the `mqlight.Client.start` function.
  * `stop()` corresponds to the `mqlight.Client.stop` function.
2. Change that occur at the network level, which can cause the transition to
   occur. For example:
  * `[broken]` occurs when an established network connection between the client
    and the server is interrupted.
  * `[connected]` occurs when the client successfully establishes a network
    connection to the server.
  * `[failed]` occurs when the client unsuccessfully attempts to establish a
    network connection to the server.
3. Events that are emitted. Specifically:
  * `<error>` indicates that an error event is emitted.
  * `<restarted>` indicates that a restarted event is emitted.
  * `<started>` indicates that a started event is emitted.
  * `<stopped>` indicates that a stopped event is emitted.
Samples
=======

To run the samples, navigate to the `mqlight/samples/` folder.

Usage:

Receiver Sample:
::
usage: recv.py [-h] [-s SERVICE] [-c TRUST_CERTIFICATE] [-t TOPIC_PATTERN]
[-i CLIENT_ID] [--destination-ttl DESTINATION_TTL]
[-n SHARE_NAME] [-f FILE] [-d DELAY] [--verbose VERBOSE]

Connect to an MQ Light server and subscribe to the specified topic.

optional arguments:
  -h, --help            show this help message and exit
  -s SERVICE, --service SERVICE
                        service to connect to, for example:
                        amqp://user:password@host:5672 or amqps://host:5671 to
                        use SSL/TLS (default: amqp://localhost)
  -c TRUST_CERTIFICATE, --trust-certificate TRUST_CERTIFICATE
                        use the certificate contained in FILE (in PEM or DER
                        format) to validate the identify of the server. The
                        connection must be secured with SSL/TLS (e.g. the
                        service URL must start with "amqps://")
  -t TOPIC_PATTERN, --topic-pattern TOPIC_PATTERN
                        subscribe to receive messages matching TOPIC_PATTERN
                        (default: public)
  -i CLIENT_ID, --id CLIENT_ID
                        the ID to use when connecting to MQ Light (default:
                        send_[0-9a-f]{7})
  --destination-ttl DESTINATION_TTL
                        set destination time-to-live to DESTINATION_TTL
                        seconds (default: None)
  -n SHARE_NAME, --share-name SHARE_NAME
                        optionally, subscribe to a shared destination using
                        SHARE_NAME as the share name.
  -f FILE, --file FILE  write the payload of the next message received to FILE
                        (overwriting previous file contents then end. (default
                        is to print messages to stdout)
  -d DELAY, --delay DELAY
                        delay for DELAY seconds each time a message is
                        received. (default: 0)
  --verbose VERBOSE     print additional information about each message.
                        (default: False)

Sender Sample:
::
usage: send.py [-h] [-s SERVICE] [-c TRUST_CERTIFICATE] [-t TOPIC]
[-i CLIENT_ID] [--message-ttl MESSAGE_TTL] [-d DELAY] [-r REPEAT]
[--sequence SEQUENCE] [-f FILE][MESSAGE [MESSAGE ...]]

Send a message to an MQ Light server.

positional arguments:
  MESSAGE               message to be sent (default: ['Hello world !'])

optional arguments:
  -h, --help            show this help message and exit
  -s SERVICE, --service SERVICE
                        service to connect to, for example:
                        amqp://user:password@host:5672 or amqps://host:5671 to
                        use SSL/TLS (default: amqp://localhost)
  -c TRUST_CERTIFICATE, --trust-certificate TRUST_CERTIFICATE
                        use the certificate contained in FILE (in PEM or DER
                        format) to validate the identify of the server. The
                        connection must be secured with SSL/TLS (e.g. the
                        service URL must start with "amqps://")
  -t TOPIC, --topic TOPIC
                        send messages to topic TOPIC (default: public)
  -i CLIENT_ID, --id CLIENT_ID
                        the ID to use when connecting to MQ Light (default:
                        send_[0-9a-f]{7})
  --message-ttl MESSAGE_TTL
                        set message time-to-live to MESSAGE_TTL seconds
                        (default: None)
  -d DELAY, --delay DELAY
                        add NUM seconds delay between each request (default:
                        0)
  -r REPEAT, --repeat REPEAT
                        send messages REPEAT times, if REPEAT <= 0 then repeat
                        forever (default: 1)
  --sequence SEQUENCE   prefix a sequence number to the message payload,
                        ignored for binary messages (default: False)
  -f FILE, --file FILE  send FILE as binary data. Cannot be specified at the
                        same time as MESSAGE
Feedback
--------

You can help shape the product we release by trying out the beta code and
leaving your `feedback
<https://developer.ibm.com/community/groups/service/html/communityview?communityUuid=00a6a6d0-9601-44cb-a2a2-b0b26811790a>`_).

Reporting bugs
^^^^^^^^^^^^^^

If you think you've found a bug, please leave us `feedback
<https://developer.ibm.com/community/groups/service/html/communityview?communityUuid=00a6a6d0-9601-44cb-a2a2-b0b26811790a>`).
To help us fix the bug a log might be helpful. You can get a log by setting the
environment variable ``MQLIGHT_PYTHON_LOG`` to ``debug`` and by collecting the
output that goes to stderr when you run your application.

Release notes
-------------

9.9.9999999999
^^^^^^^^^^^^^^

* Initial beta release.
