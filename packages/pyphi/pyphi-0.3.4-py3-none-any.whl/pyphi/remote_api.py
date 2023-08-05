#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Remote API
~~~~~~~~~~

Exposes PyPhi functions to a JSON-RPC remote API.
"""

import logging
import numpy as np
from jsonrpc import dispatcher

from . import compute, json
from .network import Network
from .subsystem import Subsystem


# Create a logger for this module.
log = logging.getLogger(__name__)


@dispatcher.add_method
def big_mip(subsystem_indices, network):
    # TODO make dedicated methods for converting a JSON-network or subsystem
    # into the actual Python object
    tpm = network['tpm']
    current_state = network['currentState']
    past_state = network['pastState']
    cm = network['connectivityMatrix']
    network = Network(np.array(tpm), current_state, past_state,
                      connectivity_matrix=np.array(cm))
    subsystem = Subsystem(subsystem_indices, network)
    return json.make_encodable(compute.big_mip(subsystem))
