
import os
import json
import time
import requests
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class LLMConfig:
    api_key: str
    base_url: str
    model: str
    max_tokens: int = 4000
    temperature: float = 0.0
    timeout: int = 60

@dataclass
class EvaluationRequest:
    prompt: str
    model: str
    config: LLMConfig

@dataclass
class EvaluationResponse:
    model: str
    response_text: str
    parsed_evaluation: Optional[Dict[str, Any]]
    success: bool
    error: Optional[str]
    response_time: float
    tokens_used: Optional[int]

class LLMClient:
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.session = requests.Session()
        
    def make_request(self, prompt: str) -> EvaluationResponse:
        raise NotImplementedError("Subclasses must implement make_request")

class DeepSeekClient(LLMClient):
    
    def __init__(self, api_key: str):
        config = LLMConfig(
            api_key=api_key,
            base_url="https://api.deepseek.com/v1",
            model="deepseek-chat",
            max_tokens=4000,
            temperature=0.0
        )
        super().__init__(config)
        
    def make_request(self, prompt: str) -> EvaluationResponse:
        start_time = time.time()
        
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.config.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert in automated testing and Playwright. Provide detailed, structured evaluations of test quality in JSON format. The evaluation should be based on the scenario and the code."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "stream": False
        }
        
        try:
            response = self.session.post(
                f"{self.config.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            response_data = response.json()
            response_time = time.time() - start_time
            
            content = response_data["choices"][0]["message"]["content"]
            tokens_used = response_data.get("usage", {}).get("total_tokens")
            
            parsed_evaluation = self._parse_evaluation_response(content)
            
            return EvaluationResponse(
                model="DeepSeek",
                response_text=content,
                parsed_evaluation=parsed_evaluation,
                success=True,
                error=None,
                response_time=response_time,
                tokens_used=tokens_used
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            return EvaluationResponse(
                model="DeepSeek",
                response_text="",
                parsed_evaluation=None,
                success=False,
                error=str(e),
                response_time=response_time,
                tokens_used=None
            )
    
    def _parse_evaluation_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        try:
            import re
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    return None
            
            return json.loads(json_str)
        except Exception:
            return None

class OpenAIClient(LLMClient):
    
    def __init__(self, api_key: str):
        config = LLMConfig(
            api_key=api_key,
            base_url="https://api.openai.com/v1",
            model="gpt-4",
            max_tokens=4000,
            temperature=0.3
        )
        super().__init__(config)
        
    def make_request(self, prompt: str) -> EvaluationResponse:
        start_time = time.time()
        
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.config.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert in automated testing and Playwright. Provide detailed, structured evaluations of test quality in JSON format."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature
        }
        
        try:
            response = self.session.post(
                f"{self.config.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            response_data = response.json()
            response_time = time.time() - start_time
            
            content = response_data["choices"][0]["message"]["content"]
            tokens_used = response_data.get("usage", {}).get("total_tokens")
            
            parsed_evaluation = self._parse_evaluation_response(content)
            
            return EvaluationResponse(
                model="GPT-4",
                response_text=content,
                parsed_evaluation=parsed_evaluation,
                success=True,
                error=None,
                response_time=response_time,
                tokens_used=tokens_used
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            return EvaluationResponse(
                model="GPT-4",
                response_text="",
                parsed_evaluation=None,
                success=False,
                error=str(e),
                response_time=response_time,
                tokens_used=None
            )
    
    def _parse_evaluation_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        try:
            import re
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    return None
            
            return json.loads(json_str)
        except Exception:
            return None

class LLMEvaluator:
    
    def __init__(self, api_keys: Dict[str, str]):
        self.clients = {}
        
        if "deepseek" in api_keys and api_keys["deepseek"]:
            self.clients["deepseek"] = DeepSeekClient(api_keys["deepseek"])
        
        if "openai" in api_keys and api_keys["openai"]:
            self.clients["openai"] = OpenAIClient(api_keys["openai"])
        
        if not self.clients:
            raise ValueError("At least one API key must be provided")
    
    def evaluate_with_model(self, prompt: str, model: str) -> EvaluationResponse:
        if model not in self.clients:
            raise ValueError(f"Model {model} not available. Available: {list(self.clients.keys())}")
        
        return self.clients[model].make_request(prompt)
    
    def evaluate_with_all_models(self, prompt: str) -> Dict[str, EvaluationResponse]:
        results = {}
        
        for model_name, client in self.clients.items():
            print(f"Evaluating with {model_name}...")
            results[model_name] = client.make_request(prompt)
            time.sleep(1)  
        
        return results
    
    def compare_models(self, prompt: str) -> Dict[str, Any]:
        results = self.evaluate_with_all_models(prompt)
        
        comparison = {
            "models_compared": list(results.keys()),
            "results": results,
            "comparison_summary": self._create_comparison_summary(results)
        }
        
        return comparison
    
    def _create_comparison_summary(self, results: Dict[str, EvaluationResponse]) -> Dict[str, Any]:
        summary = {
            "success_rates": {},
            "average_scores": {},
            "response_times": {},
            "token_usage": {}
        }
        
        for model, response in results.items():
            summary["success_rates"][model] = response.success
            summary["response_times"][model] = response.response_time
            summary["token_usage"][model] = response.tokens_used
            
            if response.parsed_evaluation and response.success:
                overall_score = response.parsed_evaluation.get("overall_score", 0)
                summary["average_scores"][model] = overall_score
        
        return summary

def load_api_keys() -> Dict[str, str]:
    keys = {}
    
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if deepseek_key:
        keys["deepseek"] = deepseek_key
    if openai_key:
        keys["openai"] = openai_key
    
    config_file = Path("api_config.json")
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                keys = config.get("api_keys", {})
        except Exception as e:
            print(f"Error loading config file: {e}")
    
    return keys


if __name__ == "__main__":
    keys = load_api_keys()
    evaluator = LLMEvaluator(api_keys=keys)
