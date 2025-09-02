import argparse
import os
import sys
from dataclasses import dataclass


@dataclass
class ReplChoice:
    mode: str
    reason: str | None


def choose_repl(force: str | None) -> ReplChoice:
    if force == "fallback" or os.getenv("MUTANTS2_NO_PTK") == "1":
        return ReplChoice("Fallback", "forced_fallback")
    try:
        import prompt_toolkit  # noqa: F401
    except Exception as e:  # pragma: no cover
        return ReplChoice("Fallback", f"import_error: {e.__class__.__name__}")
    if force == "ptk":
        return ReplChoice("PTK", None)
    return ReplChoice("PTK", None) if sys.stdin.isatty() else ReplChoice("Fallback", "not_tty")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dev", action="store_true")
    parser.add_argument("--macro-profile")
    parser.add_argument("--ptk", action="store_true")
    parser.add_argument("--no-ptk", action="store_true")
    args = parser.parse_args()

    dev = args.dev or os.environ.get("MUTANTS2_DEV") == "1"
    if args.ptk and args.no_ptk:
        print("Cannot use both --ptk and --no-ptk")
        sys.exit(1)

    force = "ptk" if args.ptk else ("fallback" if args.no_ptk else None)
    choice = choose_repl(force)
    if args.ptk and choice.mode != "PTK":
        print(f"prompt_toolkit unavailable ({choice.reason})")
        sys.exit(1)

    from mutants2.cli.shell import make_context

    ctx = make_context(
        dev=dev,
        macro_profile=args.macro_profile,
        repl_mode=choice.mode,
        repl_reason=choice.reason,
    )

    if choice.mode == "PTK":
        from mutants2.cli.repl import PtkRepl

        PtkRepl(ctx).run()
    else:
        from mutants2.cli.repl import FallbackRepl

        FallbackRepl(ctx).run()


if __name__ == "__main__":  # pragma: no cover
    main()
