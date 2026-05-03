from typing import Any, Dict, List, TypedDict, Union, Tuple
from langchain_core.messages import AIMessage, HumanMessage

class AgentState(TypedDict):
    messagesHistory: List[Union[HumanMessage, AIMessage]]

    useCase: str
    useCaseReview: Dict[str, Any]
    useCaseReviewRound: int
    previousUseCase: str

    architecture: Dict[str, List[Dict[str, Any]]]
    architectureReview: Dict[str, Any]
    architectureReviewRound: int
    previousArchitecture: Dict[str, List[Dict[str, Any]]]

    graphRagResults: List[Dict[str, Any]]

    generatedFunctionsCode: List[Dict[str, str]]
    modifiedFunctions: List[Tuple[str, str]]

    invalidFunctions: List[Tuple[str, str]]
    functionValidationErrors: Dict[Tuple[str, str], str]
    functionValidationRound: int
    classValidationRound: int

    finalProgram: str

    programValidationErrors: List[Dict[str, Any]]
    programValidationRound: int

    testableMethods: List[Tuple[str, str]]
    generatedUnitTests: List[Dict[str, str]]
    testValidationRound: int

    generatedIntegrationTests: List[str]

    activityDiagram: str
    activityDiagramReview: str

    usersFeedback: str
    persistToGraph: bool
