import boto
import logging
import traceback
import socket
import time

from boto.ec2.blockdevicemapping import BlockDeviceType
from boto.ec2.blockdevicemapping import BlockDeviceMapping

from base import *
from contextlib import contextmanager

class EC2(AbstractCloud):
    """
    AWS EC2 driver
    """
    cloud = 'ec2'
    mandatory_fields = ['region', 'itype']

    def __init__(self, logger, maxwait=300):
        AbstractCloud.__init__(self, logger, maxwait)
        logging.getLogger('boto').setLevel(logging.CRITICAL)

    def set_default_params(self, params, cloud_access_config):
        try:
            if not 'bmap' in params:
                params['bmap'] = [{'name': '/dev/sda1', 'size': '15', 'delete_on_termination': True}]
            if not 'userdata' in params:
                params['userdata'] = None
            params['credentials'] = {'ec2_access_key': cloud_access_config[self.cloud]['ec2_access_key'],
                                     'ec2_secret_key': cloud_access_config[self.cloud]['ec2_secret_key']}

            params['ssh'] = {'keypair': cloud_access_config[self.cloud]['ssh'][params['region']][0],
                             'keyfile': cloud_access_config[self.cloud]['ssh'][params['region']][1]}
        except Exception, err:
            raise PermanentCloudException('Error while setting up required cloud params: %s' % err)


    def get_connection(self, params):
        '''get cloud connection'''
        try:
            return self._get_connection(params)
        except boto.exception.EC2ResponseError, err:
            # Boto errors should be handled according to their error Message - there are some well-known ones
            self.logger.debug('got boto error during instance creation: %s' % err)
            if str(err).find('<Code>InvalidParameterValue</Code>') != -1:
                # InvalidParameterValue is really bad
                raise PermanentCloudException('got error connecting to ec2: %s' % err)
            else:
                raise
        except socket.error, err:
            # Unexpected error happened
            raise TemporaryCloudException('Socket error connecting to EC2: ' + traceback.format_exc())

    @contextmanager
    def connection(self, params):
        connection = self.get_connection(params)
        try:
            yield connection
        finally:
            connection.close()

    def get_image(self, params):
        '''get cloud image'''
        try:
            with self.connection(params) as connection:
                image = connection.get_image(params['ami'])
            return image
        except boto.exception.EC2ResponseError, err:
            # Boto errors should be handled according to their error Message - there are some well-known ones
            self.logger.debug('got boto error during instance creation: %s' % err)
            if str(err).find('<Code>InvalidAMIID.NotFound</Code>') != -1:
                # No such AMI in the region
                raise PermanentCloudException('AMI %s not found in %s' % (params['ami'], params['region']))
            else:
                raise

    def create(self, params):
        try:
            ssh_key_name = params['ssh']['keypair']

            bmap = self._get_bmap(params)
            image = self.get_image(params)

            reservation = image.run(
                instance_type=params['cloudhwname'],
                key_name=ssh_key_name,
                block_device_map=bmap,
                subnet_id=params.get('subnet_id'),
                user_data=params.get('userdata')
            )
            myinstance = reservation.instances[0]
            count = 0
            # Sometimes EC2 failes to return something meaningful without small timeout between run_instances() and update()
            time.sleep(10)
            while myinstance.update() == 'pending' and count < self.maxwait / 5:
                # Waiting out instance to appear
                self.logger.debug('waiting for %s %s %s', params['region'], params['ami'], params['cloudhwname'])
                time.sleep(5)
                count += 1
            instance_state = myinstance.update()
            if instance_state == 'running':
                # Instance appeared - scheduling 'setup' stage
                myinstance.add_tag('Name', "%s-validation" % params['ami'])
                result = myinstance.__dict__
                self.logger.info('EC2: Created instance %s %s %s %s %s', params['region'], params['ami'],
                                    params['cloudhwname'], result['id'], result['public_dns_name'])
                # packing creation results into params
                params['id'] = result['id']
                params['instance'] = result.copy()
                if result['public_dns_name'] != '':
                    params['hostname'] = result['public_dns_name']
                else:
                    params['hostname'] = result['private_ip_address']
                return params
            elif instance_state == 'pending':
                # maxwait seconds is enough to create an instance. If not -- EC2 failed.
                result = myinstance.__dict__
                if 'id' in result.keys():
                    # terminate stucked instance
                    params['id'] = result['id']
                    params['instance'] = result.copy()
                    self.terminate(params)
                raise UnknownCloudException('Error during instance creation: timeout in pending state')
            else:
                # error occured
                raise UnknownCloudException('Error during instance creation: ' + instance_state)

        except boto.exception.EC2ResponseError, err:
            # Boto errors should be handled according to their error Message - there are some well-known ones
            self.logger.debug('got boto error during instance creation: %s' % err)
            if str(err).find('<Code>InstanceLimitExceeded</Code>') != -1:
                # InstanceLimit is temporary problem
                raise TemporaryCloudException('got InstanceLimitExceeded - not increasing ntry')
            elif str(err).find('<Code>AuthFailure</Code>') != -1:
                # Not authorized is permanent
                raise PermanentCloudException('not authorized for AMI %s in %s' % (params['ami'], params['region']))
            elif str(err).find('<Code>Unsupported</Code>') != -1:
                # Unsupported hardware in the region
                raise SkipCloudException('got Unsupported - most likely the permanent error: %s' % err)
            elif str(err).find('<Code>InvalidSubnetID.NotFound</Code>') != -1:
                # Invalid subnet-id --- skip the instantiation
                raise SkipCloudException('got InvalidSubnetID - skipping: %s, %s, %s (%s)' % (params['ami'],
                                            params['region'], params['itype'], err))
            else:
                raise

    def get_instance(self, params):
        with self.connection(params) as connection:
            try:
                instance = connection.get_only_instances([params['id']])[0]
            except IndexError:
                raise PermanentCloudException('no instances found for %s' % params['id'])
        return instance

    def update(self, params):
        myinstance = self.get_instance(params)
        result = myinstance.__dict__.copy()
        params['instance'] = result
        params['hostname'] = result['public_dns_name'] or result['private_ip_address']

    def terminate(self, params):
        instance = self.get_instance(params)
        instance.terminate()

    def get_console_output(self, params):
        instance = self.get_instance(params)
        return instance.get_console_output().output

    def _get_connection(self, params):
        ec2_access_key, ec2_secret_key = params['credentials']['ec2_access_key'], params['credentials']['ec2_secret_key']
        endpoint = params.get('region_endpoint', None)
        reg = boto.ec2.get_region(params['region'], aws_access_key_id=ec2_access_key, aws_secret_access_key=ec2_secret_key, endpoint=endpoint)
        connection = reg.connect(aws_access_key_id=ec2_access_key, aws_secret_access_key=ec2_secret_key)
        return connection

    def _get_bmap(self, params):
        bmap = BlockDeviceMapping()
        for device in params['bmap']:
            if not 'name' in device.keys():
                self.logger.debug('bad device ' + str(device))
                continue
            dev = BlockDeviceType()
            if 'size' in device.keys():
                dev.size = device['size']
            if 'delete_on_termination' in device.keys():
                dev.delete_on_termination = device['delete_on_termination']
            if 'ephemeral_name' in device.keys():
                dev.ephemeral_name = device['ephemeral_name']
            bmap[device['name']] = dev
        return bmap
