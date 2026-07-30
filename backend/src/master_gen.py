import json
import uuid 
from pathlib import Path
from typing import List, Dict, Optional


class MasterManager:
    def __init__(self, folder_name: str = "master_data"):
        # 1. Path(__file__).resolve() -> absolute path to this script
        # 2. .parent                  -> directory containing this script
        # 3. .parent                  -> the parent directory above that
        script_parent = Path(__file__).resolve().parent.parent

        self.store_dir = script_parent / folder_name
        self.store_dir.mkdir(parents=True, exist_ok=True)

        self.master_file = self.store_dir / "master_resume.json"

        self.data = self._initialize_empty_structure()
        self.load()

    def _initialize_empty_structure(self) -> Dict:
        return {
            "profile": {
                "name": "",
                "email": "",
                "title": "",
                "phone": "",
                "location": "",
                "links": {}
            },
            "summaries": {},       # e.g. "data_engineer": "committed to making data work for you"
            "education": [],       # list of education entries with unique IDs
            "experiences": [],     # list of experience entries with unique IDs
            "certifications": [],  # list of certification entries with unique IDs
            "projects": [],        # list of project entries with unique IDs
            "skills": {}           # e.g. "languages": [], "frameworks": [], etc.
        }

    def load(self) -> Dict:
        if self.master_file.exists():
            with open(self.master_file, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        else:
            self.save()
        return self.data

    def save(self) -> None:
        with open(self.master_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    # --- Profile & Summaries ---
    def update_profile(self, **kwargs) -> None:
        self.data["profile"].update(kwargs)
        self.save()

    def add_summary(self, key: str, text: str) -> None:
        """Adds or updates a job-specific summary profile."""
        self.data["summaries"][key] = text
        self.save()

    def delete_summary(self, key: str) -> bool:
        if key in self.data["summaries"]:
            del self.data["summaries"][key]
            self.save()
            return True
        return False

    # --- Education CRUD ---
    def add_education(
        self,
        degree: str,
        university: str,
        start_year: str,
        end_year: str,
        major: str,
        bullets: Optional[List[str]] = None,
        minor: Optional[str] = None
    ) -> str:
        ed_id = f"ed_{uuid.uuid4().hex[:8]}"
        entry = {
            "id": ed_id,
            "degree": degree,
            "uni": university,
            "start": start_year,
            "end": end_year,
            "major": major,
            "minor": minor,
            "bullets": bullets or []
        }
        self.data["education"].append(entry)
        self.save()
        return ed_id

    def update_education(
        self,
        ed_id: str,
        degree: Optional[str] = None,
        university: Optional[str] = None,
        start_year: Optional[str] = None,
        end_year: Optional[str] = None,
        major: Optional[str] = None,
        minor: Optional[str] = None,
        bullets: Optional[List[str]] = None
    ) -> bool:
        for item in self.data["education"]:
            if item["id"] == ed_id:
                updates = {
                    "degree": degree,
                    "uni": university,
                    "start": start_year,
                    "end": end_year,
                    "major": major,
                    "minor": minor,
                    "bullets": bullets
                }
                changed_fields = {k: v for k, v in updates.items() if v is not None}
                item.update(changed_fields)
                self.save()
                return True
        return False

    def delete_education(self, ed_id: str) -> bool:
        initial_len = len(self.data["education"])
        self.data["education"] = [
            item for item in self.data["education"] if item["id"] != ed_id
        ]
        if len(self.data["education"]) < initial_len:
            self.save()
            return True
        return False

    # --- Work Experience CRUD ---
    def add_work_experience(
        self,
        company: str,
        role: str,
        dates: str,
        bullets: List[str],
        tags: List[str],
        location: str = ""
    ) -> str:
        exp_id = f"exp_{uuid.uuid4().hex[:8]}"
        entry = {
            "id": exp_id,
            "company": company,
            "role": role,
            "dates": dates,
            "location": location,
            "tags": tags,
            "bullets": bullets
        }
        self.data["experiences"].append(entry)
        self.save()
        return exp_id

    def update_work_experience(
        self,
        exp_id: str,
        company: Optional[str] = None,
        role: Optional[str] = None,
        dates: Optional[str] = None,
        bullets: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        location: Optional[str] = None
    ) -> bool:
        for item in self.data["experiences"]:
            if item["id"] == exp_id:
                updates = {
                    "company": company,
                    "role": role,
                    "dates": dates,
                    "location": location,
                    "tags": tags,
                    "bullets": bullets
                }
                changed_fields = {k: v for k, v in updates.items() if v is not None}
                item.update(changed_fields)
                self.save()
                return True
        return False

    def delete_work_experience(self, exp_id: str) -> bool:
        initial_len = len(self.data["experiences"])
        self.data["experiences"] = [
            item for item in self.data["experiences"] if item["id"] != exp_id
        ]
        if len(self.data["experiences"]) < initial_len:
            self.save()
            return True
        return False

    # --- Projects CRUD ---
    def add_project(
        self,
        title: str,
        description: str,
        tags: List[str],
        link: str = "",
        bullets: Optional[List[str]] = None
    ) -> str:
        proj_id = f"proj_{uuid.uuid4().hex[:8]}"
        entry = {
            "id": proj_id,
            "title": title,
            "description": description,
            "tags": tags,
            "link": link,
            "bullets": bullets or []
        }
        self.data["projects"].append(entry)
        self.save()
        return proj_id

    def update_project(
        self,
        proj_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        link: Optional[str] = None,
        bullets: Optional[List[str]] = None,
    ) -> bool:
        for item in self.data["projects"]:
            if item["id"] == proj_id:
                updates = {
                    "title": title,
                    "description": description,
                    "tags": tags,
                    "link": link,
                    "bullets": bullets
                }
                changed_fields = {k: v for k, v in updates.items() if v is not None}
                item.update(changed_fields)
                self.save()
                return True
        return False

    def delete_project(self, proj_id: str) -> bool:
        initial_len = len(self.data["projects"])
        self.data["projects"] = [
            item for item in self.data["projects"] if item["id"] != proj_id
        ]
        if len(self.data["projects"]) < initial_len:
            self.save()
            return True
        return False

    # --- Certifications CRUD ---
    def add_certification(
        self,
        name: str,
        issuer: str,
        date_obtained: str,
        expiration_date: Optional[str] = None,
        credential_id: Optional[str] = None,
        link: Optional[str] = None
    ) -> str:
        cert_id = f"cert_{uuid.uuid4().hex[:8]}"
        entry = {
            "id": cert_id,
            "name": name,
            "issuer": issuer,
            "date": date_obtained,
            "expires": expiration_date,
            "credential_id": credential_id,
            "link": link
        }
        self.data["certifications"].append(entry)
        self.save()
        return cert_id

    def update_certification(
        self,
        cert_id: str,
        name: Optional[str] = None,
        issuer: Optional[str] = None,
        date_obtained: Optional[str] = None,
        expiration_date: Optional[str] = None,
        credential_id: Optional[str] = None,
        link: Optional[str] = None
    ) -> bool:
        for item in self.data["certifications"]:
            if item["id"] == cert_id:
                updates = {
                    "name": name,
                    "issuer": issuer,
                    "date": date_obtained,
                    "expires": expiration_date,
                    "credential_id": credential_id,
                    "link": link
                }
                changed_fields = {k: v for k, v in updates.items() if v is not None}
                item.update(changed_fields)
                self.save()
                return True
        return False

    def delete_certification(self, cert_id: str) -> bool:
        initial_len = len(self.data["certifications"])
        self.data["certifications"] = [
            item for item in self.data["certifications"] if item["id"] != cert_id
        ]
        if len(self.data["certifications"]) < initial_len:
            self.save()
            return True
        return False

    # --- Skills Management ---
    def add_skill(self, category: str, skill_name: str) -> None:
        """Adds a skill under a given category (e.g., 'languages', 'frameworks')."""
        if category not in self.data["skills"]:
            self.data["skills"][category] = []
        
        if skill_name not in self.data["skills"][category]:
            self.data["skills"][category].append(skill_name)
            self.save()

    def remove_skill(self, category: str, skill_name: str) -> bool:
        """Removes a skill from a specific category."""
        if category in self.data["skills"] and skill_name in self.data["skills"][category]:
            self.data["skills"][category].remove(skill_name)
            self.save()
            return True
        return False

    def set_skills_by_category(self, category: str, skills_list: List[str]) -> None:
        """Bulk updates or sets an entire skill category list."""
        self.data["skills"][category] = skills_list
        self.save()

    # --- Generic Tag Search ---
    def get_items_by_tags(self, section: str, tags: List[str], match_all: bool = False) -> List[Dict]:
        """Utility for GUI filtering: Finds experiences or projects matching tags."""
        items = self.data.get(section, [])
        target_tags = set(tag.lower() for tag in tags)
        
        results = []
        for item in items:
            item_tags = set(t.lower() for t in item.get("tags", []))
            if match_all:
                if target_tags.issubset(item_tags):
                    results.append(item)
            else:
                if not target_tags.isdisjoint(item_tags):
                    results.append(item)
        return results