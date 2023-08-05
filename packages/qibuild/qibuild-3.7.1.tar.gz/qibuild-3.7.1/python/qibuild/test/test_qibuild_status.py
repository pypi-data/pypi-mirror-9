def test_simple(qibuild_action, record_messages):
    qibuild_action.add_test_project("world")
    qibuild_action.add_test_project("hello")
    qibuild_action("configure", "world")
    record_messages.reset()
    qibuild_action("status")
    assert record_messages.find("world")
    assert record_messages.find("hello")
