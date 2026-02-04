"""
Preserver - Your Personal Digital Twin Creator

A modern, privacy-first application to help you create a digital twin of yourself
by gathering and storing your personal data locally in LLM-ready formats.

Author: Gogolian and the open-source community
License: MIT
"""

import gradio as gr
import os
import json
import datetime
import random
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict


# Configuration
QUESTIONS_DIR = Path("questions")
ANSWERS_DIR_TEMPLATE = Path("answers/data-{}")
EXPORTS_DIR = Path("exports")


@dataclass
class Answer:
    """Represents a single question-answer pair."""
    question: str
    answer: str
    category: str
    question_id: str
    timestamp: str
    
    def to_llm_format(self) -> Dict:
        """Convert to a format suitable for LLM training."""
        return {
            "instruction": self.question,
            "output": self.answer,
            "category": self.category,
            "timestamp": self.timestamp
        }
    
    def to_conversation_format(self) -> Dict:
        """Convert to conversation format for chat-based LLM training."""
        return {
            "messages": [
                {"role": "user", "content": self.question},
                {"role": "assistant", "content": self.answer}
            ],
            "category": self.category,
            "timestamp": self.timestamp
        }


class PreserverApp:
    """Main application class for Preserver."""
    
    def __init__(self):
        self.questions_cache: Dict[str, Dict[str, str]] = {}
        self._load_questions()
    
    def _load_questions(self) -> None:
        """Load all questions from the questions directory into cache."""
        self.questions_cache = {}
        
        if not QUESTIONS_DIR.exists():
            return
            
        for category_dir in sorted(QUESTIONS_DIR.iterdir()):
            if category_dir.is_dir():
                category = category_dir.name
                self.questions_cache[category] = {}
                
                # Sort question files numerically
                question_files = sorted(
                    category_dir.glob("*.txt"),
                    key=lambda x: int(x.stem.replace("q", "")) if x.stem.replace("q", "").isdigit() else 0
                )
                
                for q_file in question_files:
                    question_id = q_file.stem
                    with open(q_file, "r", encoding="utf-8") as f:
                        self.questions_cache[category][question_id] = f.read().strip()
    
    def get_categories(self) -> List[str]:
        """Get all available question categories."""
        return sorted(self.questions_cache.keys())
    
    def get_total_questions(self) -> int:
        """Get total number of questions."""
        return sum(len(qs) for qs in self.questions_cache.values())
    
    def get_category_stats(self, username: str) -> Dict[str, Tuple[int, int]]:
        """Get answered/total stats for each category."""
        stats = {}
        for category, questions in self.questions_cache.items():
            total = len(questions)
            answered = 0
            for q_id in questions:
                answer_path = self._get_answer_path(username, category, q_id)
                if answer_path.exists():
                    answered += 1
            stats[category] = (answered, total)
        return stats
    
    def get_progress(self, username: str) -> Tuple[int, int]:
        """Get overall progress (answered, total)."""
        if not username:
            return 0, self.get_total_questions()
            
        answered = 0
        total = 0
        
        for category, questions in self.questions_cache.items():
            for q_id in questions:
                total += 1
                answer_path = self._get_answer_path(username, category, q_id)
                if answer_path.exists():
                    answered += 1
        
        return answered, total
    
    def _get_answer_path(self, username: str, category: str, question_id: str) -> Path:
        """Get the path where an answer should be stored."""
        return ANSWERS_DIR_TEMPLATE.parent / f"data-{username}" / category / f"{question_id}.txt"
    
    def get_next_question(self, username: str, category: Optional[str] = None, randomize: bool = True) -> Optional[Tuple[str, str, str]]:
        """
        Get the next unanswered question.
        Returns: (question_text, category, question_id) or None if all answered
        """
        categories = [category] if category else self.get_categories()
        
        # Collect all unanswered questions
        unanswered = []
        for cat in categories:
            if cat not in self.questions_cache:
                continue
                
            question_ids = list(self.questions_cache[cat].keys())
            
            for q_id in question_ids:
                answer_path = self._get_answer_path(username, cat, q_id)
                if not answer_path.exists():
                    unanswered.append((self.questions_cache[cat][q_id], cat, q_id))
        
        if not unanswered:
            return None
        
        # Return random question if randomize is True, otherwise return first
        if randomize:
            return random.choice(unanswered)
        else:
            # Sort by category and question ID for deterministic order
            unanswered.sort(key=lambda x: (x[1], int(x[2].replace("q", "")) if x[2].replace("q", "").isdigit() else 0))
            return unanswered[0]
    
    def save_answer(self, username: str, question: str, answer: str, 
                    category: str, question_id: str) -> bool:
        """Save an answer to disk."""
        try:
            answer_path = self._get_answer_path(username, category, question_id)
            answer_path.parent.mkdir(parents=True, exist_ok=True)
            
            answer_obj = Answer(
                question=question,
                answer=answer,
                category=category,
                question_id=question_id,
                timestamp=datetime.datetime.now().isoformat()
            )
            
            # Save in structured format
            with open(answer_path, "w", encoding="utf-8") as f:
                json.dump(asdict(answer_obj), f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error saving answer: {e}")
            return False
    
    def get_all_answers(self, username: str) -> List[Answer]:
        """Get all answers for a user."""
        answers = []
        answers_dir = ANSWERS_DIR_TEMPLATE.parent / f"data-{username}"
        
        if not answers_dir.exists():
            return answers
        
        for category_dir in sorted(answers_dir.iterdir()):
            if category_dir.is_dir():
                for answer_file in sorted(category_dir.glob("*.txt")):
                    try:
                        with open(answer_file, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            answers.append(Answer(**data))
                    except (json.JSONDecodeError, TypeError):
                        # Handle legacy format
                        with open(answer_file, "r", encoding="utf-8") as f:
                            content = f.read()
                        # Parse legacy format
                        if "<USER>" in content and "<ANSWER>" in content:
                            parts = content.split("<ANSWER>")
                            question = parts[0].replace("<USER>", "").strip()
                            answer_text = parts[1].strip() if len(parts) > 1 else ""
                            answers.append(Answer(
                                question=question,
                                answer=answer_text,
                                category=category_dir.name,
                                question_id=answer_file.stem,
                                timestamp=""
                            ))
        
        return answers
    
    def export_for_llm(self, username: str, format_type: str = "jsonl") -> Optional[str]:
        """
        Export all answers in LLM-training format.
        
        format_type: 'jsonl', 'json', or 'conversation'
        Returns: path to exported file
        """
        answers = self.get_all_answers(username)
        if not answers:
            return None
        
        EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format_type == "jsonl":
            export_path = EXPORTS_DIR / f"{username}_training_data_{timestamp}.jsonl"
            with open(export_path, "w", encoding="utf-8") as f:
                for answer in answers:
                    f.write(json.dumps(answer.to_llm_format(), ensure_ascii=False) + "\n")
        
        elif format_type == "conversation":
            export_path = EXPORTS_DIR / f"{username}_conversations_{timestamp}.jsonl"
            with open(export_path, "w", encoding="utf-8") as f:
                for answer in answers:
                    f.write(json.dumps(answer.to_conversation_format(), ensure_ascii=False) + "\n")
        
        else:  # json
            export_path = EXPORTS_DIR / f"{username}_all_data_{timestamp}.json"
            with open(export_path, "w", encoding="utf-8") as f:
                json.dump({
                    "username": username,
                    "export_date": timestamp,
                    "total_answers": len(answers),
                    "answers": [asdict(a) for a in answers]
                }, f, indent=2, ensure_ascii=False)
        
        return str(export_path)
    
    def import_from_json(self, username: str, json_data: str) -> Tuple[bool, str, int]:
        """
        Import answers from JSON export.
        
        Args:
            username: The username to import data for
            json_data: JSON string containing exported data
        
        Returns:
            Tuple of (success, message, count_imported)
        """
        try:
            data = json.loads(json_data)
            
            # Validate the JSON structure
            if "answers" not in data:
                return False, "Invalid JSON format: missing 'answers' field", 0
            
            imported_count = 0
            skipped_count = 0
            
            for answer_data in data["answers"]:
                try:
                    # Check if this answer already exists
                    answer_path = self._get_answer_path(
                        username, 
                        answer_data["category"], 
                        answer_data["question_id"]
                    )
                    
                    # Skip if already answered (don't overwrite)
                    if answer_path.exists():
                        skipped_count += 1
                        continue
                    
                    # Create the answer object and save it
                    answer_obj = Answer(
                        question=answer_data["question"],
                        answer=answer_data["answer"],
                        category=answer_data["category"],
                        question_id=answer_data["question_id"],
                        timestamp=answer_data.get("timestamp", datetime.datetime.now().isoformat())
                    )
                    
                    # Save the answer
                    answer_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(answer_path, "w", encoding="utf-8") as f:
                        json.dump(asdict(answer_obj), f, indent=2, ensure_ascii=False)
                    
                    imported_count += 1
                
                except (KeyError, TypeError) as e:
                    # Skip malformed answers
                    continue
            
            message = f"Successfully imported {imported_count} answers"
            if skipped_count > 0:
                message += f" ({skipped_count} already existed and were skipped)"
            
            return True, message, imported_count
        
        except json.JSONDecodeError:
            return False, "Invalid JSON format", 0
        except Exception as e:
            return False, f"Error importing data: {str(e)}", 0



# Initialize the app
preserver = PreserverApp()

# UI Text
WELCOME_TEXT = """# 🧠 Welcome to Preserver

**Preserver** helps you create a digital twin of yourself by gathering your thoughts, 
memories, preferences, and perspectives.

### How it works:
1. Enter your username below
2. Answer questions about yourself
3. Your data is stored **locally** - you own it completely
4. Export anytime in LLM-ready formats

### Privacy First:
All your data stays on your machine. Nothing is sent to any server.

---
*Enter your username to begin or continue your journey.*
"""

CATEGORIES_INFO = """### 📚 Question Categories

Your digital twin is built from **{total}** questions across **{cats}** categories:

{cat_list}

---
*Select a category to focus on specific topics, or answer questions in order.*
"""


def format_category_name(cat: str) -> str:
    """Format category name for display."""
    return cat.replace("_", " ").title()


def get_progress_text(username: str) -> str:
    """Get formatted progress text."""
    if not username:
        return ""
    answered, total = preserver.get_progress(username)
    percentage = (answered / total * 100) if total > 0 else 0
    return f"📊 Progress: **{answered}/{total}** questions answered ({percentage:.1f}%)"


def get_category_dropdown_choices() -> List[str]:
    """Get formatted category choices for dropdown."""
    categories = preserver.get_categories()
    return ["All Categories"] + [format_category_name(c) for c in categories]


def create_category_stats_md(username: str) -> str:
    """Create markdown for category statistics."""
    if not username:
        return ""
    
    stats = preserver.get_category_stats(username)
    lines = []
    for cat, (answered, total) in sorted(stats.items()):
        status = "✅" if answered == total else "📝"
        lines.append(f"- {status} **{format_category_name(cat)}**: {answered}/{total}")
    
    return "\n".join(lines)


# Gradio Interface Functions
def on_username_submit(username: str) -> Tuple:
    """Handle username submission."""
    if not username or not username.strip():
        return (
            gr.update(visible=True),  # welcome panel
            gr.update(visible=False),  # main panel
            gr.update(value=""),  # progress
            gr.update(value=""),  # current question
            gr.update(value=""),  # category info
            "",  # current_question_data
            "",  # current_category
            "",  # current_qid
            ""   # username state
        )
    
    username = username.strip()
    progress_text = get_progress_text(username)
    
    # Get next question
    result = preserver.get_next_question(username)
    
    if result:
        question, category, q_id = result
        cat_display = format_category_name(category)
        question_md = f"### 💭 Category: {cat_display}\n\n{question}"
        category_stats = create_category_stats_md(username)
    else:
        question_md = "### 🎉 All Done!\n\nYou've answered all available questions. Amazing work preserving your knowledge!\n\nYou can export your data using the Export tab."
        category, q_id = "", ""
        category_stats = create_category_stats_md(username)
    
    return (
        gr.update(visible=False),  # welcome panel
        gr.update(visible=True),   # main panel
        gr.update(value=progress_text),  # progress
        gr.update(value=question_md),    # current question
        gr.update(value=category_stats), # category info
        question if result else "",  # current_question_data
        category,  # current_category
        q_id,      # current_qid
        username   # username state
    )


def on_answer_submit(answer: str, current_question: str, current_category: str, 
                     current_qid: str, username: str, selected_category: str) -> Tuple:
    """Handle answer submission."""
    if not answer or not answer.strip() or not current_question:
        return (
            gr.update(),  # question display
            gr.update(),  # answer textbox
            gr.update(),  # progress
            gr.update(),  # category stats
            current_question,
            current_category,
            current_qid
        )
    
    # Save the answer
    preserver.save_answer(username, current_question, answer.strip(), 
                          current_category, current_qid)
    
    # Get next question
    cat_filter = None
    if selected_category and selected_category != "All Categories":
        cat_filter = selected_category.lower().replace(" ", "_")
    
    result = preserver.get_next_question(username, cat_filter)
    progress_text = get_progress_text(username)
    category_stats = create_category_stats_md(username)
    
    if result:
        question, category, q_id = result
        cat_display = format_category_name(category)
        question_md = f"### 💭 Category: {cat_display}\n\n{question}"
        return (
            gr.update(value=question_md),
            gr.update(value=""),
            gr.update(value=progress_text),
            gr.update(value=category_stats),
            question,
            category,
            q_id
        )
    else:
        return (
            gr.update(value="### 🎉 All Done!\n\nYou've answered all available questions in this category. Great work!\n\nTry another category or export your data."),
            gr.update(value=""),
            gr.update(value=progress_text),
            gr.update(value=category_stats),
            "",
            "",
            ""
        )


def on_skip_question(current_question: str, current_category: str, 
                     current_qid: str, username: str, selected_category: str) -> Tuple:
    """Skip to next question without answering."""
    cat_filter = None
    if selected_category and selected_category != "All Categories":
        cat_filter = selected_category.lower().replace(" ", "_")
    
    # Get a random unanswered question, excluding the current one
    categories = [cat_filter] if cat_filter else preserver.get_categories()
    
    # Collect all unanswered questions except current
    unanswered = []
    for cat in categories:
        if cat not in preserver.questions_cache:
            continue
        
        for q_id in preserver.questions_cache[cat].keys():
            # Skip current question
            if cat == current_category and q_id == current_qid:
                continue
                
            answer_path = preserver._get_answer_path(username, cat, q_id)
            if not answer_path.exists():
                question = preserver.questions_cache[cat][q_id]
                unanswered.append((question, cat, q_id))
    
    # Pick a random question
    if unanswered:
        question, cat, q_id = random.choice(unanswered)
        cat_display = format_category_name(cat)
        question_md = f"### 💭 Category: {cat_display}\n\n{question}"
        return (
            gr.update(value=question_md),
            gr.update(value=""),
            question,
            cat,
            q_id
        )
    
    # If no other question found, stay on current
    if current_question:
        cat_display = format_category_name(current_category)
        question_md = f"### 💭 Category: {cat_display}\n\n{current_question}"
        return (
            gr.update(value=question_md),
            gr.update(value=""),
            current_question,
            current_category,
            current_qid
        )
    
    return (
        gr.update(value="### 🎉 All Done!\n\nNo more unanswered questions available."),
        gr.update(value=""),
        "",
        "",
        ""
    )


def on_category_change(selected_category: str, username: str) -> Tuple:
    """Handle category filter change."""
    if not username:
        return gr.update(), "", "", ""
    
    cat_filter = None
    if selected_category and selected_category != "All Categories":
        cat_filter = selected_category.lower().replace(" ", "_")
    
    result = preserver.get_next_question(username, cat_filter)
    
    if result:
        question, category, q_id = result
        cat_display = format_category_name(category)
        question_md = f"### 💭 Category: {cat_display}\n\n{question}"
        return gr.update(value=question_md), question, category, q_id
    else:
        return (
            gr.update(value="### ✅ Category Complete!\n\nAll questions in this category have been answered."),
            "",
            "",
            ""
        )


def on_export(username: str, export_format: str) -> str:
    """Handle data export."""
    if not username:
        return "⚠️ Please enter a username first."
    
    format_map = {
        "JSONL (Instruction Format)": "jsonl",
        "JSONL (Conversation Format)": "conversation",
        "JSON (Complete Export)": "json"
    }
    
    format_type = format_map.get(export_format, "jsonl")
    export_path = preserver.export_for_llm(username, format_type)
    
    if export_path:
        return f"✅ Data exported successfully!\n\n📁 File: `{export_path}`"
    else:
        return "⚠️ No answers to export. Answer some questions first!"


def on_logout() -> Tuple:
    """Handle logout/switch user."""
    return (
        gr.update(visible=True),   # welcome panel
        gr.update(visible=False),  # main panel
        gr.update(value=""),       # progress
        gr.update(value=""),       # current question
        gr.update(value=""),       # category stats
        "",  # current_question_data
        "",  # current_category
        "",  # current_qid
        ""   # username state
    )


def on_import_data(username_input: str, filepath: str) -> str:
    """Handle data import from JSON file."""
    if not filepath:
        return "⚠️ Please select a JSON file to import."
    
    if not username_input or not username_input.strip():
        return "⚠️ Please enter a username first."
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            json_data = f.read()
        
        success, message, count = preserver.import_from_json(username_input.strip(), json_data)
        
        if success:
            return f"✅ {message}"
        else:
            return f"⚠️ {message}"
    
    except Exception as e:
        return f"❌ Error reading file: {str(e)}"



# Build Gradio Interface
custom_css = """
#main-container {
    max-width: 900px;
    margin: 0 auto;
}
.question-box {
    font-size: 1.1em;
    padding: 20px;
    background: linear-gradient(135deg, #8b9dc3 0%, #9d8b9f 100%);
    color: white;
    border-radius: 10px;
    margin-bottom: 15px;
}
.progress-bar {
    font-size: 1.2em;
    font-weight: bold;
    color: #7d9b7d;
}
.category-stats {
    background: #f5f3f0;
    padding: 15px;
    border-radius: 8px;
}
"""

with gr.Blocks() as app:
    # State variables
    username_state = gr.State("")
    current_question_data = gr.State("")
    current_category = gr.State("")
    current_qid = gr.State("")
    
    with gr.Column(elem_id="main-container"):
        gr.Markdown("# 🧠 Preserver")
        gr.Markdown("*Create your digital twin by preserving your thoughts, memories, and personality.*")
        
        # Welcome Panel
        with gr.Column(visible=True) as welcome_panel:
            gr.Markdown(WELCOME_TEXT)
            
            with gr.Row():
                username_input = gr.Textbox(
                    label="Your Username",
                    placeholder="Enter a unique username...",
                    scale=3
                )
                start_btn = gr.Button("🚀 Start", variant="primary", scale=1)
            
            # Import section
            gr.Markdown("---\n### 📥 Import Previous Session\nHave an exported JSON file? Upload it to continue where you left off.")
            
            with gr.Row():
                import_file = gr.File(
                    label="Upload JSON Export",
                    file_types=[".json"],
                    type="filepath"
                )
                import_btn = gr.Button("📤 Import", variant="secondary")
            
            import_status = gr.Markdown("")
            
            gr.Markdown(f"""
            ### 📊 Available Content
            - **{preserver.get_total_questions()}** questions across **{len(preserver.get_categories())}** categories
            - Categories include: {', '.join(format_category_name(c) for c in preserver.get_categories()[:5])}...
            """)
        
        # Main Panel
        with gr.Column(visible=False) as main_panel:
            with gr.Row():
                progress_display = gr.Markdown("", elem_classes=["progress-bar"])
                logout_btn = gr.Button("🔄 Switch User", size="sm")
            
            with gr.Tabs():
                # Answer Questions Tab
                with gr.Tab("📝 Answer Questions"):
                    with gr.Row():
                        with gr.Column(scale=3):
                            question_display = gr.Markdown("", elem_classes=["question-box"])
                            answer_input = gr.Textbox(
                                label="Your Answer",
                                placeholder="Share your thoughts...",
                                lines=4
                            )
                            with gr.Row():
                                submit_btn = gr.Button("💾 Save & Next", variant="primary", scale=2)
                                skip_btn = gr.Button("⏭️ Skip", scale=1)
                        
                        with gr.Column(scale=1):
                            category_filter = gr.Dropdown(
                                label="Filter by Category",
                                choices=get_category_dropdown_choices(),
                                value="All Categories"
                            )
                            category_stats_display = gr.Markdown("", elem_classes=["category-stats"])
                
                # Export Tab
                with gr.Tab("📤 Export Data"):
                    gr.Markdown("""
                    ### Export Your Digital Twin Data
                    
                    Export your answers in formats ready for LLM training:
                    
                    - **JSONL (Instruction Format)**: Each line is `{instruction, output}` - great for fine-tuning
                    - **JSONL (Conversation Format)**: Each line has `messages` array - for chat models
                    - **JSON (Complete Export)**: Full structured export with metadata
                    """)
                    
                    export_format = gr.Dropdown(
                        label="Export Format",
                        choices=["JSONL (Instruction Format)", "JSONL (Conversation Format)", "JSON (Complete Export)"],
                        value="JSONL (Instruction Format)"
                    )
                    export_btn = gr.Button("📥 Export My Data", variant="primary")
                    export_result = gr.Markdown("")
                
                # About Tab
                with gr.Tab("ℹ️ About"):
                    gr.Markdown("""
                    ### About Preserver
                    
                    Preserver is an open-source project designed to help you create a digital twin of yourself.
                    
                    **Key Features:**
                    - 🔒 **Privacy-First**: All data stored locally
                    - 🧠 **Comprehensive Questions**: 800+ thoughtful questions
                    - 💾 **LLM-Ready**: Export in formats ready for AI training
                    - 🔄 **Continuous**: Add to your dataset over time
                    
                    **Why Preserver?**
                    
                    People come and go too early. We've had written notes, books, voice recordings, 
                    photos, and videos to remember those who passed. But what if we could preserve more - 
                    the essence of a person, the way they think, their personality?
                    
                    Preserver aims to capture enough of you that future AI could approximate 
                    how you might respond, think, and feel.
                    
                    ---
                    
                    **License**: MIT  
                    **GitHub**: [Gogolian/preserver](https://github.com/Gogolian/preserver)
                    
                    Built with ❤️ by Gogolian and the open-source community.
                    """)
    
    # Event Handlers
    start_btn.click(
        on_username_submit,
        inputs=[username_input],
        outputs=[welcome_panel, main_panel, progress_display, question_display, 
                 category_stats_display, current_question_data, current_category, 
                 current_qid, username_state]
    )
    
    username_input.submit(
        on_username_submit,
        inputs=[username_input],
        outputs=[welcome_panel, main_panel, progress_display, question_display,
                 category_stats_display, current_question_data, current_category,
                 current_qid, username_state]
    )
    
    import_btn.click(
        on_import_data,
        inputs=[username_input, import_file],
        outputs=[import_status]
    )
    
    submit_btn.click(
        on_answer_submit,
        inputs=[answer_input, current_question_data, current_category, 
                current_qid, username_state, category_filter],
        outputs=[question_display, answer_input, progress_display, 
                 category_stats_display, current_question_data, current_category, current_qid]
    )
    
    answer_input.submit(
        on_answer_submit,
        inputs=[answer_input, current_question_data, current_category,
                current_qid, username_state, category_filter],
        outputs=[question_display, answer_input, progress_display,
                 category_stats_display, current_question_data, current_category, current_qid]
    )
    
    skip_btn.click(
        on_skip_question,
        inputs=[current_question_data, current_category, current_qid, 
                username_state, category_filter],
        outputs=[question_display, answer_input, current_question_data, 
                 current_category, current_qid]
    )
    
    category_filter.change(
        on_category_change,
        inputs=[category_filter, username_state],
        outputs=[question_display, current_question_data, current_category, current_qid]
    )
    
    export_btn.click(
        on_export,
        inputs=[username_state, export_format],
        outputs=[export_result]
    )
    
    logout_btn.click(
        on_logout,
        outputs=[welcome_panel, main_panel, progress_display, question_display,
                 category_stats_display, current_question_data, current_category,
                 current_qid, username_state]
    )


if __name__ == "__main__":
    app.launch(
        show_error=True,
    )
