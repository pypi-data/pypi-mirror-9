from ec2 import EC2
from openstack_ec2 import OpenStackEC2
from base import PermanentCloudException, AbstractCloud

def get_driver(cloud_name, logger, maxwait):
    driver_cls = AbstractCloud
    driver_clses = [driver_cls for driver_cls in [EC2, OpenStackEC2, AbstractCloud] if \
                        getattr(driver_cls, 'cloud', None) == cloud_name]
    if not driver_clses:
        raise PermanentCloudException('no driver for cloud name: %s' % cloud_name)
    driver_cls = driver_clses[0]
    driver = driver_cls(logger, maxwait)
    return driver

__all__ = ['get_driver']
