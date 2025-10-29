#!/usr/bin/env python3
"""Test that demonstrates the system requirements import fix works regardless of file loading order."""

import sys
import os
import pytest

# Add parent directory to path so we can import loader
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from loader import ReleaseNotes


def create_test_data_bad_order():
    """Create test data with a deliberately bad loading order.
    
    Files that import system_requirements are loaded BEFORE the files
    that actually define them. This would have caused a KeyError with
    the old code.
    """
    notelist = {}
    
    # Load importers FIRST (bad order)
    notelist["144.0.1"] = {
        "release": {
            "release_date": "2025-10-16",
            "import_system_requirements": "140.0esr",
        },
        "notes": [{"note": "Minor fix", "tag": "fixed"}]
    }
    
    notelist["144.0"] = {
        "release": {
            "release_date": "2025-10-14",
            "import_system_requirements": "140.0esr",
        },
        "notes": [{"note": "New features", "tag": "new"}]
    }
    
    # Load the base version LAST (this simulates os.listdir() bad order)
    notelist["140.0esr"] = {
        "release": {
            "release_date": "2025-07-07",
            "system_requirements": "Windows 10 or later, macOS 10.15 or later"
        },
        "notes": [{"note": "Major release", "tag": "new"}]
    }
    
    return notelist


def test_bad_loading_order():
    """Test that the fix handles files loaded in any order."""
    # Create instance without calling __init__ to avoid loading all YAML files
    rn = ReleaseNotes.__new__(ReleaseNotes)
    test_data = create_test_data_bad_order()
    
    result = rn.organize(test_data)
    
    # Verify all versions got the correct system requirements
    base_sysreq = result["140.0esr"]["release"]["system_requirements"]
    v144_sysreq = result["144.0"]["release"]["system_requirements"]
    v144_1_sysreq = result["144.0.1"]["release"]["system_requirements"]
    
    assert v144_sysreq == base_sysreq
    assert v144_1_sysreq == base_sysreq
    assert base_sysreq == "Windows 10 or later, macOS 10.15 or later"


def test_missing_version_error():
    """Test that referencing a non-existent version throws a helpful error."""
    rn = ReleaseNotes.__new__(ReleaseNotes)
    test_data = {
        "144.0": {
            "release": {
                "release_date": "2025-10-14",
                "import_system_requirements": "999.0esr",  # Doesn't exist!
            },
            "notes": [{"note": "Test", "tag": "new"}]
        }
    }
    
    with pytest.raises(KeyError) as exc_info:
        rn.organize(test_data)
    
    error_msg = str(exc_info.value)
    assert "999.0esr" in error_msg
    assert "not found" in error_msg


def test_missing_sysreq_error():
    """Test that importing from a version without system_requirements throws a helpful error."""
    rn = ReleaseNotes.__new__(ReleaseNotes)
    test_data = {
        "145.0": {
            "release": {
                "release_date": "2025-11-01",
                "import_system_requirements": "144.0",
            },
            "notes": [{"note": "Test", "tag": "new"}]
        },
        "144.0": {
            "release": {
                "release_date": "2025-10-14",
                "import_system_requirements": "140.0esr",  # Also imports, no actual sysreq
            },
            "notes": [{"note": "Test", "tag": "new"}]
        }
    }
    
    with pytest.raises(ValueError) as exc_info:
        rn.organize(test_data)
    
    error_msg = str(exc_info.value)
    assert "144.0" in error_msg
    assert "doesn't have system_requirements" in error_msg
