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

    $ curl -i http://<bind_address>:<port>/


