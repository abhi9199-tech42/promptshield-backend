# AI Security & Safe Installation Protocol

## 1. AI-Specific Risk Mitigation

### Risk: Package Hallucination (Slopsquatting)
AI assistants may suggest packages that do not exist or are malicious "typosquats".
**Protocol:**
Before installing any AI-suggested package:
1.  **Verify Existence:** Run `pip search <package_name>` or check `https://pypi.org/project/<package_name>/`.
2.  **Check Metadata:** Verify the author, download count, and release history.
3.  **Review Source:** Look for a valid GitHub repository link on the PyPI page.

### Risk: Prompt Injection via Configuration
Malicious repositories may contain hidden instructions in config files to hijack AI assistants.
**Protocol:**
1.  **Audit Configs:** Manually review `.cursorrules`, `.vscode/settings.json`, and other dotfiles before opening a new repo in an AI IDE.
2.  **Disable Auto-Execution:** Ensure your IDE does not automatically run scripts or tasks from untrusted repositories.

### Risk: Zero-Click RCE via MCP
Model Context Protocol (MCP) tools can be exploited to run code.
**Protocol:**
1.  **Isolate:** Use AI tools in a sandboxed environment (Docker/VM) when working with untrusted code.
2.  **Restrict:** Disable file-system access for AI agents on sensitive directories unless necessary.

## 2. Safe Dependency Management
-   **Lockfiles:** Always use `package-lock.json` or `poetry.lock` to ensure consistent dependency versions.
-   **Vulnerability Scanning:** Use `npm audit` or `pip-audit` regularly.

## 3. Data Privacy
-   **No Real Secrets:** Never paste real API keys or credentials into AI chat windows.
-   **Sanitize Code:** Remove sensitive business logic or PII before asking AI for help.
-   **Context Exclusion:** Use `.cursorignore` (or `.gptignore`) to prevent your AI editor from indexing sensitive files like `.env`, `config.py`, or database files. We have included a default `.cursorignore` in this repository.
