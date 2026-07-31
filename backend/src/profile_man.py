# backend/src/profile_man.py
import json
from pathlib import Path
from typing import Dict, List, Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PROFILES_DIR = PROJECT_ROOT / "backend" / "profiles"
PROFILES_DIR.mkdir(parents=True, exist_ok=True)

class ProfileManager:
    """Manages reading/writing sub-profile preset JSON files independently of master.json."""

    @staticmethod
    def list_profiles() -> List[str]:
        """Returns a list of profile names without the .json extension."""
        return [f.stem for f in PROFILES_DIR.glob("*.json")]

    @staticmethod
    def save_profile(name: str, target_title: str, selected_ids: list, overrides: dict) -> bool:
        """Saves preset choices and bullet overrides to a modular sub-profile JSON file."""
        if not name or not name.strip():
            return False

        # Sanitize filename
        safe_name = "".join([c for c in name if c.isalnum() or c in (" ", "_", "-")]).strip()
        file_path = PROFILES_DIR / f"{safe_name}.json"

        payload = {
            "target_title": target_title,
            "selected_exp_ids": list(selected_ids),
            "overrides": overrides
        }

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
            return True
        except Exception as err:
            print(f"[ProfileManager Save Error]: {err}")
            return False

    @staticmethod
    def load_profile(name: str) -> Dict[str, Any]:
        """Loads a modular sub-profile setup."""
        file_path = PROFILES_DIR / f"{name}.json"
        if file_path.exists():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as err:
                print(f"[ProfileManager Load Error]: {err}")
        return {}

    @staticmethod
    def delete_profile(name: str) -> bool:
        """Deletes a targeted sub-profile JSON file."""
        file_path = PROFILES_DIR / f"{name}.json"
        if file_path.exists():
            try:
                file_path.unlink()
                return True
            except Exception as err:
                print(f"[ProfileManager Delete Error]: {err}")
        return False