# Claude Task Master Guide

This guide provides a summary of Claude Task Master, an AI-driven task management system designed for development workflows, particularly with Cursor AI.

## 1. Introduction

Claude Task Master is a task management system tailored for AI-driven development using Claude. Its primary purpose is to structure development work by parsing Product Requirements Documents (PRDs), generating detailed tasks, managing dependencies, and integrating seamlessly with AI development environments like Cursor.

## 2. Requirements

- **Node.js:** Version 14.0.0 or higher.
- **Anthropic API Key:** Required for interacting with Claude models.
- **Anthropic SDK:** Version 0.39.0 or higher.
- **OpenAI SDK:** Optional, needed only if using the Perplexity API integration for research-backed task generation.

## 3. Installation

You can install Task Master either globally or locally within your project.

**Global Installation:**
```bash
npm install -g task-master-ai
```

**Local Installation:**
```bash
npm install task-master-ai
```

**Important:** Task Master uses ES modules. Ensure your project's `package.json` includes:
```json
"type": "module"
```

## 4. Initialization

To set up Task Master in a new project:

**If installed globally:**
```bash
task-master init
```

**If installed locally:**
```bash
npx task-master-init
```
This command prompts for project details and creates the necessary configuration files and directory structure.

## 5. Configuration

Task Master is configured using a `.env` file at the root of your project.

**Required:**
- `ANTHROPIC_API_KEY`: Your API key for Claude.

**Optional:**
- `PERPLEXITY_API_KEY`: API key for Perplexity (if using research features).
- `MODEL`: Claude model to use (e.g., "claude-3-7-sonnet-20250219").
- `MAX_TOKENS`: Max tokens for AI responses (default: 4000).
- `TEMPERATURE`: AI response temperature (default: 0.7).
- `PERPLEXITY_MODEL`: Perplexity model (default: "sonar-medium-online").
- `DEBUG`: Enable debug logs (default: false).
- `LOG_LEVEL`: Set log level (default: info).
- `DEFAULT_SUBTASKS`: Default subtasks when expanding (default: 3).
- `DEFAULT_PRIORITY`: Default task priority (default: medium).
- `PROJECT_NAME`, `PROJECT_VERSION`: Override project details in `tasks.json`.

## 6. Core Concepts

- **Parsing PRDs:** The `task-master parse-prd <prd-file.txt>` command analyzes a PRD and automatically generates a structured list of tasks.
- **`tasks.json` Structure:** This file is the heart of the system, storing tasks with the following key fields:
    - `id`: Unique task identifier.
    - `title`: Short task name.
    - `description`: Brief explanation.
    - `status`: Current state (e.g., "pending", "in-progress", "done").
    - `dependencies`: Array of prerequisite task IDs.
    - `priority`: Importance ("high", "medium", "low").
    - `details`: In-depth implementation instructions.
    - `testStrategy`: How to verify task completion.
    - `subtasks`: An array of smaller, nested tasks for breaking down complexity.
- **Generating Task Files:** The `task-master generate` command creates individual `.txt` files for each task in the `tasks/` directory (e.g., `task_001.txt`), making them easy to reference.

## 7. Key Commands

Here are some essential Task Master commands:

- **`task-master list`**: Displays tasks, with options to filter by status (`--status`) or show subtasks (`--with-subtasks`).
- **`task-master next`**: Shows the next recommended task to work on based on status, dependencies, and priority.
- **`task-master show <id>`**: Displays detailed information about a specific task or subtask (e.g., `show 1.2`).
- **`task-master set-status --id=<id> --status=<status>`**: Updates the status of one or more tasks (comma-separated IDs). Setting a parent task to "done" also marks its subtasks as "done".
- **`task-master expand --id=<id>`**: Breaks down a complex task into subtasks, optionally using AI (`--num`, `--prompt`) or research (`--research`). Can also expand all pending tasks (`--all`).
- **`task-master update --from=<id> --prompt="<context>"`**: Updates the details and descriptions of tasks starting from a specific ID, useful when implementation plans change.
- **`task-master analyze-complexity`**: Uses AI to assess the complexity of tasks, estimate optimal subtask counts, and generate expansion prompts, saving results to a report file.
- **`task-master complexity-report`**: Displays the formatted complexity analysis report, highlighting tasks recommended for expansion.

## 8. Cursor AI Integration

Task Master integrates smoothly with Cursor AI for an enhanced development workflow.

- **Rules File:** The `task-master init` command creates a `.cursor/rules/dev_workflow.mdc` file. Cursor automatically loads this file, providing the AI agent with context about Task Master commands and workflow.
- **MCP Server Setup:** Configure Cursor to use Task Master as an MCP (Managed Command Process) server. In Cursor settings, add a new MCP server:
    - **Name:** Task Master (or similar)
    - **Type:** Command
    - **Command:** `npx -y --package task-master-ai task-master-mcp`
- **Typical Workflow in Cursor:**
    1.  **Parse PRD:** Instruct the Cursor agent (in Agent mode) to parse your PRD (`scripts/prd.txt`) using `task-master parse-prd scripts/prd.txt`.
    2.  **Generate Files:** Ask the agent to run `task-master generate` to create individual task files.
    3.  **List/Select Tasks:** Ask the agent "What tasks are available?" or "What's the next task?". The agent uses `task-master list` and `task-master next` to suggest tasks based on readiness and priority.
    4.  **Implementation:** Work with the agent to implement the selected task, referencing its details and test strategy.
    5.  **Completion:** Tell the agent when a task is done (e.g., "Task 3 is complete"). The agent runs `task-master set-status --id=3 --status=done`.
    6.  **Handle Changes:** If plans change, instruct the agent to update future tasks using `task-master update --from=<id> --prompt="..."`.
    7.  **Expand Tasks:** Ask the agent to break down complex tasks using `task-master expand --id=<id>`.

This integration allows the AI agent to manage the task lifecycle directly through Task Master commands within the Cursor environment.