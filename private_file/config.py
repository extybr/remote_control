from dataclasses import dataclass
from environs import Env


@dataclass
class SSHConfig:
    host: str
    port: int
    user: str
    password: str
    filename: str


@dataclass
class Config:
    conf: SSHConfig


def load_config(path: str or None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(conf=SSHConfig(
        host=env('HOST'),
        port=env('PORT'),
        user=env('USER'),
        password=env('PASSWORD'),
        filename=env('FILENAME'),
    )
    )
