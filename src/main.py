import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

load_dotenv()

class ProjectAnalyzer:
    """Analyzes and provides context about the user's Godot project"""
    
    def __init__(self, project_path):
        self.project_path = Path(project_path)
        self.project_exists = self.project_path.exists()
    
    def get_project_structure(self, max_depth=3):
        """Get a tree-like structure of the project"""
        if not self.project_exists:
            return "No project mounted"
        
        structure = []
        structure.append(f"Project root: {self.project_path}")
        
        try:
            for root, dirs, files in os.walk(self.project_path):
                level = root.replace(str(self.project_path), '').count(os.sep)
                if level >= max_depth:
                    dirs[:] = []  # Don't go deeper
                    continue
                
                indent = ' ' * 2 * level
                structure.append(f'{indent}{os.path.basename(root)}/')
                
                subindent = ' ' * 2 * (level + 1)
                for file in sorted(files)[:10]:  # Limit files per directory
                    if file.endswith(('.gd', '.tscn', '.tres', '.godot')):
                        structure.append(f'{subindent}{file}')
            
            return '\n'.join(structure[:100])  # Limit total lines
        except Exception as e:
            return f"Error reading project: {e}"
    
    def read_file(self, relative_path):
        """Read a file from the project"""
        try:
            file_path = self.project_path / relative_path
            if not file_path.exists():
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {e}"
    
    def find_files(self, pattern="*.gd"):
        """Find files matching a pattern"""
        if not self.project_exists:
            return []
        
        try:
            return [str(p.relative_to(self.project_path)) 
                    for p in self.project_path.rglob(pattern)][:50]
        except Exception as e:
            return []
    
    def get_project_info(self):
        """Get basic project information"""
        if not self.project_exists:
            return "No Godot project is currently mounted."
        
        info = []
        info.append(f"Project location: {self.project_path}")
        
        # Check for project.godot
        project_file = self.project_path / "project.godot"
        if project_file.exists():
            info.append("✓ Valid Godot project detected (project.godot found)")
        else:
            info.append("⚠ No project.godot found - may not be a Godot project root")
        
        # Count files
        gd_files = len(self.find_files("*.gd"))
        scene_files = len(self.find_files("*.tscn"))
        
        info.append(f"GDScript files: {gd_files}")
        info.append(f"Scene files: {scene_files}")
        
        return "\n".join(info)


class GodotAIAssistant:
    def __init__(self, api_provider="anthropic", embedding_provider="local"):
        """
        Initialize the Godot AI Assistant
        
        Args:
            api_provider: "anthropic" or "openai"
            embedding_provider: "local" (free) or "openai" (requires API key)
        """
        self.api_provider = api_provider
        self.embedding_provider = embedding_provider
        self.docs_path = Path("/app/godot_docs")
        self.db_path = Path("/app/data/chroma_db")
        self.project_path = Path(os.getenv("GODOT_PROJECT_PATH", "/app/project"))
        self.vectorstore = None
        self.qa_chain = None
        
        # Initialize project analyzer
        self.project_analyzer = ProjectAnalyzer(self.project_path)
        
        # Initialize embeddings
        if embedding_provider == "local":
            print("Using local embeddings (free, no API key needed)")
            self.embeddings = HuggingFaceEmbeddings(
                model_name="all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'}
            )
        else:
            print("Using OpenAI embeddings")
            if not os.getenv("OPENAI_API_KEY"):
                raise ValueError("OPENAI_API_KEY required for OpenAI embeddings")
            self.embeddings = OpenAIEmbeddings()
        
        # Initialize LLM based on provider
        if api_provider == "anthropic":
            if not os.getenv("ANTHROPIC_API_KEY"):
                raise ValueError("ANTHROPIC_API_KEY not found in environment")
            self.llm = ChatAnthropic(model="claude-sonnet-4-20250514", temperature=0)
        else:
            if not os.getenv("OPENAI_API_KEY"):
                raise ValueError("OPENAI_API_KEY not found in environment")
            self.llm = ChatOpenAI(model="gpt-4-turbo-preview", temperature=0)
    
    def load_or_create_vectorstore(self):
        """Load existing vectorstore or create new one from documents"""
        if self.db_path.exists() and list(self.db_path.iterdir()):
            print("Loading existing vector database...")
            self.vectorstore = Chroma(
                persist_directory=str(self.db_path),
                embedding_function=self.embeddings
            )
            print(f"Loaded {self.vectorstore._collection.count()} documents")
        else:
            print("Creating new vector database from Godot documentation...")
            self.ingest_documents()
    
    def ingest_documents(self):
        """Load and process Godot documentation into vector database"""
        if not self.docs_path.exists():
            print(f"Documentation path {self.docs_path} not found!")
            print("Please add Godot documentation to the godot_docs directory.")
            print("\nYou can:")
            print("1. Clone Godot docs: git clone https://github.com/godotengine/godot-docs.git godot_docs")
            print("2. Or manually add .rst, .md, or .txt files to godot_docs/")
            sys.exit(1)
        
        # Load documents
        print("Loading documents...")
        loader = DirectoryLoader(
            str(self.docs_path),
            glob="**/*.rst",  # Godot docs are in reStructuredText
            loader_cls=TextLoader,
            loader_kwargs={'autodetect_encoding': True}
        )
        
        try:
            documents = loader.load()
        except Exception as e:
            print(f"Error loading documents: {e}")
            print("Trying alternative file types...")
            loader = DirectoryLoader(
                str(self.docs_path),
                glob="**/*.{md,txt}",
                loader_cls=TextLoader,
                loader_kwargs={'autodetect_encoding': True}
            )
            documents = loader.load()
        
        if not documents:
            print("No documents found! Please add Godot documentation.")
            sys.exit(1)
        
        print(f"Loaded {len(documents)} documents")
        
        # Split documents
        print("Splitting documents into chunks...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        texts = text_splitter.split_documents(documents)
        print(f"Created {len(texts)} chunks")
        
        # Create vectorstore
        print("Creating embeddings and storing in vector database...")
        self.vectorstore = Chroma.from_documents(
            documents=texts,
            embedding=self.embeddings,
            persist_directory=str(self.db_path)
        )
        print("Vector database created successfully!")
    
    def setup_qa_chain(self):
        """Setup the RAG question-answering chain"""
        if not self.vectorstore:
            raise ValueError("Vectorstore not initialized. Call load_or_create_vectorstore first.")
        
        # Create custom prompt template with project awareness
        template = """You are an expert Godot game engine assistant with access to both the official Godot documentation and the user's actual project files.

IMPORTANT CAPABILITIES:
1. You can read files from the user's project by asking them to share specific file paths
2. You can see the project structure when provided
3. You should provide advice tailored to their specific project when relevant

Use the following pieces of context from the Godot documentation to answer the question at the end.

If you don't know the answer based on the context provided, just say that you don't know - don't try to make up an answer.

Always provide specific code examples when relevant, using GDScript syntax.

When the user asks about their project, you can:
- Ask them to describe what files they have
- Suggest they share relevant code snippets
- Provide targeted advice based on their project structure

Context from Godot documentation:
{context}

Question: {question}

Helpful Answer:"""
        
        QA_PROMPT = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
        
        # Create retrieval chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 4}),
            chain_type_kwargs={"prompt": QA_PROMPT},
            return_source_documents=True
        )
    
    def ask(self, question):
        """Ask a question to the Godot AI assistant"""
        if not self.qa_chain:
            raise ValueError("QA chain not initialized. Call setup_qa_chain first.")
        
        # Check if question is about project files
        enhanced_question = question
        
        # Handle special commands
        if question.lower().startswith("/project"):
            return self.handle_project_command(question)
        
        if question.lower().startswith("/read "):
            file_path = question[6:].strip()
            return self.handle_read_file(file_path)
        
        if question.lower().startswith("/list"):
            pattern = question[5:].strip() or "*.gd"
            return self.handle_list_files(pattern)
        
        print(f"\nQuestion: {question}")
        print("Thinking...\n")
        
        result = self.qa_chain.invoke({"query": enhanced_question})
        
        answer = result['result']
        sources = result['source_documents']
        
        print("Answer:")
        print(answer)
        print("\n" + "="*80)
        print(f"Sources: {len(sources)} relevant document chunks retrieved")
        print("="*80)
        
        return answer
    
    def handle_project_command(self, command):
        """Handle project-related commands"""
        if "info" in command.lower():
            print("\nProject Information:")
            print("="*80)
            print(self.project_analyzer.get_project_info())
            print("\n" + "="*80)
        elif "structure" in command.lower():
            print("\nProject Structure:")
            print("="*80)
            print(self.project_analyzer.get_project_structure())
            print("\n" + "="*80)
        else:
            print("\nProject Commands:")
            print("  /project info      - Show project information")
            print("  /project structure - Show project file structure")
            print("  /read <file>       - Read a specific file")
            print("  /list [pattern]    - List files (default: *.gd)")
        return ""
    
    def handle_read_file(self, file_path):
        """Read and display a project file"""
        content = self.project_analyzer.read_file(file_path)
        if content is None:
            print(f"\n❌ File not found: {file_path}")
            print("Tip: Use /list to see available files")
        else:
            print(f"\n📄 Contents of {file_path}:")
            print("="*80)
            print(content[:2000])  # Limit display
            if len(content) > 2000:
                print(f"\n... (showing first 2000 chars of {len(content)} total)")
            print("="*80)
            
            # Now ask if they want analysis
            print("\nFile loaded! You can now ask questions about this file.")
        return ""
    
    def handle_list_files(self, pattern):
        """List files in the project"""
        files = self.project_analyzer.find_files(pattern)
        if not files:
            print(f"\n❌ No files found matching: {pattern}")
        else:
            print(f"\n📁 Files matching '{pattern}':")
            print("="*80)
            for f in files[:50]:
                print(f"  {f}")
            if len(files) > 50:
                print(f"\n... and {len(files) - 50} more")
            print("="*80)
        return ""

def main():
    print("="*80)
    print("Godot AI Development Assistant")
    print("="*80)
    
    # Choose API provider
    api_provider = os.getenv("API_PROVIDER", "anthropic").lower()
    embedding_provider = os.getenv("EMBEDDING_PROVIDER", "local").lower()
    
    print(f"\nUsing {api_provider.upper()} API")
    print(f"Using {embedding_provider.upper()} embeddings")
    
    try:
        # Initialize assistant
        assistant = GodotAIAssistant(
            api_provider=api_provider,
            embedding_provider=embedding_provider
        )
        
        # Show project status
        print("\n" + "="*80)
        print("Project Status:")
        print("="*80)
        print(assistant.project_analyzer.get_project_info())
        print("="*80)
        
        # Load or create vector database
        assistant.load_or_create_vectorstore()
        
        # Setup QA chain
        assistant.setup_qa_chain()
        
        print("\n" + "="*80)
        print("Assistant ready! Ask me anything about Godot development.")
        print("\nSpecial Commands:")
        print("  /project info      - Show your project details")
        print("  /project structure - Show project file tree")
        print("  /read <file>       - Read a file from your project")
        print("  /list [pattern]    - List files (e.g., /list *.gd)")
        print("  quit or exit       - Exit the assistant")
        print("="*80 + "\n")
        
        # Interactive loop
        while True:
            try:
                question = input("\nYour question: ").strip()
                
                if question.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                
                if not question:
                    continue
                
                assistant.ask(question)
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}")
                continue
    
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()