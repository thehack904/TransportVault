import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "manifests" / "manifest-schema.json"
SAMPLE_PATH = REPO_ROOT / "samples" / "sample-manifest.json"


class ManifestSchemaTest(unittest.TestCase):
    def setUp(self):
        with SCHEMA_PATH.open(encoding="utf-8") as schema_file:
            self.schema = json.load(schema_file)
        self.validator = Draft202012Validator(self.schema)

    def test_sample_manifest_matches_schema(self):
        with SAMPLE_PATH.open(encoding="utf-8") as sample_file:
            sample_manifest = json.load(sample_file)

        self.validator.validate(sample_manifest)

    def test_supported_image_types_validate(self):
        base_manifest = {
            "image_name": "golden-image",
            "image_version": "1.0.0",
            "created_at": "2026-06-11T18:00:00Z",
            "created_by": "operator",
            "source_hostname": "host01",
            "source_disk": "/dev/sda",
            "source_disk_size": 107374182400,
            "partition_layout": [
                {
                    "partition_number": 1,
                    "filesystem": "ntfs",
                    "size_bytes": 107374182400,
                    "mount_point": None,
                    "bootable": True,
                }
            ],
            "tool_version": "0.1.0",
            "hash_algorithm": "sha256",
            "sha256": "abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789",
            "notes": "Validation fixture",
        }

        for image_type in (
            "rhel-golden-image",
            "windows-golden-image",
            "esxi-golden-image",
        ):
            with self.subTest(image_type=image_type):
                manifest = dict(base_manifest, image_type=image_type)
                self.validator.validate(manifest)


if __name__ == "__main__":
    unittest.main()
