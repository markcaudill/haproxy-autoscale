"""Tests for python blocks within haproxy-autoscale mako templates."""

import logging
import os
import subprocess

import unittest
from tempfile import NamedTemporaryFile
import yaml

import haproxy_autoscale
from boto.ec2.connection import EC2Connection

BASE_DIR_STR = os.path.realpath(__file__)
INSTANCE_DATA_PATH=os.path.join(os.path.dirname(BASE_DIR_STR),
                                'data/running_instances_mock.yml')

class BotoEc2InstanceMock():
    """Mock boto.ec2.instance.Instance from yaml instance of HttpMock."""

    def __init__(self, mock_dict):
        for key in mock_dict.keys():
            setattr(self, key, mock_dict[key])


class templateTestCase(unittest.TestCase):

    def setUp(self):
        try:
            self.version = subprocess.check_output(['haproxy', '-vv'])
        except OSError as e:
            raise RuntimeError('No haproxy binary found in path')

        logging.NullHandler
        data_filehandle = open(INSTANCE_DATA_PATH)
        self.mock_data = yaml.safe_load(data_filehandle)
        mock_sg_one_str = self.mock_data.keys()[0]
        mock_instances_sg_one = []
        for instance_data in self.mock_data[mock_sg_one_str]:
            mock_instances_sg_one.append(BotoEc2InstanceMock(
                             self.mock_data[mock_sg_one_str][instance_data]))
        mock_instances = {mock_sg_one_str: mock_instances_sg_one}

        self.data_dir_str = os.path.join(os.path.dirname(BASE_DIR_STR), 'data')
                
        self.running_instances_mock = mock_instances


    def tearDown(self):
        #pass
        os.remove(self.test_conf_filepath)

    def test_simple_config(self):

        template = os.path.join(self.data_dir_str, 'simple_example.tpl')
        self.test_conf_filepath = NamedTemporaryFile(delete=True).name
        haproxy_conf_str = haproxy_autoscale.generate_haproxy_config(
                                        template=template,
                                        instances=self.running_instances_mock)
        haproxy_autoscale.file_contents(filename=self.test_conf_filepath,
                                        content=haproxy_conf_str)
        test_conf_output = check_conf(conf_filepath=self.test_conf_filepath)
        self.assertEqual(test_conf_output[0], True,
                     ("Configuration parsing failed:\n%s"
                      %test_conf_output[1]))


    @unittest.skip('stub')
    def test_find_required_tag(self):
        pass

    @unittest.skip('stub')
    def test_autobackend_config(self):
        template = os.path.join(self.data_dir_str,
                                            'autobackends_example.tpl')
        self.test_conf_filepath = NamedTemporaryFile(delete=True).name
        haproxy_conf_str = haproxy_autoscale.generate_haproxy_config(
                                        template=template,
                                        instances=self.running_instances_mock)
        haproxy_autoscale.file_contents(filename=self.test_conf_filepath,
                                        content=haproxy_conf_str)
        test_conf_output = check_conf(conf_filepath=self.test_conf_filepath)
        self.assertEqual(test_conf_output[0], True,
                     ("Configuration parsing failed:\n%s"
                      %test_conf_output[1]))

    def test_autobackend_one_prefix(self):
        template = os.path.join(self.data_dir_str,
                                            'autobackends_one_prefix_example.tpl')
        self.test_conf_filepath = NamedTemporaryFile(delete=True).name
        haproxy_conf_str = haproxy_autoscale.generate_haproxy_config(
                                        template=template,
                                        instances=self.running_instances_mock)
        haproxy_autoscale.file_contents(filename=self.test_conf_filepath,
                                        content=haproxy_conf_str)
        test_conf_output = check_conf(conf_filepath=self.test_conf_filepath)
        self.assertEqual(test_conf_output[0], True,
                     ("Configuration parsing failed:\n%s"
                      %test_conf_output[1]))

    def test_autobackend_three_prefixes(self):
        template = os.path.join(self.data_dir_str,
                                            'autobackends_three_prefixes_example.tpl')
        self.test_conf_filepath = NamedTemporaryFile(delete=True).name
        haproxy_conf_str = haproxy_autoscale.generate_haproxy_config(
                                        template=template,
                                        instances=self.running_instances_mock)
        haproxy_autoscale.file_contents(filename=self.test_conf_filepath,
                                        content=haproxy_conf_str)
        test_conf_output = check_conf(conf_filepath=self.test_conf_filepath)
        self.assertEqual(test_conf_output[0], True,
                     ("Configuration parsing failed:\n%s"
                      %test_conf_output[1]))

    @unittest.skip('stub')
    def test_skip_without_required_tag(self):
        pass


# TODO: merge tests to module haproxy-autoscale/tests branch and import here
def check_conf(conf_filepath):
    """Wrap haproxy -c -f.

    Args:
        conf_filepath: Str, path to an haproxy configuration file.
    Returns:
        valid_config: Bool, true if configuration passed parsing.
    """

    try:
        subprocess.check_output(['haproxy', '-c', '-f', conf_filepath],
                                stderr=subprocess.STDOUT)
        valid_config = True
        error_output = None
    except subprocess.CalledProcessError as e:
        valid_config = False
        error_output = e.output

    return (valid_config, error_output)


if __name__ == '__main__':
    templateTestSuite = (unittest.TestLoader().
                         loadTestsFromTestCase(templateTestCase))
