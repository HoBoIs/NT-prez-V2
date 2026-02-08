
from dataclasses import dataclass
@dataclass 
class mediaInfo:
    duration: float | None = None
    startTime: float | None = None
    isPlaying: bool = False
