# model.py
from typing import Dict, Any, Optional, List, Union
import openai
import litellm
from litellm import completion
import os

class ModelClient:
    """Base class for different model clients"""
    def __init__(self, model_name: str = None):
        self.model_name = model_name
        
    def chat_completion(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
        raise NotImplementedError("Subclasses must implement this method")

class OpenAIClient(ModelClient):
    """Client for OpenAI models"""
    def __init__(self, api_key: str = None, model_name: str = "gpt-4o"):
        super().__init__(model_name=model_name)
        self.client = openai.OpenAI(api_key=api_key or os.environ.get("OPENAI_API_KEY"))
    
    def chat_completion(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature
        )
        return response.choices[0].message.content

class OpenRouterClient(ModelClient):
    """Client for OpenRouter API"""
    def __init__(self, api_key: str = None, model_name: str = "anthropic/claude-3-opus"):
        super().__init__(model_name=model_name)
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        # Configure OpenRouter
        openai.api_key = self.api_key
        openai.base_url = "https://openrouter.ai/api/v1"
        self.client = openai.OpenAI()
    
    def chat_completion(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            headers={
                "HTTP-Referer": "https://your-app-url.com",  # Replace with your actual URL
                "X-Title": "Your Application Name"  # Replace with your app name
            }
        )
        return response.choices[0].message.content

class LiteLLMClient(ModelClient):
    """Client for LiteLLM which supports multiple providers"""
    def __init__(self, api_key: str = None, model_name: str = "gpt-4", litellm_provider: str = None):
        super().__init__(model_name=model_name)
        self.api_key = api_key
        self.litellm_provider = litellm_provider
        
        # Set up API key for the specified provider
        if self.litellm_provider == "openai":
            os.environ["OPENAI_API_KEY"] = self.api_key or os.environ.get("OPENAI_API_KEY", "")
        elif self.litellm_provider == "anthropic":
            os.environ["ANTHROPIC_API_KEY"] = self.api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        elif self.litellm_provider == "openrouter":
            os.environ["OPENROUTER_API_KEY"] = self.api_key or os.environ.get("OPENROUTER_API_KEY", "")
        # Add other providers as needed
    
    def chat_completion(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # If a specific provider is defined, use it
        model_param = self.model_name
        if self.litellm_provider:
            # For some providers, LiteLLM needs format: "provider/model"
            if self.litellm_provider not in self.model_name:
                model_param = f"{self.litellm_provider}/{self.model_name}"
        
        response = litellm.completion(
            model=model_param,
            messages=messages,
            temperature=temperature
        )
        
        return response.choices[0].message.content

class ModelConfig:
    """Configuration class for a LLM model"""
    def __init__(
        self,
        provider: str = "openai",
        model_name: str = None,
        api_key: str = None,
        litellm_provider: str = None,
        temperature: float = 0.7
    ):
        self.provider = provider.lower()
        self.model_name = model_name
        self.api_key = api_key
        self.litellm_provider = litellm_provider
        self.temperature = temperature
        
        # Set defaults based on provider
        if not self.model_name:
            if self.provider == "openai":
                self.model_name = "gpt-4o"
            elif self.provider == "openrouter":
                self.model_name = "anthropic/claude-3-opus"
            elif self.provider == "litellm":
                self.model_name = "gpt-4o"
        
    def create_client(self) -> ModelClient:
        """Create and return a model client based on this configuration"""
        if self.provider == "openai":
            return OpenAIClient(api_key=self.api_key, model_name=self.model_name)
        elif self.provider == "openrouter":
            return OpenRouterClient(api_key=self.api_key, model_name=self.model_name)
        elif self.provider == "litellm":
            return LiteLLMClient(
                api_key=self.api_key, 
                model_name=self.model_name, 
                litellm_provider=self.litellm_provider
            )
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

def create_model(
    provider: str = "openai",
    model_name: str = None,
    api_key: str = None,
    litellm_provider: str = None,
    temperature: float = 0.7
) -> ModelClient:
    """
    Create and return a model client with the specified configuration
    
    Args:
        provider: The LLM provider (openai, openrouter, litellm)
        model_name: The specific model to use
        api_key: The API key for the provider
        litellm_provider: For litellm, the specific provider to use
        temperature: The temperature parameter for the model
        
    Returns:
        ModelClient: A configured model client
    """
    config = ModelConfig(
        provider=provider,
        model_name=model_name,
        api_key=api_key,
        litellm_provider=litellm_provider,
        temperature=temperature
    )
    return config.create_client()