"""Phase 4A Validation Script - QA Lead

Tests new multi-channel bot integration foundation:
1. Meta sender service (meta_sender.py)
2. Message dispatcher (message_sender.py)
3. ConversationState changes (state.py)
4. CRUD helper (get_channel_config_for_user)

Runs tests and generates validation report.
"""

import subprocess
import sys
from pathlib import Path

def run_tests(test_path, description):
    """Run pytest and return results."""
    print(f"\n{'='*70}")
    print(f"Testing: {description}")
    print(f"{'='*70}\n")

    result = subprocess.run(
        [sys.executable, "-m", "pytest", test_path, "-v", "-k", "not trio", "--tb=short"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent.parent
    )

    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    return result.returncode == 0

def main():
    """Run all validation tests and generate report."""
    print("Phase 4A Foundation Validation")
    print("="*70)

    results = {}

    # Test 1: MessageSender dispatcher
    results["MessageSender"] = run_tests(
        "apps/bot-engine/tests/unit/test_message_sender.py",
        "MessageSender (multi-channel dispatcher)"
    )

    # Test 2: MetaSenderService
    results["MetaSender"] = run_tests(
        "apps/bot-engine/tests/unit/test_meta_sender.py",
        "MetaSenderService (Instagram/Messenger)"
    )

    # Test 3: CRUD helper
    results["CRUD Helper"] = run_tests(
        "packages/database/tests/test_crud_channel_config.py",
        "get_channel_config_for_user() CRUD helper"
    )

    # Summary
    print("\n" + "="*70)
    print("VALIDATION SUMMARY")
    print("="*70)

    all_passed = True
    for component, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"{component:30} {status}")
        if not passed:
            all_passed = False

    print("="*70)

    if all_passed:
        print("\nRECOMMENDATION: Safe to commit")
        return 0
    else:
        print("\nRECOMMENDATION: Fixes needed - see failures above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
