"""AWT command-line interface."""

from __future__ import annotations

import click

from memory.state import WorkflowStore

store = WorkflowStore("workflow_store.json")


@click.group()
def cli() -> None:
    """Agentic Workflow TDD."""


@cli.command("tasks")
def list_tasks() -> None:
    """List workflow tasks."""
    rows = store.list()
    if not rows:
        click.echo("No tasks.")
        return
    for task in rows:
        click.echo(f"{task.id}\t{task.state.value}\t{task.name}")


@cli.command("create")
@click.argument("name")
@click.option("--description", default="", help="Task description")
def create(name: str, description: str) -> None:
    """Create a task in SPEC."""
    task = store.create(name, description)
    click.echo(task.id)


@cli.command("show")
@click.argument("task_id")
def show(task_id: str) -> None:
    """Print one task as JSON-ish lines."""
    task = store.get(task_id)
    if not task:
        raise click.ClickException(f"Task {task_id} not found")
    click.echo(f"{task.id}  {task.state.value}  {task.name}")
    if task.red_report_path:
        click.echo(f"red-report: {task.red_report_path}")
