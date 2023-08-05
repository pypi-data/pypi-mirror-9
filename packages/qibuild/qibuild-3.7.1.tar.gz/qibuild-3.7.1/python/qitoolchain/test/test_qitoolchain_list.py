from qibuild.test.conftest import QiBuildAction
from qitoolchain.test.conftest import QiToolchainAction

def test_no_toolchain(qitoolchain_action, record_messages):
    qitoolchain_action("list")
    assert record_messages.find("No toolchain yet")

def test_default_toolchain(cd_to_tmpdir, record_messages):
    qibuild_action = QiBuildAction()
    qitoolchain_action = QiToolchainAction()
    qitoolchain_action("create", "bar")
    qitoolchain_action("create", "foo", "--default")
    record_messages.reset()
    qitoolchain_action("list")
    assert record_messages.find(" bar")
    assert record_messages.find("\* foo")
