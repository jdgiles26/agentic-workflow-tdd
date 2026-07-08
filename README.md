# agentic-workflow-tdd
AI-driven Test-Driven Development platform orchestrating specialized agents (Backend, Frontend, Edge Case, UI, Integration) withlocal LLMs (ollama, llama.cpp) for automated test generation and execution
gentic Workflow TDD System
Overview
The Agentic Workflow TDD System is a comprehensive framework for managing software development tasks using a Test-Driven Development (TDD) approach with multi-agent collaboration. The system orchestrates autonomous agents through a structured workflow state machine, ensuring rigorous testing and certification of each task before progression.

System Architecture
Core Components
Workflow State Manager: Manages task states and transitions using a SQLite database
CLI Interface: Click-based command-line interface for workflow management
Agent Framework: PyAutoGen-based multi-agent system for task execution
LLM Client: Ollama integration for local LLM inference
Browser Automation: Playwright for web-based task execution
Technology Stack
Language: Python 3.10+
Workflow Orchestration: LangGraph, LangChain
Multi-Agent Framework: PyAutoGen (AG2)
LLM Integration: Ollama (llama3.1:8b, codellama:7b, mistral:7b)
Testing: pytest, pytest-asyncio, pytest-cov
Browser Automation: Playwright
Database: SQLite for persistence, Redis for caching
CLI: Click + Rich for terminal UI
TDD Workflow States
The system implements a five-state workflow with a rejection loop:

SPEC → TEST-FAIL → CODE → TEST-PASS → CERTIFY
                    ↑                   ↓
                                        └────── REJECTED ────┘
                                        ```

                                        ### State Descriptions

                                        1. **SPEC**: Task specification and requirements definition
                                        2. **TEST-FAIL**: Test cases defined but failing (expected)
                                        3. **CODE**: Implementation in progress
                                        4. **TEST-PASS**: All tests passing
                                        5. **CERTIFY**: Ready for certification review
                                        6. **REJECTED**: Certification failed, returns to SPEC

                                        ## Installation

                                        ```bash
                                        # Clone the repository
                                        git clone https://github.com/jdgiles26/agentic-workflow-tdd
                                        cd agentic-workflow-tdd

                                        # Install dependencies
                                        pip install -r requirements.txt

                                        # Install package in editable mode
                                        pip install -e .
                                        ```

                                        ## CLI Usage

                                        ### Initialize Project

                                        ```bash
                                        awt init
                                        ```

                                        ### Start New Task

                                        ```bash
                                        awt start "Task name" "Task description"
                                        ```

                                        ### Set Specification

                                        ```bash
                                        awt spec <task_id> "Task specification details"
                                        ```

                                        ### Set Test Cases

                                        ```bash
                                        awt tests <task_id> "Test case definitions"
                                        ```

                                        ### Set Implementation Code

                                        ```bash
                                        awt code <task_id> "Implementation code"
                                        ```

                                        ### Transition State

                                        ```bash
                                        awt transition <task_id> <new_state>
                                        ```

                                        ### Request Certification

                                        ```bash
                                        awt certify <task_id>
                                        ```

                                        ### Approve/Reject Certification

                                        ```bash
                                        awt certify_decision <task_id> approve|reject "Decision notes"
                                        ```

                                        ### View Status

                                        ```bash
                                        # Single task status
                                        awt status <task_id>

                                        # All tasks
                                        awt status
                                        ```

                                        ### View Logs

                                        ```bash
                                        awt logs <task_id>
                                        ```

                                        ### Export Task Data

                                        ```bash
                                        awt export <task_id> --format json|yaml|markdown
                                        ```

                                        ## API Reference

                                        ### WorkflowStateManager

                                        ```python
                                        from src.workflow.state_manager import WorkflowStateManager, WorkflowState, Task

                                        # Initialize with database path
                                        manager = WorkflowStateManager("workflow.db")

                                        # Create task
                                        task = manager.create_task("Task Name", "Description")

                                        # Get task
                                        task = manager.get_task(task_id)

                                        # Transition state
                                        task = manager.transition_state(task_id, WorkflowState.TEST_FAIL)

                                        # Update content
                                        task = manager.update_task_content(
                                                task_id,
                                                    spec="Specification",
                                                        tests="Tests",
                                                            code="Code"
                                        )

                                        # List all tasks
                                        tasks = manager.list_tasks()

                                        # Get transition logs
                                        logs = manager.get_transition_logs(task_id)
                                        ```

                                        ## A2A Protocol

                                        The system uses a JSON-based Agent-to-Agent (A2A) protocol with the following message types:

                                        - **task_assignment**: Assign task to agent
                                        - **status_update**: Report progress
                                        - **result_submission**: Submit completed work
                                        - **certification_request**: Request certification
                                        - **certification_result**: Certification decision

                                        ## Security Considerations

                                        - All credentials stored in `.env` file (not committed to version control)
                                        - SQLite database with file-based access control
                                        - No external API calls without explicit user consent
                                        - Local LLM inference via Ollama

                                        ## Performance

                                        - SQLite operations: <50ms average
                                        - State transitions: <100ms
                                        - Task listing: <50ms for 1000+ tasks
                                        - Memory footprint: <100MB idle
                                        
                                        ## Development
                                        
                                        ```bash
                                        # Run tests
                                        pytest tests/ -v --cov=src
                                        
                                        # Format code
                                        black src/ tests/
                                        
                                        # Lint code
                                        ruff check src/ tests/
                                        
                                        # Type checking
                                        mypy src/
                                        ```
                                        
                                        ## License
                                        
                                        MIT License - see LICENSE file for details.
                                        
                                        ## Contributing
                                        
                                        1. Fork the repository
                                        2. Create feature branch
                                        3. Write tests
                                        4. Implement feature
                                        5. Ensure all tests pass
                                        6. Submit pull request
                                        >>>>
                                        )
