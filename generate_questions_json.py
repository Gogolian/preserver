#!/usr/bin/env python3
"""
Generate questions.json from the questions directory.

This script reads all questions from the questions directory and creates
a JSON file that can be used by the HTML/JS version of Preserver.
"""

import json
import os
from pathlib import Path


def generate_questions_json():
    """Generate questions.json from the questions directory."""
    questions_dir = Path(__file__).parent / "questions"
    questions = {}
    
    for category_dir in sorted(questions_dir.iterdir()):
        if category_dir.is_dir():
            category = category_dir.name
            questions[category] = {}
            
            # Sort question files numerically
            question_files = sorted(
                category_dir.glob("*.txt"),
                key=lambda x: int(x.stem.replace("q", "")) if x.stem.replace("q", "").isdigit() else 0
            )
            
            for q_file in question_files:
                question_id = q_file.stem
                with open(q_file, "r", encoding="utf-8") as f:
                    questions[category][question_id] = f.read().strip()
    
    # Write to questions.json
    output_path = Path(__file__).parent / "questions.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)
    
    # Calculate stats
    total_questions = sum(len(qs) for qs in questions.values())
    total_categories = len(questions)
    
    print(f"✅ Generated questions.json")
    print(f"   Categories: {total_categories}")
    print(f"   Questions: {total_questions}")
    print(f"   Output: {output_path}")
    
    return questions


if __name__ == "__main__":
    generate_questions_json()
