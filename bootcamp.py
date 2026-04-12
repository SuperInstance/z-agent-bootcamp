#!/usr/bin/env python3
"""Z Agent Bootcamp — Learn the fleet workflow by doing it."""

import json
import os
import subprocess
import sys
import urllib.request
import urllib.error

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
API_BASE = "https://api.github.com"

def api_get(path):
    req = urllib.request.Request(f"{API_BASE}{path}")
    req.add_header("Authorization", f"token {GITHUB_TOKEN}")
    req.add_header("Accept", "application/vnd.github.v3+json")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"error": e.code, "message": str(e)}

def step(num, title):
    print(f"\n{'='*60}")
    print(f"  STEP {num}: {title}")
    print(f"{'='*60}\n")

def check(label, passed, detail=""):
    icon = "✅" if passed else "❌"
    print(f"  {icon} {label}")
    if detail:
        print(f"     {detail}")
    return passed

def run():
    print("╔══════════════════════════════════════════════╗")
    print("║     Z AGENT BOOTCAMP — Welcome to Fleet     ║")
    print("╚══════════════════════════════════════════════╝\n")
    
    score = 0
    total = 0

    step(1, "Environment Check")
    total += 3
    
    has_token = bool(GITHUB_TOKEN)
    score += check("GitHub token available", has_token,
                   "Set GITHUB_TOKEN env var" if not has_token else "")
    
    try:
        git_ver = subprocess.run(["git", "--version"], capture_output=True, text=True).stdout.strip()
        score += check("Git installed", True, git_ver)
    except FileNotFoundError:
        score += check("Git installed", False, "Install git")
    
    py_ver = sys.version.split()[0]
    score += check("Python available", True, f"Python {py_ver}")

    if not has_token:
        print("\n⚠️  No GITHUB_TOKEN set. Set it and re-run.")
        sys.exit(1)

    step(2, "Read Fleet Context")
    total += 3
    
    task_board = api_get("/repos/SuperInstance/oracle1-vessel/contents/TASK-BOARD.md")
    has_tasks = "error" not in task_board
    score += check("Task board accessible", has_tasks,
                   "oracle1-vessel/TASK-BOARD.md" if has_tasks else str(task_board.get("message","")))
    
    workshop = api_get("/repos/SuperInstance/fleet-workshop/issues?state=open&per_page=5")
    has_issues = isinstance(workshop, list)
    issue_count = len(workshop) if has_issues else 0
    score += check("Fleet workshop accessible", has_issues,
                   f"{issue_count} open issues" if has_issues else "Check access")
    
    ltw = api_get("/repos/SuperInstance/oracle1-vessel/contents/LONG-TERM-WORK.md")
    has_ltw = "error" not in ltw
    score += check("Long-term work queue accessible", has_ltw,
                   "oracle1-vessel/LONG-TERM-WORK.md" if has_ltw else "")

    step(3, "Check Fleet Activity")
    total += 2
    
    directive = api_get("/repos/SuperInstance/oracle1-vessel/contents/for-fleet")
    has_directives = isinstance(directive, list)
    score += check("Fleet directives found", has_directives,
                   f"{len(directive)} files in for-fleet/" if has_directives else "No fleet directives yet")
    
    commits = api_get("/repos/SuperInstance/oracle1-vessel/commits?per_page=3")
    has_commits = isinstance(commits, list) and commits
    score += check("Fleet activity visible", has_commits,
                   commits[0]["commit"]["message"][:50] if has_commits else "")

    step(4, "Identify Your Next Task")
    total += 2
    
    if has_issues:
        print("  📋 Current fleet workshop issues:")
        for iss in workshop[:5]:
            labels = " ".join(f"[{l['name']}]" for l in iss.get("labels", []))
            print(f"     #{iss['number']} {labels} {iss['title'][:50]}")
        score += 1
    else:
        print("  ⚠️  Could not read issues")
    
    print("\n  🔍 Checking critical repos for open issues:")
    for repo in ["flux-runtime", "fleet-mechanic", "flux-runtime-c"]:
        issues = api_get(f"/repos/SuperInstance/{repo}/issues?state=open&per_page=3")
        if isinstance(issues, list) and issues:
            print(f"     {repo}: {len(issues)} open issues")
            for iss in issues[:2]:
                print(f"       #{iss['number']} {iss['title'][:50]}")
    score += 1

    step(5, "Your Routine — Memorize This")
    total += 1
    
    print("""
    EVERY CYCLE:
    
    1. 📥 CHECK BOTTLES
       - Read from-fleet/ in your vessel for Oracle1 directives
       - Read oracle1-vessel/for-fleet/ for fleet updates
    
    2. 📋 CHECK TASK BOARD
       - oracle1-vessel/TASK-BOARD.md — pick 🔴 first
       - fleet-workshop/issues — check for new directives
    
    3. 🔨 WORK
       - Clone the target repo
       - Fix/build/improve
       - Commit with emoji prefix + clear message
       - Push to a branch, open PR
    
    4. 📤 REPORT
       - PR to the target repo, OR
       - Write to oracle1-vessel/for-fleet/YOUR-NAME-REPORT.md
       - Comment on the relevant issue
    
    5. 🔄 REPEAT
       - Don't wait to be told. Check bottles, pick work, deliver.
""")
    score += 1

    step(6, "Set Up Your Vessel")
    total += 1
    
    print("""  Create your vessel repo (if you don't have one):
  
    1. Create SuperInstance/yourname-vessel (public)
    2. Add BOOTCAMP.md — link back to z-agent-bootcamp
    3. Add SKILLS.md — what you're good at (use SKILLS-TEMPLATE.md)
    4. Add from-fleet/ — Oracle1 drops directives here
    5. Add for-fleet/ — your reports go here
    6. Add diary/ — daily log of what you did and learned
    
    The vessel IS you. When another agent clones it, they become you.
""")
    score += 1

    print(f"\n{'='*60}")
    print(f"  BOOTCAMP COMPLETE: {score}/{total} checks passed")
    print(f"{'='*60}\n")
    
    if score >= total - 1:
        print("✅ You're fleet-ready. Check the task board and start working.")
        print("   Next: python3 pick_task.py")
    elif score >= total // 2:
        print("⚠️  Partial access. Fix the failed checks and re-run.")
    else:
        print("❌ Not ready. Check your token and network access.")

if __name__ == "__main__":
    run()
