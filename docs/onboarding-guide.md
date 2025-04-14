# PrimordialEncounters Onboarding Guide

This comprehensive guide outlines the complete workflow for contributing to the PrimordialEncounters project, including initial setup, task management with TaskMaster, and proper procedures for task execution and completion.

## Table of Contents

1. [Initial Setup](#1-initial-setup)
   - [Environment Setup](#environment-setup)
   - [Repository Setup](#repository-setup)
   - [TaskMaster Setup](#taskmaster-setup)
   - [Python Environment Setup](#python-environment-setup)

2. [Pre-Task Procedures](#2-pre-task-procedures)
   - [Reviewing Available Tasks](#reviewing-available-tasks)
   - [Selecting a Task](#selecting-a-task)
   - [Understanding Task Requirements](#understanding-task-requirements)
   - [Creating a Feature Branch](#creating-a-feature-branch)

3. [During-Task Procedures](#3-during-task-procedures)
   - [Marking Task as In-Progress](#marking-task-as-in-progress)
   - [Implementing the Task](#implementing-the-task)
   - [Writing Tests](#writing-tests)
   - [Running Tests Locally](#running-tests-locally)
   - [Documenting Your Code](#documenting-your-code)

4. [Post-Task Procedures](#4-post-task-procedures)
   - [Code Review Preparation](#code-review-preparation)
   - [Committing Changes](#committing-changes)
   - [Running the Full Test Suite](#running-the-full-test-suite)
   - [Creating a Pull Request](#creating-a-pull-request)
   - [Verifying Task Completion](#verifying-task-completion)
   - [Marking Task as Complete](#marking-task-as-complete)

5. [Common Mistakes and How to Avoid Them](#5-common-mistakes-and-how-to-avoid-them)
   - [Workflow Violations](#workflow-violations)
   - [Task Management Errors](#task-management-errors)
   - [Git and Commit Mistakes](#git-and-commit-mistakes)
   - [Testing Oversights](#testing-oversights)

6. [Best Practices](#6-best-practices)
   - [Code Quality Standards](#code-quality-standards)
   - [Testing Standards](#testing-standards)
   - [Documentation Standards](#documentation-standards)
   - [Git Workflow Standards](#git-workflow-standards)

7. [Workflow Checklist](#7-workflow-checklist)
   - [Before Starting a Task](#before-starting-a-task)
   - [During Implementation](#during-implementation)
   - [Before Submitting](#before-submitting)
   - [Completion](#completion)

---

## 1. Initial Setup

### Environment Setup

1. **Install Required Software**:
   - Python 3.8+ (required for core functionality)
   - Node.js (required for TaskMaster)
   - Git (required for version control)

2. **Configure Git**:
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"
   ```

### Repository Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/ImmortalDemonGod/PrimordialEncounters.git
   cd PrimordialEncounters
   ```

2. **Set Up Remote**:
   ```bash
   git remote add upstream https://github.com/ImmortalDemonGod/PrimordialEncounters.git
   ```

### TaskMaster Setup

1. **Install TaskMaster Globally**:
   ```bash
   npm install -g task-master-ai
   ```

2. **Create Required Directories**:
   ```bash
   mkdir -p tasks
   ```

3. **Configure Environment Variables**:
   Create a `.env` file in the project root with the following content:
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

4. **Create TaskMaster Batch File**:
   Create a file named `run-task-master.bat` in the project root with the following content:
   ```batch
   @echo off
   npx task-master-ai %*
   ```

### Python Environment Setup

1. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   ```

2. **Activate the Virtual Environment**:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## 2. Pre-Task Procedures

### Reviewing Available Tasks

1. **List All Tasks**:
   ```bash
   .\run-task-master.bat list
   ```

2. **View Tasks with Subtasks**:
   ```bash
   .\run-task-master.bat list --with-subtasks
   ```

3. **View Complexity Report** (if available):
   ```bash
   .\run-task-master.bat complexity-report
   ```

### Selecting a Task

1. **Find the Next Recommended Task**:
   ```bash
   .\run-task-master.bat next
   ```

2. **View Detailed Task Information**:
   ```bash
   .\run-task-master.bat show <task_id>
   ```
   Replace `<task_id>` with the ID of the task you want to view (e.g., `2` or `3.1`).

### Understanding Task Requirements

1. **Review Task Details Thoroughly**:
   - Read the task description, implementation details, and test strategy
   - Understand the dependencies and how this task fits into the overall project
   - Identify any potential challenges or areas requiring further research

2. **Expand Complex Tasks if Needed**:
   ```bash
   .\run-task-master.bat expand --id=<task_id> --num=<number_of_subtasks>
   ```
   This breaks down a complex task into manageable subtasks.

### Creating a Feature Branch

1. **Ensure Your Main Branch is Up-to-Date**:
   ```bash
   git checkout master
   git pull upstream master
   ```

2. **Create a New Branch**:
   ```bash
   git checkout -b task/<task_id>-<short-description>
   ```
   Example: `git checkout -b task/2.1-nbody-simulation-class`

---

## 3. During-Task Procedures

### Marking Task as In-Progress

1. **Update Task Status**:
   ```bash
   .\run-task-master.bat set-status --id=<task_id> --status=in-progress
   ```

2. **If Working on a Subtask**:
   ```bash
   .\run-task-master.bat set-status --id=<subtask_id> --status=in-progress
   ```

### Implementing the Task

1. **Follow the Implementation Plan** outlined in the task details.

2. **Adhere to Project Coding Standards**:
   - Follow PEP 8 for Python code
   - Use consistent naming conventions
   - Include docstrings for all functions, classes, and modules
   - Add type hints where appropriate

3. **Implement in Small, Testable Increments**:
   - Write code for a small piece of functionality
   - Write tests for that functionality
   - Run tests to ensure the code works as expected
   - Repeat for the next piece of functionality

### Writing Tests

1. **Create Test Files**:
   - Place test files in the `tests/` directory
   - Name test files with the prefix `test_` followed by the name of the module being tested
   - Example: `test_nbody.py` for testing `src/nbody.py`

2. **Write Comprehensive Tests**:
   - Unit tests for individual functions and methods
   - Integration tests for interactions between components
   - Edge case tests for boundary conditions
   - Error handling tests for expected exceptions

3. **Aim for 100% Code Coverage**:
   - Test all code paths
   - Test all edge cases
   - Test all error conditions

### Running Tests Locally

1. **Run Tests for Your Module**:
   ```bash
   python -m pytest tests/test_<your_module>.py -v
   ```

2. **Run Tests with Coverage**:
   ```bash
   python -m pytest tests/test_<your_module>.py --cov=src.<your_module>
   ```

### Documenting Your Code

1. **Add Docstrings** to all functions, classes, and modules:
   ```python
   def function_name(param1, param2):
       """
       Brief description of the function.

       Parameters
       ----------
       param1 : type
           Description of param1
       param2 : type
           Description of param2

       Returns
       -------
       return_type
           Description of return value

       Raises
       ------
       ExceptionType
           When and why this exception is raised
       """
       # Function implementation
   ```

2. **Add Comments** for complex logic or algorithms.

3. **Update README.md** if your changes affect the project's usage or features.

---

## 4. Post-Task Procedures

### Code Review Preparation

1. **Review Your Own Code**:
   - Check for logical errors
   - Ensure code readability
   - Verify all tests pass
   - Confirm documentation is complete

2. **Run Static Analysis Tools**:
   ```bash
   # If using flake8
   flake8 src/<your_module>.py

   # If using pylint
   pylint src/<your_module>.py
   ```

### Committing Changes

1. **Stage Files Individually**:
   ```bash
   git add src/<file_name>
   ```

2. **Commit Each File Separately with Descriptive Messages**:
   ```bash
   git commit -m "[Task #<task_id>] <Descriptive message about the specific change>"
   ```
   Example: `git commit -m "[Task #2.1] Implement NBodySimulation class with REBOUND integration"`

3. **Include in Each Commit Message**:
   - Task ID reference
   - Clear description of what changed
   - Why the change was made (if not obvious)
   - Any limitations or considerations

### Running the Full Test Suite

1. **Run All Tests**:
   ```bash
   python -m pytest
   ```

2. **Run with Full Coverage Report**:
   ```bash
   python -m pytest --cov=src --cov-report=html
   ```

3. **Verify 100% Code Coverage**:
   - Open `htmlcov/index.html` in a browser
   - Ensure all your new code is covered by tests
   - Add additional tests if coverage is less than 100%

4. **Fix Any Test Failures** before proceeding.

### Creating a Pull Request

1. **Push Your Branch**:
   ```bash
   git push origin task/<task_id>-<short-description>
   ```

2. **Create a Pull Request** on GitHub:
   - Navigate to the repository on GitHub
   - Click "Pull Requests" > "New Pull Request"
   - Select your branch
   - Fill in the PR template with:
     - Task ID reference
     - Summary of changes
     - Testing performed
     - Screenshots (if applicable)
     - Any additional notes

3. **Request Review** from appropriate team members.

### Verifying Task Completion

1. **Review Task Requirements**:
   - Re-read the original task description
   - Verify that all requirements have been implemented
   - Confirm all subtasks are complete

2. **Verify Test Coverage**:
   ```bash
   python -m pytest --cov=src --cov-report=term
   ```
   - Ensure 100% code coverage for your changes
   - Verify all tests are passing

3. **Check Documentation**:
   - Confirm all new code has proper docstrings
   - Verify README.md is updated if needed
   - Ensure any new configuration options are documented

### Marking Task as Complete

1. **Only After PR Approval and Merge**:
   ```bash
   .\run-task-master.bat set-status --id=<task_id> --status=done
   ```
   - ⚠️ **IMPORTANT**: Never mark a task as done until the PR is approved and merged

2. **Verify Each Subtask Individually**:
   - Check each subtask's requirements separately
   - Mark subtasks as done one by one
   ```bash
   .\run-task-master.bat set-status --id=<subtask_id> --status=done
   ```

3. **Clean Up**:
   ```bash
   git checkout master
   git pull upstream master
   git branch -d task/<task_id>-<short-description>
   ```

---

## 5. Common Mistakes and How to Avoid Them

This section highlights common mistakes that can occur during the development process and provides explicit guidance on how to avoid them. Following these guidelines will help maintain project quality and consistency.

### Workflow Violations

1. **❌ Skipping the Feature Branch**
   - **Mistake**: Working directly on the master branch instead of creating a dedicated feature branch.
   - **Consequence**: Risk of conflicts, harder to review changes, and potential for breaking the main codebase.
   - **Correct Approach**: Always create a feature branch before starting work on a task.
   ```bash
   git checkout -b task/<task_id>-<short-description>
   ```

2. **❌ Implementing Multiple Tasks in One Branch**
   - **Mistake**: Working on multiple unrelated tasks in a single branch.
   - **Consequence**: Difficult code reviews, inability to merge tasks independently.
   - **Correct Approach**: Create separate branches for each task, even if they seem related.

3. **❌ Skipping Steps in the Workflow**
   - **Mistake**: Jumping directly to implementation without following the pre-task procedures.
   - **Consequence**: Misalignment with project goals, potential rework.
   - **Correct Approach**: Always follow the complete workflow: review task → create branch → mark as in-progress → implement → test → commit → PR → mark as done.

### Task Management Errors

1. **❌ Not Marking Tasks as In-Progress**
   - **Mistake**: Starting work on a task without updating its status in TaskMaster.
   - **Consequence**: Other team members might start working on the same task, causing duplication of effort.
   - **Correct Approach**: Always mark tasks as in-progress before starting work.
   ```bash
   .\run-task-master.bat set-status --id=<task_id> --status=in-progress
   ```

2. **❌ Marking Tasks as Done Prematurely**
   - **Mistake**: Marking a task as done before completing all required steps (tests, PR, review).
   - **Consequence**: Incomplete work might be considered finished, leading to quality issues.
   - **Correct Approach**: Only mark tasks as done after PR approval and merge.

3. **❌ Not Verifying Subtask Completion**
   - **Mistake**: Marking a parent task as complete without verifying all subtasks are done.
   - **Consequence**: Incomplete work might be overlooked.
   - **Correct Approach**: Verify each subtask individually before marking the parent task as complete.

### Git and Commit Mistakes

1. **❌ Bulk Commits**
   - **Mistake**: Committing multiple files or changes in a single commit.
   - **Consequence**: Difficult to review, understand, or revert specific changes.
   - **Correct Approach**: Commit each file separately with a descriptive message.
   ```bash
   git add src/<single_file>
   git commit -m "[Task #<task_id>] <Specific change description>"
   ```

2. **❌ Vague Commit Messages**
   - **Mistake**: Using generic messages like "Fix bug" or "Update code".
   - **Consequence**: Difficult to understand the purpose of changes when reviewing history.
   - **Correct Approach**: Include task ID, what changed, and why (if not obvious).
   ```bash
   git commit -m "[Task #2.1] Add velocity validation to prevent negative values"
   ```

3. **❌ Not Referencing Task IDs**
   - **Mistake**: Omitting task IDs from commit messages.
   - **Consequence**: Difficult to trace changes back to requirements.
   - **Correct Approach**: Always include the task ID in square brackets at the start of commit messages.

### Testing Oversights

1. **❌ Skipping Tests**
   - **Mistake**: Implementing functionality without corresponding tests.
   - **Consequence**: Potential for undetected bugs and regressions.
   - **Correct Approach**: Write tests for all new functionality, aiming for 100% coverage.

2. **❌ Not Running the Full Test Suite**
   - **Mistake**: Only running tests for the specific module you changed.
   - **Consequence**: Missing integration issues or regressions in other parts of the codebase.
   - **Correct Approach**: Always run the full test suite before submitting a PR.
   ```bash
   python -m pytest
   ```

3. **❌ Ignoring Test Coverage**
   - **Mistake**: Not checking or improving test coverage.
   - **Consequence**: Parts of the code remain untested, increasing risk of bugs.
   - **Correct Approach**: Check coverage reports and add tests to reach 100% coverage.
   ```bash
   python -m pytest --cov=src --cov-report=html
   ```

---

## 6. Best Practices

### Code Quality Standards

1. **Readability**:
   - Use meaningful variable and function names
   - Keep functions small and focused
   - Follow the Single Responsibility Principle

2. **Maintainability**:
   - Write modular code
   - Avoid code duplication
   - Use appropriate design patterns

3. **Performance**:
   - Optimize critical sections
   - Be mindful of memory usage
   - Use appropriate data structures

### Testing Standards

1. **Test Coverage**:
   - Aim for 100% code coverage
   - Test all edge cases
   - Test error conditions

2. **Test Quality**:
   - Write independent tests
   - Use appropriate assertions
   - Mock external dependencies

3. **Test Organization**:
   - Group related tests
   - Use descriptive test names
   - Follow the Arrange-Act-Assert pattern

### Documentation Standards

1. **Code Documentation**:
   - Add docstrings to all functions, classes, and modules
   - Document parameters, return values, and exceptions
   - Explain complex algorithms

2. **Project Documentation**:
   - Keep README.md up-to-date
   - Document API changes
   - Provide usage examples

3. **Comment Quality**:
   - Explain why, not what
   - Keep comments up-to-date
   - Use TODO comments for future improvements

### Git Workflow Standards

1. **Branch Management**:
   - One branch per task
   - Keep branches short-lived
   - Rebase before merging

2. **Commit Quality**:
   - One logical change per commit
   - Write descriptive commit messages
   - Reference task IDs in commit messages

3. **Pull Request Etiquette**:
   - Keep PRs focused and small
   - Respond promptly to review comments
   - Thank reviewers for their feedback

---

## 7. Workflow Checklist

Use this checklist to ensure you've followed all the required steps for each task:

### Before Starting a Task
- [ ] Reviewed task details and requirements
- [ ] Created a feature branch (`git checkout -b task/<task_id>-<short-description>`)
- [ ] Marked task as in-progress in TaskMaster

### During Implementation
- [ ] Followed coding standards
- [ ] Written tests for all new functionality
- [ ] Added proper documentation
- [ ] Run tests locally and fixed any issues

### Before Submitting
- [ ] Committed each file individually with descriptive messages
- [ ] Run the full test suite
- [ ] Verified 100% code coverage
- [ ] Reviewed your own code

### Completion
- [ ] Created a pull request
- [ ] Addressed review feedback
- [ ] Verified PR is approved and merged
- [ ] Marked task as done in TaskMaster
- [ ] Cleaned up (deleted local branch after merge)

---

By following this guide, you'll ensure a smooth and consistent workflow for all contributions to the PrimordialEncounters project. This structured approach helps maintain high code quality, comprehensive test coverage, and clear documentation throughout the development process.
