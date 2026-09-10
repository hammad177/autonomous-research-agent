from autonomous_research_agent.schemas.report import Report


def render_report_markdown(report: Report) -> str:
    lines = [f"# {report.title}", "", "## Summary", "", report.summary, ""]

    for section in report.sections:
        lines.append(f"## {section.heading}")
        lines.append("")
        lines.append(section.content)
        lines.append("")
        if section.sources:
            lines.append(f"*Sources: {', '.join(section.sources)}*")
            lines.append("")

    return "\n".join(lines)
