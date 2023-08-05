from upstart.system import UpstartSystem, DirectUpstartBus
from upstart.job import UpstartJob

from aj.api import *
from aj.plugins.services.api import ServiceManager, Service


@component(ServiceManager)
class UpstartServiceManager (ServiceManager):
    id = 'upstart'
    name = 'Upstart'

    @classmethod
    def __verify__(cls):
        try:
            UpstartSystem()
            return True
        except:
            try:
                UpstartSystem(bus=DirectUpstartBus())
                return True
            except:
                return False

    def __init__(self, context):
        self.bus = None
        try:
            self.upstart = UpstartSystem()
        except:
            self.bus = DirectUpstartBus()
            self.upstart = UpstartSystem(bus=self.bus)

    def __fix_name(self, name):
        return name.replace('_2d', '-').replace('_2e', '.')

    def list(self):
        for job_name in self.upstart.get_all_jobs():
            yield self.get(job_name)

    def get(self, id):
        job = UpstartJob(id, bus=self.bus)
        service = Service(self)
        service.id = id
        service.name = self.__fix_name(id)
        try:
            service.state = job.get_status()['state']
            service.running = service.state == 'running'
        except:
            service.running = False
        return service

    def start(self, id):
        UpstartJob(id).start()

    def stop(self, id):
        UpstartJob(id).stop()

    def restart(self, id):
        UpstartJob(id).restart()
