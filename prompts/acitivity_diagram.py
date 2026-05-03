INITIAL_GENERATION_DIAGRAM_PROMPT = """
ROLE:
Expert in UML activity diagrams and program flow modeling

TASK:
Generate a minimal and syntactically correct PlantUML activity diagram representing real execution flow

INPUTS:
Architecture (reference only):
{architecture}

Use Case (interpretation aid):
{useCase}

Source Code (PRIMARY SOURCE OF TRUTH):
{finalProgram}

PRIORITY:
1. Correct execution flow from code
2. Valid PlantUML syntax
3. Simplicity and readability

SOURCE OF TRUTH RULE:
- Derive behavior ONLY from source code
- Use Use Case ONLY to clarify intent
- Do NOT invent actions not present in code

ENTRY POINT RULE:
- Start from main() or program entry point
- If no explicit main → infer top-level execution flow

FLOW RULES:
- Follow actual execution order
- Include major method calls and decisions
- Include conditions and loops ONLY if explicitly present
- Ensure full flow from start to stop

ABSTRACTION RULE:
- Convert code logic into high-level actions
- Use short verb-based phrases
- Do NOT include:
- code syntax
- variable names
- method names
- implementation details

ACTION RULES:
- Each action represents a meaningful system step
- Keep actions concise and readable
- Each action MUST end with ';'

CONDITION RULES:
- Use conceptual conditions (not code expressions)
- Keep conditions short and readable

DIAGRAM RULES:
- Use ONLY:
start / stop
:action;
if / else / endif
while / endwhile
repeat / repeat while

STRUCTURE RULES:
- Every if MUST have endif
- Every loop MUST be properly closed
- Avoid deep nesting
- Maximum 20 actions

FLOW COMPLETENESS:
- Diagram MUST represent complete execution path
- No disconnected or partial flows

CONSTRAINTS:
- Output ONLY PlantUML code
- MUST start with '@startuml' and end with '@enduml'

FORBIDDEN:
- explanations or comments
- copying code into diagram
- using technical identifiers
- inventing behavior
- using unsupported UML constructs (fork, join, notes, arrows)

OUTPUT FORMAT:
Return ONLY valid PlantUML code

EXAMPLE:
@startuml
start
:initialize system;
if (valid input) then (yes)
:process request;
else (no)
:handle error;
endif
stop
@enduml
"""

REVIEW_GENERATION_DIAGRAM_PROMPT = """
ROLE:
Expert in revising PlantUML activity diagrams

TASK:
Apply minimal corrections to the diagram strictly based on the review issues

INPUTS:
Review Issues:
{activityDiagramReview}

Current Diagram:
{activityDiagram}

PRIORITY:
1. Maintain valid PlantUML syntax
2. Apply review corrections
3. Preserve existing structure and flow

PATCHING PRINCIPLE:
- Treat current diagram as authoritative baseline
- Apply ONLY minimal necessary changes
- Unchanged lines MUST remain identical

ISSUE-TO-CHANGE RULE:
- Each modification MUST directly correspond to a review issue
- Do NOT modify anything not mentioned in the review

CHANGE LOCALIZATION:
- Modify ONLY parts directly affected by issues
- Do NOT propagate changes beyond required scope

FLOW PRESERVATION:
- Preserve existing correct execution flow
- Do NOT alter behavior unless required by review

REVIEW INTERPRETATION:
- Apply ONLY explicitly stated issues
- Do NOT expand or reinterpret review
- Do NOT introduce additional improvements

SYNTAX RULES:
- Output MUST be valid PlantUML
- MUST start with @startuml and end with @enduml
- All control structures MUST be balanced (if/endif, loops)

CONSTRAINTS:
- MUST NOT rewrite entire diagram unless absolutely necessary
- MUST NOT introduce new behavior
- MUST NOT remove correct existing steps
- MUST preserve diagram structure

FORBIDDEN:
- refactoring or simplifying diagram
- renaming actions unnecessarily
- adding new actions not required by review
- reordering flow without necessity
- stylistic improvements

OUTPUT FORMAT:
Return ONLY valid PlantUML code
Do not include explanations or comments outside the code
"""

REVIEW_INITIAL_DIAGRAM_PROMPT = """
ROLE:
Strict reviewer of PlantUML activity diagrams

TASK:
Identify real defects in the activity diagram with respect to syntax and actual program execution flow

INPUTS:
Activity Diagram:
{activityDiagram}

Program (SOURCE OF TRUTH):
{finalProgram}

Use Case (reference only):
{useCase}

PRIORITY:
1. PlantUML syntax correctness
2. Execution flow correctness
3. Behavioral completeness
4. Proper abstraction level

SOURCE OF TRUTH RULE:
- Program defines actual behavior
- Diagram MUST match program execution
- Use Case is only for interpretation support

DEFECT DEFINITION:
Report an issue ONLY if:
- PlantUML syntax is invalid or incomplete
- execution flow is incorrect or inconsistent with program
- required behavior is missing in diagram
- diagram includes behavior not present in program
- abstraction level is clearly incorrect (too low or missing key steps)

VALIDATION AREAS:

1. SYNTAX:
- Missing @startuml / @enduml
- Invalid or unsupported syntax
- Unbalanced structures (if/endif, loops)

2. FLOW CORRECTNESS:
- Incorrect execution order
- Missing major branches or decisions
- Illogical or unreachable flow

3. BEHAVIOR COVERAGE:
- Missing key steps from execution
- Missing entry point (main or equivalent)

4. ABSTRACTION:
- Presence of code-level details (variables, method names)
- Missing essential high-level actions

CONSTRAINTS:
- MUST report only real, evidence-based defects
- MUST NOT infer issues without clear evidence
- MUST NOT report stylistic preferences
- MUST NOT propose redesign or improvements
- MUST NOT mention correct parts

FORBIDDEN:
- overanalysis beyond visible diagram
- assumptions not grounded in code
- suggesting better wording or style
- enforcing subjective diagram preferences

OUTPUT FORMAT:
- Use bullet points starting with "- "
- One bullet = one issue
- Maximum 7 issues, ordered by importance
- Fewer if fewer real defects exist
- If no issues exist → output exactly: OK

OUTPUT RULE:
- Output ONLY the issues or OK
- Do not include explanations or commentary outside the list of issues
"""

FEEDBACK_TYPE_PROMPT = """
ROLE:
Strict classifier of user feedback for requirement vs implementation changes

TASK:
Classify whether feedback requires updating system requirements or only fixing implementation

INPUTS:
User Feedback:
{feedback}

Current Use Case:
{useCase}

Current Architecture:
{architecture}

PRIORITY:
1. Detect changes in intended system behavior
2. Distinguish bugs from requirement changes
3. Avoid false positives for requirement updates

BEHAVIOR DELTA RULE:
- Compare feedback with current Use Case and Architecture
- Determine whether feedback describes:
- incorrect implementation of existing behavior
OR
- a change in intended behavior

CLASSIFICATION:

CODE_FIX:
- Feedback describes bugs, incorrect outputs, or missing functionality
- Behavior is ALREADY defined in Use Case or Architecture
- System failed to implement existing requirement correctly

USE_CASE_UPDATE:
- Feedback introduces NEW behavior not present in Use Case or Architecture
- Feedback CHANGES existing behavior or expected outcomes
- Feedback modifies rules, constraints, or logic

DECISION RULE:
- If behavior in feedback ≠ behavior in Use Case → USE_CASE_UPDATE
- If behavior in feedback = already defined → CODE_FIX

MIXED FEEDBACK RULE:
- If feedback contains BOTH bug reports AND new/changed requirements → USE_CASE_UPDATE

CONSERVATIVE RULE:
- If uncertain → classify as CODE_FIX
- Do NOT assume new requirements unless clearly stated

CONSTRAINTS:
- MUST base decision on explicit evidence
- MUST compare against Use Case and Architecture
- MUST NOT treat bugs as new requirements
- MUST NOT expand or reinterpret feedback

FORBIDDEN:
- inferring unstated requirements
- over-interpreting vague feedback
- assuming intent beyond explicit text
- classifying based on wording alone

OUTPUT FORMAT:
- Do not include explanations or commentary outside the JSON
- Return ONLY valid JSON in the following format:

{{
"classification": "CODE_FIX" or "USE_CASE_UPDATE"
}}
"""