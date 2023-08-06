import hashlib
import pytest
import py
from devpi_server.replica import *  # noqa
from devpi_common.url import URL

def loads(bytestring):
    return load(py.io.BytesIO(bytestring))

pytestmark = [pytest.mark.notransaction]

def test_view_name2serials(pypistage, testapp):
    pypistage.mock_simple("package", '<a href="/package-1.0.zip" />',
                          pypiserial=15)
    r = testapp.get("/root/pypi/+name2serials", expect_errors=False)
    io = py.io.BytesIO(r.body)
    entries = load(io)
    assert entries["package"] == 15


class TestChangelog:
    replica_uuid = "111"
    replica_url = "http://qwe"

    @pytest.fixture
    def reqchangelog(self, testapp):
        def reqchangelog(serial):
            req_headers = {H_REPLICA_UUID: self.replica_uuid,
                           H_REPLICA_OUTSIDE_URL: self.replica_url}
            return testapp.get("/+changelog/%s" % serial, expect_errors=False,
                                headers=req_headers)
        return reqchangelog

    def get_latest_serial(self, testapp):
        r = testapp.get("/+changelog/nop", expect_errors=False)
        return int(r.headers["X-DEVPI-SERIAL"])

    def test_get_latest_serial(self, testapp, mapp):
        latest_serial = self.get_latest_serial(testapp)
        assert latest_serial >= -1
        mapp.create_user("hello", "pass")
        assert self.get_latest_serial(testapp) == latest_serial + 1

    def test_get_since(self, testapp, mapp, noiter, reqchangelog):
        mapp.create_user("this", password="p")
        latest_serial = self.get_latest_serial(testapp)
        r = reqchangelog(latest_serial)
        body = b''.join(r.app_iter)
        data = loads(body)
        assert "this" in str(data)

    def test_get_wait(self, reqchangelog, testapp, mapp, noiter, monkeypatch):
        mapp.create_user("this", password="p")
        latest_serial = self.get_latest_serial(testapp)
        monkeypatch.setattr(testapp.xom.keyfs.notifier.cv_new_transaction,
                            "wait", lambda *x: 0/0)
        with pytest.raises(ZeroDivisionError):
            reqchangelog(latest_serial+1)

    def test_get_wait_blocking_ends(self, testapp, mapp, noiter, monkeypatch,
                                    reqchangelog):
        mapp.create_user("this", password="p")
        latest_serial = self.get_latest_serial(testapp)
        monkeypatch.setattr(MasterChangelogRequest, "MAX_REPLICA_BLOCK_TIME",
                            0.01)
        monkeypatch.setattr(MasterChangelogRequest, "WAKEUP_INTERVAL",
                            0.001)
        r = reqchangelog(latest_serial+1)
        assert r.status_code == 202
        assert int(r.headers["X-DEVPI-SERIAL"]) == latest_serial


class TestPyPIProxy:
    def test_pypi_proxy(self, xom, reqmock):
        from devpi_server.keyfs import dump
        url = "http://localhost:3141/root/pypi/+name2serials"
        master_url = URL("http://localhost:3141")
        proxy = PyPIProxy(xom._httpsession, master_url)
        io = py.io.BytesIO()
        dump({"hello": 42}, io)
        data = io.getvalue()
        reqmock.mockresponse(url=url, code=200, method="GET", data=data)
        name2serials = proxy.list_packages_with_serial()
        assert name2serials == {"hello": 42}

    def test_replica_startup(self, replica_xom):
        assert isinstance(replica_xom.proxy, PyPIProxy)


def test_pypi_project_changed(replica_xom):
    handler = PypiProjectChanged(replica_xom)
    class Ev:
        value = dict(projectname="newproject", serial=12)
        typedkey = replica_xom.keyfs.get_key("PYPILINKS")(name="newproject")
    handler(Ev())
    assert replica_xom.pypimirror.name2serials["newproject"] == 12
    class Ev2:
        value = dict(projectname="newproject", serial=15)
        typedkey = replica_xom.keyfs.get_key("PYPILINKS")(name="newproject")
    handler(Ev2())
    assert replica_xom.pypimirror.name2serials["newproject"] == 15

    class Ev3:
        typedkey = replica_xom.keyfs.get_key("PYPILINKS")(name="newproject")
        value = None
    handler(Ev3())
    assert "newproject" not in replica_xom.pypimirror.name2serials


class TestReplicaThread:
    @pytest.fixture
    def rt(self, makexom):
        xom = makexom(["--master=http://localhost"])
        rt = ReplicaThread(xom)
        xom.thread_pool.register(rt)
        return rt

    @pytest.fixture
    def mockchangelog(self, reqmock):
        def mockchangelog(num, code, data=b'',
                          headers={H_MASTER_UUID: "123"}):
            reqmock.mockresponse("http://localhost/+changelog/%s" % num,
                                 code=code, data=data, headers=headers)
        return mockchangelog

    def test_thread_run_fail(self, rt, mockchangelog, caplog):
        rt.thread.sleep = lambda x: 0/0
        mockchangelog(0, code=404)
        with pytest.raises(ZeroDivisionError):
            rt.thread_run()
        assert caplog.getrecords("404.*failed fetching*")

    def test_thread_run_decode_error(self, rt, mockchangelog, caplog):
        rt.thread.sleep = lambda x: 0/0
        mockchangelog(0, code=200, data=b'qwelk')
        with pytest.raises(ZeroDivisionError):
            rt.thread_run()
        assert caplog.getrecords("could not process")

    def test_thread_run_ok(self, rt, mockchangelog, caplog, xom):
        rt.thread.sleep = lambda *x: 0/0
        data = xom.keyfs._fs.get_raw_changelog_entry(0)
        assert data
        mockchangelog(0, code=200, data=data)
        mockchangelog(1, code=404, data=data)
        with pytest.raises(ZeroDivisionError):
            rt.thread_run()
        assert caplog.getrecords("committed")

    def test_thread_run_no_uuid(self, rt, mockchangelog, caplog, xom):
        rt.thread.sleep = lambda x: 0/0
        mockchangelog(0, code=200, data=b'123', headers={})
        with pytest.raises(ZeroDivisionError):
            rt.thread_run()
        assert caplog.getrecords("remote.*no.*UUID")

    def test_thread_run_ok_uuid_change(self, rt, mockchangelog, caplog, xom):
        rt.thread.sleep = lambda *x: 0/0
        data = xom.keyfs._fs.get_raw_changelog_entry(0)
        assert data
        mockchangelog(0, code=200, data=data)
        mockchangelog(1, code=200, data=data,
                      headers={"x-devpi-master-uuid": "001"})
        with pytest.raises(ZeroDivisionError):
            rt.thread_run()
        assert caplog.getrecords("master UUID.*001.*does not match")

    def test_thread_run_try_again(self, rt, mockchangelog, caplog):
        l = [1]
        def exit_if_shutdown():
            l.pop()
        rt.thread.exit_if_shutdown = exit_if_shutdown
        mockchangelog(0, code=202)
        with pytest.raises(IndexError):
            rt.thread_run()
        assert caplog.getrecords("trying again")


def test_clean_request_headers(blank_request):
    from devpi_server.replica import clean_request_headers
    request = blank_request()
    request.headers['Foo'] = 'bar'
    assert 'host' in request.headers
    assert 'foo' in request.headers
    headers = clean_request_headers(request)
    assert 'host' not in headers
    assert 'foo' in headers


def test_clean_response_headers(mock):
    from devpi_server.replica import clean_response_headers
    response = mock.Mock()
    response.headers = dict(foo='bar')
    # make sure the result is a case insensitive header dict
    headers = clean_response_headers(response)
    assert 'foo' in headers
    assert 'FOO' in headers
    assert 'bar' not in headers
    headers['egg'] = 'ham'
    assert 'egg' in headers
    assert 'EGG' in headers


class TestTweenReplica:
    def test_nowrite(self, xom, blank_request):
        l = []
        def wrapped_handler(request):
            l.append(xom.keyfs.get_current_serial())
            return Response("")
        handler = tween_replica_proxy(wrapped_handler, {"xom": xom})
        handler(blank_request())
        assert l == [xom.keyfs.get_current_serial()]

    def test_write_proxies(self, makexom, blank_request, reqmock, monkeypatch):
        xom = makexom(["--master", "http://localhost"])
        reqmock.mock("http://localhost/blankpath",
                     code=200, headers={"X-DEVPI-SERIAL": "10"})
        l = []
        monkeypatch.setattr(xom.keyfs.notifier, "wait_tx_serial",
                            lambda x: l.append(x))
        handler = tween_replica_proxy(None, {"xom": xom})
        response = handler(blank_request(method="PUT"))
        assert response.headers.get("X-DEVPI-SERIAL") == "10"
        assert l == [10]

    def test_preserve_reason(self, makexom, blank_request, reqmock, monkeypatch):
        xom = makexom(["--master", "http://localhost"])
        reqmock.mock("http://localhost/blankpath",
                     code=200, reason="GOOD", headers={"X-DEVPI-SERIAL": "10"})
        l = []
        monkeypatch.setattr(xom.keyfs.notifier, "wait_tx_serial",
                            lambda x: l.append(x))
        handler = tween_replica_proxy(None, {"xom": xom})
        response = handler(blank_request(method="PUT"))
        assert response.status == "200 GOOD"

    def test_write_proxies_redirect(self, makexom, blank_request, reqmock, monkeypatch):
        xom = makexom(["--master", "http://localhost",
                       "--outside-url=http://my.domain"])
        reqmock.mock("http://localhost/blankpath",
                     code=302, headers={"X-DEVPI-SERIAL": "10",
                                        "location": "http://localhost/hello"}
        )
        l = []
        monkeypatch.setattr(xom.keyfs.notifier, "wait_tx_serial",
                            lambda x: l.append(x))
        handler = tween_replica_proxy(None, {"xom": xom})
        # normally the app is wrapped by OutsideURLMiddleware, since this is
        # not the case here, we have to set the host explicitly
        response = handler(
            blank_request(method="PUT", headers=dict(host='my.domain')))
        assert response.headers.get("X-DEVPI-SERIAL") == "10"
        assert response.headers.get("location") == "http://my.domain/hello"
        assert l == [10]

    def test_hop_headers(self, makexom, blank_request, reqmock, monkeypatch):
        xom = makexom(["--master", "http://localhost"])
        reqmock.mock("http://localhost/blankpath",
                     code=200, headers={
                        "Connection": "Keep-Alive, Foo",
                        "Foo": "abc",
                        "Keep-Alive": "timeout=30",
                        "X-DEVPI-SERIAL": "0"})
        monkeypatch.setattr(xom.keyfs.notifier, "wait_tx_serial",
                            lambda x: x)
        handler = tween_replica_proxy(None, {"xom": xom})
        response = handler(blank_request(method="PUT"))
        assert 'connection' not in response.headers
        assert 'foo' not in response.headers
        assert 'keep-alive' not in response.headers

def replay(xom, replica_xom):
    for serial in range(replica_xom.keyfs.get_next_serial(),
                        xom.keyfs.get_next_serial()):
        if serial == -1:
            continue
        change_entry = xom.keyfs._fs.get_changes(serial)
        threadlog.info("importing to replica %s", serial)
        replica_xom.keyfs.import_changes(serial, change_entry)

class TestFileReplication:
    @pytest.fixture
    def replica_xom(self, makexom):
        from devpi_server.replica import ReplicationErrors
        replica_xom = makexom(["--master", "http://localhost"])
        keyfs = replica_xom.keyfs
        replica_xom.errors = ReplicationErrors(replica_xom.config.serverdir)
        for key in (keyfs.STAGEFILE, keyfs.PYPIFILE_NOMD5):
            keyfs.subscribe_on_import(
                key, ImportFileReplica(replica_xom, replica_xom.errors))
        return replica_xom

    def test_no_set_default_indexes(self, replica_xom):
        assert replica_xom.keyfs.get_current_serial() == -1

    def test_nowrite(self, replica_xom):
        with pytest.raises(replica_xom.keyfs.ReadOnly):
            with replica_xom.keyfs.transaction(write=True):
                pass
        with pytest.raises(replica_xom.keyfs.ReadOnly):
            with replica_xom.keyfs.transaction():
                replica_xom.keyfs.restart_as_write_transaction()


    def test_transaction_api(self, replica_xom, xom):
        with xom.keyfs.transaction(write=True):
            xom.model.create_user("hello", "pass")
        with xom.keyfs.transaction(write=True):
            xom.model.create_user("world", "pass")

        replay(xom, replica_xom)

        serial = xom.keyfs.get_current_serial() - 1
        with replica_xom.keyfs.transaction(at_serial=serial):
            assert not replica_xom.model.get_user("world")
            assert replica_xom.model.get_user("hello")


    def test_fetch(self, gen, reqmock, xom, replica_xom):
        replay(xom, replica_xom)
        content1 = b'hello'
        md5 = hashlib.md5(content1).hexdigest()
        link = gen.pypi_package_link("pytest-1.8.zip#md5=%s" % md5, md5=False)
        with xom.keyfs.transaction(write=True):
            entry = xom.filestore.maplink(link)
            assert not entry.file_exists()

        replay(xom, replica_xom)
        with replica_xom.keyfs.transaction():
            r_entry = replica_xom.filestore.get_file_entry(entry.relpath)
            assert not r_entry.file_exists()
            assert r_entry.meta

        with xom.keyfs.transaction(write=True):
            entry.file_set_content(content1)

        # first we try to return something wrong
        master_url = replica_xom.config.master_url
        master_file_path = master_url.joinpath(entry.relpath).url
        xom.httpget.mockresponse(master_file_path, code=200, content=b'13')
        replay(xom, replica_xom)
        assert list(replica_xom.errors.errors.keys()) == [
            'root/pypi/+f/5d4/1402abc4b2a76/pytest-1.8.zip']
        with replica_xom.errors.errorsfn.open() as f:
            persisted_errors = json.load(f)
        assert persisted_errors == replica_xom.errors.errors
        with replica_xom.keyfs.transaction():
            assert not r_entry.file_exists()
            assert not os.path.exists(r_entry._filepath)

        # then we try to return the correct thing
        with xom.keyfs.transaction(write=True):
            entry.file_set_content(content1, md5=md5)
        xom.httpget.mockresponse(master_file_path, code=200, content=content1)
        replay(xom, replica_xom)
        assert replica_xom.errors.errors == {}
        with replica_xom.errors.errorsfn.open() as f:
            persisted_errors = json.load(f)
        assert persisted_errors == replica_xom.errors.errors
        with replica_xom.keyfs.transaction():
            assert r_entry.file_exists()
            assert r_entry.file_get_content() == content1

        # now we produce a delete event
        with xom.keyfs.transaction(write=True):
            entry.delete()
        replay(xom, replica_xom)
        with replica_xom.keyfs.transaction():
            assert not r_entry.file_exists()

    def test_fetch_later_deleted(self, gen, reqmock, xom, replica_xom):
        replay(xom, replica_xom)
        content1 = b'hello'
        md5 = hashlib.md5(content1).hexdigest()
        link = gen.pypi_package_link("pytest-1.8.zip#md5=%s" % md5, md5=False)
        with xom.keyfs.transaction(write=True):
            entry = xom.filestore.maplink(link)
            assert not entry.file_exists()

        master_url = replica_xom.config.master_url
        master_file_path = master_url.joinpath(entry.relpath).url

        # first we create
        with xom.keyfs.transaction(write=True):
            entry.file_set_content(content1)

        # then we delete
        with xom.keyfs.transaction(write=True):
            entry.file_delete()
            entry.delete()
        assert not os.path.exists(entry._filepath)

        # and simulate what the master will respond
        xom.httpget.mockresponse(master_file_path, status_code=410)

        # and then we try to see if we can replicate the create and del changes
        replay(xom, replica_xom)

        with replica_xom.keyfs.transaction():
            r_entry = replica_xom.filestore.get_file_entry(entry.relpath)
            assert not r_entry.file_exists()

    def test_fetch_pypi_nomd5(self, gen, reqmock, xom, replica_xom):
        replay(xom, replica_xom)
        content1 = b'hello'
        link = gen.pypi_package_link("some-1.8.zip", md5=False)
        with xom.keyfs.transaction(write=True):
            entry = xom.filestore.maplink(link)
            assert not entry.file_exists()
            assert not entry.md5

        replay(xom, replica_xom)
        with replica_xom.keyfs.transaction():
            r_entry = replica_xom.filestore.get_file_entry(entry.relpath)
            assert not r_entry.file_exists()
            assert r_entry.meta
            assert not r_entry.md5

        with xom.keyfs.transaction(write=True):
            entry.file_set_content(content1)

        master_url = replica_xom.config.master_url
        master_file_path = master_url.joinpath(entry.relpath).url
        # simulate some 500 master server error
        replica_xom.httpget.mockresponse(master_file_path, status_code=500,
                                         content=b'')
        with pytest.raises(FileReplicationError):
            replay(xom, replica_xom)

        # now get the real thing
        replica_xom.httpget.mockresponse(master_file_path, status_code=200,
                                         content=content1)
        replay(xom, replica_xom)
        with replica_xom.keyfs.transaction():
            assert r_entry.file_exists()
            assert r_entry.file_get_content() == content1


    @pytest.mark.parametrize("code", [200, 500])
    def test_cache_remote_file_fails(self, xom, replica_xom, gen,
                                     monkeypatch, reqmock, code):
        l = []
        monkeypatch.setattr(xom.keyfs.notifier, "wait_tx_serial",
                            lambda x: l.append(x))
        with xom.keyfs.transaction(write=True):
            link = gen.pypi_package_link("pytest-1.8.zip", md5=True)
            entry = xom.filestore.maplink(link)
            assert entry.md5 and not entry.file_exists()
        replay(xom, replica_xom)
        with replica_xom.keyfs.transaction():
            headers={"content-length": "3",
                     "last-modified": "Thu, 25 Nov 2010 20:00:27 GMT",
                     "content-type": "application/zip",
                     "X-DEVPI-SERIAL": "10"}
            entry = replica_xom.filestore.get_file_entry(entry.relpath)
            url = replica_xom.config.master_url.joinpath(entry.relpath).url
            reqmock.mockresponse(url, code=code,
                                 headers=headers, data=b'123')
            if code == 200:
                l = []
                monkeypatch.setattr(replica_xom.keyfs.notifier, "wait_tx_serial",
                    lambda serial: l.append(serial))
            with pytest.raises(entry.BadGateway):
                entry.cache_remote_file_replica()
            if code == 200:
                assert len(l) == 1
                assert l[0] == 10


def test_should_fetch_remote_file():
    from devpi_server.views import should_fetch_remote_file
    from devpi_server.replica import H_REPLICA_FILEREPL
    class Entry:
        eggfragment = "some"
        def file_exists(self):
            return True
    assert should_fetch_remote_file(Entry(), {})
    assert not \
           should_fetch_remote_file(Entry(), {H_REPLICA_FILEREPL: str("YES")})


