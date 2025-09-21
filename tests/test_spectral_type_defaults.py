import importlib.util
import sys
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).resolve().parents[1] / "src" / "yarara" / "sts" / "star_type.py"
spec = importlib.util.spec_from_file_location("yarara_star_type", MODULE_PATH)
star_type = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = star_type
assert spec.loader is not None
spec.loader.exec_module(star_type)

apply_spectral_type_defaults = star_type.apply_spectral_type_defaults
create_default_star_info = star_type.create_default_star_info
select_ccf_mask = star_type.select_ccf_mask


def test_apply_defaults_for_m_dwarf_updates_expected_fields():
    star_info = create_default_star_info("TestStar")
    star_info["Sp_type"]["fixed"] = "M4V"

    apply_spectral_type_defaults(star_info)

    assert star_info["Teff"]["fixed"] == 3550
    assert star_info["Log_g"]["fixed"] == 5.0
    assert star_info["Mstar"]["fixed"] == 0.35
    assert star_info["Rstar"]["fixed"] == 0.35
    assert star_info["FWHM"]["fixed"] == 4.3
    assert star_info["Contrast"]["fixed"] == 0.35
    assert star_info["stellar_template"]["fixed"] == "MARCS_T3500_g5.0"


def test_apply_defaults_keeps_user_values():
    star_info = create_default_star_info("AnotherStar")
    star_info["Sp_type"]["fixed"] = "M2V"
    star_info["FWHM"]["fixed"] = 5.1

    apply_spectral_type_defaults(star_info)

    assert star_info["FWHM"]["fixed"] == 5.1


def test_select_mask_prefers_available_m_dwarf_mask():
    mask, desired = select_ccf_mask("M3V", {"M2", "K5", "G2"})

    assert desired == "M2"
    assert mask == "M2"


def test_select_mask_falls_back_to_k_when_m_mask_missing():
    mask, desired = select_ccf_mask("M5V", {"K5", "G2"})

    assert desired == "M2"
    assert mask == "K5"


def test_select_mask_requires_at_least_one_mask():
    with pytest.raises(FileNotFoundError):
        select_ccf_mask("M1V", set())
