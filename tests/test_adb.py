from app.adb import Device


def test_device_dataclass():
    dev = Device(serial="ABC123", state="device")
    assert dev.serial == "ABC123"
    assert dev.state == "device"
