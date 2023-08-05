# Copyright (c) 2014 Cisco Systems
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
# @author: Ivar Lazzaro (ivar-lazzaro), Cisco Systems Inc.

import argparse
import logging as log

from apicapi import apic_client


def clean(args):
    apic_session = apic_client.RestClient(log, "", [args.apic_ip],
                                          args.apic_username,
                                          args.apic_password, args.ssl)
    apic_session.login()
    classes = ['infraNodeP', 'infraAccPortP', 'fvTenant',
               'physDomP', 'infraNodeP', 'infraLeafS',
               'infraNodeBlk', 'infraRsAccPortP', 'infraAccPortP',
               'infraHPortS', 'infraPortBlk',
               'infraAccPortGrp', 'infraRsAttEntP', 'infraAttEntityP',
               'infraRsDomP', 'infraRsVlanNs', 'infraAccBndlGrp',
               'infraRsAttEntP', 'infraRsLacpPol', 'lacpLagPol',
               'fvnsVlanInstP', 'fvnsEncapBlk', 'fvnsVxlanInstP',
               'bgpRRP', 'bgpRRNodePEp', 'bgpAsP', 'fabricFuncP']
    [apic_session.delete_class(x) for x in classes]


parser = argparse.ArgumentParser(description='Cleans APIC infra profiles')
parser.add_argument('apic_ip', help='APIC ip address')
parser.add_argument('apic_username', help='APIC username')
parser.add_argument('apic_password', help='APIC password')
parser.add_argument('--ssl', help='Wether to use SSL or not', default=False)


def main():
    args = parser.parse_args()
    clean(args)
