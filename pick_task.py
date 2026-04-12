#!/usr/bin/env python3
"""Pick the highest-priority task from the fleet task board."""

import json
import os
import urllib.request

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
API_BASE = "https://api.github.com"

def api_get(path):
    req = urllib.request.Request(f"{API_BASE}{path}")
    req.add_header("Authorization", f"token {GITHUB_TOKEN}")
    req.add_header("Accept", "application/vnd.github.v3+json")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}

def main():
    print("📋 FLEET TASK PICKER\n")
    
    issues = api_get("/repos/SuperInstance/fleet-workshop/issues?state=open")
    
    print("🔴 FLEET WORKSHOP ISSUES (highest priority first):\n")
    if isinstance(issues, list):
        for iss in issues:
            labels = " ".join(f"[{l['name']}]" for l in iss.get("labels", []))
            print(f"  #{iss['number']} {labels}")
            print(f"     {iss['title']}")
            print(f"     {iss['html_url']}\n")
    
    print("🔧 CRITICAL REPO ISSUES:\n")
    for repo in ["flux-runtime", "flux-runtime-c", "fleet-mechanic"]:
        issues = api_get(f"/repos/SuperInstance/{repo}/issues?state=open&per_page=5")
        if isinstance(issues, list) and issues:
            print(f"  {repo}:")
            for iss in issues:
                print(f"    #{iss['number']} {iss['title'][:60]}")
            print()
    
    print("📨 RECENT FLEET DISPATCHES:\n")
    directives = api_get("/repos/SuperInstance/oracle1-vessel/contents/for-fleet")
    if isinstance(directives, list):
        for d in directives:
            print(f"  {d['name']}")
    
    print("\n\nPick a 🔴 task. Clone the repo. Fix it. Push a PR. Report in for-fleet/.")

if __name__ == "__main__":
    main()
