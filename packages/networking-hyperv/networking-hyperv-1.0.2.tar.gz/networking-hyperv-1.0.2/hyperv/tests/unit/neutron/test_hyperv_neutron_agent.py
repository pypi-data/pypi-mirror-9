# Copyright 2013 Cloudbase Solutions SRL
# Copyright 2013 Pedro Navarro Perez
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

"""
Unit tests for Windows Hyper-V virtual switch neutron driver
"""

import mock

from hyperv.neutron import constants
from hyperv.neutron import hyperv_neutron_agent
from hyperv.neutron import utils
from hyperv.neutron import utilsfactory
from hyperv.tests import base


class TestHyperVNeutronAgent(base.BaseTestCase):

    _FAKE_PORT_ID = 'fake_port_id'

    def setUp(self):
        super(TestHyperVNeutronAgent, self).setUp()

        utilsfactory._get_windows_version = mock.MagicMock(
            return_value='6.2.0')

        self.agent = hyperv_neutron_agent.HyperVNeutronAgentMixin()
        self.agent.plugin_rpc = mock.Mock()
        self.agent._utils = mock.MagicMock()
        self.agent.sec_groups_agent = mock.MagicMock()
        self.agent.context = mock.Mock()
        self.agent.agent_id = mock.Mock()

    def test_load_physical_network_mappings(self):
        test_mappings = ['fake_network_1:fake_vswitch',
                         'fake_network_2:fake_vswitch_2', '*:fake_vswitch_3']
        expected = [('fake\\_network\\_1', 'fake_vswitch'),
                    ('fake\\_network\\_2', 'fake_vswitch_2'),
                    ('.*', 'fake_vswitch_3')]

        self.agent._load_physical_network_mappings(test_mappings)

        self.assertEqual(expected,
                         self.agent._physical_network_mappings.items())

    @mock.patch.object(hyperv_neutron_agent.HyperVNeutronAgentMixin,
                       "_get_vswitch_name")
    def test_provision_network_exception(self, mock_get_vswitch_name):
        self.assertRaises(utils.HyperVException, self.agent._provision_network,
                          mock.sentinel.FAKE_PORT_ID,
                          mock.sentinel.FAKE_NET_UUID,
                          mock.sentinel.FAKE_NETWORK_TYPE,
                          mock.sentinel.FAKE_PHYSICAL_NETWORK,
                          mock.sentinel.FAKE_SEGMENTATION_ID)
        mock_get_vswitch_name.assert_called_once_with(
            mock.sentinel.FAKE_NETWORK_TYPE,
            mock.sentinel.FAKE_PHYSICAL_NETWORK)

    @mock.patch.object(hyperv_neutron_agent.HyperVNeutronAgentMixin,
                       "_get_vswitch_name")
    def test_provision_network_vlan(self, mock_get_vswitch_name):
        vswitch_name = mock_get_vswitch_name.return_value
        self.agent._provision_network(mock.sentinel.FAKE_PORT_ID,
                                      mock.sentinel.FAKE_NET_UUID,
                                      constants.TYPE_VLAN,
                                      mock.sentinel.FAKE_PHYSICAL_NETWORK,
                                      mock.sentinel.FAKE_SEGMENTATION_ID)
        mock_get_vswitch_name.assert_called_once_with(
            constants.TYPE_VLAN,
            mock.sentinel.FAKE_PHYSICAL_NETWORK)
        set_switch = self.agent._utils.set_switch_external_port_trunk_vlan
        set_switch.assert_called_once_with(vswitch_name,
                                           mock.sentinel.FAKE_SEGMENTATION_ID,
                                           constants.TRUNK_ENDPOINT_MODE)

    @mock.patch.object(hyperv_neutron_agent.HyperVNeutronAgentMixin,
                       "_get_vswitch_name")
    def test_provision_network_flat(self, mock_get_vswitch_name):
        self.agent._provision_network(mock.sentinel.FAKE_PORT_ID,
                                      mock.sentinel.FAKE_NET_UUID,
                                      constants.TYPE_FLAT,
                                      mock.sentinel.FAKE_PHYSICAL_NETWORK,
                                      mock.sentinel.FAKE_SEGMENTATION_ID)
        mock_get_vswitch_name.assert_called_once_with(
            constants.TYPE_FLAT,
            mock.sentinel.FAKE_PHYSICAL_NETWORK)

    @mock.patch.object(hyperv_neutron_agent.HyperVNeutronAgentMixin,
                       "_get_vswitch_name")
    def test_provision_network_local(self, mock_get_vswitch_name):
        self.agent._provision_network(mock.sentinel.FAKE_PORT_ID,
                                      mock.sentinel.FAKE_NET_UUID,
                                      constants.TYPE_LOCAL,
                                      mock.sentinel.FAKE_PHYSICAL_NETWORK,
                                      mock.sentinel.FAKE_SEGMENTATION_ID)
        mock_get_vswitch_name.assert_called_once_with(
            constants.TYPE_LOCAL,
            mock.sentinel.FAKE_PHYSICAL_NETWORK)

    def test_port_bound_enable_metrics(self):
        self.agent.enable_metrics_collection = True
        self._test_port_bound(True)

    def test_port_bound_no_metrics(self):
        self.agent.enable_metrics_collection = False
        self._test_port_bound(False)

    def _test_port_bound(self, enable_metrics):
        port = mock.MagicMock()
        mock_enable_metrics = mock.MagicMock()
        net_uuid = 'my-net-uuid'

        with mock.patch.multiple(
                self.agent._utils,
                connect_vnic_to_vswitch=mock.MagicMock(),
                set_vswitch_port_vlan_id=mock.MagicMock(),
                enable_port_metrics_collection=mock_enable_metrics):

            self.agent._port_bound(port, net_uuid, 'vlan', None, None)

            self.assertEqual(enable_metrics, mock_enable_metrics.called)

    def test_port_unbound(self):
        map = {
            'network_type': 'vlan',
            'vswitch_name': 'fake-vswitch',
            'ports': [],
            'vlan_id': 1}
        net_uuid = 'my-net-uuid'
        network_vswitch_map = (net_uuid, map)
        with mock.patch.object(self.agent,
                               '_get_network_vswitch_map_by_port_id',
                               return_value=network_vswitch_map):
            with mock.patch.object(
                    self.agent._utils,
                    'disconnect_switch_port'):
                self.agent._port_unbound(net_uuid)

    def test_port_enable_control_metrics_ok(self):
        self.agent.enable_metrics_collection = True
        self.agent._port_metric_retries[self._FAKE_PORT_ID] = (
            self.agent._metrics_max_retries)

        with mock.patch.multiple(self.agent._utils,
                                 can_enable_control_metrics=mock.MagicMock(),
                                 enable_control_metrics=mock.MagicMock()):

            self.agent._utils.can_enable_control_metrics.return_value = True
            self.agent._port_enable_control_metrics()
            self.agent._utils.enable_control_metrics.assert_called_with(
                self._FAKE_PORT_ID)

        self.assertNotIn(self._FAKE_PORT_ID, self.agent._port_metric_retries)

    def test_port_enable_control_metrics_maxed(self):
        self.agent.enable_metrics_collection = True
        self.agent._metrics_max_retries = 3
        self.agent._port_metric_retries[self._FAKE_PORT_ID] = 3

        with mock.patch.multiple(self.agent._utils,
                                 can_enable_control_metrics=mock.MagicMock(),
                                 enable_control_metrics=mock.MagicMock()):

            self.agent._utils.can_enable_control_metrics.return_value = False
            for i in range(4):
                self.assertIn(self._FAKE_PORT_ID,
                              self.agent._port_metric_retries)
                self.agent._port_enable_control_metrics()

        self.assertNotIn(self._FAKE_PORT_ID, self.agent._port_metric_retries)

    def test_treat_devices_added_returns_true_for_missing_device(self):
        attrs = {'get_devices_details_list.side_effect': Exception()}
        self.agent.plugin_rpc.configure_mock(**attrs)
        self.assertTrue(self.agent._treat_devices_added([{}]))

    def mock_treat_devices_added(self, details, func_name):
        """Mock treat devices added.

        :param details: the details to return for the device
        :param func_name: the function that should be called
        :returns: whether the named function was called
        """
        attrs = {'get_devices_details_list.return_value': [details]}
        self.agent.plugin_rpc.configure_mock(**attrs)
        with mock.patch.object(self.agent, func_name) as func:
            self.assertFalse(self.agent._treat_devices_added([{}]))
        return func.called

    def test_treat_devices_added_updates_known_port(self):
        details = mock.MagicMock()
        details.__contains__.side_effect = lambda x: True
        with mock.patch.object(self.agent.plugin_rpc,
                               "update_device_up") as func:
            self.assertTrue(self.mock_treat_devices_added(details,
                                                          '_treat_vif_port'))
            self.assertTrue(func.called)

    def test_treat_devices_added_missing_port_id(self):
        details = mock.MagicMock()
        details.__contains__.side_effect = lambda x: False
        with mock.patch.object(self.agent.plugin_rpc,
                               "update_device_up") as func:
            self.assertFalse(self.mock_treat_devices_added(details,
                                                           '_treat_vif_port'))
            self.assertFalse(func.called)

    def test_treat_devices_removed_returns_true_for_missing_device(self):
        attrs = {'update_device_down.side_effect': Exception()}
        self.agent.plugin_rpc.configure_mock(**attrs)
        self.assertTrue(self.agent._treat_devices_removed([{}]))

    def mock_treat_devices_removed(self, port_exists):
        details = dict(exists=port_exists)
        attrs = {'update_device_down.return_value': details}
        self.agent.plugin_rpc.configure_mock(**attrs)
        with mock.patch.object(self.agent, '_port_unbound') as func:
            self.assertFalse(self.agent._treat_devices_removed([{}]))
        self.assertEqual(func.called, not port_exists)

    def test_treat_devices_removed_unbinds_port(self):
        self.mock_treat_devices_removed(False)

    def test_treat_devices_removed_ignores_missing_port(self):
        self.mock_treat_devices_removed(False)
