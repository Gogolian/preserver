#!/usr/bin/env python3
"""
Preserver CLI - Command-line interface for Preserver operations.

This tool allows you to:
- Export user data in various formats
- Aggregate all answers into a single file
- View statistics about questions and answers
- Validate question files
- Generate sample data for testing
"""

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
from dataclasses import asdict

# Add parent directory for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import PreserverApp, Answer, QUESTIONS_DIR, ANSWERS_DIR_TEMPLATE, EXPORTS_DIR


def cmd_stats(args):
    """Show statistics about the Preserver data."""
    app = PreserverApp()
    
    print("\n🧠 Preserver Statistics")
    print("=" * 50)
    
    # Question stats
    categories = app.get_categories()
    total_questions = app.get_total_questions()
    
    print(f"\n📚 Questions:")
    print(f"   Total categories: {len(categories)}")
    print(f"   Total questions: {total_questions}")
    
    if args.verbose:
        print("\n   Questions per category:")
        for cat in sorted(categories):
            count = len(app.questions_cache.get(cat, {}))
            print(f"   - {cat}: {count}")
    
    # Answer stats if user specified
    if args.user:
        print(f"\n👤 User: {args.user}")
        answered, total = app.get_progress(args.user)
        percentage = (answered / total * 100) if total > 0 else 0
        print(f"   Answered: {answered}/{total} ({percentage:.1f}%)")
        
        if args.verbose:
            stats = app.get_category_stats(args.user)
            print("\n   Progress per category:")
            for cat, (ans, tot) in sorted(stats.items()):
                status = "✅" if ans == tot else "📝"
                print(f"   {status} {cat}: {ans}/{tot}")
    
    # List all users with answers
    answers_base = ANSWERS_DIR_TEMPLATE.parent
    if answers_base.exists():
        users = [d.name.replace("data-", "") for d in answers_base.iterdir() 
                 if d.is_dir() and d.name.startswith("data-")]
        if users:
            print(f"\n👥 Users with answers: {len(users)}")
            if args.verbose:
                for user in sorted(users):
                    answered, _ = app.get_progress(user)
                    print(f"   - {user}: {answered} answers")
    
    print()


def cmd_export(args):
    """Export user data to a file."""
    app = PreserverApp()
    
    if not args.user:
        print("❌ Error: --user is required for export")
        sys.exit(1)
    
    print(f"\n📤 Exporting data for user: {args.user}")
    
    answers = app.get_all_answers(args.user)
    
    if not answers:
        print("⚠️  No answers found for this user.")
        sys.exit(1)
    
    print(f"   Found {len(answers)} answers")
    
    # Determine output path
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if args.output:
        output_path = Path(args.output)
    else:
        EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
        ext = "jsonl" if args.format in ["jsonl", "conversation"] else "json"
        output_path = EXPORTS_DIR / f"{args.user}_{args.format}_{timestamp}.{ext}"
    
    # Export based on format
    if args.format == "jsonl":
        with open(output_path, "w", encoding="utf-8") as f:
            for answer in answers:
                f.write(json.dumps(answer.to_llm_format(), ensure_ascii=False) + "\n")
    
    elif args.format == "conversation":
        with open(output_path, "w", encoding="utf-8") as f:
            for answer in answers:
                f.write(json.dumps(answer.to_conversation_format(), ensure_ascii=False) + "\n")
    
    elif args.format == "json":
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump({
                "username": args.user,
                "export_date": datetime.now().isoformat(),
                "total_answers": len(answers),
                "answers": [asdict(a) for a in answers]
            }, f, indent=2, ensure_ascii=False)
    
    elif args.format == "markdown":
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"# Digital Twin Data: {args.user}\n\n")
            f.write(f"*Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
            f.write(f"**Total Answers:** {len(answers)}\n\n")
            f.write("---\n\n")
            
            # Group by category
            by_category = {}
            for answer in answers:
                if answer.category not in by_category:
                    by_category[answer.category] = []
                by_category[answer.category].append(answer)
            
            for category in sorted(by_category.keys()):
                cat_display = category.replace("_", " ").title()
                f.write(f"## {cat_display}\n\n")
                
                for answer in by_category[category]:
                    f.write(f"### Q: {answer.question}\n\n")
                    f.write(f"**A:** {answer.answer}\n\n")
                    if answer.timestamp:
                        f.write(f"*Answered: {answer.timestamp}*\n\n")
                    f.write("---\n\n")
    
    print(f"✅ Exported to: {output_path}")


def cmd_aggregate(args):
    """Aggregate all answers from all users into a single file."""
    app = PreserverApp()
    
    answers_base = ANSWERS_DIR_TEMPLATE.parent
    if not answers_base.exists():
        print("⚠️  No answers directory found.")
        sys.exit(1)
    
    all_answers = []
    users = []
    
    for user_dir in answers_base.iterdir():
        if user_dir.is_dir() and user_dir.name.startswith("data-"):
            username = user_dir.name.replace("data-", "")
            users.append(username)
            
            user_answers = app.get_all_answers(username)
            for answer in user_answers:
                answer_dict = asdict(answer)
                answer_dict["username"] = username
                all_answers.append(answer_dict)
    
    if not all_answers:
        print("⚠️  No answers found.")
        sys.exit(1)
    
    print(f"\n📊 Aggregating data from {len(users)} users")
    print(f"   Total answers: {len(all_answers)}")
    
    # Determine output path
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = EXPORTS_DIR / f"aggregated_all_users_{timestamp}.json"
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "export_date": datetime.now().isoformat(),
            "total_users": len(users),
            "total_answers": len(all_answers),
            "users": users,
            "answers": all_answers
        }, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Aggregated data saved to: {output_path}")


def cmd_validate(args):
    """Validate question files."""
    print("\n🔍 Validating question files...")
    
    issues = []
    question_count = 0
    
    for category_dir in QUESTIONS_DIR.iterdir():
        if category_dir.is_dir():
            for q_file in category_dir.glob("*.txt"):
                question_count += 1
                
                try:
                    with open(q_file, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                    
                    if not content:
                        issues.append(f"Empty file: {q_file}")
                    elif len(content) < 10:
                        issues.append(f"Very short question ({len(content)} chars): {q_file}")
                    elif not (content.endswith("?") or content.endswith(".")):
                        issues.append(f"Doesn't end with ? or .: {q_file}")
                
                except Exception as e:
                    issues.append(f"Error reading {q_file}: {e}")
    
    print(f"   Checked {question_count} questions")
    
    if issues:
        print(f"\n⚠️  Found {len(issues)} issues:")
        for issue in issues[:20]:  # Show first 20
            print(f"   - {issue}")
        if len(issues) > 20:
            print(f"   ... and {len(issues) - 20} more")
    else:
        print("✅ All questions are valid!")


def cmd_list_categories(args):
    """List all question categories."""
    app = PreserverApp()
    categories = app.get_categories()
    
    print(f"\n📚 Question Categories ({len(categories)} total):\n")
    
    for cat in sorted(categories):
        count = len(app.questions_cache.get(cat, {}))
        display_name = cat.replace("_", " ").title()
        print(f"   {display_name}: {count} questions")
    
    print()


def cmd_random_question(args):
    """Show a random unanswered question."""
    import random
    
    app = PreserverApp()
    
    # Get all unanswered questions
    unanswered = []
    categories = [args.category] if args.category else app.get_categories()
    
    for cat in categories:
        if cat not in app.questions_cache:
            continue
        
        for q_id, question in app.questions_cache[cat].items():
            if args.user:
                answer_path = app._get_answer_path(args.user, cat, q_id)
                if answer_path.exists():
                    continue
            unanswered.append((question, cat, q_id))
    
    if not unanswered:
        print("✅ No unanswered questions found!")
        return
    
    question, category, q_id = random.choice(unanswered)
    cat_display = category.replace("_", " ").title()
    
    print(f"\n📂 Category: {cat_display}")
    print(f"❓ {question}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Preserver CLI - Manage your digital twin data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py stats                        # Show overall statistics
  python cli.py stats --user john            # Show stats for user 'john'
  python cli.py export --user john           # Export John's data as JSONL
  python cli.py export --user john -f json   # Export as JSON
  python cli.py aggregate                    # Aggregate all users' data
  python cli.py validate                     # Validate question files
  python cli.py categories                   # List all categories
  python cli.py random                       # Show a random question
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show statistics")
    stats_parser.add_argument("--user", "-u", help="Username to show stats for")
    stats_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    # Export command
    export_parser = subparsers.add_parser("export", help="Export user data")
    export_parser.add_argument("--user", "-u", required=True, help="Username to export")
    export_parser.add_argument("--format", "-f", default="jsonl",
                               choices=["jsonl", "conversation", "json", "markdown"],
                               help="Export format (default: jsonl)")
    export_parser.add_argument("--output", "-o", help="Output file path")
    
    # Aggregate command
    agg_parser = subparsers.add_parser("aggregate", help="Aggregate all users' data")
    agg_parser.add_argument("--output", "-o", help="Output file path")
    
    # Validate command
    subparsers.add_parser("validate", help="Validate question files")
    
    # Categories command
    subparsers.add_parser("categories", help="List all categories")
    
    # Random question command
    random_parser = subparsers.add_parser("random", help="Show a random question")
    random_parser.add_argument("--user", "-u", help="Show unanswered question for user")
    random_parser.add_argument("--category", "-c", help="Filter by category")
    
    args = parser.parse_args()
    
    if args.command == "stats":
        cmd_stats(args)
    elif args.command == "export":
        cmd_export(args)
    elif args.command == "aggregate":
        cmd_aggregate(args)
    elif args.command == "validate":
        cmd_validate(args)
    elif args.command == "categories":
        cmd_list_categories(args)
    elif args.command == "random":
        cmd_random_question(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
