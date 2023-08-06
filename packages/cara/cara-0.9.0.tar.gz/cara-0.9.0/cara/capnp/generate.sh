#!/bin/bash
CAPNPC_CARA=$(which capnp-cara || echo ../../gen/capnpc-cara)
CAPNP_LOC=${1:-/usr/local/include/capnp/}
capnp compile -o $CAPNPC_CARA ${CAPNP_LOC}*.capnp --src-prefix=${CAPNP_LOC}
