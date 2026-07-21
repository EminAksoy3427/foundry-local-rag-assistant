# Final Audit Report

- Generated at: `2026-07-21T13:07:58.053626+00:00`
- Release ready: `True`
- Blocking checks passed: `14/14`
- All checks passed: `14/14`

## Project configuration

- Chat model: `phi-4-mini`
- Max tokens: `160`
- Temperature: `0.0`

## Audit checks

| Check | Status | Blocking | Details |
|---|---:|---:|---|
| JSON report loading | PASS | True | 7/7 reports loaded successfully. |
| Report schema versions | PASS | True | {'retrieval': 1, 'generation': 1, 'generation_latency': 1, 'model_comparison': 1, 'performance_baseline': 1, 'performance_optimized': 1, 'performance_report': 1} |
| Retrieval regression | PASS | True | passed=12, failed=0, accuracy=100.00%, FP=0, FN=0 |
| Generation regression | PASS | True | passed=5, failed=0, accuracy=100.00% |
| Generation latency selection | PASS | True | selected_max_tokens=160, runtime_default=160 |
| Chat model selection | PASS | True | selected_model=phi-4-mini, runtime_default=phi-4-mini, quality=100.00% |
| Baseline performance correctness | PASS | True | passed=9, failed=0 |
| Persistent session performance | PASS | True | passed=9, failed=0, answered_reuse=True, unsupported_behavior=True |
| Performance benchmark report | PASS | True | passed=9, failed=0 |
| Python source compilation | PASS | True | All src Python files compiled. |
| Required project files | PASS | True | All required files exist. |
| Tracked-file hygiene | PASS | True | No forbidden generated or environment files are tracked. |
| Secret-pattern scan | PASS | True | No secret patterns detected. |
| Runtime default configuration | PASS | True | model=phi-4-mini, max_tokens=160, temperature=0.0 |

## Evaluation snapshot

- Retrieval passed: `12/12`
- Retrieval accuracy: `100.00%`
- False positives: `0`
- False negatives: `0`
- Generation passed: `5/5`
- Generation accuracy: `100.00%`
- Selected chat model: `phi-4-mini`
- Selected model quality: `100.00%`

## Git state during audit

The following expected working-tree changes existed while the audit was generated:

- `A  CHANGELOG.md`
- `M  README.md`
- `M  docs/project-notes.md`
- `A  docs/release-notes-v1.0.0.md`
- `M  reports/evaluation_report.json`
- `A  reports/final_audit_report.json`
- `A  reports/final_audit_report.md`
- `M  reports/generation_evaluation_report.json`
- `A  src/final_audit.py`
- `A  src/final_audit_demo.py`

## Release conclusion

All blocking audit checks passed. The project is eligible for the `v1.0.0` release workflow.
