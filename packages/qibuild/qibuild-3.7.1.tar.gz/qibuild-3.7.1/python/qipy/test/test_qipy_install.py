def test_install(qipy_action, tmpdir):
    big_project = qipy_action.add_test_project("big_project")
    dest = tmpdir.join("dest")
    qipy_action("install", "big_project", dest.strpath)
    site_packages = dest.join("lib", "python2.7", "site-packages")
    assert site_packages.join("spam.py").check(file=True)
    assert site_packages.join("foo", "bar", "baz.py").check(file=True)
    assert dest.join("bin", "script.py").check(file=True)

def test_install_with_distutils(qipy_action, tmpdir):
    with_distutils = qipy_action.add_test_project("with_distutils")
    dest = tmpdir.join("dest")
    qipy_action("bootstrap")
    qipy_action("install", "foo", dest.strpath)
    assert dest.join("bin", "foo").check(file=True)
