from data_loader import DataLoader

class ConsoleOutputManager:
  def __init__(self, lang: str) -> None:
    self.lang = lang
    pass

  def get_string(self, string_name: str) -> str|None:
    loader = DataLoader('src/output/data/' + self.lang + '.json')
    return loader.get(string_name)

  def print_welcome(self) -> None:
    print("="*80)
    print(self.get_string('app_title'))
    print("="*80)
  
  def print_config(self, config: dict) -> None:
    print(f"\nUsing {config['api_provider'].upper()} API")
    print(f"Using {config['embedding_provider'].upper()} embeddings")