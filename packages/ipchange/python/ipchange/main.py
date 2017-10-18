# -*- mode: python; python-indent: 4 -*-
import ncs
import _ncs
from ncs.application import Service
from ncs.dp import Action

# ------------------------
# SERVICE CALLBACK EXAMPLE
# ------------------------
class ServiceCallbacks(Service):

    # The create() callback is invoked inside NCS FASTMAP and
    # must always exist.
    @Service.create
    def cb_create(self, tctx, root, service, proplist):
        self.log.info('Service create(service=', service._path, ')')

        vars = ncs.template.Variables()
        vars.add('DUMMY', '127.0.0.1')
        template = ncs.template.Template(service)
        template.apply('ipchange-template', vars)

class setoriginalip(Action):
    @Action.action
    def cb_action(self, uinfo, name, kp, input, output):
        #if the your actions take more than 240 seconds, increase the action_set_timeout
        _ncs.dp.action_set_timeout(uinfo,240)
        with ncs.maapi.single_write_trans(uinfo.username, uinfo.context) as trans:
            action = ncs.maagic.get_node(trans, kp)

            output.result = ''
            m = ncs.maapi.Maapi()
            try:
                service = ncs.maagic.get_node(trans, kp, shared=False)
                root = ncs.maagic.get_root(trans)
                print('running setoriginalip')
                device = root.ncs__devices.device[service.device]
                if device.ipchange__original_ipaddress:
                    device.address = device.ipchange__original_ipaddress
                    print('changed address back to ' + str(device.ipchange__original_ipaddress))
                    del(device.ipchange__original_ipaddress)
                    print('deleted ipchange__original_ipaddress')

                if device.ipchange__secondary_ipaddress:
                    print('secondary address: ' + device.ipchange__secondary_ipaddress)

                if service.use_secondary_ipaddress:
                    del(service.use_secondary_ipaddress)
                    print('deleted use_secondary_ipaddress')

                output.result += 'OK'

            except KeyError:
                output.result = "Error: wrong key in path (i.e no service found): " + str(service)
                return
            trans.apply()

            # if we run a specific command
            # if input.command:
            #     run_command(action, input.command, trans, output, self)
            # else:
            #     # If no command is specified we will run all the tests
            #     for cmd in action.commands:
            #         run_command(action, cmd.name, trans, output, self)
            # self.log.info('commiting action: ', name)
            # trans.apply()
            # self.log.info('commiting done action: ', name)

# ---------------------------------------------
# COMPONENT THREAD THAT WILL BE STARTED BY NCS.
# ---------------------------------------------
class Main(ncs.application.Application):
    def setup(self):
        # The application class sets up logging for us. It is accessible
        # through 'self.log' and is a ncs.log.Log instance.
        self.log.info('Main RUNNING')

        # Service callbacks require a registration for a 'service point',
        # as specified in the corresponding data model.
        #
        self.register_service('ipchange-servicepoint', ServiceCallbacks)
        self.register_action('setoriginalip', setoriginalip)

        # If we registered any callback(s) above, the Application class
        # took care of creating a daemon (related to the service/action point).

        # When this setup method is finished, all registrations are
        # considered done and the application is 'started'.

    def teardown(self):
        # When the application is finished (which would happen if NCS went
        # down, packages were reloaded or some error occurred) this teardown
        # method will be called.

        self.log.info('Main FINISHED')
