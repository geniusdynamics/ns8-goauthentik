#!/usr/bin/env python3

#
# Copyright (C) 2023 Nethesis S.r.l.
# SPDX-License-Identifier: GPL-3.0-or-later
#

import sys
import agent
import agent.tasks
import os


agent_id = agent.resolve_agent_id('traefik@node')
host = os.environ['TRAEFIK_HOST']
le = True if os.environ['TRAEFIK_LETS_ENCRYPT'] == "True" else False

if le:
    agent.tasks.run_nowait(
        agent_id=agent_id, # e.g. module/traefik1
        action='set-certificate',
        data={
            "fqdn":host,
            "sync": True,
        },
        parent='', # Run as a root task
        extra={
            'title': 'set-certificate',
            'isNotificationHidden': False,
        },
    )