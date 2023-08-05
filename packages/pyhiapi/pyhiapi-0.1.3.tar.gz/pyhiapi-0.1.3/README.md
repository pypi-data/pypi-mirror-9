# pyhiapi
A very simple API endpoint, easily deployable for testing purposes

## Installation

    sudo pip install pyhiapi

## Usage

    hiapi [-b <bind address>] [-p <port>]
    
    -b, --bind-address: The interface you want to listen on
    -p, --port: The port you want to listen on

hiapi defaults to `localhost:4000`.

## Testing

You can just curl the service, perhaps like this:

    $ curl -i http://localhost:4000/

    HTTP/1.0 200 OK
    Content-Type: text/html; charset=utf-8
    Content-Length: 4
    Server: Werkzeug/0.9.6 Python/2.7.8
    Date: Fri, 23 Jan 2015 03:38:14 GMT

    Hi!

