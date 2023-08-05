# coding: utf-8

from qingcloud.cli.iaas_client.actions.base import BaseAction
from qingcloud.cli.misc.utils import explode_array

class DissociateEipsFromLoadBalancerAction(BaseAction):

    action = 'DissociateEipsFromLoadBalancer'
    command = 'dissociate-eips-from-loadbalancer'
    usage = '%(prog)s -l <loadbalancer> -e <eips> [-f <conf_file>]'
    description = 'Dissociate one or more eips from load balancer'

    @classmethod
    def add_ext_arguments(cls, parser):

        parser.add_argument('-l', '--loadbalancer', dest='loadbalancer',
                action='store', type=str, default='',
                help='ID of load balancer.')

        parser.add_argument('-e', '--eips', dest='eips',
                action='store', type=str, default='',
                help='the comma separated IDs of eips you want to dissociate.')

    @classmethod
    def build_directive(cls, options):
        required_params = {
                'loadbalancer': options.loadbalancer,
                'eips': options.eips,
                }
        for param in required_params:
            if required_params[param] is None or required_params[param] == '':
                print('error: [%s] should be specified' % param)
                return None

        return {
                'loadbalancer': options.loadbalancer,
                'eips': explode_array(options.eips)
                }
