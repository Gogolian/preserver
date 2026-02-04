[![justforfunnoreally.dev badge](https://img.shields.io/badge/justforfunnoreally-dev-9ff)](https://justforfunnoreally.dev)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)

# 🧠 Preserver: Your Personal Digital Twin Creator

> *Preserve your thoughts, memories, and personality for the future.*

## About Preserver

Preserver is an open-source project designed to help you create a **digital twin** of yourself. By gathering and storing your personal data **locally**, Preserver empowers you to train future Language Learning Models (LLMs) to respond as you would, creating a unique digital representation of your thoughts and personality.

**Why Preserver?**

People come and go too early. We've had written notes, books, voice recordings, photos, and videos to remember those who passed. But what if we could preserve more—the essence of a person, the way they think, their personality, their unique perspective on life?

Preserver aims to capture enough of *you* that future AI could approximate how you might respond, think, and feel.

## ✨ Key Features

- 🔒 **Privacy-First**: All data is stored locally—you own it completely
- 📝 **990+ Questions**: Comprehensive questions across 33 life categories
- 💾 **LLM-Ready Exports**: Export in JSONL (instruction/conversation format) or JSON
- 📊 **Progress Tracking**: Track your journey across categories
- 🔄 **Two Versions**: Python (Gradio) app or pure HTML/JS standalone version
- 🎯 **Category Filtering**: Focus on specific life aspects
- 📤 **Multiple Export Formats**: Ready for fine-tuning various LLM architectures
- 🚀 **Open Source**: Community-driven development

## 🚀 Getting Started

### Option 1: Python Version (Recommended)

The Python version offers a full-featured experience with Gradio.

**Prerequisites:**
- Python 3.8+
- pip

**Installation:**

```bash
# Clone the repository
git clone https://github.com/Gogolian/preserver.git
cd preserver

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

Open your web browser and navigate to the URL shown in the terminal (typically `http://127.0.0.1:7860`).

### Option 2: HTML/JS Version (No Installation Required)

For a completely dependency-free experience, simply open `index.html` in your web browser!

```bash
# Just open the file
open index.html  # macOS
# or
xdg-open index.html  # Linux
# or just double-click index.html on Windows
```

**Note:** The HTML version stores data in your browser's local storage and includes a representative subset of questions.

## 📚 Question Categories

Preserver includes **990+** carefully crafted questions across **33 categories**:

| Category | Description |
|----------|-------------|
| 🧑 Personal Info | Basic biographical information |
| 👶 Childhood | Early memories and formative years |
| 🎯 Goals | Aspirations and ambitions |
| 💭 Beliefs | Core values and worldview |
| 🎭 Personality | Character traits and tendencies |
| 💕 Relationships | Connections with others |
| ⭐ Preferences | Likes, dislikes, and favorites |
| 💼 Career | Professional life and work |
| 🎨 Hobbies | Leisure activities and passions |
| 📸 Memories | Significant life moments |
| 💻 Technology | Digital life and tech perspectives |
| 🌟 Spirituality | Inner life and meaning |
| 📱 Social Media | Online presence and habits |
| 🧭 Life Philosophy | Wisdom and life principles |
| 💬 Opinions | Views on society and issues |
| ... and 18 more categories! |

## 📤 Export Formats

Export your data in formats ready for LLM training:

### JSONL (Instruction Format)
```json
{"instruction": "What are your top three long-term life goals?", "output": "...", "category": "goals"}
```

### JSONL (Conversation Format)
```json
{"messages": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}], "category": "goals"}
```

### JSON (Complete Export)
```json
{
  "username": "your_name",
  "export_date": "2024-01-15T10:30:00",
  "total_answers": 150,
  "answers": [...]
}
```

## 🛠 How It Works

1. **Start** the app and enter your username
2. **Answer** questions about your life, thoughts, and experiences
3. **Track** your progress across all categories
4. **Export** your data in LLM-ready formats
5. **Train** a personalized AI model (future integration coming!)

## 🤝 Contributing

We welcome contributions from the community! Here are some ways you can help:

- 📝 Add new questions to the `questions` directory
- 🎨 Improve the user interface
- 🔧 Enhance data storage and retrieval methods
- 🌍 Add multilingual support
- 💡 Suggest new features

Please read our [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

### Adding Questions

1. Navigate to the `questions/` directory
2. Choose or create a category folder
3. Add a new `.txt` file with your question
4. Submit a pull request!

## 🗺 Roadmap

- [x] ~~Script to aggregate answers into a single file per user~~
- [x] ~~Pure HTML/JS version to run locally without Python~~
- [x] ~~Progress tracking and visualization~~
- [x] ~~Category-based filtering~~
- [x] ~~Multiple export formats~~
- [ ] Voice input support
- [ ] Multilingual support
- [ ] Integration with popular LLM training frameworks
- [ ] Mobile app for on-the-go data collection
- [ ] AI-assisted question generation
- [ ] Data visualization dashboard

## ⚠️ Disclaimer

Preserver is an experimental project in its early stages. The author and contributors hold no liability for the use or misuse of this software. Always be cautious about the personal information you provide and how you use your digital twin.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 💖 Funding

If you'd like to support this project, see [funding.json](misc/funding.json).

---

<p align="center">
Built with ❤️ by <a href="https://github.com/Gogolian">Gogolian</a> and the open-source community.
</p>

<p align="center">
<strong>Your data, your twin, your future!</strong>
</p>
