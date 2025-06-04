# AI Best Practices for DevSteward AI Development

This document outlines key best practices for developing, integrating, and maintaining the AI components within DevSteward AI, particularly those interacting with local Large Language Models (LLMs) via Ollama.

## 1. LLM Interaction (Ollama)

### 1.1. Prompt Engineering

- **Clarity and Specificity:** Prompts should be clear, unambiguous, and specific about the task the LLM needs to perform (e.g., "Classify the following project based on its file structure and README content into one of these categories: [...] Provide the output in JSON format with keys: 'category', 'technology', 'confidence'.").
- **Context is Key:** Provide sufficient and relevant context. For DevSteward AI, this includes key file names, directory structure snippets, and README content. Avoid overwhelming the LLM with irrelevant data.
- **Iterative Refinement:** Prompt engineering is an iterative process. Start with a basic prompt, test it with various inputs, analyze the LLM's responses, and refine the prompt for better accuracy and consistency.
- **Role-Playing (Optional but useful):** You can instruct the LLM to act as an "expert software project classifier" to guide its response style and focus.
- **Few-Shot Examples (If needed):** If simple prompting isn't consistently accurate, consider adding a few examples of input and desired output directly into the prompt to guide the LLM.

### 1.2. Model Selection (Ollama)

- **Task-Appropriate Models:** DevSteward AI allows users to select installed Ollama models. Different models have varying strengths in reasoning, instruction following, and speed. Test with a few to find good candidates for project classification.
- **Balance Capability and Resources:** Larger models might be more accurate but slower and require more system resources. Consider providing guidance to users on model selection based on their hardware and needs.
- **Consistency:** Be aware that different models (or even versions of the same model) might interpret prompts differently or have different output formats by default. Aim for prompts that are robust across a range of sensible models.

### 1.3. API Usage & Response Parsing

- **Structured Output:** Explicitly request the LLM to provide its output in a structured format (e.g., JSON). This makes parsing much more reliable. Include the desired JSON schema in your prompt.
- **Error Handling:** Implement robust error handling for Ollama API calls (e.g., Ollama server not running, network issues, model not available, invalid requests).
- **Response Validation:** Validate the structure and content of the LLM's response. If it doesn't conform to the expected JSON schema or contains unexpected values, have fallback logic (e.g., log the issue, mark classification as low confidence, or rely on heuristics).
- **Timeout Management:** Implement timeouts for LLM calls to prevent the application from hanging if a model is slow or unresponsive.

## 2. Data Handling for AI

### 2.1. Input Preparation

- **Relevance and Conciseness:** Carefully select the data passed to the LLM. For project classification, this might include:
  - A summarized list of file extensions and key filenames (e.g., `package.json`, `pom.xml`, `Cargo.toml`).
  - The content of `README.md` (or a summary if it's very long).
  - Snippets from key configuration or main source files if deemed highly indicative.
- **Token Limits:** Be mindful of the context window (token limit) of the chosen LLM. Ensure your input doesn't exceed this limit. Consider techniques like summarizing longer texts if necessary.

### 2.2. Privacy & Security

- **Local by Design:** A core benefit of using Ollama is that all data processing by the LLM happens locally on the user's machine, enhancing privacy. Emphasize this to users.
- **No Sensitive Data Transmission:** Ensure no project data is inadvertently sent to external services unless explicitly stated for a future feature with user consent.

## 3. AI Component Design (e.g., `llm_analyzer.py`)

### 3.1. Modularity and Encapsulation

- **Isolate AI Logic:** The code responsible for interacting with the LLM (prompt creation, API calls, response parsing) should be encapsulated in a dedicated module(s) (e.g., `llm_analyzer.py`).
- **Clear Interface:** This module should have a well-defined API for other parts of the application to use, abstracting away the complexities of direct LLM interaction.

### 3.2. Testability

- **Unit Testing:** Write unit tests for the AI interaction module.
- **Mocking LLM Responses:** Use mocking libraries (e.g., Python's `unittest.mock` or `pytest-mock`) to simulate Ollama API responses. This allows testing of prompt formatting, response parsing, and decision logic without actual LLM calls, making tests fast and deterministic.
- **Test Different Scenarios:** Test with various mocked LLM outputs, including valid classifications, uncertain responses, and malformed/error responses.

### 3.3. Configuration

- **Model Choice:** Allow the user (or the application via settings) to configure which Ollama model is used.
- **Prompt Customization (Advanced):** For future flexibility, consider if parts of prompts (e.g., instructions, output format requests) could be made configurable, but balance this with complexity.

### 3.4. Logging

- **Detailed AI Interaction Logs:** Log key information about AI interactions for debugging and auditing:
  - Timestamp.
  - The Ollama model used.
  - The (potentially summarized or sanitized) prompt sent to the LLM.
  - The raw response from the LLM.
  - The parsed/structured output used by the application.
  - Any errors encountered during the process.
- **Sanitization:** Be mindful not to log excessively large chunks of user file content if it's not necessary for debugging the AI interaction itself.

## 4. User Experience (UX) with AI

### 4.1. Transparency

- **Indicate AI Usage:** Clearly inform the user when AI is being used to analyze their projects or suggest actions.
- **Explain AI's Role:** Briefly explain what the AI is doing (e.g., "Analyzing project content to suggest an organizational category").

### 4.2. User Control & Confirmation

- **Model Selection:** Allow users to choose from their available Ollama models.
- **Dry Run & Confirmation:** The "Dry Run" feature is crucial. Always show users what the AI (in conjunction with the application logic) suggests before any changes are made to their file system, and require explicit confirmation.
- **Override Capability:** Users should always be able to override or ignore AI-driven suggestions.

### 4.3. Handling Uncertainty & Errors

- **Confidence Scores:** If the LLM can provide a confidence score for its classification (or if you can infer one), display this to the user.
- **Fallback Mechanisms:** If the AI's classification is low-confidence or fails, the application could:
  - Fall back to purely heuristic-based classification.
  - Ask the user for manual classification.
  - Clearly indicate the uncertainty.
- **User-Friendly Error Messages:** If an AI operation fails (e.g., Ollama connection error), display a clear, human-readable message in the GUI.

### 4.4. Performance Considerations

- **Latency:** Local LLMs can have noticeable latency. Use asynchronous operations where possible for AI calls to avoid freezing the UI.
- **Loading Indicators:** Display loading indicators or progress messages during AI processing to manage user expectations.

## 5. Ethical Considerations & Responsible AI

### 5.1. Bias Awareness

- **Model Biases:** Pre-trained LLMs can inherit biases from their training data. While less critical for project classification than for generative text, be aware that a model might theoretically favor or misinterpret certain types of projects or coding languages if its training data was skewed. Regular testing with diverse project types can help identify this.
- **Fairness:** Ensure the application's logic that uses AI outputs doesn't inadvertently create unfair or unexpected outcomes.

### 5.2. Reliability and Consistency

- **Probabilistic Nature:** LLMs are probabilistic. The same input might not always produce the exact same output, especially for more creative tasks (though for classification with strong prompting, it should be fairly consistent). Design your system to be robust to minor variations if possible, or use settings like temperature (if Ollama exposes it easily per call for the model) to control randomness.
- **Testing for Consistency:** Test classifications with a variety of projects.

### 5.3. Accountability

- **Human in the Loop:** The "Dry Run" and user confirmation step ensure human oversight and accountability before any actions are taken based on AI suggestions. This is a cornerstone of responsible AI implementation.

## 6. Iteration & Evaluation

### 6.1. Start Simple

- Begin with a focused AI capability (e.g., basic project type classification).
- Iteratively enhance the AI's role based on user feedback and observed performance.

### 6.2. Evaluation Metrics

- **Accuracy:** How often does the AI correctly classify project types (can be validated against manual classifications or user corrections)?
- **User Acceptance:** How often do users accept the AI's suggested organizational placements?
- **Feedback Collection:** Provide a simple way for users to report misclassifications or provide feedback on AI suggestions.

### 6.3. Continuous Improvement

- Regularly review the performance of the AI component.
- Refine prompts, test new Ollama models, or adjust parsing logic as needed based on evaluation and user feedback.

By adhering to these best practices, DevSteward AI can leverage the power of local LLMs responsibly and effectively to provide a valuable service to its users.
