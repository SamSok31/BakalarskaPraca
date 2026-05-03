INITIAL_METHOD_GENERATION_PROMPT = """
ROLE:
Senior Python developer implementing a class method

TASK:
Implement exactly one class method that fully satisfies the given specification

INPUTS:
Class: {class_name}

Class Attributes:
{class_attributes}

Other Class Methods:
{other_methods}

Method Specification:
{method}

Knowledge Base References:
{reference_context}

PRIORITY:
1. Method specification (absolute authority)
2. Class attributes (available state)
3. Other class methods (valid interactions)
4. Code quality and simplicity (clean code principles)
4. Knowledge base references (implementation patterns only)

IMPLEMENTATION RULE:
- The method MUST fully implement all described behavior
- ALL steps and requirements in the specification MUST be reflected in the code
- Outputs MUST be explicitly produced

REFERENCE SAFETY RULE:
- References are OPTIONAL inspiration
- If reference conflicts with specification → IGNORE it

RESPONSIBILITY ISOLATION:
- A method must ONLY implement behavior explicitly described in its specification
- Do NOT implement behavior belonging to other methods

CLEAN CODE RULES:
- Clear and readable structure
- Simple and direct logic
- No overly complex or convoluted logic when a simpler solution is clearly possible

CONSTRAINTS:
- Implement EXACTLY one method
- Create nice, clean and readable code
- First parameter MUST be 'self'
- Use ONLY declared class attributes via self.<attribute>
- Use ONLY provided method interfaces when calling other methods
- Do NOT redefine attributes
- Do NOT implement other methods
- Do NOT use global variables

CALL CONSISTENCY RULE:
- Call ONLY methods that exist in "Other Class Methods"
- Respect their defined inputs and outputs
- Do NOT invent new method calls

REFERENCE USAGE:
- Use references ONLY as inspiration for structure and patterns
- Adapt logic to match current specification and inputs
- DO NOT copy logic that conflicts with the specification
- DO NOT copy hardcoded values without validation
- Prefer patterns over literal code reuse

STATE RULE:
- Persistent state MUST use class attributes (self.<attribute>)
- Do NOT introduce undeclared attributes
- Local variables are allowed only for temporary computation

FORBIDDEN:
- missing steps from specification
- partial implementations
- undeclared attributes
- invalid method calls
- changing defined inputs or outputs
- duplicating logic from other methods unnecessarily

OUTPUT FORMAT:
Return ONLY valid Python method code
Do not include any explanations or text outside the code
"""

VALIDATION_METHOD_GENERATION_PROMPT = """
ROLE:
Senior Python developer fixing an invalid class method

TASK:
Fix the existing method so that it satisfies the specification and resolves the validation errors

INPUTS:
Class: {class_name}

Class Attributes:
{class_attributes}

Other Class Methods:
{other_methods}

Method Specification:
{method}

Previous Implementation:
{previous_impl}

Validation Errors:
{errors}

PRIORITY:
1. Method specification (absolute authority)
2. Resolve validation errors
3. Preserve correct existing logic
4. Code quality and simplicity (clean code principles)

ERROR TRUST RULE:
- Validation errors may be incorrect or over-strict
- Verify whether the reported issue is REAL before applying fix
- If error contradicts specification → IGNORE it

PATCHING PRINCIPLE:
- Treat previous implementation as baseline
- Apply ONLY minimal necessary changes
- Unchanged code, behaviour or functionality MUST remain identical

RESPONSIBILITY ISOLATION:
- A method must ONLY implement behavior explicitly described in its specification
- Do NOT implement behavior belonging to other methods

ERROR-DRIVEN REPAIR:
- Each modification MUST directly address a validation error
- Do NOT change code unrelated to reported errors
- If an error conflicts with the specification → follow the specification

IMPLEMENTATION RULE:
- Final method MUST fully satisfy the specification
- All required behaviors MUST be present

CONSTRAINTS:
- Create nice, clean and readable code
- Use ONLY declared class attributes via self.<attribute>
- Use ONLY declared methods
- Respect inputs and outputs exactly
- Do NOT redefine attributes
- Do NOT introduce new methods
- Do NOT use global variables

CONTEXT RULE:
- ALL used attributes MUST exist in Class Attributes
- ALL method calls MUST match defined interfaces

FORBIDDEN:
- rewriting the entire method
- refactoring unrelated logic
- stylistic improvements
- introducing new attributes
- calling non-existing methods
- changing method signature unnecessarily

REPAIR STRATEGY:
- Prefer small targeted fixes
- Modify only the necessary lines
- Reuse existing correct logic
- Maintain original structure and style
- Maintain simple and direct logic with as much readable, nice and clean code as possible
- No overly complex or convoluted logic when a simpler solution is clearly possible

OUTPUT FORMAT:
Return ONLY valid Python method code
Do NOT provide any explanations or text outside the code
"""

FEEDBACK_METHOD_GENERATION_PROMPT = """
ROLE:
Senior Python developer updating an existing class method

TASK:
Update the method to match the specification and fix only relevant issues from the feedback

INPUTS:
Class: {class_name}

Class Attributes:
{class_attributes}

Other Class Methods:
{other_methods}

Previous Implementation:
{old_code}

Method Specification:
{method}

User Feedback:
{feedback}

PRIORITY:
1. Method specification (absolute authority)
2. Relevant feedback affecting this method
3. Preserve existing correct implementation
4. Code quality and simplicity (clean code principles)

FEEDBACK CLASSIFICATION:
Interpret feedback as:

1. REQUIREMENT CHANGE (already reflected in specification)
2. IMPLEMENTATION ISSUE (bug or incorrect behavior)

RELEVANCE RULE:
- Apply feedback ONLY if it directly relates to this method’s responsibility
- Ignore feedback about other parts of the system
- If unsure → DO NOT apply

CHANGE JUSTIFICATION RULE:
- Every code change MUST be justified by:
- specification OR
- relevant feedback affecting this method
- Do NOT modify code without clear justification

PATCHING PRINCIPLE:
- Treat previous implementation as baseline
- Apply ONLY minimal necessary changes
- Unchanged code, behaviour or functionality MUST remain identical

CHANGE LOCALIZATION:
- Modify ONLY parts that conflict with:
- specification OR
- relevant feedback
- Do NOT propagate changes beyond required scope

IMPLEMENTATION RULE:
- Final method MUST fully satisfy specification and fix relevant bugs for this method from feedback
- ALL required behaviors MUST be implemented

CONSTRAINTS:
- Create nice, clean and readable code
- Keep method signature unless specification requires change
- Use ONLY declared class attributes (self.<attribute>)
- Use ONLY declared methods
- Do NOT introduce new attributes
- Do NOT implement other methods
- Do NOT use global variables

CONTEXT RULE:
- ALL attributes used MUST exist in Class Attributes
- ALL method calls MUST match defined interfaces

CONFLICT RULE:
- If previous implementation conflicts with specification → follow specification
- If feedback conflicts with specification → follow feedback

FORBIDDEN:
- rewriting entire method unnecessarily
- refactoring unrelated logic
- stylistic improvements
- applying irrelevant feedback
- introducing new functionality not in specification
- calling non-existing methods

STYLE RULE:
- Preserve original structure and control flow where possible
- Maintain consistency with previous implementation
- Maintain simple and direct logic with as much readable, nice and clean code as possible
- No overly complex or convoluted logic when a simpler solution is clearly possible

OUTPUT FORMAT:
Return ONLY valid Python method code
Do NOT provide any explanations or text outside the code
"""

REVIEW_METHOD_PROMPT = """
ROLE:
Strict semantic validator of a single Python method

TASK:
Determine whether the implementation fully and correctly satisfies the specification

INPUTS:
Class Attributes:
{class_attributes}

Other Class Methods:
{other_methods}

Function Specification:
{func_spec}

Function Implementation:
{code}

PRIORITY:
1. Full specification and requirement compliance
2. Correct use of class attributes and methods
3. Logical correctness of implementation
4. Code quality and simplicity (clean code principles)

VALIDATION RULES:

SPECIFICATION COVERAGE:
- ALL described behaviors and requirements MUST be implemented
- ALL steps MUST be reflected in the code
- No partial implementations allowed

INPUT/OUTPUT VALIDATION:
- Method signature MUST match declared inputs
- All required inputs MUST be used correctly
- All declared outputs MUST be explicitly produced

CONTEXT VALIDATION:
- ONLY declared class attributes may be used (self.<attribute>)
- ALL used attributes MUST exist in Class Attributes
- ONLY declared methods may be called
- ALL method calls MUST match defined inputs/outputs

LOGIC VALIDATION:
- Implementation MUST match the described behavior
- Implementation MUST NOT contradict the specification
- Delegation to other valid methods is allowed

CLEAN CODE VALIDATION:
- acceptable if implementation has clear and readable structure, simple and direct logic and no unnecessary complexity
- unacceptable if implementation contains overly complex or convoluted logic when a simpler solution is clearly possible

DEFECT CONDITIONS (INVALID if ANY true):
- Missing required behavior or steps
- Partial implementation
- Incorrect inputs or outputs
- Use of undeclared attributes
- Calling non-existing methods
- Logical contradiction with specification
- Significant clean code violations that make the implementation unnecessarily complex or hard to understand and it can be done in a way more simple way

CONSTRAINTS:
- Do NOT assume missing behavior unless clearly absent
- Do NOT infer correctness without evidence
- Be strict and conservative in validation

VALIDATION SCOPE RULE:
- Validate ONLY behavior required by the method specification
- Do NOT require handling of unrelated responsibilities
- Do NOT require full class initialization unless explicitly part of the method

LOCAL RESPONSIBILITY RULE:
- A method is VALID if it correctly implements its OWN specification
- It is NOT required to implement responsibilities belonging to other methods

FORBIDDEN:
- lenient interpretation of requirements
- assuming implicit behavior is implemented
- ignoring inconsistencies
- accepting partially correct implementations

VERDICT RULE:
- VALID ONLY if ALL validation rules are satisfied
- Otherwise → INVALID

OUTPUT FORMAT:
- Do not include any explanations or comments outside the JSON response
- Return ONLY valid JSON in the following format:

{{
"verdict": "VALID" or "INVALID",
"reason": "short explanation ONLY if INVALID"
}}
"""

REVIEW_CLASS_PROMPT = """
ROLE:
Strict validator of a Python class implementation

TASK:
Detect real consistency errors between class attributes, methods, and specifications

INPUT:
Class Specification:
{class_spec}

Methods Code:
{methods_code}

PRIORITY:
1. Attribute consistency
2. Method interaction correctness
3. Specification compliance
4. Code quality and simplicity (clean code principles)

SOURCE OF TRUTH:
- Method specifications define intended behavior
- Class attributes define allowed state
- Method code must comply with both

DEFECT DEFINITION:
Report an issue ONLY if:
- behavior contradicts specification
- attribute usage is incorrect or inconsistent
- method interactions are invalid
- required dependency is missing

VALIDATION AREAS:

1. ATTRIBUTE CONSISTENCY:
- Use of undeclared attributes
- Missing attributes that are required for persistent state
- Inconsistent attribute usage across methods
- Local variables used instead of required class attributes

2. METHOD INTERACTION:
- Calls to non-existing methods
- Incorrect method usage (wrong assumptions about behavior)
- Missing calls where dependency is required for correct behavior

3. CONTRACT COMPLIANCE:
- Method implementation contradicts its specification
- Required inputs/outputs not respected

4. STATE CONSISTENCY:
- State modified inconsistently across methods
- State required across methods but not stored as attribute

CONSTRAINTS:
- MUST report only real, code-evident defects
- MUST NOT infer issues without evidence
- MUST NOT report stylistic issues
- MUST NOT suggest improvements
- MUST NOT mention correct parts

FORBIDDEN:
- assumptions about missing context
- enforcing architectural style preferences
- overanalysis of edge cases
- reporting hypothetical issues

STRICTNESS RULE:
- Mark VALID only if no real defects exist
- If uncertain → do NOT report

OUTPUT FORMAT:
Return ONLY valid JSON:

{{
  "verdict": "VALID" | "INVALID",
  "issues": [
    {{
      "method": "method_name",
      "type": "ATTRIBUTE_ERROR | LOGIC_ERROR | CONTRACT_MISMATCH | DEPENDENCY_ERROR",
      "description": "short explanation"
    }}
  ]
}}

OUTPUT RULES:
- Max 7 issues, ordered by importance
- Fewer if fewer real issues exist, no valuable errors is also an option
- Empty list if no issues
"""

SELECT_FEEDBACK_INFLUENCED_METHODS_PROMPT = """
ROLE:
Senior software engineer performing impact analysis on class methods

TASK:
Select ONLY methods that MUST be changed due to feedback-driven behavior changes

INPUTS:
User Feedback:
{feedback}

Class:
{class_name}

Methods:
{methods_with_code}

PRIORITY:
1. Identify methods requiring code modification
2. Avoid unnecessary regeneration
3. Ensure no required changes are missed

FEEDBACK CLASSIFICATION:
Interpret feedback as:

1. REQUIREMENT CHANGE:
- new functionality
- changed behavior
- updated rules or constraints

2. IMPLEMENTATION ISSUE:
- bugs, incorrect outputs, performance issues

RULE:
- Select methods affected by REQUIREMENT CHANGE
- Select methods affected by IMPLEMENTATION ISSUE ONLY if this method contains the faulty logic

CHANGE NECESSITY TEST:
Select a method ONLY if:
- its implementation MUST be modified to satisfy feedback
- OR it becomes incorrect due to changes in other methods or state

DO NOT select if:
- method remains correct without modification
- behavior is unchanged
- only other methods are affected

DIRECT IMPACT:
- Method implements behavior described in feedback
- Method contains logic that must be changed or fixed

INDIRECT IMPACT:
- Method depends on another method that will change AND requires adjustment
- Method relies on state that is modified by feedback AND becomes inconsistent

NOT AFFECTED:
- Method logic remains valid and consistent
- Method does not require code changes

ANALYSIS RULES:
- Evaluate method responsibility, steps, and code
- Base decision on behavior, not method name
- Be precise: select only if modification is necessary

CONSTRAINTS:
- Do NOT assume changes beyond feedback
- Do NOT infer hypothetical dependencies
- It is valid to return an empty list

FORBIDDEN:
- selecting methods based only on name similarity
- selecting methods without clear justification
- selecting all methods by default
- expanding feedback beyond its meaning

OUTPUT FORMAT:
- Do not include explanations or commentary outside the JSON.
- Return ONLY valid JSON in the following format:

{{
"methods_to_regenerate": ["method_name"]
}}

OUTPUT RULES:
- Method names MUST exactly match input
- No duplicates
- Empty list if no methods require change
"""

