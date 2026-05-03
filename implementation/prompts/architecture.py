INITIAL_DESIGN_PROMPT = """
ROLE:
Senior software architect specialized in Python system design

TASK:
Design a complete and minimal architecture that fully implements the Use Case

INPUTS:
Use Case:
{useCase}

User Task:
{userTask}

PRIORITY:
1. Complete coverage of all required behavior and requirements
2. Correct mapping of behavior and requirements to methods
3. Minimal and clear architecture

COVERAGE RULE:
- EVERY behavior from Main Success Scenario MUST be represented in methods
- Special Requirements MUST be reflected in appropriate method special requirements definitions
- Relevant Extensions MUST be supported
- No required behavior or requirement may be omitted

TRACEABILITY RULE:
- Each Use Case step MUST be traceable to one or more methods
- Methods MUST collectively cover the full interaction flow

CLASS DESIGN RULES:
- Each class MUST have a single clear responsibility
- Prefer minimal number of classes
- Small systems MAY use a single main class

ATTRIBUTE RULES:
- Attributes MUST represent persistent system state
- Any data shared across methods MUST be stored as attributes
- Attributes MUST correspond to entities from the Use Case
- Only combine attributes into a list or set if they are very similar in meaning.

METHOD DESIGN RULES:
- Each method MUST represent a meaningful system action
- Methods MUST align with Use Case steps
- Methods MUST define clear inputs and outputs
- Methods MUST include sufficient steps for implementation
- Methods MUST include all special requierments that are conncted to them

STATE RULE:
- Persistent data MUST be stored in class attributes
- DO NOT rely on local variables for shared state
- If data is used across multiple steps → it MUST be an attribute

CONSTRAINTS:
- MUST use object-oriented design
- MUST keep architecture minimal but complete
- MUST avoid trivial or redundant methods
- MUST ensure methods operate on class state

FORBIDDEN:
- missing required behavior
- unnecessary classes or methods
- implementation details (no code)
- global state assumptions
- vague or underspecified methods

OUTPUT FORMAT:
- Do not include explanations or commentary outside the JSON.
- Return ONLY valid JSON using this schema:

{{
"classes": [
    {{
    "name": "string",
    "responsibility": "string",
    "attributes": [
        {{"name": "string", "type": "string", "description": "string"}}
    ],
    "methods": [
        {{
        "name": "string",
        "summary": "string",
        "description": "string",
        "steps": ["string"],
        "inputs": [{{"name": "string", "type": "string", "description": "string"}}],
        "outputs": [{{"name": "string", "type": "string", "description": "string"}}],
        "special requirements": ["string"]
        }}
    ]
    }}
]
}}
"""

REVIEW_DESIGN_PROMPT = """
ROLE:
Senior software architect specialized in revising Python architectures

TASK:
Apply corrections to the architecture created from the use case strictly based on the provided review issues

INPUTS:
Current Architecture:
{architecture}

Review Issues:
{architectureReview}

Use Case (reference):
{useCase}

PRIORITY:
1. Apply review corrections
2. Preserve existing architecture
3. Minimize scope of changes

PATCHING PRINCIPLE:
- Treat current architecture as authoritative baseline
- Apply only minimal necessary changes
- Unaffected parts MUST remain unchanged

CHANGE LOCALIZATION RULE:
- Modify ONLY elements directly related to review issues
- Do NOT propagate changes beyond required scope
- Keep all unrelated classes, methods, and attributes identical

USE CASE CONSISTENCY RULE:
- Apply a correction ONLY if it is consistent with the Use Case
- If a review issue contradicts the Use Case → IGNORE it
- Use Case defines intended system behavior

CONSTRAINTS:
- MUST apply only explicitly listed issues
- MUST NOT introduce new functionality unless required by issues
- MUST NOT redesign unaffected parts
- MUST preserve existing correct behavior

FORBIDDEN:
- refactoring or improving unrelated parts
- removing correct functionality
- interpreting issues beyond their explicit meaning

OUTPUT FORMAT:
- Do not include explanations or commentary outside the JSON.
- Return ONLY valid JSON using the SAME schema as input:

{{
"classes": [
    {{
    "name": "string",
    "responsibility": "string",
    "attributes": [
        {{"name": "string", "type": "string", "description": "string"}}
    ],
    "methods": [
        {{
        "name": "string",
        "summary": "string",
        "description": "string",
        "steps": ["string"],
        "inputs": [{{"name": "string", "type": "string", "description": "string"}}],
        "outputs": [{{"name": "string", "type": "string", "description": "string"}}],
        "special requirements": ["string"]
        }}
    ]
    }}
]
}}
"""

FEEDBACK_DESIGN_PROMPT = """
ROLE:
Senior software architect specialized in updating architectures from user feedback

TASK:
Update the architecture ONLY if feedback implies a change in intended system behavior

INPUTS:
Current Architecture:
{architecture}

User Feedback:
{usersFeedback}

Updated Use Case:
{useCase}

PRIORITY:
1. Apply requirement-level changes from feedback
2. Ensure consistency with updated Use Case
3. Preserve existing architecture
4. Minimize scope of changes

FEEDBACK CLASSIFICATION:
Interpret feedback as:

1. REQUIREMENT CHANGE (APPLY):
- new functionality is requested
- existing functionality must behave differently
- constraints or rules are changed

2. IMPLEMENTATION ISSUE (IGNORE):
- bug reports
- incorrect outputs
- performance problems
- technical errors

RULE:
- ONLY apply REQUIREMENT CHANGE items
- IGNORE implementation issues unless they clearly imply behavior change

PATCHING PRINCIPLE:
- Treat current architecture as authoritative baseline
- Apply only minimal necessary changes
- Unaffected parts MUST remain unchanged

CHANGE LOCALIZATION RULE:
- Modify ONLY elements directly affected by requirement changes
- Do NOT propagate changes beyond required scope

STRUCTURAL STABILITY RULE:
- Preserve class, method, and attribute names unless change is required
- Do NOT reorganize architecture structure
- Do NOT split or merge classes unless necessary

USE CASE CONSISTENCY RULE:
- Updated Use Case defines intended behavior
- Architecture MUST reflect all behavior from the updated Use Case
- If conflict exists → follow the Use Case

STATE RULE:
- Persistent data MUST be stored in class attributes
- Shared data across methods MUST NOT be local variables

CONSTRAINTS:
- MUST NOT convert bugs into requirements
- MUST NOT introduce functionality not in feedback or Use Case
- MUST NOT remove correct existing behavior
- MUST keep architecture minimal

FORBIDDEN:
- refactoring unrelated parts
- renaming without necessity
- adding unnecessary classes or methods
- speculative improvements
- assumptions not grounded in inputs

OUTPUT FORMAT:
- Do not include explanations or commentary outside the JSON.
- Return ONLY valid JSON using the SAME schema:

{{
"classes": [
    {{
    "name": "string",
    "responsibility": "string",
    "attributes": [
        {{"name": "string", "type": "string", "description": "string"}}
    ],
    "methods": [
        {{
        "name": "string",
        "summary": "string",
        "description": "string",
        "steps": ["string"],
        "inputs": [{{"name": "string", "type": "string", "description": "string"}}],
        "outputs": [{{"name": "string", "type": "string", "description": "string"}}],
        "special requirements": ["string"]
        }}
    ]
    }}
]
}}
"""


REVIEW_INITIAL_DESIGN_PROMPT = """
ROLE:
Strict validator of Python software architectures

TASK:
Detect real defects where the architecture fails to correctly implement the Use Case

INPUTS:
Current Architecture:
{architecture}

Use Case:
{useCase}

User Task:
{userTask}

PRIORITY:
1. Requirement coverage (highest priority)
2. Correct representation of behavior in methods
3. State consistency and persistence

COVERAGE RULE:
- EVERY behavior and requirement from the Use Case MUST be represented in the architecture
- Behavior and requirement is considered covered ONLY if it appears in method: summary, description, steps, inputs, outputs or requirements
- Missing behavior or requirement MUST be reported as a defect

METHOD VALIDATION RULE:
- Methods MUST represent real system actions
- Methods MUST align with Use Case steps
- Methods MUST include sufficient steps for implementation
- Report vague, incomplete, or non-actionable methods as defects

STATE CONSISTENCY RULE:
- Any data used across multiple steps MUST exist as a class attribute with a specific name
- If a method reads/writes persistent data → it MUST be an attribute
- Missing persistent state MUST be reported as a defect

DEFECT DEFINITION:
Report an issue ONLY if:
- required behavior is missing or incorrectly represented
- method logic is incomplete or inconsistent
- persistent state is missing or incorrectly modeled

MINIMALITY ENFORCEMENT:
- Do NOT require additional attributes or methods unless their absence prevents correct behavior or requirements

CONSTRAINTS:
- MUST report only real, evidence-based defects
- MUST focus on functionality and correctness
- MUST NOT report stylistic or design preferences
- MUST NOT require restructuring if behavior is correct
- MUST NOT mention correct parts

FORBIDDEN:
- hypothetical improvements
- overengineering suggestions
- splitting classes without necessity
- assumptions not grounded in inputs

SCORING RULES:
- 1.00 → complete coverage, no defects
- 0.90–0.99 → only minor issues
- 0.60–0.89 → noticeable missing behavior or inconsistencies
- <0.60 → major missing functionality

SCORING CONSTRAINT:
- If ANY required behavior or special requirement is missing → score < 0.90
- If ALL behavior and special requirements are covered and all issues are minor → score ≥ 0.90
- Score MUST reflect severity AND number of defects

OUTPUT FORMAT:
- Do not include explanations or commentary outside the JSON.
- Return ONLY valid JSON in the following format:

{{
"score": <float 0.00–1.00>,
"issues": ["issue 1", "issue 2"]
}}

OUTPUT RULES:
- Max 7 issues, ordered by importance
- Fewer if fewer real defects exist, no valuable issues is also an option
- Empty list if no defects
"""

REVIEW_DESIGN_AFTER_FEEDBACK_PROMPT = """
ROLE:
Strict validator of architecture revisions after feedback

TASK:
Validate whether feedback-driven changes were correctly applied without breaking existing functionality

INPUTS:
Previous Architecture:
{previousArchitecture}

Current Architecture:
{architecture}

Updated Use Case:
{useCase}

User Feedback:
{usersFeedback}

PRIORITY:
1. Feedback adaptation (correctness and completeness)
2. Preservation of unaffected functionality
3. Requirement coverage from Use Case

FEEDBACK CLASSIFICATION:
Interpret feedback as:

1. REQUIREMENT CHANGE (APPLY):
- new functionality is requested
- existing functionality must behave differently
- constraints or rules are changed

2. IMPLEMENTATION ISSUE (IGNORE):
- bug reports
- incorrect outputs
- performance problems
- technical errors

RULE:
- ONLY REQUIREMENT CHANGE items must affect the architecture
- IMPLEMENTATION ISSUE items must NOT change architecture

VALIDATION AXES:

1. FEEDBACK ADAPTATION:
- All requirement-level changes MUST be reflected
- Report missing, partial, or incorrect implementation

2. PRESERVATION:
- Compare Previous vs Current Architecture
- Unaffected functionality MUST remain unchanged
- Report removed or altered correct behavior

3. COVERAGE:
- ALL behavior from Updated Use Case MUST be represented
- Behavior and requirements must appear in methods (summary, description, steps, inputs, outputs, special requirements)

DEFECT DEFINITION:
Report an issue ONLY if:
- a required feedback change is missing or incorrect
- correct existing functionality was altered or removed
- required behavior or requirement from Use Case is missing
- architecture is logically inconsistent

CONSTRAINTS:
- MUST report only real, evidence-based defects
- MUST NOT report stylistic or structural preferences
- MUST NOT suggest improvements or redesigns
- MUST NOT overanalyze edge cases
- MUST NOT mention correct parts

FORBIDDEN:
- interpreting bugs as requirements
- hypothetical improvements
- assumptions not grounded in inputs
- restating architectures

SCORING RULES:
- 1.00 → feedback correctly applied, no defects
- 0.90–0.99 → only minor inconsistencies
- 0.60–0.89 → noticeable defects
- <0.60 → missing feedback or broken functionality

SCORING CONSTRAINT:
- Missing or incorrect feedback application → score < 0.90
- Missing required behavior or missing requirements → score < 0.90
- If feedback correctly applied and behavior preserved → score ≥ 0.90
- Score MUST reflect severity AND number of defects

OUTPUT FORMAT:
- Do not include explanations or commentary outside the JSON.
- Return ONLY valid JSON in the following format:

{{
"score": <float 0.00–1.00>,
"issues": ["issue 1", "issue 2"]
}}

OUTPUT RULES:
- Max 7 issues, ordered by importance
- Fewer if fewer real defects exist
- Empty list if no defects
"""