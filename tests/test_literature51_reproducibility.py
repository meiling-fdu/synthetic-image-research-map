"""Negative checks for the workspace/checkout boundary and exact receipt bytes."""
import gzip
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts import literature51_reproducibility as replay


class Literature51ReproducibilityTests(unittest.TestCase):
    def test_partial_workspace_fails(self):
        with tempfile.TemporaryDirectory() as name:
            root=Path(name);(root/'one').write_bytes(b'one')
            expected={'one':hashlib.sha256(b'one').hexdigest(),'two':hashlib.sha256(b'two').hexdigest()}
            with self.assertRaisesRegex(AssertionError,'Incomplete'):
                replay.verify_workspace_files(root,expected)

    def test_changed_local_file_fails(self):
        with tempfile.TemporaryDirectory() as name:
            root=Path(name);(root/'one').write_bytes(b'changed')
            with self.assertRaisesRegex(AssertionError,'changed'):
                replay.verify_workspace_files(root,{'one':hashlib.sha256(b'one').hexdigest()})

    def test_strict_original_workspace_cannot_be_absent(self):
        with tempfile.TemporaryDirectory() as name:
            with self.assertRaisesRegex(AssertionError,'Incomplete'):
                replay.verify_workspace_files(Path(name),{'one':'hash'},require_present=True)

    def test_complete_workspace_is_hash_verified(self):
        with tempfile.TemporaryDirectory() as name:
            root=Path(name);(root/'one').write_bytes(b'one')
            self.assertEqual(replay.verify_workspace_files(root,{'one':hashlib.sha256(b'one').hexdigest()},require_present=True),
                             'original_workspace_hashes_verified')

    def test_archived_receipt_must_reproduce_exact_original_bytes(self):
        with tempfile.TemporaryDirectory() as name:
            root=Path(name);content=b'<failure>preserve trailing whitespace  \n</failure>\n'
            archive=root/'receipt.xml.gz';archive.write_bytes(gzip.compress(content,mtime=0))
            path=root/replay.PREFLIGHT;path.parent.mkdir(parents=True)
            path.write_text(json.dumps({'lossless_archives':{'receipt.xml':{
                'path':'receipt.xml.gz','original_sha256':hashlib.sha256(content).hexdigest()}}}))
            self.assertEqual(replay.preserved_bytes(root,'receipt.xml'),content)
            archive.write_bytes(gzip.compress(b'changed failure text',mtime=0))
            with self.assertRaises(AssertionError):
                replay.preserved_bytes(root,'receipt.xml')

    def test_non_archived_missing_dependency_fails(self):
        with tempfile.TemporaryDirectory() as name:
            root=Path(name);path=root/replay.PREFLIGHT;path.parent.mkdir(parents=True)
            path.write_text(json.dumps({'lossless_archives':{}}))
            with self.assertRaises(FileNotFoundError):
                replay.preserved_bytes(root,'missing-primary.json')

    def test_materializer_never_overwrites_different_existing_input(self):
        with tempfile.TemporaryDirectory() as name:
            root=Path(name);archive=root/'input.csv.gz';content=b'column\nvalue\n'
            archive.write_bytes(gzip.compress(content,mtime=0))
            path=root/replay.PREFLIGHT;path.parent.mkdir(parents=True)
            path.write_text(json.dumps({'reproduction_inputs':{'data/processed/input.csv':{
                'path':'input.csv.gz','original_sha256':hashlib.sha256(content).hexdigest()}}}))
            replay.materialize_export_inputs(root)
            target=root/'data/processed/input.csv';self.assertEqual(target.read_bytes(),content)
            target.write_bytes(b'local edit')
            with self.assertRaises(AssertionError):
                replay.materialize_export_inputs(root)
            self.assertEqual(target.read_bytes(),b'local edit')

    def test_corrupt_materialization_archive_fails_before_writing(self):
        with tempfile.TemporaryDirectory() as name:
            root=Path(name);(root/'input.csv.gz').write_bytes(gzip.compress(b'wrong',mtime=0))
            path=root/replay.PREFLIGHT;path.parent.mkdir(parents=True)
            path.write_text(json.dumps({'reproduction_inputs':{'data/processed/input.csv':{
                'path':'input.csv.gz','original_sha256':hashlib.sha256(b'expected').hexdigest()}}}))
            with self.assertRaises(AssertionError):
                replay.materialize_export_inputs(root)
            self.assertFalse((root/'data/processed/input.csv').exists())


if __name__=='__main__':
    unittest.main()
