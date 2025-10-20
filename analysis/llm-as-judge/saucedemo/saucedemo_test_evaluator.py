import os
import json
import glob
import time
from typing import List, Dict, Any
from dataclasses import dataclass

import sys
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_TODO_EVAL_DIR = os.path.abspath(os.path.join(_THIS_DIR, '..', 'ToDo-Evaluation'))
if _TODO_EVAL_DIR not in sys.path:
    sys.path.append(_TODO_EVAL_DIR)

from llm_api_client import LLMEvaluator, load_api_keys

@dataclass
class TestExecutionInfo:
    app_name: str
    model: str
    test_name: str
    scenario: str
    generated_code: str
    log_file_path: str

class SauceDemoTestEvaluator:
    
    def __init__(self):
        self.available_models = ["deepseek", "openai"]
        api_keys = load_api_keys()
        self.llm_evaluator = LLMEvaluator(api_keys)
        
        self.evaluation_criteria = [
            "scenario_code_alignment",
            "code_structure",
            "selector_quality", 
            "best_practices"
        ]
        
        self.saucedemo_directories = {
            "deepseek": "SauceDemo/deepseek",
            "openai": "SauceDemo/openai"
        }
    
    def discover_test_executions(self) -> List[TestExecutionInfo]:
        test_executions = []
        
        for model, base_path in self.saucedemo_directories.items():
            pattern = f"{base_path}/*/"
            subdirs = glob.glob(pattern)
            
            for subdir in subdirs:
                test_name = os.path.basename(subdir.rstrip('/'))
                log_file = os.path.join(subdir, "test_execution.log")
                
                if os.path.exists(log_file):
                    try:
                        with open(log_file, 'r', encoding='utf-8') as f:
                            log_content = f.read()
                        
                        parsed_data = self._parse_log_file(log_content)
                        
                        if parsed_data and "generated_test" in parsed_data:
                            generated_test = parsed_data["generated_test"]
                            scenario = generated_test.get("scenario", "")
                            code = generated_test.get("code", "")
                            
                            if code.startswith("```javascript"):
                                code = code.replace("```javascript", "").strip()
                            if code.endswith("```"):
                                code = code[:-3].strip()
                            
                            test_executions.append(TestExecutionInfo(
                                app_name="SauceDemo",
                                model=model,
                                test_name=test_name,
                                scenario=scenario,
                                generated_code=code,
                                log_file_path=log_file
                            ))
                            
                    except Exception as e:
                        print(f"Error reading {log_file}: {e}")
        
        return test_executions
    
    def _parse_log_file(self, log_content: str) -> Dict[str, Any]:
        try:
            lines = log_content.strip().split('\n')
            
            for i in range(len(lines) - 1, -1, -1):
                line = lines[i].strip()
                if line.startswith('{'):
                    json_lines = lines[i:]
                    json_str = '\n'.join(json_lines)
                    
                    try:
                        data = json.loads(json_str)
                        if "generated_test" in data:
                            return data
                    except json.JSONDecodeError:
                        continue
            
            return None
        except Exception as e:
            print(f"Error parsing JSON from log: {e}")
            return None
    
    def create_evaluation_prompt(self, scenario: str, code: str, test_name: str) -> str:
        return f"""# SauceDemo Test Code Evaluation - Scenario vs Code Alignment

You are a senior Playwright testing engineer. Evaluate whether the following test scenario and the generated code align for SauceDemo application.

## Test Info:
- **Test Name**: {test_name}
- **Scenario**: {scenario}

## Generated Code:
```javascript
{code}
```

## EVALUATION CRITERIA (Score each from 1-5):

### 1. SCENARIO-CODE ALIGNMENT - MOST IMPORTANT
**Scoring Guidelines:**
- **5**: Scenario fully implemented, steps in correct order, nothing missing
- **4**: Nearly complete, minor omissions or order issues
- **3**: Partially implemented, notable steps missing or incorrect
- **2**: Major differences between scenario and code
- **1**: Does not match the scenario at all


### 2. CODE STRUCTURE
**Scoring Guidelines:**
- **5**: Excellent async/await usage, clean organization
- **4**: Good structure with minor issues
- **3**: Basic structure, some async issues
- **2**: Poor organization, missing async usage
- **1**: Very poor structure, no async

### 3. SELECTOR QUALITY
**Scoring Guidelines:**
- **5**: Uses data-testid, role, or semantic selectors
- **4**: Good selector strategies
- **3**: Mixed selector types
- **2**: Mostly fragile selectors (CSS class, ID)
- **1**: Very fragile selectors

**Selector Priority (best to worst):**
1. **data-testid** selectors (most robust) - +2 pts
2. **role** selectors (a11y-based) - +2 pts
3. **Semantic** selectors (button, input, etc.) - +1 pt
4. **Text content** selectors - +0.5 pt
5. **CSS classes** (fragile) - -0.5 pt
6. **Element IDs** (fragile) - -0.5 pt

### 4. BEST PRACTICES
**Scoring Guidelines:**
- **5**: Follows all Playwright best practices
- **4**: Good practices with minor issues
- **3**: Basic practices
- **2**: Poor practices
- **1**: Very poor practices

## RESPONSE FORMAT:

Respond in this exact JSON format:

```json
{{
    "overall_score": <overall score 1-5>,
    "criteria_scores": {{
        "scenario_code_alignment": <score 1-5>,
        "code_structure": <score 1-5>,
        "selector_quality": <score 1-5>,
        "best_practices": <score 1-5>
    }},
    "detailed_analysis": {{
        "scenario_steps_coverage": {{
            "total_scenario_steps": <total steps in scenario>,
            "implemented_steps": <steps implemented in code>,
            "missing_steps": ["list of missing steps"],
            "incorrect_steps": ["list of incorrect steps"]
        }},
        "selector_analysis": {{
            "selector_types_used": ["data-testid", "role", "text", "css"],
            "robustness_score": <1-5>,
            "specific_issues": ["specific selector issues"],
            "recommendations": ["improvement suggestions"]
        }},
        "code_quality_analysis": {{
            "async_usage": "excellent|good|poor|missing",
            "organization": "excellent|good|poor",
            "best_practices_followed": ["good practices followed"],
            "best_practices_missing": ["missing practices"]
        }}
    }},
    "strengths": [
        "specific strength 1",
        "specific strength 2",
        "specific strength 3"
    ],
    "weaknesses": [
        "specific weakness 1",
        "specific weakness 2", 
        "specific weakness 3"
    ],
    "alignment_summary": {{
        "is_well_aligned": true/false,
        "alignment_percentage": <0-100>,
        "main_alignment_issues": ["main alignment issues"]
    }}
}}
```

**CRITICAL**: Be objective and consistent. Follow the scoring guide exactly. Pay special attention to scenario-code alignment.
"""

    def evaluate_test_execution(self, test_info: TestExecutionInfo, evaluation_model: str) -> Dict[str, Any]:
        print(f"Evaluating: {test_info.test_name} ({test_info.model}) - {evaluation_model} with")
        
        prompt = self.create_evaluation_prompt(
            test_info.scenario, 
            test_info.generated_code, 
            test_info.test_name
        )
        
        try:
            response = self.llm_evaluator.evaluate_with_model(prompt, evaluation_model)
            
            if response.success and response.parsed_evaluation:
                evaluation = response.parsed_evaluation
                return {
                    "success": True,
                    "test_info": {
                        "app_name": test_info.app_name,
                        "model": test_info.model,
                        "test_name": test_info.test_name,
                        "scenario": test_info.scenario,
                        "log_file_path": test_info.log_file_path
                    },
                    "overall_score": evaluation.get("overall_score", 0),
                    "criteria_scores": evaluation.get("criteria_scores", {}),
                    "detailed_analysis": evaluation.get("detailed_analysis", {}),
                    "strengths": evaluation.get("strengths", []),
                    "weaknesses": evaluation.get("weaknesses", []),
                    "alignment_summary": evaluation.get("alignment_summary", {}),
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "test_info": {
                        "app_name": test_info.app_name,
                        "model": test_info.model,
                        "test_name": test_info.test_name,
                        "scenario": test_info.scenario,
                        "log_file_path": test_info.log_file_path
                    },
                    "overall_score": 0,
                    "criteria_scores": {},
                    "detailed_analysis": {},
                    "strengths": [],
                    "weaknesses": [],
                    "alignment_summary": {},
                    "error": response.error or "Failed to parse evaluation"
                }
        except Exception as e:
            return {
                "success": False,
                "test_info": {
                    "app_name": test_info.app_name,
                    "model": test_info.model,
                    "test_name": test_info.test_name,
                    "scenario": test_info.scenario,
                    "log_file_path": test_info.log_file_path
                },
                "overall_score": 0,
                "criteria_scores": {},
                "detailed_analysis": {},
                "strengths": [],
                "weaknesses": [],
                    "alignment_summary": {},
                    "error": str(e)
            }

    def generate_json_report(self, output_file: str = "saucedemo_evaluation_results.json"):
        print("Generating JSON report for SauceDemo test evaluations...")
        
        test_executions = self.discover_test_executions()
        print(f"{len(test_executions)} test executions found")
        
        if not test_executions:
            print("No test executions found!")
            return None
        
        results = {
            "evaluation_metadata": {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_tests": len(test_executions),
                "evaluation_models": self.available_models,
                "criteria": self.evaluation_criteria
            },
            "test_evaluations": []
        }
        
        print(f"📊 {len(test_executions)} test execution işleniyor...")
        
        for i, test_info in enumerate(test_executions, 1):
            print(f"\n📋 İşleniyor {i}/{len(test_executions)}: {test_info.test_name} ({test_info.model})")
            
            test_result = {
                "test_info": {
                    "app_name": test_info.app_name,
                    "model": test_info.model,
                    "test_name": test_info.test_name,
                    "scenario": test_info.scenario,
                    "log_file_path": test_info.log_file_path
                },
                "evaluations": {}
            }
            
            for eval_model in self.available_models:
                print(f"  🤖 {test_info.model} testini {eval_model} ile değerlendiriyor...")
                
                evaluation = self.evaluate_test_execution(test_info, eval_model)
                test_result["evaluations"][eval_model] = evaluation
                
                if evaluation["success"]:
                    print(f"{eval_model}: {evaluation['overall_score']}/5")
                    alignment = evaluation.get("alignment_summary", {})
                    if alignment.get("is_well_aligned"):
                        print(f"Scenario-Code Alignment: {alignment.get('alignment_percentage', 0)}%")
                    else:
                        print(f"Scenario-Code Alignment: {alignment.get('alignment_percentage', 0)}%")
                else:
                    print(f"{eval_model}: {evaluation['error']}")
                
                time.sleep(1)
            
            results["test_evaluations"].append(test_result)
            
            if i % 3 == 0:
                self._save_progress_json(results, f"progress_{output_file}")
        
        self._save_progress_json(results, output_file)
        
        print(f"\nEvaluation completed!")
        print(f"Total evaluations: {len(results['test_evaluations'])}")
        print(f"Results saved to: {output_file}")
        
        return output_file
    
    def _save_progress_json(self, data: Dict[str, Any], filename: str):
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else ".", exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="SauceDemo Test Evaluator - JSON Format")
    parser.add_argument("--output", "-o", default="saucedemo_evaluation_results.json",
                       help="Output JSON file name")
    parser.add_argument("--models", nargs="+", choices=["deepseek", "openai"], 
                       default=["deepseek", "openai"],
                       help="Evaluation models to use")
    
    args = parser.parse_args()
    
    try:
        evaluator = SauceDemoTestEvaluator()
        evaluator.available_models = args.models
        
        output_file = evaluator.generate_json_report(args.output)
        
        if output_file:
            print(f"\nJSON report successfully created: {output_file}")
        else:
            print("\nReport not created!")
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure your API keys are set correctly:")
        print("export DEEPSEEK_API_KEY='your_key'")
        print("export OPENAI_API_KEY='your_key'")

if __name__ == "__main__":
    main()
