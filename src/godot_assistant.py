# src/godot_assistant.py
import os
from pathlib import Path
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

class GodotAIAssistant:
    def __init__(self, project_analyzer, display_manager, api_provider="anthropic", embedding_provider="local"):
        """
        Initialize the Godot AI Assistant
        
        Args:
            project_analyzer: ProjectAnalyzer instance for handling project files
            api_provider: "anthropic" or "openai"
            embedding_provider: "local" (free) or "openai" (requires API key)
        """
        self.project_analyzer = project_analyzer
        self.api_provider = api_provider
        self.embedding_provider = embedding_provider
        self.display_manager = display_manager
        self.docs_path = Path("/app/godot_docs")
        self.lore_path = Path("/app/data/lore")
        self.db_path = Path("/app/data/chroma_db")
        self.vectorstore = None
        self.qa_chain = None
        
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
            print("Creating new vector database from Godot documentation and lore...")
            self.ingest_documents()
    
    def load_lore_documents(self):
        """Load lore documents from the lore directory"""
        if not self.lore_path.exists():
            print(f"⚠ Lore directory not found: {self.lore_path}")
            return []
        
        print(f"Loading lore documents from {self.lore_path}...")
        
        # Try to load various text file types
        all_docs = []
        patterns = ["**/*.txt", "**/*.md", "**/*.rst"]
        
        for pattern in patterns:
            try:
                loader = DirectoryLoader(
                    str(self.lore_path),
                    glob=pattern,
                    loader_cls=TextLoader,
                    loader_kwargs={'autodetect_encoding': True}
                )
                docs = loader.load()
                all_docs.extend(docs)
                if docs:
                    print(f"  Loaded {len(docs)} {pattern} files")
            except Exception as e:
                print(f"  Warning loading {pattern}: {e}")
        
        if all_docs:
            print(f"✓ Total lore documents loaded: {len(all_docs)}")
            # Add metadata to identify lore documents
            for doc in all_docs:
                doc.metadata['source_type'] = 'lore'
        else:
            print("⚠ No lore documents found")
        
        return all_docs
    
    def ingest_documents(self):
        """Load and process Godot documentation AND lore into vector database"""
        all_documents = []
        
        # Load Godot documentation
        if not self.docs_path.exists():
            self.display_manager.print_error_doc_missing(self.docs_path)
        else:
            print("Loading Godot documentation...")
            loader = DirectoryLoader(
                str(self.docs_path),
                glob="**/*.rst",  # Godot docs are in reStructuredText
                loader_cls=TextLoader,
                loader_kwargs={'autodetect_encoding': True}
            )
            
            try:
                documents = loader.load()
                # Mark as documentation
                for doc in documents:
                    doc.metadata['source_type'] = 'documentation'
                all_documents.extend(documents)
                print(f"✓ Loaded {len(documents)} documentation files")
            except Exception as e:
                print(f"Error loading documentation: {e}")
        
        # Load lore documents
        lore_documents = self.load_lore_documents()
        all_documents.extend(lore_documents)
        
        if not all_documents:
            print("⚠ No documents found! The assistant will have limited capabilities.")
            print("Add documentation to godot_docs/ and/or lore to data/lore/")
            # Don't exit, allow assistant to work with just prompts
            return
        
        print(f"\nTotal documents to process: {len(all_documents)}")
        print(f"  - Documentation: {len([d for d in all_documents if d.metadata.get('source_type') == 'documentation'])}")
        print(f"  - Lore: {len([d for d in all_documents if d.metadata.get('source_type') == 'lore'])}")
        
        # Split documents
        print("\nSplitting documents into chunks...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        texts = text_splitter.split_documents(all_documents)
        print(f"Created {len(texts)} chunks")
        
        # Create vectorstore
        print("Creating embeddings and storing in vector database...")
        self.vectorstore = Chroma.from_documents(
            documents=texts,
            embedding=self.embeddings,
            persist_directory=str(self.db_path)
        )
        print("✓ Vector database created successfully!")
    
    def setup_qa_chain(self):
        """Setup the RAG question-answering chain"""
        if not self.vectorstore:
            raise ValueError("Vectorstore not initialized. Call load_or_create_vectorstore first.")
        
        template = """You are an expert Godot game engine assistant with access to:
1. Official Godot documentation
2. Game/project lore and world-building documents
3. The user's actual project files

IMPORTANT CAPABILITIES:
- You can read files from the user's project by asking them to share specific file paths
- You can see the project structure when provided
- You have access to lore documents that describe the game's world, characters, story, and setting
- You should provide advice tailored to their specific project when relevant

When answering questions about lore, story, characters, or world-building:
- Use the lore documents provided in the context
- Be specific and reference details from the lore
- Help maintain consistency with established lore

When answering technical Godot questions:
- Use the Godot documentation in the context
- Provide specific code examples using GDScript syntax
- Reference best practices

If you don't know the answer based on the context provided, just say that you don't know - don't make up information.

Context (may include documentation and/or lore):
{context}

Question: {question}

Helpful Answer:"""
        
        QA_PROMPT = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
        
        # Create retrieval chain with increased k for better lore coverage
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 6}),
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
        
        if question.lower().startswith("/lore"):
            return self.handle_lore_command()
        
        print(f"\nQuestion: {question}")
        print("Thinking...\n")
        
        result = self.qa_chain.invoke({"query": enhanced_question})
        
        answer = result['result']
        sources = result['source_documents']
        
        print("Answer:")
        print(answer)
        print("\n" + "="*80)
        
        # Show source types
        doc_sources = [s for s in sources if s.metadata.get('source_type') == 'documentation']
        lore_sources = [s for s in sources if s.metadata.get('source_type') == 'lore']
        
        print(f"Sources: {len(sources)} relevant chunks retrieved")
        if doc_sources:
            print(f"  - {len(doc_sources)} from documentation")
        if lore_sources:
            print(f"  - {len(lore_sources)} from lore")
        print("="*80)
        
        return answer
    
    def handle_project_command(self, command):
        """Handle project-related commands"""
        if "info" in command.lower():
            self.display_manager.print_info(self.project_analyzer)
        elif "structure" in command.lower():
            self.display_manager.print_structure(self.project_analyzer)
        else:
            self.display_manager.print_commands()
        return ""
    
    def handle_lore_command(self):
        """Handle lore-related commands"""
        print("\nLore Status:")
        print("="*80)
        
        if not self.lore_path.exists():
            print(f"❌ Lore directory not found: {self.lore_path}")
            print("Create the directory and add .txt, .md, or .rst files")
        else:
            print(f"✓ Lore directory: {self.lore_path}")
            
            # Count lore files
            lore_files = []
            for pattern in ["*.txt", "*.md", "*.rst"]:
                lore_files.extend(list(self.lore_path.rglob(pattern)))
            
            if lore_files:
                print(f"✓ Found {len(lore_files)} lore files:")
                for f in lore_files:
                    rel_path = f.relative_to(self.lore_path)
                    size = f.stat().st_size
                    print(f"  - {rel_path} ({size:,} bytes)")
            else:
                print("⚠ No lore files found")
                print("Add .txt, .md, or .rst files to the lore directory")
        
        print("="*80)
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