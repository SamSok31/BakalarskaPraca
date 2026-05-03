INITIAL_USECASE_GENERATION_PROMPT = """
ROLE:
Senior software engineer specialized in requirements analysis

TASK:
Transform the user task into a structured Use Case by extracting all functional requirements and analyzing the user task.

INPUT:
User Task:
{userTask}

PRIORITY:
1. Extract ALL functional requirements from the user task
2. Ensure completeness of system behavior
3. Keep abstraction suitable for architecture design

REQUIREMENT EXTRACTION RULES:
- MUST include all explicitly stated requirements
- MUST include necessary implied requirements that are clearly required for correct behavior
- MUST NOT invent new big functionality beyond what is logically implied
- MUST resolve ambiguities conservatively based on the task
- MUST stay at system behavior level (no implementation details)

SECTION RULES:
- Goal = main objective of the actor
- System Responsibilities = system capabilities (not steps)
- Preconditions = required system state before execution
- Postconditions = resulting system state after success
- Main Success Scenario = step-by-step interaction flow
- Extensions = alternative or exceptional flows
- Special Requirements = constraints (UI, libraries, performance)

FORBIDDEN:
- algorithms or data structures
- class/method descriptions

REFERENCE EXAMPLE:
Use Case: Draw Circle on Canvas
Primary Actor: User
Goal: Create a circle on the drawing canvas.

System Responsibilities:
- Maintain the state of the drawing canvas.
- Process user click events on the canvas.
- Generate graphical shapes based on user actions.
- Render shapes on the canvas.

Preconditions:
- The application window is open.
- A drawing canvas is visible to the user.

Postconditions:
- A circle is displayed on the canvas at the selected position.

Main Success Scenario:
1. User selects the circle drawing tool.
2. User clicks on a position on the canvas.
3. System receives the click coordinates.
4. System generates a circle centered at the selected position.
5. System renders the circle on the canvas.

Extensions:
2a. Click occurs outside the canvas → System ignores the input.

Special Requirements:
- The circle should be clearly visible on the canvas.
- The graphical interface must be implemented using the Tkinter library.
- The canvas should update immediately after the shape is created.

OUTPUT FORMAT:
- Return ONLY the Use Case. Do NOT include explanations or commentary outside the Use Case structure
- Preserve exact section structure from the reference
"""

REVIEW_USECASE_REVISION_PROMPT = """
ROLE:
Senior software engineer specialized in revising Use Cases

TASK:
Apply corrections to the Use Case strictly based on the provided review issues

INPUTS:
Current Use Case:
{useCase}

Review Issues:
{issues}

PRIORITY:
1. Review issues may be incorrect or over-strict, analyze them, validate them whether the review issue is REAL before applying fix
2. Correct defects identified in valid review issues
3. Preserve original content and structure
4. Minimize scope of changes

PATCHING PRINCIPLE:
- Treat the current Use Case as the authoritative base
- Apply only minimal necessary changes
- Unaffected content MUST remain unchanged
- Prefer editing specific lines instead of rewriting sections

CHANGE RULES:
- Modify ONLY parts directly related to review issues
- Preserve all correct behavior and requirements
- Do NOT rephrase or improve unrelated text
- Do NOT expand beyond the scope of issues

CONSTRAINTS:
- MUST apply only explicitly listed issues
- MUST NOT introduce new functionality unless required by issues
- MUST preserve exact section names and order
- MUST maintain internal consistency after changes

SECTION RULES:
- Goal = main objective of the actor
- System Responsibilities = system capabilities (not steps)
- Preconditions = required system state before execution
- Postconditions = resulting system state after success
- Main Success Scenario = step-by-step interaction flow
- Extensions = alternative or exceptional flows
- Special Requirements = constraints (UI, libraries, performance)

FORBIDDEN:
- rewriting entire sections
- stylistic improvements
- adding new requirements not present in issues
- removing correct existing behavior

OUTPUT FORMAT:
- Return ONLY the revised Use Case. Do NOT include explanations or commentary outside the Use Case structure.
- Preserve exact structure and sections from the current Use Case.
"""

FEEDBACK_USECASE_REVISION_PROMPT = """
ROLE:
Senior software engineer specialized in updating Use Cases from user feedback

TASK:
Update the Use Case on the basis of the user feedback which implies a change in intended system behavior

INPUTS:
Current Use Case:
{useCase}

User Feedback:
{feedback}

PRIORITY:
1. Detect requirement-level changes in feedback
2. Preserve all existing correct functionality
3. Minimize scope of changes

FEEDBACK CLASSIFICATION:
Feedback may contain:

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
- IGNORE implementation issues unless they clearly imply a change in intended behavior

PATCHING PRINCIPLE:
- Treat current Use Case as authoritative base
- Apply minimal necessary changes
- Unaffected content MUST remain unchanged

CHANGE RULES:
- Modify ONLY parts directly affected by requirement changes
- Preserve all correct existing behavior
- Do NOT rewrite sections unnecessarily
- Do NOT expand beyond feedback scope

CONSTRAINTS:
- MUST NOT convert bugs into requirements
- MUST NOT introduce new functionality not present in feedback
- MUST preserve exact section names and order
- MUST maintain internal consistency after changes

CONSISTENCY RULE:
- Ensure updated behavior is reflected in Main Success Scenario
- Ensure no contradictions between sections

SECTION RULES:
- Goal = main objective of the actor
- System Responsibilities = system capabilities (not steps)
- Preconditions = required system state before execution
- Postconditions = resulting system state after success
- Main Success Scenario = step-by-step interaction flow
- Extensions = alternative or exceptional flows
- Special Requirements = constraints (UI, libraries, performance)

FORBIDDEN:
- interpreting bugs as new requirements
- speculative improvements
- rewriting unrelated parts
- removing correct functionality

OUTPUT FORMAT:
- Return ONLY the revised Use Case. Do NOT include explanations or commentary outside the Use Case structure.
- Preserve exact structure and sections from the current Use Case.
"""


REVIEW_INITIAL_GENERATION_USECASE_PROMPT = """
ROLE:
Strict validator of software Use Cases

TASK:
Detect real defects where the Use Case fails to correctly represent the User Task

INPUTS:
Use Case:
{useCase}

User Task:
{userTask}

PRIORITY:
1. Requirement coverage (missing or incorrect functionality)
2. Scenario correctness (missing, inconsistent, or illogical steps)
3. Internal consistency across sections

DEFECT DEFINITION:
Report an issue ONLY if:
- a required behavior or requierements from the User Task is missing, incorrect, or unclear
- a step in the scenario is logically invalid or inconsistent
- there is a contradiction between sections

NON-DEFECTS (IGNORE):
- wording preferences
- stylistic improvements
- optional enhancements
- alternative valid interpretations

CONSTRAINTS:
- MUST report only real, evidence-based defects
- MUST focus on functional correctness and completeness
- MUST NOT suggest improvements or rewrites
- MUST NOT require structural changes
- MUST NOT overanalyze edge cases
- MUST NOT mention correct parts

FORBIDDEN:
- DO NOT propose changes that are against the user task
- hypothetical problems
- assumptions not grounded in the inputs
- questioning requirements or functional behaviour which is defined in the user task
- restating or summarizing the Use Case
- expanding scope beyond the User Task
- DO NOT hallucinate or create issues that are not evidence-based defects

SCORING RULES:
- 1.00 → no defects
- 0.90–0.99 → only minor clarifications compared to the user task
- 0.60–0.89 → noticeable defects affecting correctness or completeness of the user task
- <0.60 → major missing or incorrect functionality

SCORING CONSTRAINT:
- If ANY required functionality from the user task is missing or incorrect → score < 0.90
- If ALL requirements and functionality from the user task are correctly represented → score ≥ 0.90
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
- Fewer if fewer real defects exist, no valuable defects is also an option
- Empty list if no defects
"""

REVIEW_GENERATION_AFTER_FEEDBACK_USECASE_PROMPT = """
ROLE:
Strict validator of Use Case revisions after feedback

TASK:
Validate whether feedback-driven changes were correctly applied without breaking existing functionality

INPUTS:
Previous Use Case:
{previousUseCase}

Revised Use Case:
{useCase}

User Feedback:
{feedback}

PRIORITY:
1. Feedback adaptation (correctness and completeness)
2. Preservation of unaffected functionality
3. Internal consistency across sections

FEEDBACK CLASSIFICATION:
Interpret feedback as:

1. REQUIREMENT CHANGE (must be applied)
- new functionality is requested
- existing functionality must behave differently
- constraints or rules are changed

2. IMPLEMENTATION ISSUE (must be ignored)
- bug reports
- incorrect outputs
- performance problems
- technical errors

RULE:
- ONLY REQUIREMENT CHANGE items must be reflected in the Use Case
- IMPLEMENTATION ISSUE items must NOT affect the Use Case

VALIDATION AXES:

1. FEEDBACK ADAPTATION:
- All requirement-level changes MUST be present
- Report if missing, partial, or incorrectly applied

2. PRESERVATION:
- Compare Previous vs Revised Use Case
- Unaffected functionality MUST remain unchanged
- Report removed or altered correct behavior

3. CONSISTENCY:
- No contradictions between sections
- Main Success Scenario must reflect updated behavior

DEFECT DEFINITION:
Report an issue ONLY if:
- a required feedback change is missing or incorrect
- unaffected behavior was altered or removed
- logical inconsistency exists

CONSTRAINTS:
- MUST report only real, evidence-based defects
- MUST NOT report stylistic or wording issues
- MUST NOT suggest improvements or rewrites
- MUST NOT require structural changes
- MUST NOT overanalyze edge cases
- MUST NOT mention correct parts

FORBIDDEN:
- interpreting bugs as requirements
- hypothetical improvements
- assumptions not grounded in inputs
- questioning requirements or functional behaviour mentioned in the user feedback
- DO NOT propose changes that are against the user feedback
- restating the Use Cases
- DO NOT hallucinate or creating issues that are not evidence-based defects

SCORING RULES:
- 1.00 → feedback correctly applied, no defects
- 0.90–0.99 → only minor inconsistencies compared to the feedback
- 0.60–0.89 → noticeable defects affecting correctness or completeness
- <0.60 → missing feedback or broken functionality

SCORING CONSTRAINT:
- Missing or incorrect feedback application → score < 0.90
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
- Fewer if fewer real defects exist, no valuable defects is also an option
- Empty list if no defects
"""