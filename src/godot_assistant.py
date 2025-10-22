# src/godot_assistant.py
"""
Core AI assistant for Godot development.
Handles RAG pipeline, document ingestion, and query processing.
"""
from typing import Optional
from pathlib import Path
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.chains.retrieval_qa.base import BaseRetrievalQA
from langchain.prompts import PromptTemplate

from config import AppConfig
from commands import CommandParser, CommandContext, CommandError

class GodotAIAssistant:
	"""AI assistant specialized in Godot game engine development"""
	
	def __init__(
		self, 
		project_analyzer, 
		display_manager, 
		config: AppConfig,
		embeddings=None,
		llm=None,
		command_parser=None
	):
		"""
		Initialize the Godot AI Assistant
		
		Args:
			project_analyzer: ProjectAnalyzer instance for handling project files
			display_manager: ConsoleOutputManager for output formatting
			config: Application configuration
			embeddings: Optional pre-initialized embeddings instance (for DI)
			llm: Optional pre-initialized LLM instance (for DI)
			command_parser: Optional pre-initialized CommandParser instance (for DI)
		"""
		self.project_analyzer = project_analyzer
		self.display_manager = display_manager
		self.config = config
		self.vectorstore = None
		self.qa_chain: BaseRetrievalQA | None = None
		self.last_read_file = None  # Track last read file for context
		
		# Initialize command parser - use provided or create new
		self.command_parser = command_parser if command_parser is not None else CommandParser()
		
		# Initialize embeddings - use provided or create new
		self.embeddings = embeddings if embeddings is not None else self._initialize_embeddings()
		
		# Initialize LLM - use provided or create new
		self.llm = llm if llm is not None else self._initialize_llm()
	
	def _initialize_embeddings(self):
		"""
		Initialize embedding model based on configuration.
		
		Returns:
			Initialized embeddings instance
		"""
		if self.config.embedding.provider == "local":
			print("Using local embeddings (free, no API key needed)")
			return HuggingFaceEmbeddings(
				model_name="all-MiniLM-L6-v2",
				model_kwargs={'device': 'cpu'}
			)
		else:
			print("Using OpenAI embeddings")
			return OpenAIEmbeddings(openai_api_key=self.config.api.openai_key)
	
	def _initialize_llm(self):
		"""
		Initialize LLM based on configuration.
		
		Returns:
			Initialized LLM instance
		"""
		if self.config.api.provider == "anthropic":
			return ChatAnthropic(
				model=self.config.llm.anthropic_model,
				temperature=self.config.llm.temperature,
				anthropic_api_key=self.config.api.anthropic_key
			)
		else:
			return ChatOpenAI(
				model=self.config.llm.openai_model,
				temperature=self.config.llm.temperature,
				openai_api_key=self.config.api.openai_key
			)
	
	def load_or_create_vectorstore(self):
		"""Load existing vectorstore or create new one from documents"""
		if self.config.paths.db_path.exists() and list(self.config.paths.db_path.iterdir()):
			print("Loading existing vector database...")
			self.vectorstore = Chroma(
				persist_directory=str(self.config.paths.db_path),
				embedding_function=self.embeddings
			)
			print(f"Loaded {self.vectorstore._collection.count()} documents")
		else:
			print("Creating new vector database from Godot documentation and lore...")
			self.ingest_documents()
	
	def load_lore_documents(self):
		"""
		Load lore documents from the lore directory.
		
		Returns:
			List of loaded lore documents
		"""
		if not self.config.paths.lore_path.exists():
			print(f"⚠ Lore directory not found: {self.config.paths.lore_path}")
			return []
		
		print(f"Loading lore documents from {self.config.paths.lore_path}...")
		
		all_docs = []
		patterns = ["**/*.txt", "**/*.md", "**/*.rst"]
		
		for pattern in patterns:
			try:
				loader = DirectoryLoader(
					str(self.config.paths.lore_path),
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
		if not self.config.paths.docs_path.exists():
			self.display_manager.print_error_doc_missing(self.config.paths.docs_path)
		else:
			print("Loading Godot documentation...")
			loader = DirectoryLoader(
				str(self.config.paths.docs_path),
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
			return
		
		print(f"\nTotal documents to process: {len(all_documents)}")
		print(f"  - Documentation: {len([d for d in all_documents if d.metadata.get('source_type') == 'documentation'])}")
		print(f"  - Lore: {len([d for d in all_documents if d.metadata.get('source_type') == 'lore'])}")
		
		# Split documents using configured chunk size
		print("\nSplitting documents into chunks...")
		text_splitter = RecursiveCharacterTextSplitter(
			chunk_size=self.config.rag.chunk_size,
			chunk_overlap=self.config.rag.chunk_overlap,
			length_function=len
		)
		texts = text_splitter.split_documents(all_documents)
		print(f"Created {len(texts)} chunks")
		
		# Create vectorstore
		print("Creating embeddings and storing in vector database...")
		self.vectorstore = Chroma.from_documents(
			documents=texts,
			embedding=self.embeddings,
			persist_directory=str(self.config.paths.db_path)
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
		
		# Create retrieval chain with configured k value
		self.qa_chain = RetrievalQA.from_chain_type(
			llm=self.llm,
			chain_type="stuff",
			retriever=self.vectorstore.as_retriever(
				search_kwargs={"k": self.config.rag.retrieval_k}
			),
			chain_type_kwargs={"prompt": QA_PROMPT},
			return_source_documents=True
		)
	
	def ask(self, question: str) -> str:
		"""
		Ask a question to the Godot AI assistant.
		
		Args:
			question: User's question or command
			
		Returns:
			The assistant's response
			
		Raises:
			ValueError: If QA chain not initialized
		"""
		if not self.qa_chain:
			raise ValueError("QA chain not initialized. Call setup_qa_chain first.")
		
		# Try to parse as a command
		try:
			command = self.command_parser.parse(question)
			if command:
				# Execute command
				context = CommandContext(
					project_analyzer=self.project_analyzer,
					display_manager=self.display_manager,
					assistant=self
				)
				result = command.execute(context)
				# Remove HTML tags for console output
				result = result.replace('<pre>', '').replace('</pre>', '')
				print(result)
				return ""
		except CommandError as e:
			print(f"\n❌ Command error: {e}")
			return ""
		
		# Not a command - process as regular question
		# Enhance question with file context if available
		enhanced_question = question
		if self.last_read_file:
			enhanced_question = f"""I previously read the file: {self.last_read_file['path']}

Here is the content of that file:
```
{self.last_read_file['content'][:4000]}
```

Now, my question is: {question}"""
		
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
		if self.last_read_file:
			print(f"  - Context: {self.last_read_file['path']}")
		print("="*80)
		
		return answer