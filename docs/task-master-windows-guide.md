# Task Master for Windows - Setup and Usage Guide

## Overview

Task Master is a task management system designed for AI-driven development with Claude. This guide provides step-by-step instructions for setting up and using Task Master on Windows, specifically for the PrimordialEncounters project.

## Prerequisites

- Windows operating system
- Administrator privileges (for installing Node.js)
- Anthropic API key (for Claude integration)

## Installation

### 1. Install Node.js

1. Download Node.js from the official website: https://nodejs.org/
2. Choose the LTS (Long Term Support) version
3. Run the installer and follow the installation wizard
4. Make sure to check the option to add Node.js to your PATH
5. Verify installation by opening a new PowerShell window and running:
   ```
   node -v
   npm -v
   ```

### 2. Install Task Master

Install Task Master globally:

```
npm install -g task-master-ai
```

### 3. Create Project Structure

Create the necessary directories:

```
mkdir tasks
```

### 4. Configure Environment Variables

Create a `.env` file in your project root with the following content:

```
# Required
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional
MODEL=claude-3-5-sonnet-20240229
MAX_TOKENS=8192
TEMPERATURE=0.7
DEBUG=false
LOG_LEVEL=info
DEFAULT_SUBTASKS=3
DEFAULT_PRIORITY=medium
```

Replace `your_anthropic_api_key_here` with your actual Anthropic API key.

### 5. Create a Batch File for Easy Access

Create a file named `run-task-master.bat` in your project root with the following content:

```
@echo off
set PATH=%PATH%;C:\Program Files\nodejs;C:\Users\%USERNAME%\AppData\Roaming\npm
C:\Users\%USERNAME%\AppData\Roaming\npm\task-master.cmd %*
```

This batch file makes it easier to run Task Master commands by ensuring the correct PATH is set.

## Task Structure

Tasks in Task Master have the following structure:

- **ID**: Unique identifier (e.g., `1`, `2.1`)
- **Title**: Brief, descriptive title
- **Description**: Concise description of what the task involves
- **Status**: Current state (`pending`, `in-progress`, `done`, `deferred`, `cancelled`)
- **Dependencies**: IDs of tasks that must be completed before this task
- **Priority**: Importance level (`high`, `medium`, `low`)
- **Details**: In-depth implementation instructions
- **Test Strategy**: Verification approach
- **Subtasks**: List of smaller, more specific tasks that make up the main task

## Basic Commands

### List Tasks

To view all tasks:

```
.\run-task-master.bat list
```

To view tasks with subtasks:

```
.\run-task-master.bat list --with-subtasks
```

To filter tasks by status:

```
.\run-task-master.bat list --status=pending
.\run-task-master.bat list --status=in-progress
.\run-task-master.bat list --status=done
```

### Show Task Details

To view details of a specific task:

```
.\run-task-master.bat show 1
```

To view details of a subtask:

```
.\run-task-master.bat show 2.1
```

### Find Next Task

To see the next recommended task to work on:

```
.\run-task-master.bat next
```

### Update Task Status

To mark a task as in-progress:

```
.\run-task-master.bat set-status --id=1 --status=in-progress
```

To mark a task as done:

```
.\run-task-master.bat set-status --id=1 --status=done
```

To update multiple tasks at once:

```
.\run-task-master.bat set-status --id=1,2,3 --status=done
```

### Expand Tasks into Subtasks

To break down a task into subtasks:

```
.\run-task-master.bat expand --id=1 --num=3
```

To provide additional context for expansion:

```
.\run-task-master.bat expand --id=1 --prompt="Focus on security aspects"
```

To expand all pending tasks:

```
.\run-task-master.bat expand --all
```

### Generate Task Files

To generate individual task files in the tasks/ directory:

```
.\run-task-master.bat generate
```

## Advanced Commands

### Update Tasks Based on New Information

To update tasks based on new information:

```
.\run-task-master.bat update --from=4 --prompt="Now we are using Express instead of Fastify."
```

### Analyze Task Complexity

To analyze the complexity of tasks:

```
.\run-task-master.bat analyze-complexity
```

### View Complexity Report

To view the complexity analysis report:

```
.\run-task-master.bat complexity-report
```

### Manage Dependencies

To add a dependency to a task:

```
.\run-task-master.bat add-dependency --id=3 --depends-on=2
```

To remove a dependency from a task:

```
.\run-task-master.bat remove-dependency --id=3 --depends-on=2
```

To validate dependencies:

```
.\run-task-master.bat validate-dependencies
```

### Add a New Task

To add a new task:

```
.\run-task-master.bat add-task --prompt="Description of the new task"
```

To add a task with dependencies:

```
.\run-task-master.bat add-task --prompt="Description" --dependencies=1,2,3
```

## Workflow Example

1. **Start your day** by checking what tasks are available:
   ```
   .\run-task-master.bat list
   ```

2. **Find the next task** to work on:
   ```
   .\run-task-master.bat next
   ```

3. **View task details**:
   ```
   .\run-task-master.bat show 2
   ```

4. **Mark the task as in-progress**:
   ```
   .\run-task-master.bat set-status --id=2 --status=in-progress
   ```

5. **Break down the task** if it's complex:
   ```
   .\run-task-master.bat expand --id=2 --num=3
   ```

6. **Work on subtasks**:
   ```
   .\run-task-master.bat show 2.1
   .\run-task-master.bat set-status --id=2.1 --status=in-progress
   ```

7. **Mark subtasks as done** when completed:
   ```
   .\run-task-master.bat set-status --id=2.1 --status=done
   ```

8. **Mark the parent task as done** when all subtasks are complete:
   ```
   .\run-task-master.bat set-status --id=2 --status=done
   ```

## Troubleshooting

### Node.js Not Found

If you get an error like `'node' is not recognized as an internal or external command`:

1. Make sure Node.js is installed
2. Check if Node.js is in your PATH
3. Try restarting your PowerShell/Command Prompt
4. Use the full path to Node.js: `"C:\Program Files\nodejs\node.exe"`

### Task Master Not Found

If you get an error like `'task-master' is not recognized as an internal or external command`:

1. Make sure Task Master is installed globally: `npm install -g task-master-ai`
2. Check if npm global bin directory is in your PATH
3. Use the full path to Task Master: `C:\Users\<username>\AppData\Roaming\npm\task-master.cmd`

### API Key Issues

If you get an error like `Error communicating with Claude: 401 {"type":"error","error":{"type":"authentication_error","message":"invalid x-api-key"}}`:

1. Make sure your Anthropic API key is valid
2. Check if the API key is correctly set in the `.env` file
3. Make sure the `.env` file is in the project root directory
4. Try regenerating your API key from the Anthropic console

### Model Issues

If you get an error related to the model:

1. Make sure you're using a valid Claude model name in the `.env` file
2. Current valid models include:
   - claude-3-5-sonnet-20240229
   - claude-3-opus-20240229
   - claude-3-haiku-20240307

## File Structure

```
PrimordialEncounters/
│
├── .env                    # Environment variables
├── run-task-master.bat     # Batch file for running Task Master
├── tasks.json              # Task data (in tasks/ directory)
├── tasks/                  # Directory for task files
│   ├── task_001.txt        # Individual task file
│   ├── task_002.txt
│   └── ...
└── scripts/                # Directory for scripts
    └── prd.txt             # Product Requirements Document
```

## Maintenance

### Updating Task Master

To update Task Master to the latest version:

```
npm update -g task-master-ai
```

### Backing Up Tasks

It's a good practice to back up your tasks.json file regularly:

```
copy tasks\tasks.json tasks\tasks_backup.json
```

## Conclusion

Task Master provides a structured approach to managing tasks for your PrimordialEncounters project. By following this guide, you can efficiently track progress, break down complex tasks, and maintain a clear overview of your project's status.

For more information, refer to the official Task Master documentation or the guide provided in the `docs/task-master-guide.md` file.
