
from __future__ import annotations
from shared.domain import SessionID 
from shared.domain import AudioChunk




class ASRSession:
    def __init__(self, session_id: SessionID, language: str) -> None:
        self.session_id = session_id
        self.language = language
        self._buffer: bytearray = bytearray()
        self.nombre_chunks_recus = 0

    def ajouter_chunk(self, chunk: AudioChunk) -> None:
        self._buffer.extend(chunk.data)
        self.nombre_chunks_recus += 1

    def obtenir_buffer(self) -> bytes:
        return bytes(self._buffer)

    def reinitialiser_buffer(self) -> None:
        self._buffer = bytearray()
        self.nombre_chunks_recus = 0