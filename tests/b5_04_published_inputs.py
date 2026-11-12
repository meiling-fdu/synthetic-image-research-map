"""Immutable B5-03 test inputs. Build only in a disposable test directory."""

from dataclasses import dataclass
import hashlib
from pathlib import Path, PurePosixPath
import subprocess
import tarfile

from scripts.restore_historical_test_fixtures import restore


BASE = "db1abff06d9ee077ae62421079059ee3af95607f"
TREE = "25b43a16a801260eadfb08d8f64336d8d04fb642"
TREE_INVENTORY_SHA256 = "70f8f55525730d169ccf946ffb5388cc289d366a27ae5154e120541ccef8bd51"
LOGICAL_INDEX_SHA256 = "8bddf4b3f7a17fa48b1058df7ae60f8e40a73a3649ebcf0b3c6ed138d35576ca"
PRIVATE_CONFIG = b"[core]\nrepositoryformatversion = 0\nbare = false\nlogallrefupdates = false\n"


def git(root, *args):
    return subprocess.check_output(["git", "--no-optional-locks", *args], cwd=root)


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def authorize():
    assert (BASE, TREE, TREE_INVENTORY_SHA256, LOGICAL_INDEX_SHA256, PRIVATE_CONFIG) == (
        "db1abff06d9ee077ae62421079059ee3af95607f",
        "25b43a16a801260eadfb08d8f64336d8d04fb642",
        "70f8f55525730d169ccf946ffb5388cc289d366a27ae5154e120541ccef8bd51",
        "8bddf4b3f7a17fa48b1058df7ae60f8e40a73a3649ebcf0b3c6ed138d35576ca",
        b"[core]\nrepositoryformatversion = 0\nbare = false\nlogallrefupdates = false\n",
    ), "Unreviewed B5-03 snapshot authorization"


def tracked_inventory(root):
    authorize()
    assert git(root, "rev-parse", BASE + "^{tree}").decode().strip() == TREE
    raw = git(root, "ls-tree", "-r", "--full-tree", "-z", BASE)
    assert sha256(raw) == TREE_INVENTORY_SHA256, "Changed B5-03 tree inventory"
    entries = {}
    for item in raw.rstrip(b"\0").split(b"\0"):
        metadata, path = item.decode().split("\t", 1)
        mode, kind, object_id = metadata.split()
        relative = PurePosixPath(path)
        assert not relative.is_absolute() and ".." not in relative.parts
        assert mode == "100644" and kind == "blob" and path not in entries
        entries[path] = object_id
    assert len(entries) == 4864
    return entries


def blob_id(raw):
    header = f"blob {len(raw)}\0".encode()
    return hashlib.sha1(header + raw).hexdigest()


def object_reader(source):
    common = git(source, "rev-parse", "--path-format=absolute", "--git-common-dir")
    return (str(Path(common.decode().strip()) / "objects") + "\n").encode()


@dataclass(frozen=True)
class PublishedInputs:
    root: Path
    source: Path
    object_reader: bytes
    index_sha256: str

    def verify(self):
        authorize()
        assert not self.root.is_relative_to(self.source)
        metadata = self.root / ".git"
        assert (metadata / "HEAD").read_bytes() == (BASE + "\n").encode()
        assert (metadata / "config").read_bytes() == PRIVATE_CONFIG
        assert (metadata / "objects/info/alternates").read_bytes() == self.object_reader == object_reader(self.source)
        assert sha256((metadata / "index").read_bytes()) == self.index_sha256
        assert sha256(git(self.root, "ls-files", "--stage", "-z")) == LOGICAL_INDEX_SHA256
        expected_metadata = {"HEAD", "config", "index", "objects/info/alternates"}
        actual_metadata = {str(p.relative_to(metadata)) for p in metadata.rglob("*") if p.is_file()}
        assert actual_metadata == expected_metadata, "Undeclared historical Git metadata"
        tracked = tracked_inventory(self.source)
        for relative, expected in tracked.items():
            path = self.root / relative
            assert path.is_file() and not path.is_symlink()
            assert blob_id(path.read_bytes()) == expected, "Changed B5-03 snapshot blob: " + relative
        inputs = restore(self.root, check=True)
        assert inputs["verified_inputs"] == 117
        expected_paths = set(tracked) | set(inputs["sha256"])
        actual_paths = {
            p.relative_to(self.root).as_posix()
            for p in self.root.rglob("*")
            if not p.relative_to(self.root).parts[0] == ".git" and (p.is_file() or p.is_symlink())
        }
        assert actual_paths == expected_paths, "Undeclared B5-03 snapshot input"
        return True


def build_published_inputs(source, destination):
    source, destination = Path(source).resolve(), Path(destination).resolve()
    assert not destination.is_relative_to(source), "Historical inputs belong outside the active checkout"
    tracked = tracked_inventory(source)
    destination.mkdir()
    command = ["git", "--no-optional-locks", "archive", "--format=tar", BASE]
    with subprocess.Popen(command, cwd=source, stdout=subprocess.PIPE) as process:
        assert process.stdout is not None
        with tarfile.open(fileobj=process.stdout, mode="r|") as archive:
            for entry in archive:
                target = destination / entry.name
                assert target.resolve().is_relative_to(destination)
                assert entry.isdir() or entry.isfile() and entry.name in tracked
                archive.extract(entry, destination, filter="data")
        assert process.wait() == 0

    metadata = destination / ".git"
    (metadata / "objects/info").mkdir(parents=True)
    (metadata / "refs").mkdir()
    alternates = object_reader(source)
    (metadata / "objects/info/alternates").write_bytes(alternates)
    (metadata / "HEAD").write_bytes((BASE + "\n").encode())
    (metadata / "config").write_bytes(PRIVATE_CONFIG)
    subprocess.run(["git", "--no-optional-locks", "read-tree", BASE], cwd=destination, check=True)
    restored = restore(destination)
    assert restored["verified_inputs"] == restored["created"] == 117
    view = PublishedInputs(destination, source, alternates, sha256((metadata / "index").read_bytes()))
    assert view.verify()
    return view
