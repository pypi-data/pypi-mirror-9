import pytest

def test_simple(qibuild_action):
    # Just check it does not crash for now
    qibuild_action("config")

def test_run_wizard(qibuild_action, interact):
    interact.answers = {
        "generator" : "Unix Makefiles",
        "ide" : "None",
    }

    qibuild_action("config", "--wizard")
