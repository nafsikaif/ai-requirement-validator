# AI Requirement Validator for Software Development

A desktop software engineering tool designed to automatically analyze natural language software requirements and detect common requirement-quality defects using a transparent, rule-based verification engine.

> **Important Implementation Notice:**
> While the official academic project title is **"AI Requirement Validator for Software Development"**, this implementation is completely **rule-based** using deterministic natural language processing (tokenization, regex, pattern heuristics, and vocabulary matching). It does **not** rely on black-box machine learning, deep learning, LLMs, or external paid APIs, making it fully explainable, 100% offline, and reproducible for college viva evaluations.

---

## 1. Project Description

In modern software engineering, poor requirements (ambiguous wording, missing actors, unmeasurable performance targets, incomplete statements, or escape clauses) are the primary cause of project failure and scope creep.

The **AI Requirement Validator for Software Development** acts as an automated quality gatekeeper. It takes a software requirement specification written in English, applies automated quality rules, and generates:
- **Validation Status**: `PASS`, `NEEDS IMPROVEMENT`, or `INVALID`
- **Quality Score**: Transparent internal rule-based ratio (e.g., `8/9 rules passed`)
- **Rule Analysis**: Rule-by-rule visual breakdown showing which rules passed (`✓ PASS`) or failed (`⚠/✗ FAIL`) across all 10 checks
- **Problems Detected**: Detailed breakdown with Severity (`HIGH`, `MEDIUM`, `LOW`), Category, Detected Token, Explanation (*Why*), and *Suggestion*
- **Suggestions for Improvement**: Actionable guidance for refining the specification
- **Recommended Improved Requirement**: A clean, measurable template without introducing vague clauses
- **Audit Persistence**: Ability to save validation records with timestamps to CSV

---

## 2. Key Features & Rules (10 Rules Implemented)

1. **Empty Requirement Check (`HIGH`)**: Immediately flags empty or whitespace-only inputs.
2. **Robust Length & Completeness Check (`HIGH`)**: 
   - Detects prematurely truncated statements.
   - Detects sentences ending on **dangling prepositions** (*with, for, in, to, at, by, from, into*).
   - Detects sentences ending on **dangling conjunctions / subordinators** (*if, when, while, as, because, unless, whether, and, or*).
   - Detects sentences ending on **hanging modal/auxiliary verbs** (*shall, should, must, will, can*).
   - Detects sentences ending on **trailing ellipses** (*...*, *…*).
   - Detects incomplete phrases (*able to*, *in order to*, *required to*).
3. **Actor Detection (`LOW` if missing)**:
   - Recognizes `"system"` as a valid actor so system requirements (e.g., *"The system shall generate a monthly report."*) pass without requiring a human actor.
   - Treats completely missing actors as minor/informational (`LOW` severity).
4. **Action Detection (`HIGH`)**:
   - Recognizes action verbs: *respond, process, retrieve, authenticate, provide, accept, reject, handle, receive, return, support, allow, manage, display, generate, calculate, send, store, update, delete, create, search, upload, download, login, register, submit*.
   - Contextual pattern matching for `<actor> + <modal> + <verb>` (e.g., *"The system should respond..."*).
5. **Expected Behavior (Modal Verbs) (`HIGH`)**: Enforces requirement standards (*shall, should, must, can, will*).
6. **Categorized Vague Word Detection (`MEDIUM`)**:
   - **Performance**: *fast, quick, quickly, slow, rapid, efficient*
   - **Quantity**: *many, few, some, several, most*
   - **Time**: *soon, later, immediately, as soon as possible*
   - **Quality**: *easy, simple, user-friendly, convenient, appropriate, reasonable, adequate*
7. **Measurability Check (`MEDIUM`)**: Identifies performance/timing claims that lack concrete quantitative metrics (e.g., *seconds*, *percentages*, *user counts*).
8. **Ambiguity Check (`MEDIUM`)**: Flags open-ended or imprecise phrasing such as *etc.*, *and/or*, *as soon as possible*, or *some users*.
9. **Atomicity Check (`MEDIUM` - IEEE 830)**: Detects compound requirements combining multiple distinct obligations with phrases like *"as well as"*, *"in addition to"*, or multiple modal verbs.
10. **Escape Clause & Loophole Detection (`MEDIUM`)**: Flags untestable escape clauses such as *"if possible"*, *"where applicable"*, *"as appropriate"*, or *"to the extent possible"*.

---

## 3. UI Theme (Brown & Half-White)

The desktop interface features a warm, distraction-free aesthetic:
- **Header**: Deep Espresso Brown (`#3E2723`) with Warm Half-White / Ivory text (`#FFF8F0`)
- **Background**: Soft Warm Half-White / Cream (`#FAF7F2`)
- **Card Frames**: Warm Ivory (`#FFFFFF`) with Tan borders (`#D7CCC8`)
- **Buttons**:
  - **Validate**: Rich Warm Chocolate Brown (`#5D4037`)
  - **Clear**: Warm Half-White Almond (`#EFEBE9`)
  - **Save**: Earthy Bronze Forest (`#4E6A34`)
- **Status Badges**:
  - `PASS`: Earthy Forest Green (`#2E7D32`)
  - `NEEDS IMPROVEMENT`: Warm Terracotta Amber (`#D84315`)
  - `INVALID`: Rust Burgundy Red (`#C62828`)

---

## 4. How to Run

1. Open your terminal or PowerShell and navigate to the project directory:
   ```bash
   cd C:\Users\nafsi\.gemini\antigravity\scratch\AI_Requirement_Validator
   ```

2. Run the application:
   ```bash
   python main.py
   ```

---

## 5. Verification & Test Scenarios

| Test Requirement | Status | Score | Problem Detected |
| :--- | :---: | :---: | :--- |
| `"The system shall authenticate a valid user within 2 seconds."` | **PASS** | **9/9** | None (Well-formed requirement) |
| `"The system shall provide users with"` | **NEEDS IMPROVEMENT** | **8/9** | Incomplete: Dangling preposition `'with'` |
| `"The user can log in when"` | **NEEDS IMPROVEMENT** | **8/9** | Incomplete: Dangling conjunction `'when'` |
| `"The system should"` | **INVALID** | **3/9** | Incomplete: Dangling modal `'should'` |
| `"The system should allow users to..."` | **NEEDS IMPROVEMENT** | **8/9** | Incomplete: Trailing ellipsis `'...'` |
| `"The system should respond quickly."` | **NEEDS IMPROVEMENT** | **7/9** | Vague term `'quickly'` (Action `'respond'` recognized!) |
| `"The system shall backup records if possible."` | **NEEDS IMPROVEMENT** | **8/9** | Escape clause loophole `'if possible'` |
| `"The system shall process orders as well as the system shall notify managers."` | **NEEDS IMPROVEMENT** | **8/9** | Non-atomic compound requirement |
| `"The system shall generate a monthly report."` | **PASS** | **9/9** | Valid system actor (does not fail) |
| `""` *(empty input)* | **INVALID** | **0/9** | Empty requirement |
