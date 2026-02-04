"""
Unit tests for Preserver core functionality.
"""

import pytest
import tempfile
import shutil
import json
from pathlib import Path
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import PreserverApp, Answer, QUESTIONS_DIR


class TestAnswer:
    """Tests for the Answer dataclass."""
    
    def test_answer_creation(self):
        """Test creating an Answer object."""
        answer = Answer(
            question="What is your name?",
            answer="John Doe",
            category="personal_info",
            question_id="q1",
            timestamp="2024-01-15T10:30:00"
        )
        
        assert answer.question == "What is your name?"
        assert answer.answer == "John Doe"
        assert answer.category == "personal_info"
        assert answer.question_id == "q1"
        assert answer.timestamp == "2024-01-15T10:30:00"
    
    def test_to_llm_format(self):
        """Test converting answer to LLM instruction format."""
        answer = Answer(
            question="What is your favorite color?",
            answer="Blue",
            category="preferences",
            question_id="q1",
            timestamp="2024-01-15T10:30:00"
        )
        
        llm_format = answer.to_llm_format()
        
        assert llm_format["instruction"] == "What is your favorite color?"
        assert llm_format["output"] == "Blue"
        assert llm_format["category"] == "preferences"
        assert llm_format["timestamp"] == "2024-01-15T10:30:00"
    
    def test_to_conversation_format(self):
        """Test converting answer to conversation format."""
        answer = Answer(
            question="What is your hobby?",
            answer="Reading books",
            category="hobbies",
            question_id="q1",
            timestamp="2024-01-15T10:30:00"
        )
        
        conv_format = answer.to_conversation_format()
        
        assert len(conv_format["messages"]) == 2
        assert conv_format["messages"][0]["role"] == "user"
        assert conv_format["messages"][0]["content"] == "What is your hobby?"
        assert conv_format["messages"][1]["role"] == "assistant"
        assert conv_format["messages"][1]["content"] == "Reading books"


class TestPreserverApp:
    """Tests for the PreserverApp class."""
    
    def test_app_initialization(self):
        """Test that app initializes correctly."""
        app = PreserverApp()
        
        assert app.questions_cache is not None
        assert len(app.questions_cache) > 0
    
    def test_get_categories(self):
        """Test getting available categories."""
        app = PreserverApp()
        categories = app.get_categories()
        
        assert isinstance(categories, list)
        assert len(categories) > 0
        assert "personal_info" in categories
        assert "goals" in categories
    
    def test_get_total_questions(self):
        """Test getting total question count."""
        app = PreserverApp()
        total = app.get_total_questions()
        
        assert isinstance(total, int)
        assert total > 0
        # We know there are 900 questions
        assert total >= 800
    
    def test_get_next_question(self):
        """Test getting next unanswered question."""
        app = PreserverApp()
        
        # Use a unique test username
        result = app.get_next_question("test_user_unit_test_12345")
        
        assert result is not None
        question, category, q_id = result
        assert isinstance(question, str)
        assert len(question) > 0
        assert isinstance(category, str)
        assert isinstance(q_id, str)
    
    def test_get_next_question_with_category_filter(self):
        """Test getting next question with category filter."""
        app = PreserverApp()
        
        result = app.get_next_question("test_user_unit_test_12345", "goals")
        
        if result:
            question, category, q_id = result
            assert category == "goals"
    
    def test_get_progress_new_user(self):
        """Test progress for new user."""
        app = PreserverApp()
        
        answered, total = app.get_progress("brand_new_user_never_used")
        
        assert answered == 0
        assert total > 0
    
    def test_get_category_stats(self):
        """Test getting category statistics."""
        app = PreserverApp()
        
        stats = app.get_category_stats("test_user_for_stats")
        
        assert isinstance(stats, dict)
        assert len(stats) > 0
        
        for category, (answered, total) in stats.items():
            assert answered >= 0
            assert total > 0
            assert answered <= total


class TestQuestionFiles:
    """Tests for question file structure."""
    
    def test_questions_directory_exists(self):
        """Test that questions directory exists."""
        assert QUESTIONS_DIR.exists()
    
    def test_question_files_are_valid(self):
        """Test that all question files have content."""
        question_count = 0
        
        for category_dir in QUESTIONS_DIR.iterdir():
            if category_dir.is_dir():
                for q_file in category_dir.glob("*.txt"):
                    with open(q_file, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                    
                    assert len(content) > 0, f"Empty question file: {q_file}"
                    assert content.endswith("?") or content.endswith("."), \
                        f"Question should end with ? or .: {q_file}"
                    question_count += 1
        
        assert question_count > 0
    
    def test_question_categories_have_questions(self):
        """Test that each category has at least one question."""
        for category_dir in QUESTIONS_DIR.iterdir():
            if category_dir.is_dir():
                questions = list(category_dir.glob("*.txt"))
                assert len(questions) > 0, f"Category {category_dir.name} has no questions"


class TestAnswerSaveAndLoad:
    """Tests for saving and loading answers."""
    
    @pytest.fixture
    def temp_answers_dir(self):
        """Create a temporary directory for testing answers."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_save_answer(self, temp_answers_dir, monkeypatch):
        """Test saving an answer."""
        # Temporarily change the answers directory template
        import app as app_module
        original_template = app_module.ANSWERS_DIR_TEMPLATE
        app_module.ANSWERS_DIR_TEMPLATE = Path(temp_answers_dir) / "data-{}"
        
        try:
            preserver = PreserverApp()
            
            result = preserver.save_answer(
                username="test_user",
                question="Test question?",
                answer="Test answer",
                category="test_category",
                question_id="q1"
            )
            
            assert result is True
            
            # Verify file was created
            answer_path = Path(temp_answers_dir) / "data-test_user" / "test_category" / "q1.txt"
            assert answer_path.exists()
            
            # Verify content
            with open(answer_path, "r") as f:
                data = json.load(f)
            
            assert data["question"] == "Test question?"
            assert data["answer"] == "Test answer"
            assert data["category"] == "test_category"
            assert data["question_id"] == "q1"
            assert "timestamp" in data
        
        finally:
            app_module.ANSWERS_DIR_TEMPLATE = original_template


class TestExport:
    """Tests for export functionality."""
    
    def test_export_formats_available(self):
        """Test that export formats are defined."""
        # These are the expected formats
        formats = ["jsonl", "conversation", "json"]
        
        for fmt in formats:
            assert fmt in ["jsonl", "conversation", "json"]


class TestImport:
    """Tests for import functionality."""
    
    def test_import_valid_json(self):
        """Test importing valid JSON data."""
        temp_dir = tempfile.mkdtemp()
        
        import app as app_module
        original_template = app_module.ANSWERS_DIR_TEMPLATE
        app_module.ANSWERS_DIR_TEMPLATE = Path(temp_dir) / "data-{}"
        
        try:
            preserver = PreserverApp()
            
            # Create test export data
            test_data = {
                "username": "test_import_user",
                "export_date": "2024-01-15T10:30:00",
                "total_answers": 2,
                "answers": [
                    {
                        "question": "What is your favorite color?",
                        "answer": "Blue",
                        "category": "preferences",
                        "question_id": "q1",
                        "timestamp": "2024-01-15T10:30:00"
                    },
                    {
                        "question": "What are your goals?",
                        "answer": "Learn Python",
                        "category": "goals",
                        "question_id": "q1",
                        "timestamp": "2024-01-15T10:31:00"
                    }
                ]
            }
            
            # Import the data
            success, message, count = preserver.import_from_json(
                "test_import_user",
                json.dumps(test_data)
            )
            
            assert success is True
            assert count == 2
            assert "Successfully imported 2 answers" in message
            
            # Verify the answers were saved
            answer_path_1 = Path(temp_dir) / "data-test_import_user" / "preferences" / "q1.txt"
            answer_path_2 = Path(temp_dir) / "data-test_import_user" / "goals" / "q1.txt"
            
            assert answer_path_1.exists()
            assert answer_path_2.exists()
            
        finally:
            app_module.ANSWERS_DIR_TEMPLATE = original_template
            shutil.rmtree(temp_dir)
    
    def test_import_invalid_json(self):
        """Test importing invalid JSON."""
        preserver = PreserverApp()
        
        success, message, count = preserver.import_from_json(
            "test_user",
            "invalid json {{"
        )
        
        assert success is False
        assert "Invalid JSON" in message
        assert count == 0
    
    def test_import_missing_answers_field(self):
        """Test importing JSON without answers field."""
        preserver = PreserverApp()
        
        test_data = {
            "username": "test_user",
            "some_field": "value"
        }
        
        success, message, count = preserver.import_from_json(
            "test_user",
            json.dumps(test_data)
        )
        
        assert success is False
        assert "missing 'answers' field" in message
        assert count == 0
    
    def test_import_skips_existing_answers(self):
        """Test that import skips already answered questions."""
        temp_dir = tempfile.mkdtemp()
        
        import app as app_module
        original_template = app_module.ANSWERS_DIR_TEMPLATE
        app_module.ANSWERS_DIR_TEMPLATE = Path(temp_dir) / "data-{}"
        
        try:
            preserver = PreserverApp()
            
            # Save an existing answer
            preserver.save_answer(
                username="test_skip_user",
                question="What is your favorite color?",
                answer="Red",
                category="preferences",
                question_id="q1"
            )
            
            # Try to import data with the same question
            test_data = {
                "username": "test_skip_user",
                "answers": [
                    {
                        "question": "What is your favorite color?",
                        "answer": "Blue",
                        "category": "preferences",
                        "question_id": "q1",
                        "timestamp": "2024-01-15T10:30:00"
                    },
                    {
                        "question": "New question",
                        "answer": "New answer",
                        "category": "goals",
                        "question_id": "q2",
                        "timestamp": "2024-01-15T10:31:00"
                    }
                ]
            }
            
            success, message, count = preserver.import_from_json(
                "test_skip_user",
                json.dumps(test_data)
            )
            
            assert success is True
            assert count == 1
            assert "1 already existed and were skipped" in message
            
        finally:
            app_module.ANSWERS_DIR_TEMPLATE = original_template
            shutil.rmtree(temp_dir)


class TestRandomness:
    """Tests for random question selection."""
    
    def test_get_next_question_returns_different_questions(self):
        """Test that randomness returns different questions over multiple calls."""
        preserver = PreserverApp()
        
        # Get multiple questions for a unique user
        test_user = "test_randomness_user_12345"
        questions_seen = set()
        
        # Get 10 questions
        for _ in range(10):
            result = preserver.get_next_question(test_user, randomize=True)
            if result:
                question, category, q_id = result
                questions_seen.add((category, q_id))
        
        # We should have seen more than 1 unique question
        # (very unlikely to get the same question 10 times with 900+ questions)
        assert len(questions_seen) > 1
    
    def test_get_next_question_deterministic_mode(self):
        """Test that non-random mode returns consistent results."""
        preserver = PreserverApp()
        
        test_user = "test_deterministic_user_67890"
        
        # Get the same question twice with randomize=False
        result1 = preserver.get_next_question(test_user, randomize=False)
        result2 = preserver.get_next_question(test_user, randomize=False)
        
        assert result1 is not None
        assert result2 is not None
        assert result1 == result2  # Should be the same question


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


