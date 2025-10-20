from src.infrastructure.openai.test_step_client import TestStepClient
from src.services.vision_analysis_service import VisionAnalysisService
from src.services.test_case_service import TestCaseService
from src.services.dom_extractor.dom_extractor_service import DOMExtractor
from src.infrastructure.openai.vision_analysis_client import VisionAnalysisClient
from src.services.test_step_planner import TestStepPlanner
from src.services.element_selector import ElementSelector
from src.services.action_performer import ActionPerformer
from dependency_injector import containers, providers
from src.infrastructure.config.settings import get_settings
from src.infrastructure.openai.element_selector_client import ElementSelectorClient
from src.infrastructure.openai.test_code_generator_client import TestCodeGeneratorClient
from src.infrastructure.playwright.playwright_client import PlaywrightClient
from src.services.test_generator_service import TestGenerator
from src.services.test_runner_service import TestRunner
from src.infrastructure.repositories.test_case_repository import TestCaseRepository
from src.infrastructure.repositories.mongodb_connection_manager import MongoDBConnectionManager


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    settings = providers.Singleton(get_settings)

    mongodb_connection_manager: providers.Singleton[MongoDBConnectionManager] = providers.Singleton(
        MongoDBConnectionManager,
        settings=settings.provided.mongodb
    )
    
    element_selector_client: providers.Singleton[ElementSelectorClient] = providers.Singleton(
        ElementSelectorClient,
        settings=settings.provided.openai
    )
    
    vision_analysis_client: providers.Singleton[VisionAnalysisClient] = providers.Singleton(
        VisionAnalysisClient,
        settings=settings.provided.openai
    )
    
    test_code_generator_client: providers.Singleton[TestCodeGeneratorClient] = providers.Singleton(
        TestCodeGeneratorClient,
        settings=settings.provided.openai
    )

    test_case_repository: providers.Singleton[TestCaseRepository] = providers.Singleton(
        TestCaseRepository,
        connection_manager=mongodb_connection_manager
    )

    playwright_client: providers.Singleton[PlaywrightClient] = providers.Singleton(
        PlaywrightClient,
        settings=settings.provided.playwright,
        test_case_repository=test_case_repository
    )
    
    test_step_client: providers.Singleton[TestStepClient] = providers.Singleton(
        TestStepClient,
        settings=settings.provided.openai
    )


    element_selector: providers.Singleton[ElementSelector] = providers.Singleton(
        ElementSelector,
        client=element_selector_client
    )

    test_step_planner: providers.Singleton[TestStepPlanner] = providers.Singleton(
        TestStepPlanner,
        test_step_client=test_step_client
    )

    action_performer: providers.Singleton[ActionPerformer] = providers.Singleton(
        ActionPerformer
    )
    
    dom_extractor_service: providers.Singleton[DOMExtractor] = providers.Singleton(
        DOMExtractor
    )
    
    vision_analysis_service: providers.Singleton[VisionAnalysisService] = providers.Singleton(
        VisionAnalysisService,
        vision_client=vision_analysis_client
    )
    
    test_generator: providers.Singleton[TestGenerator] = providers.Singleton(
        TestGenerator,
        action_performer=action_performer,
        element_selector=element_selector,
        test_step_planner=test_step_planner,
        test_code_generator=test_code_generator_client,
        dom_extractor=dom_extractor_service,
        vision_analysis_service=vision_analysis_service
    )

    test_runner: providers.Singleton[TestRunner] = providers.Singleton(
        TestRunner,
        playwright_client=playwright_client,
        test_case_repository=test_case_repository
    )
    
    test_case_service: providers.Singleton[TestCaseService] = providers.Singleton(
        TestCaseService,
        test_generator=test_generator,
        test_runner=test_runner,
        repository=test_case_repository
    )
