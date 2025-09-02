#!/usr/bin/env python3
"""Interactive initial user setup questionnaire + voice enrollment stub.

Writes responses to data/users/<user_key>/profile.json and (optionally) a
placeholder speaker embedding file if voice enrollment is selected.

Design Goals:
  * Keep pure Python + stdlib (no heavy ML deps in scaffold)
  * Deterministic user_key generation (hash of preferred name + optional secret)
  * Simple schema-driven questioning loaded from questionnaires/initial_profile_questionnaire.json
  * Extensible: plug real speaker embedding extraction later
"""
from __future__ import annotations

import argparse, json, hashlib, os, sys, datetime, getpass
from typing import Any, Dict, List

QUESTIONNAIRE_PATH = "questionnaires/initial_profile_questionnaire.json"


def load_questions(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def hash_user_key(preferred_name: str, secret: str | None) -> str:
    basis = (preferred_name.strip().lower() + "::" + (secret or ""))
    return hashlib.sha256(basis.encode()).hexdigest()[:16]


def prompt_input(q: Dict[str, Any]) -> Any:
    qtype = q["type"]
    prompt = q["prompt"].strip() + " "
    if qtype == "confirm":
        while True:
            ans = input(prompt).strip().lower()
            if ans in {"yes","y"}: return True
            if ans in {"no","n"}: return False
            print("Please answer yes or no.")
    elif qtype == "text":
        ans = input(prompt)
        return ans.strip()
    elif qtype == "choice":
        opts = q.get("options", [])
        print(f"Options: {', '.join(opts)}")
        while True:
            ans = input(prompt).strip()
            if ans in opts:
                return ans
            print("Select one of the listed options.")
    elif qtype == "multi_choice":
        opts = q.get("options", [])
        print(f"Options (comma separated): {', '.join(opts)}")
        ans = input(prompt).strip()
        chosen = [x.strip() for x in ans.split(",") if x.strip()]
        return [c for c in chosen if c in opts or c == "Other"]
    else:
        print(f"[warn] Unknown question type {qtype}; skipping", file=sys.stderr)
        return None


def fake_speaker_embedding() -> Dict[str, Any]:
    # Placeholder: real implementation would record audio & run model
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    return {
        "version": 1,
        "model": "placeholder",
        "vector": [0.0]*16,  # small dummy vector
        "created_at": now,
        "notes": "Replace with real speaker embedding pipeline"
    }


def run_interactive(secret: str | None, dry_run: bool) -> int:
    questions = load_questions(QUESTIONNAIRE_PATH)
    answers: Dict[str, Any] = {}
    print("--- Initial Profile Setup ---")
    preferred_name = None
    for q in questions:
        if q["id"] == "learner.name_preferred":
            # ensure consent first if defined earlier
            ans = prompt_input(q)
            if q.get("required") and not ans:
                print("Preferred name required.")
                return 1
            preferred_name = ans or "user"
            answers[q["id"]] = preferred_name
        else:
            # If consent question and declined, stop early
            if q["id"] == "consent.data_use":
                ans = prompt_input(q)
                answers[q["id"]] = ans
                if not ans:
                    print("Consent declined; aborting and not storing responses.")
                    return 0
                continue
            ans = prompt_input(q)
            if q.get("required") and (ans is None or ans == ""):
                print("Required question skipped; exiting.")
                return 1
            answers[q["id"]] = ans

    user_key = hash_user_key(preferred_name or "user", secret)
    base_dir = os.path.join("data", "users", user_key)
    profile_path = os.path.join(base_dir, "profile.json")
    os.makedirs(base_dir, exist_ok=True)

    # Optional voice embedding
    if answers.get("interaction.voice_opt_in"):
        embedding = fake_speaker_embedding()
        answers["voice_embedding_ref"] = "speaker_embedding.json"
    else:
        embedding = None

    metadata = {
        "user_key": user_key,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "schema_version": 1,
        "answers": answers,
    }

    if dry_run:
        print("[dry-run] Would write profile.json:")
        print(json.dumps(metadata, indent=2))
    else:
        with open(profile_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        if embedding:
            with open(os.path.join(base_dir, "speaker_embedding.json"), "w", encoding="utf-8") as f:
                json.dump(embedding, f, indent=2)
        print(f"[ok] Stored profile for {preferred_name} -> {profile_path}")
    return 0


def parse_args(argv=None):
    ap = argparse.ArgumentParser(description="Run initial setup questionnaire")
    ap.add_argument("--secret", help="Optional secret salt for user key derivation")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--prompt-secret", action="store_true", help="Interactively prompt for secret")
    return ap.parse_args(argv)


def main():
    args = parse_args()
    secret = args.secret
    if args.prompt_secret and not secret:
        secret = getpass.getpass("Enter secret salt (not stored): ")
    return run_interactive(secret, args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
