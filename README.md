# Godot AI Development Assistant

An AI-powered assistant specialized in Godot game engine development, using RAG (Retrieval Augmented Generation) over Godot documentation.

## Features

- **RAG-based responses**: Answers are grounded in official Godot documentation
- **Multiple API support**: Works with both Claude (Anthropic) and ChatGPT (OpenAI)
- **Vector database**: Uses ChromaDB for efficient document retrieval
- **Docker-based**: Easy setup and consistent environment
- **Interactive CLI**: Ask questions in real-time

## Prerequisites

- Docker Desktop installed and running with WSL 2
- API key from either:
  - Anthropic (get at https://console.anthropic.com/)
  - OpenAI (get at https://platform.openai.com/)

## Project Structure

```
godot-ai-assistant/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env                    # Your API keys (create from .env.example)
├── .env.example
├── src/
│   └── main.py            # Main application
├── godot_docs/            # Place Godot documentation here
└── data/                  # Vector database storage (auto-created)
    └── chroma_db/
```

## Setup Instructions

### 1. Create Project Directory

```bash
mkdir godot-ai-assistant
cd godot-ai-assistant
```

### 2. Create Files

Create the following files in your project directory:
- `docker-compose.yml`
- `Dockerfile`
- `requirements.txt`
- `.env.example`
- Create `src/` directory and add `main.py`

### 3. Configure API Keys and Project Path

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your API key(s)
# For Claude (recommended):
ANTHROPIC_API_KEY=sk-ant-xxxxx

# Or for OpenAI:
OPENAI_API_KEY=sk-xxxxx

# Choose which API to use:
API_PROVIDER=anthropic  # or "openai"

# IMPORTANT: Set path to your Godot project
GODOT_PROJECT_PATH=/home/yourusername/path/to/your/godot/project
```

### 4. Get Godot Documentation

You have two options:

**Option A: Clone the official Godot docs (recommended)**
```bash
git clone https://github.com/godotengine/godot-docs.git godot_docs
```

**Option B: Manual download**
- Download documentation from https://github.com/godotengine/godot-docs
- Extract to `godot_docs/` directory

### 5. Build and Run

```bash
# Build the Docker image
docker-compose build

# Run the assistant
docker-compose up
```

The first run will:
1. Process all Godot documentation
2. Create embeddings
3. Store them in the vector database (this takes a few minutes)

Subsequent runs will use the cached database and start instantly.

## Usage

Once running, you'll see an interactive prompt with project information:

```
Your question: How do I create a 2D player character?
```

### Project-Aware Features

The assistant can now access your actual Godot project files! Use these special commands:

**View project information:**
```
/project info
```
Shows your project stats (number of scripts, scenes, etc.)

**Browse project structure:**
```
/project structure
```
Shows a tree view of your project files

**List specific files:**
```
/list *.gd          # List all GDScript files
/list *.tscn        # List all scene files
/list scenes/*.tscn # List scenes in a specific folder
```

**Read a specific file:**
```
/read player.gd
/read scenes/main_menu.tscn
```

**Ask questions about your project:**
After reading files, you can ask context-aware questions like:
- "How can I improve the performance of my player.gd script?"
- "What's wrong with my collision detection in this scene?"
- "Suggest improvements to my game state management"
- "Help me refactor this code to use signals better"

### Example Session

```
Your question: /project info
Project location: /app/project
✓ Valid Godot project detected (project.godot found)
GDScript files: 23
Scene files: 15

Your question: /list *.gd
📁 Files matching '*.gd':
  player.gd
  enemy.gd
  game_manager.gd
  ...

Your question: /read player.gd
📄 Contents of player.gd:
... (file contents shown) ...

Your question: How can I optimize the movement code in my player script?
... (AI analyzes the file you just read and provides specific suggestions) ...
```

### General Questions

You can also ask general Godot questions without project context:

Example questions:
- "How do I create a 2D player character?"
- "What's the difference between Node2D and Node3D?"
- "Show me how to implement signal callbacks"
- "How do I detect collisions in Godot?"
- "What's the best way to manage game state?"

Type `quit` or `exit` to stop.

## Switching API Providers

Edit your `.env` file:

```bash
# For Claude (Anthropic)
API_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_key_here

# For ChatGPT (OpenAI)
API_PROVIDER=openai
OPENAI_API_KEY=your_key_here
```

Restart the container for changes to take effect.

## Rebuilding the Vector Database

If you want to update the documentation or rebuild the database:

```bash
# Remove the existing database
rm -rf data/chroma_db/*

# Restart the container
docker-compose up
```

## Troubleshooting

**"No documents found"**
- Ensure `godot_docs/` contains .rst files
- Try cloning the official repo: `git clone https://github.com/godotengine/godot-docs.git godot_docs`

**"No Godot project is currently mounted"**
- Check your `.env` file has `GODOT_PROJECT_PATH` set correctly
- Use absolute path, not relative
- For WSL users on Windows: Use Linux path format like `/mnt/c/Users/username/projects/my_game` NOT `C:\Users\...`
- Ensure the path points to the folder containing `project.godot`

**"API key not found"**
- Check your `.env` file exists and contains valid keys
- Restart Docker container after changing `.env`

**"Docker container won't start"**
- Ensure Docker Desktop is running
- Check WSL 2 is enabled in Docker settings
- Try `docker-compose down` then `docker-compose run --rm godot-ai-assistant`

**Slow responses**
- First-time setup takes longer (processing docs)
- Subsequent runs use cached embeddings
- Consider reducing chunk size in `main.py` if memory constrained

## Customization

### Adjust chunk size for better responses

Edit `src/main.py`:
```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,  # Increase for more context
    chunk_overlap=200,  # Increase to reduce context loss
)
```

### Change number of retrieved documents

Edit `src/main.py`:
```python
retriever=self.vectorstore.as_retriever(search_kwargs={"k": 4})  # Adjust k value
```

### Use different models

Edit `src/main.py`:
```python
# For Anthropic
self.llm = ChatAnthropic(model="claude-sonnet-4-20250514", temperature=0)

# For OpenAI
self.llm = ChatOpenAI(model="gpt-4-turbo-preview", temperature=0)
```

## Cost Considerations

- **Embeddings**: Uses OpenAI embeddings (~$0.0001 per 1K tokens)
- **Initial indexing**: One-time cost to process all docs (~$1-5 depending on doc size)
- **Queries**: Each question costs ~$0.01-0.05 depending on model and context
- **Vector DB**: ChromaDB is free and runs locally

## Next Steps

- Add a web interface using FastAPI + React
- Implement conversation history
- Add code execution/testing capabilities
- Fine-tune on Godot-specific examples
- Add multi-language support (C#, C++)

## License

This project is provided as-is for educational purposes.