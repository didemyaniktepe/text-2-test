#!/usr/bin/env python3

import json
import os
import requests
import argparse
from pathlib import Path
from typing import List, Dict, Any


class ScenarioRerunTool:
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        
    def extract_scenarios_from_logs(self, logs_directory: str) -> List[Dict[str, Any]]:
        scenarios = []
        logs_path = Path(logs_directory)
        
        if not logs_path.exists():
            print(f"Logs directory not found: {logs_directory}")
            return scenarios
            
        for log_file in logs_path.rglob("test_execution.log"):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
                    
                scenario_info = {
                    "original_scenario": log_data.get("original_scenario"),
                    "test_name": log_data.get("test_name"),
                    "url": log_data.get("generated_test", {}).get("url"),
                    "success": log_data.get("success"),
                    "log_path": str(log_file),
                    "folder_name": log_file.parent.name
                }
                
                if scenario_info["original_scenario"]:
                    scenarios.append(scenario_info)
                    
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Error reading {log_file}: {e}")
                continue
                
        return scenarios
    
    def rerun_scenario(self, scenario: str, url: str, folder_name: str = "") -> Dict[str, Any]:
        endpoint = f"{self.api_base_url}/api/tests/generate"
        
        payload = {
            "scenario": scenario,
            "url": url,
            "folder_name": folder_name
        }
        
        try:
            response = requests.post(endpoint, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "status_code": getattr(e.response, 'status_code', None)}
    
    def rerun_scenarios_from_folder(self, folder_path: str, filter_successful: bool = True, default_url: str = None, folder_name: str = None) -> List[Dict[str, Any]]:
        scenarios = self.extract_scenarios_from_logs(folder_path)
        
        if filter_successful:
            scenarios = [s for s in scenarios if s.get("success") is True]
        
        if not folder_name:
            folder_name = Path(folder_path).name
        
        results = []
        for scenario_info in scenarios:
            print(f"Rerunning: {scenario_info['test_name']}")
            print(f"Scenario: {scenario_info['original_scenario']}")
            scenario_folder_name = scenario_info["folder_name"]
            print(f"Using folder name: {scenario_folder_name}")
            
            url = "http://localhost:4000/login"
            
            result = self.rerun_scenario(
                scenario_info["original_scenario"],
                url,
                scenario_folder_name
            )
            
            results.append({
                "original_info": scenario_info,
                "rerun_result": result
            })
            
            print(f"Result: {result.get('test_id', result.get('error', 'Unknown'))}")
            print("-" * 50)
        
        return results
    
    def list_scenarios(self, folder_path: str) -> None:
        scenarios = self.extract_scenarios_from_logs(folder_path)
        
        print(f"Found {len(scenarios)} scenarios:")
        print("=" * 80)
        
        for i, scenario in enumerate(scenarios, 1):
            status = "SUCCESS" if scenario.get("success") else "FAILED"
            print(f"{i}. {scenario['test_name']} - {status}")
            print(f"   Scenario: {scenario['original_scenario']}")
            print(f"   URL: {scenario.get('url', 'Not specified')}")
            print(f"   Folder: {scenario['folder_name']}")
            print()


def main():
    parser = argparse.ArgumentParser(description="Rerun scenarios from log files")
    parser.add_argument("--logs-dir", required=True, help="Path to logs directory")
    parser.add_argument("--api-url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--list-only", action="store_true", help="Only list scenarios, don't rerun")
    parser.add_argument("--include-failed", action="store_true", help="Include failed scenarios in rerun")
    parser.add_argument("--folder", help="Specific folder to process (e.g., 'change_role')")
    parser.add_argument("--default-url", help="Default URL to use if not found in logs (e.g., 'http://localhost:8001/admin')")
    parser.add_argument("--folder-name", help="Folder name to use for log organization (e.g., 'ToDo', 'BLUEDT')")
    
    args = parser.parse_args()
    
    tool = ScenarioRerunTool(args.api_url)
    
    if args.folder:
        logs_path = os.path.join(args.logs_dir, args.folder)
    else:
        logs_path = args.logs_dir
    
    if args.list_only:
        tool.list_scenarios(logs_path)
    else:
        results = tool.rerun_scenarios_from_folder(
            logs_path, 
            filter_successful=not args.include_failed,
            default_url=args.default_url,
            folder_name=args.folder_name
        )
        
        print(f"\nCompleted rerunning {len(results)} scenarios")
        
        successful = sum(1 for r in results if "test_id" in r["rerun_result"])
        failed = len(results) - successful
        
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")


if __name__ == "__main__":
    main()
