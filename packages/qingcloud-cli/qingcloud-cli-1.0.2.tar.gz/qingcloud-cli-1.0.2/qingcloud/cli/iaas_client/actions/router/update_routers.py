# coding: utf-8

from qingcloud.cli.misc.utils import explode_array
from qingcloud.cli.iaas_client.actions.base import BaseAction

class UpdateRoutersAction(BaseAction):

    action = 'UpdateRouters'
    command = 'update-routers'
    usage = '%(prog)s -r "router_id, ..." [-f <conf_file>]'

    @classmethod
    def add_ext_arguments(cls, parser):
        parser.add_argument('-r', '--routers', dest='routers',
                action='store', type=str, default='',
                help='the comma separated IDs of routers you want to update.')

    @classmethod
    def build_directive(cls, options):
        routers = explode_array(options.routers)
        if not routers:
            return None

        return {
                'routers': routers,
                }
