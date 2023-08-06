#from __future__ import unicode_literals

import pytest
import requests.exceptions
from devpi.use import *

def test_ask_confirm(makehub, monkeypatch):
    import devpi.main
    hub = makehub(["remove", "something"])
    monkeypatch.setattr(devpi.main, "raw_input", lambda msg: "yes",
                        raising=False)
    assert hub.ask_confirm("hello")
    monkeypatch.setattr(devpi.main, "raw_input", lambda msg: "no")
    assert not hub.ask_confirm("hello")
    l = ["yes", "qwoeiu"]
    monkeypatch.setattr(devpi.main, "raw_input", lambda msg: l.pop())
    assert hub.ask_confirm("hello")

def test_ask_confirm_delete_args_yes(makehub):
    hub = makehub(["remove", "-y", "whatever"])
    assert hub.ask_confirm("hello")

class TestUnit:
    def test_write_and_read(self, tmpdir):
        path=tmpdir.join("current")
        current = Current(path)
        assert not current.simpleindex
        current.reconfigure(dict(
                pypisubmit="/post",
                simpleindex="/index",
                login="/login",
        ))
        assert current.simpleindex
        newcurrent = Current(path)
        assert newcurrent.pypisubmit == current.pypisubmit
        assert newcurrent.simpleindex == current.simpleindex
        assert newcurrent.venvdir == current.venvdir
        assert newcurrent.login == current.login

    def test_write_and_read_always_setcfg(self, tmpdir):
        path=tmpdir.join("current")
        current = Current(path)
        assert not current.simpleindex
        current.reconfigure(dict(
                pypisubmit="/post",
                simpleindex="/index",
                login="/login",
        ))
        assert current.simpleindex
        current.reconfigure(dict(always_setcfg=True))
        newcurrent = Current(path)
        assert newcurrent.always_setcfg == True
        newcurrent.reconfigure(data=dict(simpleindex="/index2"))
        current = Current(path)
        assert current.always_setcfg
        assert current.simpleindex == "/index2"

    def test_use_list_doesnt_write(self, tmpdir, cmd_devpi, mock_http_api):
        import time
        mock_http_api.set(
            "http://devpi/foo/bar/+api", 200, result=dict(
                pypisubmit="/post",
                simpleindex="/index/",
                index="foo/bar",
                bases="root/pypi",
                login="/+login",
                authstatus=["noauth", "", []]))
        mock_http_api.set(
            "http://devpi/", 200, result=dict(
                foo=dict(username="foo", indexes=dict(
                    bar=dict(bases=("root/pypi",), volatile=False)))))
        cmd_devpi("use", "http://devpi/foo/bar")
        path = tmpdir.join("client", "current.json")
        mtime = path.mtime()
        time.sleep(1.5)
        cmd_devpi("use", "-l")
        assert mtime == path.mtime()

    def test_normalize_url(self, tmpdir):
        current = Current(tmpdir.join("current"))
        current.reconfigure(dict(simpleindex="http://my.serv/index1"))
        url = current._normalize_url("index2")
        assert url == "http://my.serv/index2"

    def test_auth_multisite(self, tmpdir):
        current = Current(tmpdir.join("current"))
        login1 = "http://site.com/+login"
        login2 = "http://site2.com/+login"
        current.set_auth("hello", "pass1", login1)
        current.set_auth("hello", "pass2", login2)
        assert current.get_auth(login1) == ("hello", "pass1")
        assert current.get_auth(login2) == ("hello", "pass2")
        current.del_auth(login1)
        assert not current.get_auth(login1)
        assert current.get_auth(login2) == ("hello", "pass2")
        current.del_auth(login2)
        assert not current.get_auth(login2)

    def test_invalid_url(self, loghub, tmpdir):
        current = Current(tmpdir.join("current"))
        with pytest.raises(SystemExit):
            current.configure_fromurl(loghub, "http://heise.de:1802:31/qwe")

    def test_auth_handling(self, loghub, tmpdir):
        current = Current(tmpdir.join("current"))
        d = {
            "index": "http://l/some/index",
            "login": "http://l/login",
        }
        current.reconfigure(data=d)
        assert current.rooturl
        current.set_auth("user", "password")
        assert current.get_auth() == ("user", "password")

        # ok response
        d["authstatus"] = ["ok", "user"]
        current._configure_from_server_api(d, URL(current.rooturl))
        assert current.get_auth() == ("user", "password")

        # invalidation response
        d["authstatus"] = ["nouser", "user"]
        current._configure_from_server_api(d, URL(current.rooturl))
        assert not current.get_auth()

    def test_rooturl_on_outside_url(self, loghub, tmpdir):
        current = Current(tmpdir.join("current"))
        d = {
            "index": "http://l/subpath/some/index",
            "login": "http://l/subpath/login",
        }
        current.reconfigure(data=d)
        assert current.rooturl == "http://l/subpath/"

    def test_use_with_no_rooturl(self, capfd, cmd_devpi, monkeypatch):
        from devpi import main
        monkeypatch.setattr(main.Hub, "http_api", None)
        cmd_devpi("use", "some/index", code=None)
        out, err = capfd.readouterr()
        assert "invalid" in out

    @pytest.mark.parametrize("Exc", [
        requests.exceptions.ConnectionError,
        requests.exceptions.BaseHTTPError,
    ])
    def test_use_with_nonexistent_domain(self, capfd, cmd_devpi, Exc,
                                         monkeypatch):
        from requests.sessions import Session
        def raise_(*args, **kwargs):
            raise Exc("qwe")
        monkeypatch.setattr(Session, "request", raise_)
        cmd_devpi("use", "http://qlwkejqlwke", code=-1)
        out, err = capfd.readouterr()
        assert "could not connect" in out

    def test_use_with_basic_auth(self, cmd_devpi, mock_http_api):
        mock_http_api.set(
            "http://devpi/foo/bar/+api", 200, result=dict(
                pypisubmit="/post",
                simpleindex="/index/",
                index="foo/bar",
                bases="root/pypi",
                login="/+login",
                authstatus=["noauth", ""]))
        mock_http_api.set(
            "http://devpi/foo/ham/+api", 200, result=dict(
                pypisubmit="/post",
                simpleindex="/index/",
                index="foo/ham",
                bases="root/pypi",
                login="/+login",
                authstatus=["noauth", ""]))
        mock_http_api.set(
            "http://devpi/", 200, result=dict(
                foo=dict(username="foo", indexes=dict(
                    bar=dict(bases=("root/pypi",), volatile=False),
                    ham=dict(bases=("root/pypi",), volatile=False)))))
        # use with basic authentication
        hub = cmd_devpi("use", "http://user:password@devpi/foo/bar")
        # should work with and without explicit port if it's the default port
        assert hub.current.get_basic_auth(url="http://devpi/foo/bar") == ('user', 'password')
        assert hub.current.get_basic_auth(url="http://devpi:80/foo/bar") == ('user', 'password')
        # now we switch only the index, basic auth info should be kept
        hub = cmd_devpi("use", "/foo/ham")
        assert hub.current.get_basic_auth(url="http://devpi/foo/bar") == ('user', 'password')
        assert hub.current.get_basic_auth(url="http://devpi:80/foo/bar") == ('user', 'password')
        # just listing the index shouldn't change anything
        hub = cmd_devpi("use", "-l")
        assert hub.current.get_basic_auth(url="http://devpi/foo/bar") == ('user', 'password')
        assert hub.current.get_basic_auth(url="http://devpi:80/foo/bar") == ('user', 'password')
        # now without basic authentication
        hub = cmd_devpi("use", "http://devpi/foo/bar")
        assert hub.current.get_basic_auth(url="http://devpi/foo/bar") is None

    def test_use_with_basic_auth_https(self, cmd_devpi, mock_http_api):
        mock_http_api.set(
            "https://devpi/foo/bar/+api", 200, result=dict(
                pypisubmit="/post",
                simpleindex="/index/",
                index="foo/bar",
                bases="root/pypi",
                login="/+login",
                authstatus=["noauth", ""]))
        # use with basic authentication
        hub = cmd_devpi("use", "https://user:password@devpi/foo/bar")
        # should work with and without explicit port if it's the default port
        assert hub.current.get_basic_auth(url="https://devpi/foo/bar") == ('user', 'password')
        assert hub.current.get_basic_auth(url="https://devpi:443/foo/bar") == ('user', 'password')
        # now without basic authentication
        hub = cmd_devpi("use", "https://devpi/foo/bar")
        assert hub.current.get_basic_auth(url="https://devpi/foo/bar") is None

    def test_change_index(self, cmd_devpi, mock_http_api):
        mock_http_api.set("http://world.com/+api", 200,
                    result=dict(
                        index="/index",
                        login="/+login",
                        authstatus=["noauth", ""],
                   ))
        mock_http_api.set("http://world2.com/+api", 200,
                    result=dict(
                        login="/+login",
                        authstatus=["noauth", ""],
                   ))

        hub = cmd_devpi("use", "http://world.com")
        assert hub.current.index == "http://world.com/index"
        assert hub.current.rooturl == "http://world.com/"

        hub = cmd_devpi("use", "http://world2.com")
        assert not hub.current.index
        assert hub.current.rooturl == "http://world2.com/"

    def test_main(self, cmd_devpi, mock_http_api):
        mock_http_api.set("http://world/this/+api", 200,
                    result=dict(
                        pypisubmit="/post",
                        simpleindex="/index/",
                        index="root/some",
                        bases="root/dev",
                        login="/+login",
                        authstatus=["noauth", ""],
                   ))

        hub = cmd_devpi("use", "http://world/this")
        newapi = hub.current
        assert newapi.pypisubmit == "http://world/post"
        assert newapi.simpleindex == "http://world/index/"
        assert not newapi.venvdir

        # some url helpers
        current = hub.current
        assert current.get_index_url(slash=False) == "http://world/root/some"
        assert current.get_index_url() == "http://world/root/some/"
        assert current.get_project_url("pytest") == \
                                    "http://world/root/some/pytest/"

        #hub = cmd_devpi("use", "--delete")
        #assert not hub.current.exists()

    def test_main_list(self, out_devpi, cmd_devpi, mock_http_api):
        mock_http_api.set("http://world/+api", 200,
                    result=dict(
                        pypisubmit="",
                        simpleindex="",
                        index="",
                        bases="",
                        login="/+login",
                        authstatus=["noauth", ""],
                   ))

        cmd_devpi("use", "http://world/")
        mock_http_api.set("http://world/", 200, result=dict(
            user1=dict(indexes={"dev": {"bases": ["x"],
                "volatile": False}})
        ))
        out = out_devpi("use", "-l")
        out.stdout.fnmatch_lines("""
            user1/dev*x*False*
        """)

    def test_main_venvsetting(self, out_devpi, cmd_devpi, tmpdir, monkeypatch):
        from devpi.use import vbin
        venvdir = tmpdir
        venvdir.ensure(vbin, dir=1)
        monkeypatch.chdir(tmpdir)
        hub = cmd_devpi("use", "--venv=%s" % venvdir)
        current = Current(hub.current.path)
        assert current.venvdir == str(venvdir)
        hub = cmd_devpi("use", "--venv=%s" % venvdir)
        res = out_devpi("use")
        res.stdout.fnmatch_lines("*venv*%s" % venvdir)

        # test via env
        monkeypatch.setenv("WORKON_HOME", venvdir.dirpath())
        hub = cmd_devpi("use", "--venv=%s" % venvdir.basename)
        assert hub.current.venvdir == venvdir

    @pytest.mark.parametrize(['scheme', 'basic_auth'], [
        ('http', ''),
        ('https', ''),
        ('http', 'foo:bar@'),
        ('https', 'foo:bar@')])
    def test_main_setcfg(self, scheme, basic_auth, mock_http_api, cmd_devpi, tmpdir, monkeypatch):
        monkeypatch.setattr(PipCfg, "default_location", tmpdir.join("pip.cfg"))
        monkeypatch.setattr(DistutilsCfg, "default_location",
                            tmpdir.join("dist.cfg"))
        monkeypatch.setattr(BuildoutCfg, "default_location",
                            tmpdir.join("buildout.cfg"))
        mock_http_api.set("%s://world/+api" % scheme, 200,
                    result=dict(
                        pypisubmit="",
                        simpleindex="/simple",
                        index="/",
                        bases="",
                        login="/+login",
                        authstatus=["noauth", ""],
                   ))

        hub = cmd_devpi("use", "--set-cfg", "%s://%sworld" % (scheme, basic_auth))
        assert PipCfg.default_location.exists()
        content = PipCfg.default_location.read()
        assert "index_url = %s://%sworld/" % (scheme, basic_auth) in content
        assert DistutilsCfg.default_location.exists()
        content = DistutilsCfg.default_location.read()
        assert "index_url = %s://%sworld/" % (scheme, basic_auth) in content
        assert BuildoutCfg.default_location.exists()
        content = BuildoutCfg.default_location.read()
        assert "index = %s://%sworld/" % (scheme, basic_auth) in content
        hub = cmd_devpi("use", "--always-set-cfg=yes")
        assert hub.current.always_setcfg
        hub = cmd_devpi("use", "--always-set-cfg=no")
        assert not hub.current.always_setcfg


@pytest.mark.parametrize("input expected".split(), [
    (["hello=123", "world=42"], dict(hello="123", world="42")),
    (["hello=123=1"], dict(hello="123=1"))
    ])
def test_parse_keyvalue_spec(input, expected):
    result = parse_keyvalue_spec(input, "hello world".split())
    assert result == expected

def test_parse_keyvalue_spec_unknown_key():
    pytest.raises(KeyError, lambda: parse_keyvalue_spec(["hello=3"], ["some"]))

def test_user_no_index(loghub):
    out_index_list(loghub, {"user": {"username": "user"}})

def test_pipcfg_default_location(tmpdir, monkeypatch):
    path = PipCfg().path
    monkeypatch.setenv('PIP_CONFIG_FILE', tmpdir.join("cfg"))
    assert path != PipCfg().path

class TestCfgParsing:
    @pytest.fixture(scope="class", params=[DistutilsCfg, PipCfg, BuildoutCfg])
    def cfgclass(self, request):
        return request.param

    def test_empty(self, cfgclass, tmpdir):
        p = tmpdir.join("cfg")
        assert not cfgclass(p).exists()
        assert cfgclass(p).indexserver is None
        assert cfgclass(p).screen_name == str(p)
        assert cfgclass.default_location

    def test_read(self, cfgclass, tmpdir):
        p = tmpdir.join("cfg")
        cfg = cfgclass(p)
        cfg.write_default("http://some.com/something")
        with pytest.raises(ValueError):
            cfg.write_default("http://some.com/something")
        cfg = cfgclass(p)
        assert cfg.exists()
        assert cfg.indexserver == "http://some.com/something"
        assert cfg.screen_name == str(p)

    def test_read_config_but_no_index(self, tmpdir, cfgclass):
        path = tmpdir.join("cfg")
        path.write(cfgclass.section_name + "\n")
        cfg = cfgclass(path)
        cfg.write_indexserver("http://qwe")
        cfg = cfgclass(path)
        assert cfg.indexserver == "http://qwe"

    def test_read_config_but_no_section(self, tmpdir, cfgclass):
        path = tmpdir.join("cfg")
        path.write("")
        cfg = cfgclass(path)
        cfg.write_indexserver("http://qwe")
        cfg = cfgclass(path)
        assert cfg.indexserver == "http://qwe"

    def test_write_fresh(self, cfgclass, tmpdir):
        p = tmpdir.join("cfg")
        cfg = cfgclass(p)
        cfg.write_indexserver("http://hello.com")
        assert cfg.indexserver == "http://hello.com"

    def test_rewrite(self, cfgclass, tmpdir):
        p = tmpdir.join("cfg")
        cfgclass(p).write_default("http://some.com/something")
        cfg = cfgclass(p)
        cfg.write_indexserver("http://hello.com")
        assert cfg.indexserver == "http://hello.com"
        assert cfgclass(cfg.backup_path).indexserver == \
               "http://some.com/something"
        cfg.write_indexserver("http://hello.com")
        assert cfgclass(cfg.backup_path).indexserver == \
               "http://some.com/something"
