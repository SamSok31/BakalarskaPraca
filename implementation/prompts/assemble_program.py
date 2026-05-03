INITIAL_ASSEMBLE_PROMPT = """
ROLE:
Senior software architect and system integrator

TASK:
Assemble a complete, coherent, and runnable Python program that fully implements the Use Case

INPUTS:
Architecture:
{architecture}

Method Implementations:
{functions_code_block}

Use Case:
{useCase}

PRIORITY:
1. Full Use Case behavior execution and requierement satisfaction
2. Architecture preservation
3. Reuse of provided method implementations
4. Necessary fixes only

ARCHITECTURE PRESERVATION RULE:
- ALL classes from architecture MUST be present
- ALL methods from architecture MUST be present
- Class names, method names, and attributes from architecture MUST NOT be changed
- Do NOT remove or rename any element

USE CASE EXECUTION RULE:
- The final program MUST execute all behaviors and requirements from the Use Case
- All Main Success Scenario steps MUST be achievable through the program
- If behavior or special requirement is missing in methods implementations → fix via as minimal changes as possible

INTEGRATION COMPLETENESS:
- All classes MUST be fully defined
- All methods MUST be correctly assigned to their classes
- All attributes MUST be initialized in __init__
- All method calls MUST be valid and consistent
- Data flow between methods MUST be correct

METHOD IMMUTABILITY:
- Method bodies are authoritative
- Modify ONLY if:
- there is a clear bug
- logic prevents correct execution
- Changes MUST be as minimal and local as possible
- Do NOT rewrite entire methods

CONTROLLED REPAIR:
- Prefer fixing integration over modifying methods
- If modification is required:
- fix only incorrect or missing logic
- preserve structure and style as much as possible

CONTRACT RULE:
- Method inputs/outputs are authoritative
- Adapt call sites instead of changing method signatures
- Maintain consistent data flow

STATE CONSISTENCY:
- Attributes MUST be initialized in __init__
- All self.<attribute> usage MUST be valid
- Ensure consistent data types across calls

ORCHESTRATION RULE:
- Use the Use Case to determine execution flow
- Ensure correct sequence of operations
- Implement main() to demonstrate correct behavior

ALLOWED MODIFICATIONS:
- Add missing imports
- Fix call mismatches
- Add glue logic
- Fix logical or functional errors which are not correctly implemented from the use case
- Adding new methods, functions or attributes if it is really necessary

FORBIDDEN:
- removing or renaming classes/methods from architecture
- rewriting methods unnecessarily

FINAL CONSISTENCY CHECK:
- Ensure all domain rules (e.g., win condition) match Use Case
- If inconsistency exists → fix it even if methods disagree
- Ensure final program is perfectly executing behaviour and requirements from the use case and it has no bugs or errors

OUTPUT FORMAT:
Return ONLY valid Python code
Return the COMPLETE runnable program
Do not include explanations or comments outside the code
"""

REVIEW_REASSEMBLE_PROMPT = """
ROLE:
Senior software engineer fixing a Python program after validation failure

TASK:
Fix the program by resolving validation errors while preserving architecture and correct behavior

INPUTS:
Previous Program:
{finalProgram}

Validation Errors:
{programValidationErrors}

Use Case:
{useCase}

PRIORITY:
1. Resolve validation errors
2. Preserve architecture and structure as much as possible
3. Preserve correct existing behavior

ERROR TRUST RULE:
- Validation errors may be incorrect or over-strict
- Verify whether the reported issue is REAL before applying fix
- If error contradicts specification → IGNORE it

PATCHING PRINCIPLE:
- Treat the previous program as the baseline
- Apply ONLY as much minimal as possible necessary changes
- Unchanged code, behaviour and functionality MUST remain identical


ROOT CAUSE RULE:
- Identify the root cause of each error before fixing
- Fix the cause, NOT just the symptom
- Avoid introducing secondary issues

ERROR-DRIVEN REPAIR:
- Each code modification MUST directly correspond to a validation error
- Do NOT modify code unrelated to reported errors

ARCHITECTURE INVARIANT:
- ALL classes MUST remain present
- ALL methods MUST remain present
- Class names, method names, and attributes MUST NOT be removed or renamed
- Structure MUST be preserved unless strictly required to fix an error

CHANGE LOCALIZATION:
- Modify ONLY the smallest possible part of the code
- Do NOT propagate changes beyond required scope

USE CASE CONSISTENCY:
- Ensure fixes do not break required behavior
- Do NOT introduce new behavior
- Use Use Case only as a correctness constraint

CONTRACT RULE:
- Method inputs/outputs MUST remain consistent
- If a contract must change → update all usages consistently

INTEGRATION CONSISTENCY:
- Ensure all method calls are valid
- Ensure data flow is correct after fixes

CONSTRAINTS:
- MUST fix only reported errors
- MUST preserve correct existing logic
- MUST avoid unnecessary changes

ALLOWED MODIFICATIONS:
- Fix logical or functional errors which are not correctly implemented mentioned in validation errors
- Adding new methods, functions or attributes if it is really necessary

FORBIDDEN:
- rewriting large parts of the program
- refactoring unrelated logic
- renaming classes or methods
- removing existing functionality
- speculative improvements

FINAL CONSISTENCY CHECK:
- Ensure all domain rules (e.g., win condition) match Use Case
- If inconsistency exists → fix it even if methods disagree
- Ensure final program is perfectly executing behaviour and requirements from the use case and it has no bugs or errors

OUTPUT FORMAT:
Return ONLY valid Python code. Do NOT include explanations or comments outside the code.
Return the COMPLETE corrected program
"""

FEEDBACK_REASSEMBLE_PROMPT = """
ROLE:
Senior software architect and system integrator

TASK:
Rebuild a complete runnable Python program using updated architecture and method implementations

INPUTS:
Previous Program:
{finalProgram}

User Feedback:
{usersFeedback}

Architecture:
{architecture}

Method Implementations:
{functions_code_block}

Use Case:
{useCase}

PRIORITY:
1. Full Use Case behavior execution
2. Architecture preservation
3. Reuse of provided method implementations
4. Necessary fixes only

REBUILD PRINCIPLE:
- Construct the program from scratch using inputs
- DO NOT treat previous program as a base
- Use previous program and feedback for context about past issues and about what to avoid or repair in the next version

ARCHITECTURE COMPLETENESS:
- ALL classes from architecture MUST be present
- ALL methods from architecture MUST be present
- Class names, method names, and attributes MUST NOT be changed
- No elements may be omitted

USE CASE EXECUTION RULE:
- The final program MUST execute all behaviors and requirements from the Use Case
- All Main Success Scenario steps MUST be achievable through the program
- If behavior or special requirement is missing in methods implementations → fix via as minimal changes as possible

INTEGRATION COMPLETENESS:
- All classes MUST be fully defined
- All methods MUST be correctly assigned to their classes
- All attributes MUST be initialized in __init__
- All method calls MUST be valid and consistent
- Data flow between methods MUST be correct

METHOD IMMUTABILITY:
- Use provided method implementations as authoritative
- Modify ONLY if:
- there is a clear bug
- logic prevents correct execution
- Changes MUST be as minimal and local as possible
- Do NOT rewrite entire methods

CONTROLLED FIXES:
- Prefer fixing integration over modifying methods
- If method change is required:
- fix only incorrect logic
- preserve structure and style

ORCHESTRATION RULE:
- Build execution flow based on updated Use Case
- Ensure correct sequence of interactions
- Implement main() to demonstrate behavior

CONTRACT RULE:
- Method inputs/outputs are authoritative
- Adapt call sites instead of modifying method signatures

STATE CONSISTENCY:
- All self.<attribute> must be initialized
- Ensure consistent data flow and types

ALLOWED MODIFICATIONS:
- Add missing imports
- Fix call mismatches
- Add glue logic
- Fix logical or functional errors which are not correctly implemented from the use case
- Adding new methods, functions or attributes if it is really necessary

FORBIDDEN:
- removing or renaming classes/methods from architecture
- rewriting methods unnecessarily

FINAL CONSISTENCY CHECK:
- Ensure all domain rules (e.g., win condition) match Use Case
- If inconsistency exists → fix it even if methods disagree
- Ensure final program is perfectly executing behaviour and requirements from the use case and it has no bugs or errors
- Ensure final program perfectly meets comments and requirements from the user feedback

OUTPUT FORMAT:
Return ONLY valid Python code. Do NOT include explanations or comments outside the code.
Return COMPLETE runnable program
"""

REVIEW_INITIAL_PROGRAM_PROMPT = """
ROLE:
Strict semantic validator of a complete Python program

TASK:
Detect real defects where the program fails to correctly implement the Use Case and assign a quality score

INPUTS:
Architecture (reference only):
{architecture}

Use Case (authoritative):
{useCase}

Program:
{finalProgram}

PRIORITY:
1. Use Case behavior correctness (mandatory)
2. Execution and integration correctness
3. Architecture consistency (only if it affects correctness)

SOURCE OF TRUTH RULE:
- Use Case defines ALL required behavior
- Architecture is only a supporting reference

BEHAVIOR COVERAGE RULE:
- EVERY required behavior and special requirement from the Use Case MUST be implemented
- Each Main Success Scenario step MUST be traceable in the program
- Missing behavior or requirement MUST be reported as a defect

EXECUTION VALIDATION:
- Program flow MUST enable execution of required behavior
- main() or equivalent MUST trigger the correct sequence
- Method interactions MUST be consistent and callable

INTEGRATION CHECK:
- Method calls MUST match expected inputs/outputs
- Data flow between components MUST be valid
- No broken or inconsistent interactions

ARCHITECTURE CHECK:
- Report mismatch ONLY if it causes missing or incorrect behavior
- Structural differences are allowed if behavior is correct

DEFECT DEFINITION:
Report an issue ONLY if:
- required behavior is missing
- execution flow is broken or incomplete
- method interactions are invalid
- logic contradicts the Use Case

CONSTRAINTS:
- MUST report only real, evidence-based defects
- MUST NOT report stylistic issues
- MUST NOT suggest improvements or redesign
- MUST NOT report hypothetical edge cases
- MUST NOT mention correct parts

FORBIDDEN:
- assumptions not grounded in code
- overanalysis beyond visible behavior
- enforcing architecture if behavior is correct

STRICTNESS RULE:
- VALID ONLY if confident behavior is correct
- If uncertain → prefer lower score

SCORING RULES:
- 1.00 → all behavior correctly implemented, no defects
- 0.90–0.99 → only minor issues
- 0.60–0.89 → noticeable defects affecting behavior
- <0.60 → major missing behavior or broken execution

SCORING CONSTRAINT:
- Missing required behavior or missing special requirements → score < 0.90
- Broken execution flow → score < 0.60
- Only minor issues → score ≥ 0.90
- Score MUST reflect severity AND number of defects

OUTPUT FORMAT:
- Do not include explanations or commentary outside the JSON
- Return ONLY valid JSON in the following format:

{{
"score": <float 0.00–1.00>,
"issues": ["issue 1", "issue 2"]
}}

OUTPUT RULES:
- Max 7 issues, ordered by importance
- Fewer if fewer real defects exist, no valuable rrrors is also an option
- Empty list if no defects
"""

REVIEW_AFTER_FEEDBACK_PROGRAM_PROMPT = """
ROLE:
Strict semantic validator of a Python program after feedback-based revision

TASK:
Detect real defects in feedback implementation, Use Case behavior, and system integration, and assign a quality score

INPUTS:
Updated Architecture (reference only):
{architecture}

Updated Use Case:
{useCase}

User Feedback:
{usersFeedback}

Program:
{finalProgram}

PRIORITY:
1. Feedback implementation correctness (highest)
2. Use Case behavior completeness
3. Execution and integration correctness
4. Architecture consistency (only if it affects behavior)

SOURCE OF TRUTH:
- Use Case defines baseline behavior
- Feedback defines required changes to that behavior
- Program MUST satisfy BOTH

FEEDBACK VALIDATION:
- Identify feedback items that describe behavior changes
- Verify ALL such changes are implemented
- Report missing, partial, or incorrect implementation
- Do NOT expand feedback beyond its meaning

USE CASE VALIDATION:
- ALL required behaviors and special requirements MUST be implemented
- Each Main Success Scenario step MUST be traceable in the program

EXECUTION VALIDATION:
- Program flow MUST enable execution of required behavior
- main() or equivalent MUST trigger correct sequence
- No missing or unreachable steps

INTEGRATION CHECK:
- Method calls MUST match contracts
- Data flow MUST be consistent
- No broken or invalid interactions

DEFECT DEFINITION:
Report an issue ONLY if:
- feedback-driven behavior is missing or incorrect
- required Use Case behavior or requirement is missing
- execution flow is broken or incomplete
- method interactions are invalid

ARCHITECTURE RULE:
- Report mismatch ONLY if it causes incorrect behavior
- Structural differences are allowed if behavior is correct

CONSTRAINTS:
- MUST report only real, evidence-based defects
- MUST NOT report style issues
- MUST NOT suggest redesign
- MUST NOT report hypothetical issues
- MUST NOT mention correct parts

FORBIDDEN:
- assumptions not grounded in code
- overanalysis beyond visible behavior
- enforcing architecture unnecessarily

STRICTNESS RULE:
- VALID only if confident behavior is correct
- If uncertain → prefer lower score

SCORING RULES:
- 1.00 → feedback fully implemented, full behavior coverage, no defects
- 0.90–0.99 → only minor issues
- 0.60–0.89 → noticeable defects or partial feedback implementation
- <0.60 → missing feedback, missing behavior, or broken execution

SCORING CONSTRAINT:
- Missing feedback implementation → score < 0.90
- Missing Use Case behavior → score < 0.90
- Broken execution flow → score < 0.60
- Score MUST reflect severity AND number of defects

OUTPUT FORMAT:
- Do not include explanations or commentary outside the JSON
- Return ONLY valid JSON in the following format:

{{
"score": <float 0.00–1.00>,
"issues": ["issue 1", "issue 2"]
}}

OUTPUT RULES:
- Max 7 issues, ordered by importance
- Fewer if fewer real defects exist, no valuable errors is also an option
- Empty list if no defects
"""

PROGRAM_TO_USECASE_PROMPT = """
ROLE:
Senior software engineer specialized in requirements analysis

TASK:
Transform the given program into a structured Use Case by extracting system behavior and reconstructing functional requirements

INPUT:
Program:
{program}

PRIORITY:
1. Extract ALL implemented functional behavior
2. Reconstruct requirements as if they were originally specified
3. Match wording, abstraction, and structure of Use Case generated from user task

REQUIREMENT RECONSTRUCTION RULES:
- Convert implemented behavior into requirement-level descriptions
- Express behavior as system capabilities, not code logic
- Generalize concrete implementation into abstract requirements
- If multiple implementations represent one behavior → unify them into one requirement
- Do NOT omit behavior that is clearly implemented

ABSTRACTION RULES:
- MUST stay at system behavior level (not code)
- MUST NOT include:
  - classes, methods, variables
  - libraries or frameworks
  - UI event handling details unless essential
- Convert code flow into actor–system interaction

CONSISTENCY RULE:
- Use similar wording style as Use Case generated from user task
- Prefer generalized phrasing over implementation-specific wording
- Keep terminology consistent across sections

CONSTRAINTS:
- MUST NOT hallucinate functionality not present in code
- MUST NOT omit clearly implemented behavior
- MUST NOT introduce implementation details

SECTION RULES:
- Goal = main objective of the actor
- System Responsibilities = system capabilities (not steps)
- Preconditions = required system state before execution
- Postconditions = resulting system state after success
- Main Success Scenario = step-by-step interaction flow derived from execution
- Extensions = alternative or exceptional flows if observable
- Special Requirements = constraints inferred ONLY if clearly present (e.g., UI, performance)

FLOW DERIVATION RULE:
- Derive Main Success Scenario from actual execution flow
- Map internal logic into actor–system interactions
- Ensure steps follow realistic user interaction sequence

OUTPUT FORMAT:
- Return ONLY the Use Case
- Preserve EXACT same structure as original Use Case prompt
- Do NOT include explanations or commentary outside the use case

STRUCTURE:
Use Case:
Primary Actor:
Goal:

System Responsibilities:

Preconditions:

Postconditions:

Main Success Scenario:

Extensions:

Special Requirements:
"""

GENERATE_UNIT_TESTS_PROMPT = """
ROLE:
Python developer generating precise unit tests for a class method

TASK:
Generate 2–3 deterministic unit tests, each verifying a DIFFERENT behavior of the method

INPUTS:
Class Architecture:
{cls}

Method Specification:
{method}

Method Code:
{code}

PRIORITY:
1. Cover different meaningful behaviors from specification
2. Ensure each test detects incorrect implementation
3. Keep tests simple, deterministic, and independent

BEHAVIOR SELECTION:
- Identify 2–3 DISTINCT behaviors from the specification
- Each test MUST cover a different behavior
- Do NOT duplicate the same logic with different values
- Prefer core logic over edge cases
- Avoid trivial or obvious behaviors

TEST DESIGN RULE:
- Each test MUST validate exactly ONE behavior
- Each test MUST fail if that behavior is implemented incorrectly
- Tests MUST NOT overlap in purpose

INPUT SELECTION:
- Use simple, deterministic values
- Inputs MUST match method specification
- Avoid randomness

STATE SETUP:
- Initialize only required attributes
- Ensure valid initial state

ASSERTION RULE:
- If method returns value → assert exact expected value
- If method modifies state → assert state change explicitly
- If both → assert both
- Assertions MUST be precise and meaningful

DIVERSITY RULE:
- Tests MUST cover different logical paths OR behaviors
- Do NOT create multiple tests for the same scenario
- Do NOT vary only input values without changing tested behavior

CONTEXT RULE:
- Use ONLY declared attributes and methods
- Do NOT assume behavior not present in specification or code
- Do NOT invent outputs or side effects

CONSTRAINTS:
- Generate 2–3 separate test functions
- Each function name MUST start with test_
- Do NOT generate classes
- Instantiate exactly this class: {class_name}
- Do NOT use pytest or unittest
- Do NOT use random values
- Do NOT use trivial assertions
- Do NOT add comments

FORBIDDEN:
- testing implementation details instead of behavior
- weak assertions (e.g., assert True, assert not None)
- multiple behaviors in one test
- duplicated tests with different inputs
- unnecessary complexity

ISOLATION:
- Each test MUST run independently

OUTPUT FORMAT:
Return ONLY valid Python code
Do not include explanations or comments outside the code
"""

UNIT_TESTABILITY_PROMPT = """
ROLE:
Strict classifier of method testability for unit testing

TASK:
Determine whether the method can be meaningfully and reliably unit tested in isolation

INPUTS:
Method Specification:
{method}

Method Code:
{code}

PRIORITY:
1. Observability of behavior
2. Isolation feasibility
3. Deterministic execution

TESTABILITY CRITERIA:

A method is TESTABLE ONLY if ALL are true:
- Its behavior produces observable results:
- return value OR
- verifiable state change
- Behavior can be asserted precisely
- It can run independently without full application context
- It does NOT depend on external systems (GUI, I/O, runtime environment)
- Execution is deterministic (same input → same result)

A method is NOT_TESTABLE if ANY are true:
- No observable output or state change
- Behavior cannot be asserted meaningfully
- Depends on external systems or environment
- Requires full application flow to execute
- Behavior is non-deterministic

ORCHESTRATION RULE:
- Methods that only delegate calls are NOT_TESTABLE
- EXCEPTION: if delegation produces observable and testable results → TESTABLE

STATE RULE:
- Methods modifying class state are TESTABLE ONLY if:
- state change is clear and verifiable

CONTEXT RULE:
- Base decision ONLY on provided code and specification
- Do NOT assume mocking, patching, or external control

DECISION RULE:
- Mark TESTABLE ONLY if testability is clear and reliable
- If uncertain → mark NOT_TESTABLE

FORBIDDEN:
- assuming hidden outputs
- assuming ability to mock dependencies
- overestimating testability
- using method name as signal

OUTPUT FORMAT:
- Do not include explanations or comments outside the JSON response
- Return ONLY valid JSON in the following format:

{{
"verdict": "TESTABLE" or "NOT_TESTABLE"
}}
"""

GENERATE_INTEGRATION_TESTS_PROMPT = """
ROLE:
Python developer generating integration tests

TASK:
Generate EXACTLY 3 integration tests, each representing a DIFFERENT realistic scenario of system behavior

INPUTS:
Use Case:
{useCase}

Architecture:
{architecture}

PRIORITY:
1. Accurate execution of Use Case behavior
2. Correct system interaction and data flow
3. Meaningful assertions verifying outcomes

SCENARIO SELECTION:
- Test 1: Main Success Scenario (normal flow)
- Test 2: Alternative or variation of flow (different valid path)
- Test 3: Edge or boundary scenario (if applicable)

SCENARIO RULE:
- Each test MUST represent ONE complete scenario
- Each scenario MUST be logically different
- Do NOT duplicate the same flow with different values

TRACEABILITY:
- Each test MUST map to a coherent sequence of steps
- For Main Success Scenario → include all key steps
- For other scenarios → include relevant variations

REALISTIC FLOW:
- Call methods in logical order
- Maintain consistent system state
- Use outputs of earlier steps in later steps when applicable

INITIALIZATION:
- Properly initialize system and required objects
- Ensure valid starting state for each test

DATA FLOW RULE:
- Outputs MUST be reused when required
- Avoid artificial or disconnected inputs

ASSERTION RULE:
- Each test MUST contain at least one meaningful final assertion
- Assertions MUST verify outcome of the scenario
- Tests MUST fail if behavior is incorrect
- Do NOT use trivial assertions

DIVERSITY RULE:
- Each test MUST cover a different logical flow or scenario
- Do NOT create multiple tests for identical behavior
- Do NOT vary only input values without changing scenario

CONTEXT RULE:
- Use ONLY classes and methods defined in architecture
- Do NOT invent methods or behavior

CONSTRAINTS:
- Generate EXACTLY 3 separate test functions
- Each function name MUST start with test_
- Do NOT generate classes
- Instantiate appropriate main class(es)
- Use deterministic values
- Do NOT use pytest or unittest

FORBIDDEN:
- skipping essential steps in a scenario
- mixing multiple scenarios in one test
- duplicating flows with minor variations
- weak assertions (e.g., assert True)
- inventing unsupported flows

ISOLATION:
- Each test MUST run independently

OUTPUT FORMAT:
Return ONLY valid Python code
Do not include explanations or comments outside the code
"""