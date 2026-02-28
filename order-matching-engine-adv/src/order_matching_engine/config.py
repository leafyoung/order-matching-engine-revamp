from dataclasses import dataclass


@dataclass
class EngineConfig:
    cache_length: int = 15
    eq_price: float = 200.0
    std_dev: float = 25.0
