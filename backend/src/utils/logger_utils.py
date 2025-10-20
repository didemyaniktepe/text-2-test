import os
import json
from datetime import datetime
from pathlib import Path

class TestLogger:
    def __init__(self, original_scenario: str = "", folder_name: str = ""):
        self.test_name = original_scenario.replace(" ", "_")[:30]
        self.folder_name = folder_name
        self.log_dir = self._create_log_directory()
        self.log_file = self._create_log_file()
        self.steps = []
        self.test_data = {
            "test_name": self.test_name,
            "original_scenario": original_scenario,
            "remaining_scenario": original_scenario,
            "completed_steps": [],
            "failed_attempts": [],
            "steps": self.steps
        }
        
    def _create_log_directory(self) -> Path:
        if self.folder_name:
            log_dir = Path("logs") / self.folder_name
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_dir = Path("logs") / f"test_{self.test_name}_{timestamp}"
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir
        
    def _create_log_file(self) -> Path:
        return self.log_dir / "test_execution.log"
        
    def log_step(self, step_number: int, prompt: str, response: str, action: dict, remaining_scenario: str = None):
        step_log = {
            "step_number": step_number,
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "ai_response": response,
            "action": action,
            "remaining_scenario": remaining_scenario,
            "metrics": {
                "is_expected_step": True,
                "selector_attempts": len(self.test_data["failed_attempts"]) + 1 if action["type"] == "selector" else 0,
                "execution_success": action.get("status") == "success" if action["type"] == "action" else None
            }
        }
        
        self.steps.append(step_log)
        
        if remaining_scenario is not None:
            self.test_data["remaining_scenario"] = remaining_scenario
            
        if action["type"] == "action" and action.get("status") == "success":
            self.test_data["completed_steps"].append(prompt)
            
        self._update_log_file()
            
    def save_screenshot(self, screenshot_path: str, step_number: int):
        if not screenshot_path:
            return
            
        screenshot_name = f"step_{step_number}.png"
        new_path = self.log_dir / screenshot_name
        
        if os.path.exists(screenshot_path):
            try:
                import shutil
                shutil.copy2(screenshot_path, new_path)
                print(f"Screenshot saved to {new_path}")
            except Exception as e:
                print(f"Error copying screenshot: {str(e)}")
                try:
                    os.rename(screenshot_path, new_path)
                except Exception as e2:
                    print(f"Error renaming screenshot: {str(e2)}")
        else:
            print(f"Screenshot not found at path: {screenshot_path}")
            
        if self.steps and len(self.steps) >= step_number:
            self.steps[step_number-1]["screenshot"] = str(new_path)
            self._update_log_file()
            
    def _update_log_file(self):
        with open(self.log_file, "w", encoding="utf-8") as f:
            json.dump(self.test_data, f, indent=2, ensure_ascii=False, default=str)
            
    def add_failed_attempt(self, attempt_info: dict):
        failed_attempt = {
            "selector": attempt_info.get("selector", "unknown"),
            "action_type": attempt_info.get("action_type", "")
        }
        self.test_data["failed_attempts"].append(failed_attempt)
        
    def add_generated_test(self, test_code: str, scenario: str, url: str):
        self.test_data["generated_test"] = {
            "code": test_code,
            "scenario": scenario,
            "url": url,
            "timestamp": datetime.now().isoformat()
        }
        self._update_log_file()

    def finalize_test(self, success: bool = None):
        self.test_data["end_time"] = datetime.now().isoformat()
        self.test_data["success"] = success if success is not None else len(self.test_data["completed_steps"]) > 0
        self.test_data["metrics"] = {
            "total_steps": len(self.steps) // 2,
            "completed_steps": len(self.test_data["completed_steps"]),
            "remaining_scenario": self.test_data["remaining_scenario"],
            "total_selector_attempts": sum(len(self.test_data["failed_attempts"]) + 1 for s in self.steps if s["action"]["type"] == "selector"),
            "successful_selectors": sum(1 for s in self.steps if s["action"]["type"] == "action" and s["action"].get("status") == "success")
        }
        self._update_log_file()
