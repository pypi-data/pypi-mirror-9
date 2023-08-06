ReconnectingWebSocket
=====================

A small JavaScript library that decorates the WebSocket API to provide
a WebSocket connection that will automatically reconnect if the
connection is dropped.

It is API compatible, so when you have:

    ws = new WebSocket('ws://....');

you can replace with:

    ws = new ReconnectingWebSocket('ws://....');

### Forked Features

[Exponential backoff](http://dthain.blogspot.com/2009/02/exponential-backoff-in-distributed.html) with sensible defaults.

