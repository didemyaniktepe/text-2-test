
import json
import logging
import re
from typing import Tuple, Union

import os
import time
from src.services.test_step_planner import TestStepPlanner
from src.utils.element_utils import collect_page_elements_info
from src.services.action_performer import ActionPerformer
from playwright.async_api import async_playwright
from src.utils.logger_utils import TestLogger

from src.infrastructure.openai.test_code_generator_client import TestCodeGeneratorClient
from src.services.dom_extractor.dom_extractor_service import DOMExtractor
from src.services.element_selector import ElementSelector
from src.services.vision_analysis_service import VisionAnalysisService

logger = logging.getLogger(__name__)
class TestGenerator:
    def __init__(self, action_performer: ActionPerformer,
                 element_selector: ElementSelector,
                 vision_analysis_service: VisionAnalysisService,
                 test_step_planner: TestStepPlanner,
                 test_code_generator: TestCodeGeneratorClient,
                 dom_extractor: DOMExtractor):
        self.dom_extractor = dom_extractor
        self.element_selector = element_selector
        self.action_performer = action_performer
        self.test_step_planner = test_step_planner
        self.vision_analysis_service = vision_analysis_service
        self.test_code_generator = test_code_generator
        
      
        
    async def generate(self, scenario: str, url: str, folder_name: str = ""):
        test_logger = TestLogger(original_scenario=scenario, folder_name=folder_name)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()

            await page.goto(url)
            await page.wait_for_load_state("networkidle")
            
            remaining_scenario = scenario
            completed_steps = []
            test_steps = []
            max_iterations = 20
            iteration = 0
            failed_attempts = []
            step_desc = ""
            selector = ""
            action_type = ""
            screenshot_path = ""
            next_step = None
            
            while iteration < max_iterations:
                logger.info(f"Iteration: {iteration}")
                if failed_attempts:
                    logger.info(f"Failed attempts: {failed_attempts}")
                else:
                    logger.info("No failed attempts")
                    dom_data, screenshot_path = await self.dom_extractor.extract_dom_from_page(page)
                    print(f"Screenshot captured at: {screenshot_path}")
                    test_logger.save_screenshot(screenshot_path, iteration)
                    vision_analysis = self.vision_analysis_service.analyze_screenshot(screenshot_path, remaining_scenario, scenario, completed_steps)
                    logger.info(f"Vision analysis: {vision_analysis}")
                    next_step = self.test_step_planner.plan(vision_analysis,remaining_scenario,dom_data,completed_steps,scenario)
                    logger.info(f"Next step: {next_step}")
                    if not next_step.description:
                        logger.info("No description provided, scenario marked as complete")
                        break
                    step_desc = next_step.description.strip()
                logger.info(f"Step description: {step_desc}")
                selector, action_type, locator = self.element_selector.find_selector(step_desc, dom_data, vision_analysis, failed_attempts)
                logger.info(f"Selector: {selector}")
                logger.info(f"Action type: {action_type}")
                logger.info(f"Locator: {locator}")
                test_logger.log_step(step_number=iteration,prompt=step_desc,response=f"Selector: {selector}\nAction Type: {action_type}",action={"type": "selector", "selector": selector, "action_type": action_type,"vision_analysis": vision_analysis},remaining_scenario=remaining_scenario)
                success, used_selector, resolved_locator = await self.action_performer.perform_action(page, selector, step_desc, action_type, locator)
                logger.info(f"Used selector: {used_selector}")
                logger.info(f"Resolved locator: {resolved_locator}")
                if success:
                    logger.info(f"Success: {success}")
                    completed_steps.append(step_desc)
                    test_steps.append({"step_desc": step_desc,"selector": used_selector,"action_type": action_type,"resolved_locator": resolved_locator,"vision_analysis": vision_analysis})
                    remaining_scenario = next_step.remaining_scenario if next_step else ""
                    logger.info(f"Remaining scenario: {remaining_scenario}")
                    test_logger.log_step(step_number=iteration,prompt=step_desc,response="Action performed successfully",action={"type": "action","status": "success","selector": used_selector,"action_type": action_type,"step_desc": step_desc,"resolved_locator": resolved_locator,"vision_analysis": vision_analysis})
                    failed_attempts = []
                    await page.wait_for_timeout(1000)
                else:    
                    logger.info(f"Failed: {success}")
                    attempt_info = await collect_page_elements_info(page, selector, action_type, locator)
                    failed_attempts.append(attempt_info)
                    test_logger.add_failed_attempt(attempt_info)
                    test_logger.log_step(step_number=iteration,prompt=step_desc,response=f"Action failed: {selector + action_type}",action={"type": "action","status": "failed","selector": selector,"action_type": action_type,"resolved_locator": resolved_locator,"vision_analysis": vision_analysis})  
                if next_step and next_step.scenario_complete:
                    logger.info("Scenario is complete after successful action")
                    break
                iteration += 1

            await browser.close()
            test_code = self.test_code_generator.generate_test_code(test_steps, scenario, url)
            logger.info(f"Generated test code: {test_code}")
            
            test_logger.add_generated_test(test_code, scenario, url)
            test_logger.finalize_test(success=len(failed_attempts) == 0)
    
            return test_code
        

        