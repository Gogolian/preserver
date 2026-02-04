# Preserver: Architecture Analysis & Future Roadmap

## Current Architecture Overview

### Project Structure
```
preserver/
├── app.py                 # Main Gradio web application
├── cli.py                 # Command-line interface tool
├── index.html             # Standalone HTML/JS version
├── questions/             # Question files organized by category
│   ├── personal_info/
│   ├── childhood/
│   ├── goals/
│   └── ... (33 categories)
├── questions.json         # Generated JSON of all questions
├── answers/               # User answers (generated at runtime)
│   └── data-{username}/
├── exports/               # Exported data files
├── tests/                 # Unit tests
└── misc/                  # Funding and metadata
```

### Current Data Flow
```
User Input → Gradio/HTML Interface → Local File Storage → Export to JSONL/JSON
```

### Strengths ✅
1. **Privacy-First**: All data stored locally, no cloud dependency
2. **Simple Architecture**: Easy to understand and contribute to
3. **Multiple Interfaces**: Web (Gradio), Browser (HTML), CLI
4. **LLM-Ready Exports**: Proper formats for fine-tuning
5. **Extensible Questions**: Simple .txt file format for adding questions
6. **Zero Dependencies for HTML**: Can run without any installation

### Weaknesses & Areas for Improvement ⚠️
1. **No Database**: File-based storage doesn't scale well
2. **No Versioning**: Can't track answer changes over time
3. **Single User Focus**: No multi-user management
4. **No Backup/Sync**: Data only exists on one machine
5. **Limited Question Types**: Only text questions, no structured responses
6. **No Validation**: Answers aren't validated or guided
7. **No AI Integration**: No LLM assistance for answering or analysis

---

## Proposed Improvements

### Phase 1: Core Architecture Improvements

#### 1.1 Database Backend (SQLite)
**Priority: High**

Replace file-based storage with SQLite for better data management.

```python
# Proposed schema
class User:
    id: int
    username: str
    created_at: datetime
    settings: JSON

class Answer:
    id: int
    user_id: int
    question_id: str
    category: str
    answer_text: str
    created_at: datetime
    updated_at: datetime
    version: int  # For tracking changes

class AnswerHistory:
    id: int
    answer_id: int
    previous_text: str
    changed_at: datetime
```

**Benefits:**
- Faster queries and statistics
- Answer versioning/history
- Better data integrity
- Easier backup (single file)

#### 1.2 Configuration System
**Priority: Medium**

Add a configuration file for customizing behavior.

```yaml
# config.yaml
storage:
  backend: sqlite  # or 'files'
  path: ./data/preserver.db

questions:
  randomize: false
  skip_sensitive: false
  categories_order: alphabetical  # or 'custom'

export:
  default_format: jsonl
  include_timestamps: true
  
ui:
  theme: soft
  show_progress_bar: true
  questions_per_session: 10
```

#### 1.3 Plugin Architecture
**Priority: Low**

Enable extensibility through plugins.

```python
# plugins/voice_input.py
class VoiceInputPlugin:
    def on_question_displayed(self, question):
        # Enable voice recording
        pass
    
    def on_answer_submit(self, answer):
        # Transcribe and submit
        pass
```

---

### Phase 2: Enhanced Question System

#### 2.1 Question Types
**Priority: High**

Support multiple question types beyond free text.

```json
{
  "id": "personal_info_q1",
  "type": "text",  // text, choice, scale, date, multi-select
  "question": "What is your full name?",
  "validation": {
    "min_length": 2,
    "max_length": 100
  }
}

{
  "id": "personality_q1",
  "type": "scale",
  "question": "On a scale of 1-10, how introverted are you?",
  "min": 1,
  "max": 10,
  "labels": {
    "1": "Very Extroverted",
    "10": "Very Introverted"
  }
}

{
  "id": "preferences_q1",
  "type": "multi-select",
  "question": "What genres of music do you enjoy?",
  "options": ["Rock", "Pop", "Classical", "Jazz", "Hip-Hop", "Electronic", "Country", "Other"]
}
```

#### 2.2 Conditional Questions
**Priority: Medium**

Questions that appear based on previous answers.

```json
{
  "id": "family_q10",
  "question": "Do you have children?",
  "type": "choice",
  "options": ["Yes", "No"]
},
{
  "id": "family_q11",
  "condition": "family_q10 == 'Yes'",
  "question": "What are your children's names and ages?"
}
```

#### 2.3 Question Weights & Importance
**Priority: Low**

Allow marking questions as essential vs optional.

```json
{
  "id": "core_values_q1",
  "importance": "essential",  // essential, recommended, optional
  "question": "What are your core values?"
}
```

---

### Phase 3: AI/LLM Integration

#### 3.1 Answer Assistant
**Priority: High**

Help users articulate their thoughts better.

```
User types: "I like hiking"

AI suggests: "Could you elaborate? Consider mentioning:
- When did you start hiking?
- What's your favorite trail or hike?
- What do you enjoy most about it?
- Do you hike alone or with others?"
```

#### 3.2 Digital Twin Preview
**Priority: High**

Let users chat with their emerging digital twin.

```
[After answering 100+ questions]

User: "What would my digital twin say about my work-life balance?"

Digital Twin: "Based on your answers, you've expressed that work-life 
balance is a challenge. You mentioned working 50+ hours/week but also 
said family time is your top priority. This seems like an area of 
internal conflict you're working through..."
```

#### 3.3 Memory Extraction from Documents
**Priority: Medium**

Allow importing memories from journals, emails, social media exports.

```python
# Import from various sources
preserver.import_from_journal("my_diary.txt")
preserver.import_from_social("twitter_export.json")
preserver.import_from_photos("photos/", extract_memories=True)
```

#### 3.4 Answer Quality Scoring
**Priority: Low**

Rate how complete and detailed answers are.

```
Question: "Describe your childhood home"
Answer: "It was nice"
Score: 2/10 - "Consider adding details about location, size, 
              memorable features, and how it made you feel"
```

---

### Phase 4: Data Management & Privacy

#### 4.1 Encrypted Storage
**Priority: High**

Encrypt sensitive data at rest.

```python
# User sets a master password
preserver.enable_encryption(password="user_master_password")

# Data is encrypted with AES-256
# Password never stored, only used to derive key
```

#### 4.2 Selective Sync
**Priority: Medium**

Optional cloud backup with user control.

```yaml
sync:
  enabled: true
  provider: self-hosted  # or 'dropbox', 'gdrive', 'none'
  endpoint: https://my-server.com/preserver
  encrypt_before_sync: true
  categories_to_sync:
    - goals
    - memories
  categories_to_exclude:
    - personal_info  # Keep locally only
```

#### 4.3 Data Portability
**Priority: Medium**

Easy import/export between devices.

```bash
# Export encrypted backup
python cli.py backup --encrypt --output my_backup.preserver

# Import on another device
python cli.py restore --input my_backup.preserver
```

#### 4.4 Answer Redaction
**Priority: Low**

Allow users to mark certain answers as "private" (excluded from exports).

```python
answer.set_visibility("private")  # Won't appear in exports
answer.set_visibility("public")   # Included in exports
```

---

### Phase 5: User Experience Improvements

#### 5.1 Mobile App
**Priority: High**

React Native or Flutter app for on-the-go answering.

Features:
- Push notifications for daily questions
- Voice input
- Photo attachment for memory questions
- Offline-first with sync

#### 5.2 Progressive Web App (PWA)
**Priority: Medium**

Make the HTML version installable as a PWA.

```json
// manifest.json
{
  "name": "Preserver",
  "short_name": "Preserver",
  "start_url": "/",
  "display": "standalone",
  "theme_color": "#667eea"
}
```

#### 5.3 Gamification
**Priority: Low**

Encourage consistent engagement.

- Daily streaks
- Badges for completing categories
- Progress milestones
- Weekly "reflection" prompts

#### 5.4 Scheduled Sessions
**Priority: Low**

Set reminders to answer questions.

```yaml
schedule:
  enabled: true
  frequency: daily
  time: "20:00"
  questions_per_session: 5
  notification: true
```

---

### Phase 6: Advanced Features

#### 6.1 Multi-Language Support
**Priority: Medium**

Translate questions and support answers in any language.

```
questions/
├── en/
│   └── personal_info/
├── es/
│   └── personal_info/
├── fr/
│   └── personal_info/
```

#### 6.2 Voice & Video Answers
**Priority: Medium**

Capture more than text.

```python
answer = Answer(
    question_id="memories_q1",
    type="voice",
    audio_file="answers/audio/memories_q1.mp3",
    transcription="When I think of my happiest memory..."
)
```

#### 6.3 Relationship Mapping
**Priority: Low**

Track and visualize relationships mentioned in answers.

```
Extracted entities:
- Mom (mentioned 45 times, categories: childhood, family, memories)
- John (mentioned 12 times, categories: relationships, career)
- Sarah (mentioned 8 times, categories: childhood, memories)
```

#### 6.4 Life Timeline
**Priority: Low**

Automatically generate a timeline from answers.

```
1990 - Born in Chicago (personal_info_q12)
1995 - Started school, met first best friend (childhood_q2)
2008 - Graduated high school (education_q1)
2012 - First job at tech company (career_q1)
...
```

#### 6.5 Semantic Search
**Priority: Medium**

Search through answers using natural language.

```
Search: "times I felt proud"
Results:
- memories_q5: "Graduating summa cum laude..."
- career_q4: "Getting promoted to lead..."
- goals_q9: "Completing my first marathon..."
```

---

### Phase 7: Integration & Ecosystem

#### 7.1 LLM Training Pipeline
**Priority: High**

Direct integration with popular fine-tuning tools.

```bash
# Export directly to training format
python cli.py export --user john --format llama-factory
python cli.py export --user john --format axolotl
python cli.py export --user john --format openai-ft
```

#### 7.2 API Server
**Priority: Medium**

REST API for building custom interfaces.

```python
# api.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/questions/{category}")
async def get_questions(category: str):
    ...

@app.post("/answers")
async def submit_answer(answer: AnswerCreate):
    ...

@app.get("/export/{user_id}")
async def export_data(user_id: str, format: str):
    ...
```

#### 7.3 Browser Extension
**Priority: Low**

Capture thoughts while browsing.

- "Save this article with my thoughts"
- "Remember this quote"
- Quick question prompts

#### 7.4 Calendar Integration
**Priority: Low**

Pull in life events from calendars.

```python
# Import life events
preserver.import_from_calendar("google_calendar_export.ics")
# Auto-generates questions: "Tell me about your trip to Paris in 2019"
```

---

## Implementation Priority Matrix

| Feature | Impact | Effort | Priority |
|---------|--------|--------|----------|
| SQLite Backend | High | Medium | P1 |
| Question Types | High | Medium | P1 |
| Digital Twin Preview | High | High | P1 |
| Encrypted Storage | High | Medium | P1 |
| Answer Assistant | High | High | P2 |
| Mobile App | High | High | P2 |
| Configuration System | Medium | Low | P2 |
| Multi-Language | Medium | Medium | P2 |
| Voice Answers | Medium | Medium | P3 |
| API Server | Medium | Medium | P3 |
| Life Timeline | Medium | High | P3 |
| Gamification | Low | Medium | P4 |
| Browser Extension | Low | High | P4 |

---

## Technical Debt & Refactoring

### Current Issues
1. **Duplicate code** between `app.py` and `index.html` for question logic
2. **No type hints** in some functions
3. **Hardcoded paths** instead of configuration
4. **No logging** for debugging
5. **No rate limiting** considerations for future API

### Proposed Refactoring
1. Extract core logic into a `preserver/core.py` module
2. Add comprehensive type hints
3. Create a configuration management system
4. Add structured logging
5. Write integration tests

---

## Contribution Opportunities

### Good First Issues
- [ ] Add more questions to existing categories
- [ ] Translate questions to other languages
- [ ] Improve CSS styling in HTML version
- [ ] Add more export format options
- [ ] Write documentation

### Intermediate
- [ ] Implement SQLite backend
- [ ] Add question type support
- [ ] Create PWA manifest
- [ ] Build answer validation

### Advanced
- [ ] Implement AI answer assistant
- [ ] Build digital twin chat interface
- [ ] Create mobile app
- [ ] Implement encrypted storage

---

## Conclusion

Preserver has a solid foundation as a privacy-first digital twin creator. The key improvements should focus on:

1. **Data robustness** - SQLite backend with versioning
2. **AI integration** - Help users create better digital twins
3. **User experience** - Mobile app, gamification, reminders
4. **Privacy** - Encryption, selective sync, data control

The goal is to make it as easy as possible for people to preserve their unique perspectives, thoughts, and personalities for future generations.

---

*Last updated: February 2026*
*Contributors welcome! See CONTRIBUTING.md for guidelines.*
