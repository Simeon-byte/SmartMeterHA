import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parents[1] / "smartmeter"))

from HADiscovery import build_discovery_messages  # noqa: E402


class DiscoveryContractTests(unittest.TestCase):
    def setUp(self):
        self.messages = build_discovery_messages("Display Name", "meter_01")
        self.payloads = {payload["unique_id"]: payload for _, payload in self.messages}

    def test_topics_and_ids_are_instance_scoped(self):
        self.assertEqual(len(self.messages), 13)
        self.assertEqual(len(self.payloads), 13)
        self.assertEqual(
            {payload["device"]["identifiers"][0] for _, payload in self.messages},
            {"smartmeter:meter_01"},
        )
        self.assertEqual(
            self.payloads["smartmeter_meter_01_SpannungL1"]["state_topic"],
            "smartmeter/meter_01/SpannungL1",
        )
        self.assertEqual(
            self.payloads["smartmeter_meter_01_SpannungL1"]["availability_topic"],
            "smartmeter/meter_01/status",
        )

    def test_measurement_state_class_is_explicit(self):
        for key in ("SpannungL1", "StromL1", "MomentanleistungP"):
            payload = self.payloads[f"smartmeter_meter_01_{key}"]
            self.assertEqual(payload["state_class"], "measurement")

    def test_energy_and_blindleistung_contracts_remain_distinct(self):
        energy = self.payloads["smartmeter_meter_01_WirkenergieP"]
        blindleistung = self.payloads["smartmeter_meter_01_BlindleistungP"]
        self.assertEqual(energy["state_class"], "total_increasing")
        self.assertEqual(energy["device_class"], "energy")
        self.assertEqual(blindleistung["device_class"], "power")
        self.assertEqual(blindleistung["unit_of_measurement"], "W")
        self.assertNotIn("state_class", blindleistung)

    def test_display_name_does_not_change_technical_identity(self):
        renamed = build_discovery_messages("Another Name", "meter_01")
        self.assertEqual(
            [topic for topic, _ in self.messages],
            [topic for topic, _ in renamed],
        )
        self.assertEqual(
            [payload["unique_id"] for _, payload in self.messages],
            [payload["unique_id"] for _, payload in renamed],
        )


if __name__ == "__main__":
    unittest.main()
