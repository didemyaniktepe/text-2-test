from typing import List

class TestStepPrompt:
    @staticmethod
    def create(vision_analysis: str, remaining_scenario: str, dom_data: str, completed_steps: List[str], scenario: str) -> str:
        completed_steps_text = " -> ".join(completed_steps) if completed_steps else "None"
        return f"""
You are a test automation expert who analyzes UI and plans test steps.

INPUTS:
- VISION_ANALYSIS: "{vision_analysis}"
- DOM_DATA: "{dom_data}"
- REMAINING_SCENARIO: "{remaining_scenario}"
- COMPLETED_STEPS: "{completed_steps_text}"
- ORIGINAL_FULL_SCENARIO: "{scenario}"

TASKS:
1. Use the vision analysis to understand the current UI state (CRITICAL - this is your primary source of UI information)
2. Combine vision analysis with DOM data for complete context
3. Plan the next single action needed to continue the scenario

SCENARIO COMPLETION LOGIC:
- Check if COMPLETED_STEPS + REMAINING_SCENARIO covers ALL original requirements
- When returning the last required step, set scenario_complete to true but provide the step description
- Only return empty description when there are no more actions needed

RULES:
- ALWAYS prioritize the VISION_ANALYSIS over DOM_DATA when determining what's visible on screen
- If a navigation element is already expanded according to screenshot, skip clicking it and go to the submenu action
- Only plan actions that can be executed on the CURRENT visible UI
- Be specific with values: "Fill email field with 'user@example.com'" not just "Fill email"
- If scenario is complete, set scenario_complete to true
- For text inputs that require submission, use separate fill and press actions
- After filling text inputs, consider pressing 'Enter' key as a separate action

RESPONSE FORMAT (JSON only):
{{
    "description": "Fill the email field with 'user@example.com'",
    "reasoning": "Email field is visible and empty, this is the first step for authentication",
    "scenario_complete": false,
    "remaining_scenario": "Fill the password field with 'password123'"
}}

For the last step (when completing the scenario):
{{
    "description": "The final action that needs to be performed",
    "reasoning": "This is the final step to complete the scenario",
    "scenario_complete": true,
    "remaining_scenario": "No remaining scenario"
}}

After completing the last step (when no more actions needed):
{{
    "description": "",
    "reasoning": "All scenario steps completed successfully",
    "scenario_complete": true,
    "remaining_scenario": "No remaining scenario"
}}

Return ONLY the JSON object, no markdown formatting.
"""
