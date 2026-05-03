ENRICH_FUNCTION_PROMPT = """
ROLE:
Senior software engineer extracting semantic metadata from a Python function

TASK:
Analyze the function and extract precise, factual metadata for a knowledge graph

INPUTS:
Function Name:
{function_name}

Function Inputs:
{function_inputs}

Function Code:
{function_code}

PRIORITY:
1. Accuracy of extracted behavior
2. No hallucination or inferred intent
3. Consistent structured output

SOURCE OF TRUTH:
- The function code is the ONLY source of truth
- All descriptions MUST be directly supported by the code

SUMMARY RULE:
- One sentence describing the main purpose
- No extra detail or interpretation

DESCRIPTION RULE:
- Explain what the function does in terms of observable behavior
- Do NOT infer intent beyond code

STEP RULES:
- Steps MUST follow actual execution order
- Each step represents a meaningful operation
- Use natural language (not code)
- Do NOT include variable names or syntax
- Do NOT skip important operations
- Avoid overly low-level or overly abstract descriptions

OUTPUT RULE:
- Include ONLY values explicitly returned by the function
- If function returns multiple values → list all
- If no return statement → outputs MUST be empty list
- Do NOT include:
  - internal state changes
  - side effects
  - implicit outputs

TYPE RULE:
- Infer output types conservatively (e.g., bool, int, list, string)
- Do NOT guess complex types unless clear

CONSTRAINTS:
- Do NOT change function name or inputs
- Do NOT rewrite code
- Do NOT assume hidden behavior
- Do NOT infer future use or intent

FORBIDDEN:
- hallucinating side effects
- inventing outputs not returned
- interpreting business logic beyond code
- copying code into descriptions

OUTPUT FORMAT:
Return ONLY valid JSON:

{{
  "summary": "Short one-sentence summary.",
  "description": "Concise factual explanation.",
  "steps": [
    "Step 1",
    "Step 2"
  ],
  "outputs": [
    {{
      "name": "string",
      "type": "string",
      "description": "string"
    }}
  ]
}}

EXAMPLE:

Function:
def is_even(x):
    return x % 2 == 0

Expected output:
{{
  "summary": "Checks whether the input number is even.",
  "description": "Computes the remainder after division by two and returns whether it equals zero.",
  "steps": [
    "Compute the remainder when dividing the input by two.",
    "Compare the result with zero.",
    "Return whether the comparison is true."
  ],
  "outputs": [
    {{
      "name": "result",
      "type": "bool",
      "description": "Boolean indicating whether the input is even."
    }}
  ]
}}
"""

ADMIT_FUNCTION_PROMPT = """
ROLE:
Curator of a reusable implementation knowledge base (GraphRAG)

TASK:
Decide whether the function is worth storing for future reuse

INPUTS:
Function Description:
{func_desc}

Function Code:
{code}

PRIORITY:
1. Presence of non-trivial logic or useful idea
2. Logical correctness and completeness
3. Clarity of intent

DECISION PRINCIPLE:

The goal is to FILTER OUT only trivial or useless functions.
Most non-trivial, meaningful implementations should be ACCEPTED,
even if they are domain-specific.

ACCEPT if the function contains ANY of the following:

- Non-trivial logic (conditions, transformations, edge case handling)
- Algorithmic thinking or multi-step reasoning
- Useful pattern, abstraction, or non-obvious implementation
- Domain-specific logic that may be hard for LLMs to reconstruct

REJECT ONLY if the function is clearly trivial or useless, such as:

- Simple one-liners (e.g. direct assignments, wrappers, passthrough)
- Basic arithmetic or primitive operations with no added value
- Boilerplate getters/setters with no logic
- Extremely obvious functionality that LLM can easily regenerate

ADDITIONAL REQUIREMENTS (must still hold):

- Function must be COMPLETE (no TODOs, missing branches, placeholders)
- Behavior must be UNDERSTANDABLE from code
- No fundamentally broken or nonsensical logic

DO NOT penalize for:
- Domain specificity
- Narrow use cases
- Lack of generalization

DECISION RULE:
- Default bias is ACCEPT
- Only REJECT when clearly trivial OR broken

OUTPUT:
Return EXACTLY one word:
ACCEPT or REJECT
"""

ENRICH_CLASS_PROMPT = """
ROLE:
Senior software architect inferring class responsibility

TASK:
Infer the SINGLE high-level responsibility of the class based ONLY on its attributes and methods

INPUTS:
Class Name:
{class_name}

Attributes:
{attributes}

Methods:
{methods}

PRIORITY:
1. Accurate reflection of class purpose
2. High-level abstraction (not implementation detail)
3. No hallucination beyond provided data

SOURCE OF TRUTH:
- Use ONLY attributes and methods
- Do NOT assume behavior not present

RESPONSIBILITY RULE:
- Responsibility must describe:
  → what the class represents
  → what role it plays in the system

- It must NOT describe:
  → step-by-step behavior
  → method list
  → low-level logic

AGGREGATION RULE:
- Combine all methods and attributes into ONE coherent purpose
- Identify the common theme across methods

ABSTRACTION LEVEL:
- High-level but specific
- Example:
  GOOD: "Manages game state and rules for a board game"
  BAD: "Handles methods and attributes"
  BAD: "Processes clicks and updates values"

CLARITY RULE:
- One concise sentence
- No redundancy
- No vague words like:
  - "handles things"
  - "manages data"
  - "does operations"

CONSISTENCY RULE:
- Responsibility must align with:
  - majority of methods
  - key attributes

CONSTRAINTS:
- Do NOT invent new functionality
- Do NOT infer future use
- Do NOT include method names

FORBIDDEN:
- listing methods
- generic descriptions
- vague or empty responsibility
- mixing multiple unrelated responsibilities

OUTPUT FORMAT:
Return ONLY valid JSON:

{{
  "responsibility": "..."
}}
"""

ENRICH_ATTRIBUTE_PROMPT = """
ROLE:
Senior software architect inferring attribute semantics

TASK:
Generate precise, factual descriptions of class attributes based on their usage

INPUTS:
Class Name:
{class_name}

Attributes:
{attributes}

Methods:
{methods}

PRIORITY:
1. Accuracy based on actual usage
2. Clear and concise meaning
3. No hallucination

SOURCE OF TRUTH:
- Infer meaning primarily from how attributes are USED in methods
- Attribute name alone is NOT sufficient unless usage is unclear

USAGE RULE:
- Analyze how each attribute is:
  - read
  - modified
  - passed to methods
- Derive its role in the system from this usage

DESCRIPTION RULE:
- Each description must:
  - be short (1 sentence or less)
  - describe the role of the attribute
  - reflect actual behavior in code

GOOD EXAMPLES:
- "Current player identifier in the game"
- "Grid representing the game board state"

BAD EXAMPLES:
- "Stores value"
- "Holds data"
- "Variable for something"

PRECISION RULE:
- Be specific enough to distinguish attribute purpose
- Avoid vague or generic wording

AMBIGUITY RULE:
- If usage is unclear:
  - fall back to conservative description based on name
  - do NOT invent behavior

CONSISTENCY RULE:
- Use consistent terminology across attributes
- Align with method behavior

CONSTRAINTS:
- Keys MUST match attribute names exactly
- Do NOT add or remove attributes
- Do NOT infer hidden behavior
- Do NOT include types unless necessary

FORBIDDEN:
- generic descriptions
- hallucinated functionality
- repeating attribute name as description
- interpreting beyond visible usage

OUTPUT FORMAT:
Return ONLY valid JSON:

{{
  "attribute_name": "description"
}}
"""