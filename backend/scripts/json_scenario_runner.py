#!/usr/bin/env python3

import json
import os
import requests
import argparse
from pathlib import Path
from typing import List, Dict, Any
import time


class JsonScenarioRunner:
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        
    def load_scenarios_from_json(self, json_file_path: str) -> List[Dict[str, Any]]:
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                scenarios = json.load(f)
            return scenarios
        except FileNotFoundError:
            print(f"JSON file not found: {json_file_path}")
            return []
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON file: {e}")
            return []
    
    def load_scenarios_from_string(self, json_string: str) -> List[Dict[str, Any]]:
        try:
            scenarios = json.loads(json_string)
            return scenarios
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON string: {e}")
            return []
    
    def run_scenario(self, scenario: str, url: str, folder_name: str = "") -> Dict[str, Any]:
        endpoint = f"{self.api_base_url}/api/tests/generate"
        
        payload = {
            "scenario": scenario,
            "url": url,
            "folder_name": "saucedemo/" + "deepseek/" + folder_name
        }
        
        try:
            response = requests.post(endpoint, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "status_code": getattr(e.response, 'status_code', None)}
    
    def run_scenarios(self, scenarios: List[Dict[str, Any]], delay_seconds: float = 1.0) -> List[Dict[str, Any]]:
        results = []
        total = len(scenarios)
        
        print(f"Running {total} scenarios...")
        print("=" * 80)
        
        for i, scenario_data in enumerate(scenarios, 1):
            scenario = scenario_data.get("scenario", "")
            url = scenario_data.get("url", "")
            folder_name = scenario_data.get("folder_name", f"scenario_{i}")
            
            print(f"[{i}/{total}] Running: {folder_name}")
            print(f"Scenario: {scenario[:100]}..." if len(scenario) > 100 else f"Scenario: {scenario}")
            print(f"URL: {url}")
            print(f"Folder: {folder_name}")
            
            result = self.run_scenario(scenario, url, folder_name)
            
            results.append({
                "original_data": scenario_data,
                "result": result,
                "index": i
            })
            
            if "test_id" in result:
                print(f"Success - Test ID: {result['test_id']}")
            else:
                print(f"Failed - Error: {result.get('error', 'Unknown error')}")
            
            print("-" * 50)
            
            if delay_seconds > 0 and i < total:
                time.sleep(delay_seconds)
        
        return results
    
    def save_results(self, results: List[Dict[str, Any]], output_file: str) -> None:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"Results saved to: {output_file}")
        except Exception as e:
            print(f"Error saving results: {e}")
    
    def print_summary(self, results: List[Dict[str, Any]]) -> None:
        total = len(results)
        successful = sum(1 for r in results if "test_id" in r["result"])
        failed = total - successful
        
        print("\n" + "=" * 80)
        print("EXECUTION SUMMARY")
        print("=" * 80)
        print(f"Total scenarios: {total}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Success rate: {(successful/total*100):.1f}%" if total > 0 else "N/A")
        
        if failed > 0:
            print("\nFailed scenarios:")
            for r in results:
                if "test_id" not in r["result"]:
                    folder_name = r['original_data'].get('folder_name', f'scenario_{r["index"]}')
                    print(f"- {folder_name}: {r['result'].get('error', 'Unknown error')}")


def main():
    parser = argparse.ArgumentParser(description="Run scenarios from JSON file or string")
    parser.add_argument("--json-file", help="Path to JSON file containing scenarios")
    parser.add_argument("--json-string", help="JSON string containing scenarios")
    parser.add_argument("--api-url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between scenarios in seconds")
    parser.add_argument("--output", help="Output file to save results")
    parser.add_argument("--dry-run", action="store_true", help="Only validate JSON, don't run scenarios")
    
    args = parser.parse_args()
    
    if not args.json_file and not args.json_string:
        parser.error("Either --json-file or --json-string must be provided")
    
    runner = JsonScenarioRunner(args.api_url)
    scenarios = []
    
    if args.json_file:
        scenarios = runner.load_scenarios_from_json(args.json_file)
    elif args.json_string:
        scenarios = runner.load_scenarios_from_string(args.json_string)
    
    if not scenarios:
        print("No scenarios found or error loading scenarios")
        return
    
    print(f"Loaded {len(scenarios)} scenarios")
    
    if args.dry_run:
        print("Dry run mode - validating scenarios only:")
        for i, scenario in enumerate(scenarios, 1):
            required_fields = ["scenario", "url", "folder_name"]
            missing_fields = [field for field in required_fields if field not in scenario]
            if missing_fields:
                print(f"Scenario {i}: Missing fields {missing_fields}")
            else:
                print(f"Scenario {i}: Valid")
        return
    
    results = runner.run_scenarios(scenarios, args.delay)
    runner.print_summary(results)
    
    if args.output:
        runner.save_results(results, args.output)


if __name__ == "__main__":
    main()
