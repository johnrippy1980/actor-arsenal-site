#!/usr/bin/env python3
"""
Actor Demo Runner
==================
Runs each Apify actor up to 50 successful demo runs.
Stops immediately on first failure for each actor.

Features:
- Runs actors in demo/free mode with minimal input
- Tracks successful vs failed runs
- Stops on first failure to avoid running up costs
- Logs all results to JSON for review
- Supports resuming from a specific actor

Usage:
    python3 demo_runner.py                    # Run all actors
    python3 demo_runner.py --actor google-maps-scraper  # Run specific actor
    python3 demo_runner.py --resume           # Resume from last failure
    python3 demo_runner.py --max-runs 10      # Override max runs per actor
    python3 demo_runner.py --dry-run          # Show what would run

Environment Variables:
    APIFY_TOKEN - Required Apify API token
"""

import json
import os
import sys
import time
import argparse
from datetime import datetime
from pathlib import Path
import urllib.request
import urllib.error
import urllib.parse

# Configuration
APIFY_API_BASE = "https://api.apify.com/v2"
APIFY_TOKEN = os.environ.get("APIFY_TOKEN") or os.environ.get("APIFY_API_TOKEN", "")
MAX_RUNS_PER_ACTOR = 50
POLL_INTERVAL = 5  # seconds
RUN_TIMEOUT = 300  # 5 minutes max per run

RESULTS_FILE = Path(__file__).parent / "demo_run_results.json"
RESUME_FILE = Path(__file__).parent / ".demo_runner_resume.json"

# Default minimal inputs for different actor types
DEFAULT_INPUTS = {
    # Maps/Location scrapers
    "google-maps-scraper": {"searchQuery": "coffee shop", "maxResults": 1},
    "yelp-scraper": {"searchQuery": "restaurant", "location": "New York", "maxResults": 1},
    "apple-maps-scraper": {"query": "bank", "limit": 1},
    "bing-maps-scraper": {"searchQuery": "pharmacy", "maxResults": 1},

    # Review scrapers
    "review-scraper": {"url": "https://www.google.com/maps/place/Starbucks/@40.7580,-73.9855,17z", "maxReviews": 1},
    "tripadvisor-scraper": {"url": "https://www.tripadvisor.com/Restaurant_Review-g60763-d457808", "maxReviews": 1},
    "trustpilot-scraper": {"url": "https://www.trustpilot.com/review/apple.com", "maxReviews": 1},

    # Social media scrapers
    "instagram-scraper": {"profiles": ["instagram"], "resultsLimit": 1},
    "linkedin-profile-scraper": {"profileUrls": [], "maxProfiles": 1},  # Needs auth
    "linkedin-post-scraper": {"postUrls": [], "maxPosts": 1},
    "tiktok-scraper": {"profiles": ["tiktok"], "resultsLimit": 1},
    "facebook-page-post-scraper": {"pageUrl": "https://www.facebook.com/meta", "maxPosts": 1},
    "reddit-scraper": {"subreddit": "technology", "maxPosts": 1},
    "youtube-scraper": {"searchQuery": "test", "maxResults": 1},

    # Job scrapers
    "indeed-jobs-scraper": {"query": "software engineer", "location": "remote", "maxResults": 1},
    "linkedin-jobs-scraper": {"searchQuery": "developer", "maxResults": 1},
    "glassdoor-scraper": {"searchQuery": "data scientist", "maxResults": 1},

    # Real estate scrapers
    "zillow-scraper": {"searchQuery": "New York", "maxResults": 1},
    "redfin-scraper": {"searchUrl": "https://www.redfin.com/city/30749/NY/New-York", "maxResults": 1},
    "realtor-scraper": {"searchUrl": "https://www.realtor.com/realestateandhomes-search/New-York_NY", "maxResults": 1},
    "mls-scraper": {"query": "Austin TX", "maxResults": 1},

    # Food delivery scrapers
    "doordash-scraper": {"searchQuery": "pizza", "location": "Chicago", "maxResults": 1},
    "grubhub-scraper": {"searchQuery": "sushi", "location": "Los Angeles", "maxResults": 1},
    "ubereats-scraper": {"searchQuery": "burger", "location": "Miami", "maxResults": 1},

    # Directory scrapers
    "yellow-pages-scraper": {"searchQuery": "plumber", "location": "Texas", "maxResults": 1},
    "bbb-scraper": {"searchQuery": "contractor", "location": "Florida", "maxResults": 1},
    "manta-scraper": {"searchQuery": "electrician", "location": "California", "maxResults": 1},
    "angi-scraper": {"category": "plumbing", "location": "Denver", "maxResults": 1},

    # Business/Company scrapers
    "crunchbase-scraper": {"searchQuery": "AI startup", "maxResults": 1},
    "company-contact-enricher": {"domain": "anthropic.com"},
    "g2-scraper": {"productUrl": "https://www.g2.com/products/slack", "maxReviews": 1},
    "clutch-scraper": {"searchQuery": "web development", "maxResults": 1},
    "goodfirms-scraper": {"category": "mobile app development", "maxResults": 1},
    "capterra-scraper": {"searchQuery": "project management", "maxResults": 1},
    "product-hunt-scraper": {"maxProducts": 1},

    # SEO/Technical
    "google-serp-scraper": {"queries": ["test query"], "maxResults": 1},
    "people-also-ask-scraper": {"query": "how to", "maxQuestions": 1},
    "google-lighthouse-checker": {"url": "https://example.com"},
    "rich-results-tester": {"url": "https://example.com"},
    "robots-txt-checker": {"url": "https://example.com"},
    "sitemap-generator": {"startUrl": "https://example.com", "maxUrls": 1},
    "technical-seo-auditor": {"url": "https://example.com"},
    "website-crawler": {"startUrl": "https://example.com", "maxPages": 1},

    # Citation/Local SEO
    "citation-checker": {"businessName": "Starbucks", "city": "Seattle", "state": "WA"},
    "citation-builder": {"businessName": "Test Business", "address": "123 Main St", "city": "Test", "state": "CA", "zip": "90210"},
    "local-leads-scraper": {"query": "dentist", "location": "Boston", "maxResults": 1},

    # Misc
    "meta-ad-library": {"searchQuery": "coffee", "maxAds": 1},
    "google-ads-transparency": {"advertiserName": "Nike", "maxAds": 1},
    "nextdoor-scraper": {"location": "San Francisco", "maxPosts": 1},
    "quora-research": {"query": "best programming language", "maxAnswers": 1},
    "local-news-monitor": {"location": "New York", "maxArticles": 1},

    # Fallback minimal input for unknown actors
    "_default": {"maxResults": 1, "limit": 1}
}


def get_actor_input(actor_name: str) -> dict:
    """Get appropriate minimal demo input for an actor."""
    # Check for exact match first
    if actor_name in DEFAULT_INPUTS:
        return DEFAULT_INPUTS[actor_name]

    # Check for partial matches
    for key, value in DEFAULT_INPUTS.items():
        if key in actor_name or actor_name in key:
            return value

    # Return default
    return DEFAULT_INPUTS["_default"]


def fetch_actors() -> list[dict]:
    """Fetch all actors from Apify API."""
    actors = []
    offset = 0
    limit = 100

    print("Fetching actors from Apify...")

    while True:
        url = f"{APIFY_API_BASE}/acts?offset={offset}&limit={limit}&my=true&token={APIFY_TOKEN}"

        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                data = json.loads(response.read().decode())
                items = data.get("data", {}).get("items", [])

                if not items:
                    break

                actors.extend(items)

                if len(items) < limit:
                    break

                offset += limit
        except Exception as e:
            print(f"Error fetching actors: {e}")
            break

    print(f"Found {len(actors)} actors")
    return actors


def start_actor_run(actor_id: str, actor_name: str, input_data: dict) -> dict | None:
    """Start an actor run with the given input."""
    url = f"{APIFY_API_BASE}/acts/{actor_id}/runs?token={APIFY_TOKEN}"

    try:
        data = json.dumps(input_data).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode())
            return result.get("data", {})
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        print(f"    HTTP Error {e.code}: {error_body[:200]}")
        return None
    except Exception as e:
        print(f"    Error starting run: {e}")
        return None


def check_run_status(run_id: str) -> dict | None:
    """Check the status of an actor run."""
    url = f"{APIFY_API_BASE}/actor-runs/{run_id}?token={APIFY_TOKEN}"

    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            result = json.loads(response.read().decode())
            return result.get("data", {})
    except Exception as e:
        print(f"    Error checking run status: {e}")
        return None


def wait_for_run(run_id: str, timeout: int = RUN_TIMEOUT) -> dict:
    """Wait for a run to complete and return its final status."""
    start_time = time.time()

    while time.time() - start_time < timeout:
        status = check_run_status(run_id)

        if not status:
            return {"status": "UNKNOWN", "error": "Could not fetch status"}

        run_status = status.get("status", "UNKNOWN")

        if run_status in ["SUCCEEDED", "FAILED", "TIMED-OUT", "ABORTED"]:
            return {
                "status": run_status,
                "exitCode": status.get("exitCode"),
                "startedAt": status.get("startedAt"),
                "finishedAt": status.get("finishedAt"),
                "usageTotalUsd": status.get("usageTotalUsd", 0),
            }

        time.sleep(POLL_INTERVAL)

    return {"status": "TIMEOUT", "error": f"Run did not complete within {timeout}s"}


def run_actor_demos(actor: dict, max_runs: int, dry_run: bool = False) -> dict:
    """Run demo runs for a single actor until max_runs or first failure."""
    actor_id = actor.get("id", "")
    actor_name = actor.get("name", "unknown")
    actor_title = actor.get("title", actor_name)

    result = {
        "actor_id": actor_id,
        "actor_name": actor_name,
        "actor_title": actor_title,
        "successful_runs": 0,
        "failed_runs": 0,
        "runs": [],
        "stopped_reason": None,
    }

    print(f"\n{'='*60}")
    print(f"Actor: {actor_title}")
    print(f"ID: {actor_id}")
    print(f"Target: {max_runs} successful runs")
    print(f"{'='*60}")

    input_data = get_actor_input(actor_name)
    print(f"Input: {json.dumps(input_data, indent=2)}")

    if dry_run:
        print("[DRY RUN] Would execute runs here")
        return result

    for run_num in range(1, max_runs + 1):
        print(f"\n  Run {run_num}/{max_runs}...")

        # Start the run
        run_info = start_actor_run(actor_id, actor_name, input_data)

        if not run_info:
            result["failed_runs"] += 1
            result["runs"].append({
                "run_number": run_num,
                "status": "FAILED_TO_START",
                "timestamp": datetime.now().isoformat()
            })
            result["stopped_reason"] = "Failed to start run"
            print(f"    FAILED to start run. Stopping actor demos.")
            break

        run_id = run_info.get("id", "")
        print(f"    Run ID: {run_id}")

        # Wait for completion
        final_status = wait_for_run(run_id)
        status = final_status.get("status", "UNKNOWN")

        run_record = {
            "run_number": run_num,
            "run_id": run_id,
            "status": status,
            "cost_usd": final_status.get("usageTotalUsd", 0),
            "timestamp": datetime.now().isoformat()
        }
        result["runs"].append(run_record)

        if status == "SUCCEEDED":
            result["successful_runs"] += 1
            print(f"    SUCCESS (${final_status.get('usageTotalUsd', 0):.4f})")
        else:
            result["failed_runs"] += 1
            result["stopped_reason"] = f"Run failed with status: {status}"
            print(f"    FAILED with status: {status}")
            print(f"    Stopping actor demos due to failure.")
            break

        # Small delay between runs
        time.sleep(1)

    if result["successful_runs"] == max_runs:
        result["stopped_reason"] = "Reached target successful runs"
        print(f"\n  Completed {max_runs} successful runs!")

    return result


def save_results(results: list[dict]) -> None:
    """Save all results to JSON file."""
    output = {
        "generated_at": datetime.now().isoformat(),
        "total_actors": len(results),
        "summary": {
            "fully_successful": sum(1 for r in results if r["successful_runs"] == MAX_RUNS_PER_ACTOR),
            "partial_success": sum(1 for r in results if 0 < r["successful_runs"] < MAX_RUNS_PER_ACTOR),
            "all_failed": sum(1 for r in results if r["successful_runs"] == 0 and r["failed_runs"] > 0),
            "not_run": sum(1 for r in results if r["successful_runs"] == 0 and r["failed_runs"] == 0),
        },
        "results": results
    }

    with open(RESULTS_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to {RESULTS_FILE}")


def save_resume_state(actor_name: str) -> None:
    """Save resume state for later continuation."""
    with open(RESUME_FILE, "w") as f:
        json.dump({"last_actor": actor_name, "timestamp": datetime.now().isoformat()}, f)


def load_resume_state() -> str | None:
    """Load resume state if exists."""
    if RESUME_FILE.exists():
        with open(RESUME_FILE) as f:
            data = json.load(f)
            return data.get("last_actor")
    return None


def main():
    parser = argparse.ArgumentParser(description="Run Apify actor demos")
    parser.add_argument("--actor", help="Run specific actor only")
    parser.add_argument("--resume", action="store_true", help="Resume from last failure")
    parser.add_argument("--max-runs", type=int, default=MAX_RUNS_PER_ACTOR, help="Max successful runs per actor")
    parser.add_argument("--dry-run", action="store_true", help="Show what would run without executing")
    args = parser.parse_args()

    if not APIFY_TOKEN:
        print("ERROR: APIFY_TOKEN environment variable is required")
        print("Set it with: export APIFY_TOKEN='your-token-here'")
        sys.exit(1)

    print("=" * 60)
    print("Actor Demo Runner")
    print("=" * 60)
    print(f"Max runs per actor: {args.max_runs}")
    print(f"Dry run: {args.dry_run}")

    # Fetch actors
    actors = fetch_actors()

    if not actors:
        print("ERROR: No actors found")
        sys.exit(1)

    # Filter actors if specific one requested
    if args.actor:
        actors = [a for a in actors if a.get("name") == args.actor or args.actor in a.get("name", "")]
        if not actors:
            print(f"ERROR: Actor '{args.actor}' not found")
            sys.exit(1)
        print(f"Running for specific actor: {actors[0].get('name')}")

    # Handle resume
    start_index = 0
    if args.resume:
        last_actor = load_resume_state()
        if last_actor:
            for i, actor in enumerate(actors):
                if actor.get("name") == last_actor:
                    start_index = i + 1
                    print(f"Resuming after: {last_actor}")
                    break

    # Run demos
    results = []

    for i, actor in enumerate(actors[start_index:], start=start_index):
        actor_name = actor.get("name", "unknown")

        try:
            result = run_actor_demos(actor, args.max_runs, args.dry_run)
            results.append(result)

            # Save progress
            save_resume_state(actor_name)

        except KeyboardInterrupt:
            print("\n\nInterrupted by user. Saving progress...")
            save_results(results)
            sys.exit(0)
        except Exception as e:
            print(f"\nError running {actor_name}: {e}")
            results.append({
                "actor_id": actor.get("id", ""),
                "actor_name": actor_name,
                "successful_runs": 0,
                "failed_runs": 1,
                "runs": [],
                "stopped_reason": f"Exception: {str(e)}"
            })

    # Save final results
    save_results(results)

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    fully_successful = sum(1 for r in results if r["successful_runs"] == args.max_runs)
    partial = sum(1 for r in results if 0 < r["successful_runs"] < args.max_runs)
    failed = sum(1 for r in results if r["successful_runs"] == 0 and r["failed_runs"] > 0)

    print(f"Total actors processed: {len(results)}")
    print(f"Fully successful ({args.max_runs} runs): {fully_successful}")
    print(f"Partial success: {partial}")
    print(f"Failed on first run: {failed}")

    # List failed actors
    if failed > 0:
        print(f"\nActors that failed on first run:")
        for r in results:
            if r["successful_runs"] == 0 and r["failed_runs"] > 0:
                print(f"  - {r['actor_name']}: {r['stopped_reason']}")


if __name__ == "__main__":
    main()
