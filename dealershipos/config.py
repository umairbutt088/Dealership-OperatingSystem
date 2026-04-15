from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DEALERSHIP_", env_file=".env", extra="ignore")

    data_dir: Path = Path(__file__).resolve().parent.parent / "data"
    database_url: str = "sqlite:///./data/dealershipos.db"
    bootstrap_from_asset: bool = True
    cars_subdir: str = "Cars"
    investors_subdir: str = "Investors"
    invoices_subdir: str = "Invoices"

    @property
    def sqlite_path(self) -> Path:
        if self.database_url.startswith("sqlite:///./"):
            return (Path(__file__).resolve().parent.parent / self.database_url.replace("sqlite:///./", "")).resolve()
        if self.database_url.startswith("sqlite:////"):
            return Path(self.database_url.replace("sqlite:////", "/"))
        return self.data_dir / "dealershipos.db"

    @property
    def cars_base(self) -> Path:
        return self.data_dir / self.cars_subdir

    @property
    def investors_base(self) -> Path:
        return self.data_dir / self.investors_subdir

    @property
    def invoices_base(self) -> Path:
        return self.data_dir / self.invoices_subdir


settings = Settings()
