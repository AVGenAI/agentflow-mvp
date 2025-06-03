"""
LLM Factory for supporting multiple LLM providers
"""
import os
from typing import Optional, Any

try:
    from langchain_openai import ChatOpenAI
except ImportError:
    ChatOpenAI = None
    
try:
    from langchain_community.llms import Ollama
    from langchain_community.chat_models import ChatOllama
except ImportError:
    Ollama = None
    ChatOllama = None
    
try:
    from langchain.schema import BaseLanguageModel
except ImportError:
    BaseLanguageModel = Any


class LLMFactory:
    """Factory class for creating LLM instances based on configuration"""
    
    @staticmethod
    def create_llm(
        provider: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> Optional[BaseLanguageModel]:
        """
        Create an LLM instance based on the provider
        
        Args:
            provider: LLM provider (openai, ollama, mock)
            model_name: Model name to use
            temperature: Temperature setting for the model
            **kwargs: Additional provider-specific arguments
            
        Returns:
            LLM instance or None for mock mode
        """
        # Get provider from environment if not specified
        if provider is None:
            provider = os.getenv("LLM_PROVIDER", "mock").lower()
        
        print(f"Initializing LLM with provider: {provider}")
        
        if provider == "openai":
            return LLMFactory._create_openai_llm(model_name, temperature, **kwargs)
        elif provider == "ollama":
            return LLMFactory._create_ollama_llm(model_name, temperature, **kwargs)
        elif provider == "mock":
            print("Running in mock mode - no LLM will be used")
            return None
        else:
            print(f"Unknown provider: {provider}. Running in mock mode.")
            return None
    
    @staticmethod
    def _create_openai_llm(
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> Optional[ChatOpenAI]:
        """Create OpenAI LLM instance"""
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            print("WARNING: OPENAI_API_KEY not set. Cannot use OpenAI provider.")
            return None
        
        if model_name is None:
            model_name = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
        
        try:
            return ChatOpenAI(
                model=model_name,
                temperature=temperature,
                openai_api_key=api_key,
                **kwargs
            )
        except Exception as e:
            print(f"Error creating OpenAI LLM: {e}")
            return None
    
    @staticmethod
    def _create_ollama_llm(
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> Optional[ChatOllama]:
        """Create Ollama LLM instance"""
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        if model_name is None:
            model_name = os.getenv("OLLAMA_MODEL", "llama2")
        
        try:
            # Test if Ollama is running
            import requests
            try:
                response = requests.get(f"{base_url}/api/tags", timeout=5)
                if response.status_code != 200:
                    print(f"WARNING: Ollama server not responding at {base_url}")
                    return None
            except requests.exceptions.RequestException:
                print(f"WARNING: Cannot connect to Ollama at {base_url}")
                print("Make sure Ollama is running: ollama serve")
                return None
            
            # Create ChatOllama instance for better compatibility with agent framework
            return ChatOllama(
                model=model_name,
                temperature=temperature,
                base_url=base_url,
                **kwargs
            )
        except Exception as e:
            print(f"Error creating Ollama LLM: {e}")
            return None
    
    @staticmethod
    def get_available_models(provider: str) -> list:
        """Get list of available models for a provider"""
        if provider == "openai":
            return [
                "gpt-4-turbo-preview",
                "gpt-4",
                "gpt-3.5-turbo",
                "gpt-3.5-turbo-16k"
            ]
        elif provider == "ollama":
            # Try to get models from Ollama API
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            try:
                import requests
                response = requests.get(f"{base_url}/api/tags", timeout=5)
                if response.status_code == 200:
                    models_data = response.json()
                    return [model["name"] for model in models_data.get("models", [])]
            except:
                pass
            # Return common models if API call fails
            return [
                "llama2",
                "mistral",
                "codellama",
                "llama2:13b",
                "llama2:70b",
                "mixtral",
                "neural-chat",
                "starling-lm",
                "orca-mini"
            ]
        return []