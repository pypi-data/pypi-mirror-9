from __future__ import unicode_literals
import sys
import os
import json
import py
import logging
from devpi_common.validation import normalize_name
from devpi_common.metadata import splitbasename, BasenameMeta
from devpi_server.main import fatal
import devpi_server


def do_export(path, xom):
    path = py.path.local(path)
    tw = py.io.TerminalWriter()
    if path.check() and path.listdir():
        fatal("export directory %s must not exist or be empty" % path)
    path.ensure(dir=1)
    tw.line("creating %s" % path)
    dumper = Exporter(tw, xom)
    with xom.keyfs.transaction(write=False):
        dumper.dump_all(path)
    return 0

def do_import(path, xom):
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    path = py.path.local(path)
    tw = py.io.TerminalWriter()

    if not path.check():
        fatal("path for importing not found: %s" %(path))

    with xom.keyfs.transaction():
        if not xom.model.is_empty():
            fatal("serverdir must not contain users or stages: %s" %
                  xom.config.serverdir)
    importer = Importer(tw, xom)
    importer.import_all(path)
    importer.wait_for_events()
    return 0


class Exporter:
    DUMPVERSION = "2"
    def __init__(self, tw, xom):
        self.tw = tw
        self.xom = xom
        self.config = xom.config
        self.filestore = xom.filestore

        self.export = {}
        self.export_users = self.export["users"] = {}
        self.export_indexes = self.export["indexes"] = {}

    def write_file(self, content, dest):
        dest.dirpath().ensure(dir=1)
        with dest.open("wb") as f:
            f.write(content)
        self.tw.line("write file at %s" %(dest.relto(self.basepath),))
        return dest.relto(self.basepath)

    def warn(self, msg):
        self.tw.line(msg, red=True)

    def completed(self, msg):
        self.tw.line("dumped %s" % msg, bold=True)

    def dump_all(self, path):
        self.basepath = path
        self.export["dumpversion"] = self.DUMPVERSION
        self.export["pythonversion"] = list(sys.version_info)
        self.export["devpi_server"] = devpi_server.__version__
        self.export["secret"] = self.config.secret
        self.export["uuid"] = self.xom.config.get_master_uuid()
        for user in self.xom.model.get_userlist():
            userdir = path.join(user.name)
            data = user.get(credentials=True)
            indexes = data.pop("indexes", {})
            self.export_users[user.name] = data
            self.completed("user %r" % user.name)
            for indexname, indexconfig in indexes.items():
                stage = self.xom.model.getstage(user.name, indexname)
                if stage.ixconfig["type"] == "mirror":
                    continue
                indexdir = userdir.ensure(indexname, dir=1)
                IndexDump(self, stage, indexdir).dump()
        self._write_json(path.join("dataindex.json"), self.export)

    def _write_json(self, path, data):
        writedata = json.dumps(data, indent=2)
        path.dirpath().ensure(dir=1)
        self.tw.line("writing %s, length %s" %(path.relto(self.basepath),
                                               len(writedata)))
        path.write(writedata)


class IndexDump:
    def __init__(self, exporter, stage, basedir):
        self.exporter = exporter
        self.stage = stage
        self.basedir = basedir
        self.indexmeta = exporter.export_indexes[stage.name] = {}
        self.indexmeta["projects"] = {}
        self.indexmeta["indexconfig"] = stage.ixconfig
        self.indexmeta["files"] = []

    def dump(self):
        import copy
        for name in self.stage.list_projectnames_perstage():
            data = {}
            versions = self.stage.list_versions_perstage(name)
            for version in versions:
                data[version] = copy.deepcopy(
                    self.stage.get_versiondata_perstage(name, version))
            for val in data.values():
                val.pop("+elinks", None)
            norm_name = normalize_name(name)
            assert norm_name not in self.indexmeta["projects"]
            self.indexmeta["projects"][norm_name] = data

            for version in data:
                vername = data[version]["name"]
                linkstore = self.stage.get_linkstore_perstage(vername, version)
                self.dump_releasefiles(linkstore)
                self.dump_toxresults(linkstore)
                content = self.stage.get_doczip(vername, version)
                if content:
                    self.dump_docfile(vername, version, content)
        self.exporter.completed("index %r" % self.stage.name)

    def dump_releasefiles(self, linkstore):
        for link in linkstore.get_links(rel="releasefile"):
            entry = self.exporter.filestore.get_file_entry(link.entrypath)
            assert entry.file_exists(), entry.relpath
            content = entry.file_get_content()
            relpath = self.exporter.write_file(
                content,
                self.basedir.join(linkstore.projectname, entry.basename))
            self.add_filedesc("releasefile", linkstore.projectname, relpath,
                               version=linkstore.version,
                               entrymapping=entry.meta.copy(),
                               log=link.get_logs())

    def dump_toxresults(self, linkstore):
        for tox_link in linkstore.get_links(rel="toxresult"):
            reflink = linkstore.stage.get_link_from_entrypath(tox_link.for_entrypath)
            relpath = self.exporter.write_file(
                content=tox_link.entry.file_get_content(),
                dest=self.basedir.join(linkstore.projectname, reflink.md5,
                                       tox_link.basename)
            )
            self.add_filedesc(type="toxresult",
                              projectname=linkstore.projectname,
                              relpath=relpath,
                              version=linkstore.version,
                              for_entrypath=reflink.entrypath,
                              log=tox_link.get_logs())

    def add_filedesc(self, type, projectname, relpath, **kw):
        assert self.exporter.basepath.join(relpath).check()
        d = kw.copy()
        d["type"] = type
        d["projectname"] = projectname
        d["relpath"] = relpath
        self.indexmeta["files"].append(d)
        self.exporter.completed("%s: %s " %(type, relpath))

    def dump_docfile(self, projectname, version, content):
        p = self.basedir.join("%s-%s.doc.zip" %(projectname, version))
        with p.open("wb") as f:
            f.write(content)
        relpath = p.relto(self.exporter.basepath)
        self.add_filedesc("doczip", projectname, relpath, version=version)


class Importer:
    def __init__(self, tw, xom):
        self.tw = tw
        self.xom = xom
        self.filestore = xom.filestore
        self.tw = tw

    def read_json(self, path):
        self.tw.line("reading json: %s" %(path,))
        return json.loads(path.read())

    def warn(self, msg):
        self.tw.line(msg, red=True)

    def import_all(self, path):
        self.import_rootdir = path
        self.import_data = self.read_json(path.join("dataindex.json"))
        self.dumpversion = self.import_data["dumpversion"]
        if self.dumpversion not in ("1", "2"):
            fatal("incompatible dumpversion: %r" %(self.dumpversion,))
        uuid = self.import_data.get("uuid")
        if uuid is not None:
            self.xom.config.set_uuid(uuid)
        self.import_users = self.import_data["users"]
        self.import_indexes = self.import_data["indexes"]
        self.xom.config.secret = secret = self.import_data["secret"]
        self.xom.config.secretfile.write(secret)

        # first create all users
        for username, userconfig in self.import_users.items():
            with self.xom.keyfs.transaction(write=True):
                if username == "root":
                    user = self.xom.model.get_user(username)
                else:
                    user = self.xom.model.create_user(username, password="")
                user._set(userconfig)

        # memorize index inheritance structure
        tree = IndexTree()
        tree.add("root/pypi")  # a root index
        for stagename, import_index in self.import_indexes.items():
            bases = import_index["indexconfig"].get("bases")
            tree.add(stagename, bases)

        # create stages in inheritance/root-first order
        stages = []
        for stagename in tree.iternames():
            with self.xom.keyfs.transaction(write=True):
                if stagename == "root/pypi":
                    assert self.xom.model.getstage(stagename)
                    continue
                import_index = self.import_indexes[stagename]
                indexconfig = import_index["indexconfig"]
                user, index = stagename.split("/")
                user = self.xom.model.get_user(user)
                stage = user.create_stage(index, **indexconfig)
            stages.append(stage)
        del tree

        # create projects and releasefiles for each index
        for stage in stages:
            assert stage.name != "root/pypi"
            import_index = self.import_indexes[stage.name]
            projects = import_index["projects"]
            #normalized = self.normalize_index_projects(projects)
            for project, versions in projects.items():
                for version, versiondata in versions.items():
                    with self.xom.keyfs.transaction(write=True):
                        assert "+elinks" not in versiondata
                        versiondata.pop('+doczip', None)
                        versiondata.pop(':action', None)
                        assert not any(True for x in versiondata if x.startswith('+'))
                        if not versiondata.get("version"):
                            name = versiondata["name"]
                            self.warn("%r: version metadata has no explicit "
                                      "version, setting derived %r" %
                                      (name, version))
                            versiondata["version"] = version
                        stage.set_versiondata(versiondata)

            # import release files
            for filedesc in import_index["files"]:
                with self.xom.keyfs.transaction(write=True):
                    self.import_filedesc(stage, filedesc)

    def wait_for_events(self):
        latest_serial = self.xom.keyfs.get_next_serial() - 1
        self.tw.line("waiting for events until latest_serial %s"
                     % latest_serial)
        self.xom.keyfs.notifier.wait_event_serial(latest_serial)
        self.tw.line("importing finished")

    def import_filedesc(self, stage, filedesc):
        assert stage.ixconfig["type"] != "mirror"
        rel = filedesc["relpath"]
        projectname = filedesc["projectname"]
        p = self.import_rootdir.join(rel)
        assert p.check(), p
        if filedesc["type"] == "releasefile":
            mapping = filedesc["entrymapping"]
            if self.dumpversion == "1":
                # previous versions would not add a version attribute
                version = BasenameMeta(p.basename).version
            else:
                version = filedesc["version"]

            link = stage.store_releasefile(projectname, version,
                                           p.basename, p.read("rb"),
                                           last_modified=mapping["last_modified"])
            assert link.entry.md5 == mapping["md5"]
            self.import_pre2_toxresults(stage, link.entry)
        elif filedesc["type"] == "doczip":
            basename = os.path.basename(rel)
            name, version, suffix = splitbasename(basename)
            link = stage.store_doczip(name, version, p.read("rb"))
        elif filedesc["type"] == "toxresult":
            linkstore = stage.get_linkstore_perstage(filedesc["projectname"],
                                           filedesc["version"])
            link, = linkstore.get_links(entrypath=filedesc["for_entrypath"])
            link = stage.store_toxresult(link, json.loads(p.read("rb").decode("utf8")))
        else:
            fatal("unknown file type: %s" % (type,))
        history_log = filedesc.get('log')
        if history_log is None:
            link.add_log('upload', '<import>', dst=stage.name)
        else:
            link.add_logs(history_log)

    def import_pre2_toxresults(self, stage, releasefile_entry):
        # pre 2.0 export structure (called "attachments")
        md5 = releasefile_entry.md5
        type_path = self.import_rootdir.join("attach", md5, "toxresult")
        if not type_path.exists():
            return
        releasefile_link = stage.get_link_from_entrypath(
                entrypath=releasefile_entry.relpath)
        type = type_path.basename
        for i in range(len(type_path.listdir())):
            attachment_data = type_path.join(str(i)).read(mode="rb")
            attachment_data = attachment_data.decode('utf-8')
            toxresultdata = json.loads(attachment_data)
            self.tw.line("importing pre-2.0 test  results %s/%s" %(md5, type))
            tox_link = stage.store_toxresult(releasefile_link, toxresultdata)
            tox_link.add_log('upload', '<import>')
            self.tw.line("imported %s" % tox_link.entrypath)


class IndexTree:
    """ sort index inheritance structure to that we can
    create in root->child order.
    """
    def __init__(self):
        self.name2children = {}
        self.name2bases = {}

    def add(self, name, bases=None):
        self.name2bases[name] = bases or []
        if not bases:
            self.name2children.setdefault(None, []).append(name)
        else:
            for base in bases:
                children = self.name2children.setdefault(base, [])
                children.append(name)

    def iternames(self):
        pending = [None]
        created = set()
        while pending:
            name = pending.pop(0)
            for base in self.name2bases.get(name, []):
                if base not in created:
                    pending.append(name)
                    break
            else:
                if name not in created:
                    if name:
                        yield name
                    created.add(name)
                    for child in self.name2children.get(name, []):
                        if child not in created:
                            pending.append(child)

