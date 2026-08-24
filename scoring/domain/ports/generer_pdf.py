from abc import ABC, abstractmethod

class GenererPDF(ABC):

    @abstractmethod
    async def generer_pdf(self , session_id : str) :
        ...


