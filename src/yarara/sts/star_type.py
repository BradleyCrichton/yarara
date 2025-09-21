from __future__ import annotations

from typing import Any, Collection, Dict, Optional, Tuple, TYPE_CHECKING, cast

if TYPE_CHECKING:  # pragma: no cover - typing helper
    from . import StarInfo


_DEFAULT_STAR_INFO_FIXED_VALUES: Dict[str, Any] = {
    "Simbad_name": "-",
    "Sp_type": "G2V",
    "Ra": "00 00 00.0000",
    "Dec": "00 00 00.0000",
    "Pma": 0.0,
    "Pmd": 0.0,
    "Rv_sys": 0.0,
    "Mstar": 1.0,
    "Rstar": 1.0,
    "magU": -26.0,
    "magB": -26.2,
    "magV": -26.8,
    "magR": -26.8,
    "UB": 0.0,
    "BV": 0.6,
    "VR": 0.0,
    "Dist_pc": 0.0,
    "Teff": 5775,
    "Log_g": 4.5,
    "FeH": 0.0,
    "Vsini": 2.0,
    "Vmicro": 1.0,
    "Prot": 25,
    "Pmag": 11,
    "FWHM": 6.0,
    "Contrast": 0.5,
    "CCF_delta": 5,
    "stellar_template": "MARCS_T5750_g4.5",
}


_SPECTRAL_CLASS_DEFAULTS: Dict[str, Dict[str, Any]] = {
    "K": {
        "Mstar": 0.8,
        "Rstar": 0.8,
        "Teff": 4800,
        "Log_g": 4.6,
        "FWHM": 5.5,
        "Contrast": 0.45,
        "stellar_template": "MARCS_T4750_g4.5",
    },
    "M": {
        "Mstar": 0.35,
        "Rstar": 0.35,
        "Teff": 3550,
        "Log_g": 5.0,
        "FWHM": 4.3,
        "Contrast": 0.35,
        "stellar_template": "MARCS_T3500_g5.0",
    },
}


_DEFAULT_MASK_BY_CLASS: Dict[str, str] = {
    "O": "G2",
    "B": "G2",
    "A": "G2",
    "F": "G2",
    "G": "G2",
    "K": "K5",
    "M": "M2",
}


_MASK_FALLBACKS: Dict[str, Tuple[str, ...]] = {
    "G2": ("K5", "M2"),
    "K5": ("G2", "M2"),
    "M2": ("K5", "G2"),
}


def create_default_star_info(starname: str) -> "StarInfo":
    star_info: "StarInfo" = {"Name": starname}
    for key, value in _DEFAULT_STAR_INFO_FIXED_VALUES.items():
        star_info[key] = cast(Dict[str, Any], {"fixed": value})
    return star_info


def _spectral_class_from_type(sp_type: Optional[str]) -> str:
    if not sp_type:
        return "G"
    for char in sp_type.upper():
        if char.isalpha():
            return char
    return "G"


def apply_spectral_type_defaults(star_info: "StarInfo") -> None:
    sp_type_entry = star_info.get("Sp_type")
    sp_type_value: Optional[str]
    if isinstance(sp_type_entry, dict):
        sp_type_value = cast(Optional[str], sp_type_entry.get("fixed"))
    else:
        sp_type_value = cast(Optional[str], sp_type_entry)

    spectral_class = _spectral_class_from_type(sp_type_value)
    overrides = _SPECTRAL_CLASS_DEFAULTS.get(spectral_class)
    if overrides is None:
        return

    for field, value in overrides.items():
        container = cast(Dict[str, Any], star_info.setdefault(field, {}))
        current_value = container.get("fixed")
        default_value = _DEFAULT_STAR_INFO_FIXED_VALUES.get(field)
        if current_value is None or current_value == default_value:
            container["fixed"] = value


def _determine_ccf_mask(desired_mask: str, available_masks: Collection[str]) -> str:
    if desired_mask in available_masks:
        return desired_mask

    for fallback in _MASK_FALLBACKS.get(desired_mask, ()):
        if fallback in available_masks:
            return fallback

    if available_masks:
        return sorted(set(available_masks))[0]

    raise FileNotFoundError("No CCF mask files available")


def select_ccf_mask(sp_type: Optional[str], available_masks: Collection[str]) -> Tuple[str, str]:
    spectral_class = _spectral_class_from_type(sp_type)
    desired_mask = _DEFAULT_MASK_BY_CLASS.get(spectral_class, "G2")
    mask = _determine_ccf_mask(desired_mask, available_masks)
    return mask, desired_mask
