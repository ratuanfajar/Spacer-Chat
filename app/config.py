import os
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        extra="ignore",          
        case_sensitive=False     
    )
    
    PROJECT_NAME: str = "Spacer Chat"
    
    # API Config
    OPENAI_API_KEY: str
    OPENAI_BASE_URL: str = "https://openrouter.ai/api/v1"
    MODEL_NAME: str = "openai/gpt-4o-mini"
    EMBEDDING_MODEL: str = "BAAI/bge-m3"
    
    # TiDB Config
    HOST: str
    PORT: int = 4000
    DB_USERNAME: str
    DB_PASSWORD: str
    DATABASE: str = "spacer_chat"
    TABLE_NAME: str = "embedded_documents"
    CA_PATH: str = "isrgrootx1.pem"
    
    @property
    def TIDB_CONNECTION_STRING(self) -> str:
        return (
            f"mysql+pymysql://{self.DB_USERNAME}:{self.DB_PASSWORD}@"
            f"{self.HOST}:{self.PORT}/{self.DATABASE}"
            f"?ssl_ca={self.CA_PATH}&ssl_verify_cert=true&ssl_verify_identity=true"
        )

    # Processing
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

settings = Settings()