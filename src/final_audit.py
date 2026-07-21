from __future__ import annotations

import compileall
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.generator import (
    CHAT_MODEL_ALIAS,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TEMPERATURE,
)


BASE_DIR = Path(__file__).resolve().parents[1]
REPORTS_DIR = BASE_DIR / "reports"

FINAL_AUDIT_JSON_PATH = (
    REPORTS_DIR / "final_audit_report.json"
)

FINAL_AUDIT_MARKDOWN_PATH = (
    REPORTS_DIR / "final_audit_report.md"
)

REPORT_FILES = {
    "retrieval": "evaluation_report.json",
    "generation": (
        "generation_evaluation_report.json"
    ),
    "generation_latency": (
        "generation_latency_report.json"
    ),
    "model_comparison": (
        "model_comparison_report.json"
    ),
    "performance_baseline": (
        "performance_baseline.json"
    ),
    "performance_optimized": (
        "performance_optimized.json"
    ),
    "performance_report": (
        "performance_report.json"
    ),
}

REQUIRED_PROJECT_FILES = [
    "README.md",
    "docs/project-notes.md",
    "src/cli.py",
    "src/generator.py",
    "src/rag_service.py",
    "src/evaluation_report_demo.py",
    "src/generation_evaluation_demo.py",
    "src/generation_latency.py",
    "src/model_comparison.py",
]

SECRET_PATTERN = "|".join(
    [
        "OPENAI" + "_API_KEY",
        "AZURE_OPENAI" + "_API_KEY",
        "SUPABASE_SERVICE_ROLE" + "_KEY",
        "SECRET" + "_KEY",
        "PRIVATE" + "_KEY",
        "BEGIN" + " RSA",
        r"password\s*=",
        r"api[_-]?key\s*=",
    ]
)

def normalize_percentage(
    value: Any,
) -> float:
    """
    Orani 0-1 veya 0-100 biciminden
    yuzde bicimine donusturur.
    """
    if value is None:
        return 0.0

    number = float(value)

    if 0.0 <= number <= 1.0:
        return number * 100.0

    return number


def create_check(
    name: str,
    passed: bool,
    details: str,
    blocking: bool = True,
) -> dict[str, Any]:
    """
    Standart bir audit kontrol sonucu
    olusturur.
    """
    return {
        "name": name,
        "passed": bool(passed),
        "blocking": blocking,
        "details": details,
    }


def run_git_command(
    arguments: list[str],
) -> subprocess.CompletedProcess[str]:
    """
    Proje kokunde bir Git komutu calistirir.
    """
    return subprocess.run(
        ["git", *arguments],
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def load_reports() -> tuple[
    dict[str, dict[str, Any]],
    dict[str, str],
]:
    """
    Gerekli JSON raporlarini yukler.
    """
    reports: dict[str, dict[str, Any]] = {}
    errors: dict[str, str] = {}

    for report_key, filename in (
        REPORT_FILES.items()
    ):
        report_path = REPORTS_DIR / filename

        try:
            data = json.loads(
                report_path.read_text(
                    encoding="utf-8",
                )
            )

            if not isinstance(data, dict):
                raise ValueError(
                    "JSON kok degeri nesne degil."
                )

            reports[report_key] = data

        except Exception as error:
            errors[report_key] = (
                f"{type(error).__name__}: "
                f"{error}"
            )

    return reports, errors


def find_selected_max_tokens(
    selected_configuration: Any,
) -> int | None:
    """
    Generation latency raporundaki secili
    max-token degerini guvenli bicimde bulur.
    """
    if not isinstance(
        selected_configuration,
        dict,
    ):
        return None

    possible_keys = [
        "max_tokens",
        "max_token_configuration",
        "configuration",
    ]

    for key in possible_keys:
        value = selected_configuration.get(
            key
        )

        if isinstance(value, int):
            return value

        if isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                continue

        if isinstance(value, dict):
            nested_value = value.get(
                "max_tokens"
            )

            if isinstance(nested_value, int):
                return nested_value

    return None


def collect_git_hygiene() -> dict[str, Any]:
    """
    Takip edilen istenmeyen dosyalari,
    gizli bilgi kaliplarini ve calisma alani
    durumunu inceler.
    """
    tracked_result = run_git_command(
        ["ls-files"]
    )

    tracked_files = [
        line.strip()
        for line in tracked_result.stdout.splitlines()
        if line.strip()
    ]

    forbidden_files = []

    for tracked_file in tracked_files:
        normalized = tracked_file.replace(
            "\\",
            "/",
        ).lower()

        is_forbidden = any(
            [
                normalized.startswith(
                    ".venv/"
                ),
                "/__pycache__/"
                in f"/{normalized}/",
                normalized.endswith(".pyc"),
                normalized
                == "storage/rag.db",
                normalized.endswith("/.env"),
                normalized == ".env",
            ]
        )

        if is_forbidden:
            forbidden_files.append(
                tracked_file
            )

    secret_result = run_git_command(
        [
            "grep",
            "-n",
            "-I",
            "-E",
            SECRET_PATTERN,
        ]
    )

    if secret_result.returncode == 0:
        secret_matches = [
            line
            for line in (
                secret_result.stdout.splitlines()
            )
            if line.strip()
        ]
        secret_scan_error = None

    elif secret_result.returncode == 1:
        secret_matches = []
        secret_scan_error = None

    else:
        secret_matches = []
        secret_scan_error = (
            secret_result.stderr.strip()
            or "Git secret scan failed."
        )

    status_result = run_git_command(
        ["status", "--short"]
    )

    worktree_status = [
        line
        for line in (
            status_result.stdout.splitlines()
        )
        if line.strip()
    ]

    return {
        "tracked_file_count": len(
            tracked_files
        ),
        "forbidden_tracked_files": (
            forbidden_files
        ),
        "secret_matches": secret_matches,
        "secret_scan_error": (
            secret_scan_error
        ),
        "worktree_status": (
            worktree_status
        ),
    }


def create_markdown_report(
    report: dict[str, Any],
) -> str:
    """
    JSON audit raporunun okunabilir Markdown
    karsiligini olusturur.
    """
    summary = report["summary"]
    configuration = report[
        "project_configuration"
    ]
    snapshots = report["report_snapshots"]

    lines = [
        "# Final Audit Report",
        "",
        (
            f"- Generated at: "
            f"`{report['generated_at']}`"
        ),
        (
            f"- Release ready: "
            f"`{summary['release_ready']}`"
        ),
        (
            f"- Blocking checks passed: "
            f"`{summary['blocking_passed']}/"
            f"{summary['blocking_total']}`"
        ),
        (
            f"- All checks passed: "
            f"`{summary['passed_checks']}/"
            f"{summary['total_checks']}`"
        ),
        "",
        "## Project configuration",
        "",
        (
            f"- Chat model: "
            f"`{configuration['chat_model']}`"
        ),
        (
            f"- Max tokens: "
            f"`{configuration['max_tokens']}`"
        ),
        (
            f"- Temperature: "
            f"`{configuration['temperature']}`"
        ),
        "",
        "## Audit checks",
        "",
        "| Check | Status | Blocking | Details |",
        "|---|---:|---:|---|",
    ]

    for check in report["checks"]:
        status = (
            "PASS"
            if check["passed"]
            else "FAIL"
        )

        details = str(
            check["details"]
        ).replace("|", "/")

        lines.append(
            f"| {check['name']} "
            f"| {status} "
            f"| {check['blocking']} "
            f"| {details} |"
        )

    retrieval = snapshots["retrieval"]
    generation = snapshots["generation"]
    model = snapshots["model_comparison"]

    lines.extend(
        [
            "",
            "## Evaluation snapshot",
            "",
            (
                f"- Retrieval passed: "
                f"`{retrieval['passed_cases']}/"
                f"{retrieval['strict_cases']}`"
            ),
            (
                f"- Retrieval accuracy: "
                f"`{retrieval['overall_accuracy']:.2f}%`"
            ),
            (
                f"- False positives: "
                f"`{retrieval['false_positive']}`"
            ),
            (
                f"- False negatives: "
                f"`{retrieval['false_negative']}`"
            ),
            (
                f"- Generation passed: "
                f"`{generation['passed_cases']}/"
                f"{generation['total_cases']}`"
            ),
            (
                f"- Generation accuracy: "
                f"`{generation['overall_accuracy']:.2f}%`"
            ),
            (
                f"- Selected chat model: "
                f"`{model['selected_model']}`"
            ),
            (
                f"- Selected model quality: "
                f"`{model['quality_rate']:.2f}%`"
            ),
            "",
            "## Git state during audit",
            "",
        ]
    )

    worktree_status = report[
        "git_hygiene"
    ]["worktree_status"]

    if worktree_status:
        lines.append(
            "The following expected working-tree "
            "changes existed while the audit was "
            "generated:"
        )
        lines.append("")

        for status_line in worktree_status:
            lines.append(
                f"- `{status_line}`"
            )

    else:
        lines.append(
            "The working tree was clean."
        )

    lines.extend(
        [
            "",
            "## Release conclusion",
            "",
        ]
    )

    if summary["release_ready"]:
        lines.append(
            "All blocking audit checks passed. "
            "The project is eligible for the "
            "`v1.0.0` release workflow."
        )
    else:
        lines.append(
            "At least one blocking audit check "
            "failed. The release workflow must "
            "not continue until the failure is "
            "resolved."
        )

    lines.append("")

    return "\n".join(lines)


def run_final_audit() -> dict[str, Any]:
    """
    Projenin final release audit'ini calistirir
    ve JSON ile Markdown raporlari uretir.
    """
    reports, report_errors = load_reports()
    checks: list[dict[str, Any]] = []

    reports_loaded = (
        len(reports) == len(REPORT_FILES)
        and not report_errors
    )

    checks.append(
        create_check(
            name="JSON report loading",
            passed=reports_loaded,
            details=(
                f"{len(reports)}/"
                f"{len(REPORT_FILES)} reports "
                "loaded successfully."
                if reports_loaded
                else str(report_errors)
            ),
        )
    )

    schema_versions = {
        key: report.get("schema_version")
        for key, report in reports.items()
    }

    schema_valid = (
        reports_loaded
        and all(
            version == 1
            for version in (
                schema_versions.values()
            )
        )
    )

    checks.append(
        create_check(
            name="Report schema versions",
            passed=schema_valid,
            details=str(schema_versions),
        )
    )

    retrieval_report = reports.get(
        "retrieval",
        {},
    )
    retrieval_summary = retrieval_report.get(
        "summary",
        {},
    )

    retrieval_accuracy = normalize_percentage(
        retrieval_summary.get(
            "overall_accuracy"
        )
    )

    retrieval_valid = all(
        [
            retrieval_summary.get(
                "failed_cases"
            )
            == 0,
            retrieval_accuracy == 100.0,
            retrieval_summary.get(
                "false_positive"
            )
            == 0,
            retrieval_summary.get(
                "false_negative"
            )
            == 0,
        ]
    )

    checks.append(
        create_check(
            name="Retrieval regression",
            passed=retrieval_valid,
            details=(
                f"passed="
                f"{retrieval_summary.get('passed_cases')}, "
                f"failed="
                f"{retrieval_summary.get('failed_cases')}, "
                f"accuracy="
                f"{retrieval_accuracy:.2f}%, "
                f"FP="
                f"{retrieval_summary.get('false_positive')}, "
                f"FN="
                f"{retrieval_summary.get('false_negative')}"
            ),
        )
    )

    generation_report = reports.get(
        "generation",
        {},
    )
    generation_summary = generation_report.get(
        "summary",
        {},
    )

    generation_accuracy = normalize_percentage(
        generation_summary.get(
            "overall_accuracy"
        )
    )

    generation_valid = all(
        [
            generation_summary.get(
                "failed_cases"
            )
            == 0,
            generation_accuracy == 100.0,
            normalize_percentage(
                generation_summary.get(
                    "source_accuracy"
                )
            )
            == 100.0,
            normalize_percentage(
                generation_summary.get(
                    "concept_accuracy"
                )
            )
            == 100.0,
            normalize_percentage(
                generation_summary.get(
                    "fallback_accuracy"
                )
            )
            == 100.0,
        ]
    )

    checks.append(
        create_check(
            name="Generation regression",
            passed=generation_valid,
            details=(
                f"passed="
                f"{generation_summary.get('passed_cases')}, "
                f"failed="
                f"{generation_summary.get('failed_cases')}, "
                f"accuracy="
                f"{generation_accuracy:.2f}%"
            ),
        )
    )

    latency_report = reports.get(
        "generation_latency",
        {},
    )

    fastest_configuration = (
        latency_report.get(
            "fastest_valid_configuration"
        )
    )

    selected_max_tokens = (
        find_selected_max_tokens(
            fastest_configuration
        )
    )

    latency_valid = (
        isinstance(
            fastest_configuration,
            dict,
        )
        and selected_max_tokens
        == DEFAULT_MAX_TOKENS
    )

    checks.append(
        create_check(
            name="Generation latency selection",
            passed=latency_valid,
            details=(
                f"selected_max_tokens="
                f"{selected_max_tokens}, "
                f"runtime_default="
                f"{DEFAULT_MAX_TOKENS}"
            ),
        )
    )

    model_report = reports.get(
        "model_comparison",
        {},
    )

    fastest_model = model_report.get(
        "fastest_valid_model"
    )

    if isinstance(fastest_model, dict):
        selected_model = fastest_model.get(
            "model_alias"
        )
        model_quality = normalize_percentage(
            fastest_model.get(
                "quality_rate"
            )
        )
        model_checks_passed = bool(
            fastest_model.get(
                "all_quality_checks_passed"
            )
        )
    else:
        selected_model = None
        model_quality = 0.0
        model_checks_passed = False

    model_valid = all(
        [
            selected_model
            == CHAT_MODEL_ALIAS,
            model_quality == 100.0,
            model_checks_passed,
        ]
    )

    checks.append(
        create_check(
            name="Chat model selection",
            passed=model_valid,
            details=(
                f"selected_model={selected_model}, "
                f"runtime_default="
                f"{CHAT_MODEL_ALIAS}, "
                f"quality="
                f"{model_quality:.2f}%"
            ),
        )
    )

    baseline_report = reports.get(
        "performance_baseline",
        {},
    )
    baseline_summary = baseline_report.get(
        "summary",
        {},
    )

    baseline_valid = all(
        [
            baseline_summary.get(
                "failed_runs"
            )
            == 0,
            normalize_percentage(
                baseline_summary.get(
                    "correctness_rate"
                )
            )
            == 100.0,
        ]
    )

    checks.append(
        create_check(
            name="Baseline performance correctness",
            passed=baseline_valid,
            details=(
                f"passed="
                f"{baseline_summary.get('passed_runs')}, "
                f"failed="
                f"{baseline_summary.get('failed_runs')}"
            ),
        )
    )

    optimized_report = reports.get(
        "performance_optimized",
        {},
    )
    optimized_summary = optimized_report.get(
        "summary",
        {},
    )

    optimized_valid = all(
        [
            optimized_summary.get(
                "failed_runs"
            )
            == 0,
            normalize_percentage(
                optimized_summary.get(
                    "correctness_rate"
                )
            )
            == 100.0,
            bool(
                optimized_summary.get(
                    "answered_model_reuse_correct"
                )
            ),
            bool(
                optimized_summary.get(
                    "unsupported_model_behavior_correct"
                )
            ),
        ]
    )

    checks.append(
        create_check(
            name="Persistent session performance",
            passed=optimized_valid,
            details=(
                f"passed="
                f"{optimized_summary.get('passed_runs')}, "
                f"failed="
                f"{optimized_summary.get('failed_runs')}, "
                "answered_reuse="
                f"{optimized_summary.get(
                    'answered_model_reuse_correct'
                )}, "
                "unsupported_behavior="
                f"{optimized_summary.get(
                    'unsupported_model_behavior_correct'
                )}"
            ),
        )
    )

    performance_report = reports.get(
        "performance_report",
        {},
    )
    performance_summary = (
        performance_report.get(
            "summary",
            {},
        )
    )

    performance_valid = all(
        [
            performance_summary.get(
                "failed_runs"
            )
            == 0,
            normalize_percentage(
                performance_summary.get(
                    "correctness_rate"
                )
            )
            == 100.0,
        ]
    )

    checks.append(
        create_check(
            name="Performance benchmark report",
            passed=performance_valid,
            details=(
                f"passed="
                f"{performance_summary.get('passed_runs')}, "
                f"failed="
                f"{performance_summary.get('failed_runs')}"
            ),
        )
    )

    compile_success = compileall.compile_dir(
        str(BASE_DIR / "src"),
        quiet=1,
    )

    checks.append(
        create_check(
            name="Python source compilation",
            passed=compile_success,
            details=(
                "All src Python files compiled."
                if compile_success
                else "At least one Python file "
                "failed to compile."
            ),
        )
    )

    missing_project_files = [
        relative_path
        for relative_path in (
            REQUIRED_PROJECT_FILES
        )
        if not (
            BASE_DIR / relative_path
        ).exists()
    ]

    checks.append(
        create_check(
            name="Required project files",
            passed=(
                not missing_project_files
            ),
            details=(
                "All required files exist."
                if not missing_project_files
                else (
                    "Missing: "
                    + ", ".join(
                        missing_project_files
                    )
                )
            ),
        )
    )

    git_hygiene = collect_git_hygiene()

    forbidden_files = git_hygiene[
        "forbidden_tracked_files"
    ]

    checks.append(
        create_check(
            name="Tracked-file hygiene",
            passed=not forbidden_files,
            details=(
                "No forbidden generated or "
                "environment files are tracked."
                if not forbidden_files
                else str(forbidden_files)
            ),
        )
    )

    secret_scan_valid = all(
        [
            not git_hygiene[
                "secret_matches"
            ],
            git_hygiene[
                "secret_scan_error"
            ]
            is None,
        ]
    )

    checks.append(
        create_check(
            name="Secret-pattern scan",
            passed=secret_scan_valid,
            details=(
                "No secret patterns detected."
                if secret_scan_valid
                else (
                    str(
                        git_hygiene[
                            "secret_matches"
                        ]
                    )
                    or str(
                        git_hygiene[
                            "secret_scan_error"
                        ]
                    )
                )
            ),
        )
    )

    runtime_configuration_valid = all(
        [
            CHAT_MODEL_ALIAS
            == "phi-4-mini",
            DEFAULT_MAX_TOKENS == 160,
            DEFAULT_TEMPERATURE == 0.0,
        ]
    )

    checks.append(
        create_check(
            name="Runtime default configuration",
            passed=runtime_configuration_valid,
            details=(
                f"model={CHAT_MODEL_ALIAS}, "
                f"max_tokens="
                f"{DEFAULT_MAX_TOKENS}, "
                f"temperature="
                f"{DEFAULT_TEMPERATURE}"
            ),
        )
    )

    blocking_checks = [
        check
        for check in checks
        if check["blocking"]
    ]

    blocking_passed = sum(
        check["passed"]
        for check in blocking_checks
    )

    passed_checks = sum(
        check["passed"]
        for check in checks
    )

    release_ready = (
        blocking_passed
        == len(blocking_checks)
    )

    retrieval_dataset = (
        retrieval_report.get(
            "dataset",
            {},
        )
    )

    strict_cases = (
        retrieval_dataset.get(
            "strict_case_count"
        )
        or retrieval_dataset.get(
            "strict_cases"
        )
        or retrieval_summary.get(
            "passed_cases",
            0,
        )
        + retrieval_summary.get(
            "failed_cases",
            0,
        )
    )

    report = {
        "schema_version": 1,
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "audit_type": (
            "foundry_local_rag_final_release"
        ),
        "target_release": "v1.0.0",
        "summary": {
            "release_ready": release_ready,
            "total_checks": len(checks),
            "passed_checks": passed_checks,
            "failed_checks": (
                len(checks) - passed_checks
            ),
            "blocking_total": len(
                blocking_checks
            ),
            "blocking_passed": (
                blocking_passed
            ),
            "blocking_failed": (
                len(blocking_checks)
                - blocking_passed
            ),
        },
        "project_configuration": {
            "chat_model": CHAT_MODEL_ALIAS,
            "max_tokens": (
                DEFAULT_MAX_TOKENS
            ),
            "temperature": (
                DEFAULT_TEMPERATURE
            ),
        },
        "checks": checks,
        "report_snapshots": {
            "retrieval": {
                "strict_cases": strict_cases,
                "passed_cases": (
                    retrieval_summary.get(
                        "passed_cases",
                        0,
                    )
                ),
                "failed_cases": (
                    retrieval_summary.get(
                        "failed_cases",
                        0,
                    )
                ),
                "overall_accuracy": (
                    retrieval_accuracy
                ),
                "false_positive": (
                    retrieval_summary.get(
                        "false_positive",
                        0,
                    )
                ),
                "false_negative": (
                    retrieval_summary.get(
                        "false_negative",
                        0,
                    )
                ),
            },
            "generation": {
                "total_cases": (
                    generation_summary.get(
                        "total_cases",
                        0,
                    )
                ),
                "passed_cases": (
                    generation_summary.get(
                        "passed_cases",
                        0,
                    )
                ),
                "failed_cases": (
                    generation_summary.get(
                        "failed_cases",
                        0,
                    )
                ),
                "overall_accuracy": (
                    generation_accuracy
                ),
            },
            "generation_latency": {
                "selected_max_tokens": (
                    selected_max_tokens
                ),
                "measured_run_count": (
                    latency_report.get(
                        "measured_run_count"
                    )
                ),
            },
            "model_comparison": {
                "selected_model": (
                    selected_model
                ),
                "quality_rate": (
                    model_quality
                ),
                "measured_run_count": (
                    model_report.get(
                        "measured_run_count"
                    )
                ),
            },
            "performance": {
                "baseline_passed_runs": (
                    baseline_summary.get(
                        "passed_runs"
                    )
                ),
                "optimized_passed_runs": (
                    optimized_summary.get(
                        "passed_runs"
                    )
                ),
                "persistent_reuse_correct": (
                    optimized_summary.get(
                        "answered_model_reuse_correct"
                    )
                ),
            },
        },
        "git_hygiene": git_hygiene,
        "report_sources": REPORT_FILES,
        "report_errors": report_errors,
    }

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    FINAL_AUDIT_JSON_PATH.write_text(
        json.dumps(
            report,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    markdown_report = (
        create_markdown_report(
            report
        )
    )

    FINAL_AUDIT_MARKDOWN_PATH.write_text(
        markdown_report,
        encoding="utf-8",
    )

    return {
        "report": report,
        "json_path": (
            FINAL_AUDIT_JSON_PATH
        ),
        "markdown_path": (
            FINAL_AUDIT_MARKDOWN_PATH
        ),
    }