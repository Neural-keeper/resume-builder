# frontend/state/modular_manager.py
from typing import Set, Dict, List, Any
from backend.src.profile_man import ProfileManager


class ModularManagerState:
    """Frontend state orchestrator for active sub-profile selections and overrides."""

    def __init__(self, master_manager):
        self.master_manager = master_manager
        self.active_profile_name: str = "Default"
        self.target_title: str = "Software Engineer"
        self.selected_exp_ids: Set[str] = set()
        self.overrides: Dict[str, str] = {}

        # Default initialization: select all experiences from master data
        self.reset_to_master()

    def reset_to_master(self):
        """Resets selections back to full master data."""
        exps = self.master_manager.data.get("experiences", [])
        self.selected_exp_ids = {exp["id"] for exp in exps if "id" in exp}

    def toggle_experience(self, exp_id: str, is_included: bool):
        """Includes or excludes an experience entry by ID."""
        if is_included:
            self.selected_exp_ids.add(exp_id)
        else:
            self.selected_exp_ids.discard(exp_id)

    def set_override(self, exp_id: str, override_text: str):
        """Sets or updates a local bullet override for a specific experience ID."""
        self.overrides[exp_id] = override_text

    def get_effective_experiences(self) -> List[Dict[str, Any]]:
        """
        Combines master experience data with local sub-profile selection
        and bullet overrides for live rendering or PDF compilation.
        """
        result = []
        for exp in self.master_manager.data.get("experiences", []):
            eid = exp.get("id")
            if eid in self.selected_exp_ids:
                exp_copy = exp.copy()
                
                # Apply local override if user modified the bullets
                if eid in self.overrides:
                    raw_text = self.overrides[eid]
                    exp_copy["bullets"] = [
                        b.strip() for b in raw_text.split("\n") if b.strip()
                    ]
                result.append(exp_copy)
        return result

    def load_preset(self, profile_name: str) -> bool:
        """Loads a sub-profile JSON preset into active UI state."""
        data = ProfileManager.load_profile(profile_name)
        if data:
            self.active_profile_name = profile_name
            self.target_title = data.get("target_title", self.target_title)
            self.selected_exp_ids = set(data.get("selected_exp_ids", []))
            self.overrides = data.get("overrides", {})
            return True
        return False

    def save_preset(self, profile_name: str) -> bool:
        """Persists active state into a named sub-profile JSON file."""
        success = ProfileManager.save_profile(
            name=profile_name,
            target_title=self.target_title,
            selected_ids=self.selected_exp_ids,
            overrides=self.overrides
        )
        if success:
            self.active_profile_name = profile_name
        return success