from rag.pipeline import RagPipeline
from rag.prompts import CHAT_SYSTEM, CHAT_USER_TEMPLATE
from tools.lmstudio_client import chat_completion
import config

class ChatAgent:
    def __init__(self):
        self.pipeline = RagPipeline()

    def answer(self, question: str):
        context, hits = self.pipeline.build_context(question, config.TOP_K)
        user_msg = CHAT_USER_TEMPLATE.format(
            question=question, 
            context=context or "(sin contexto disponible)"
        )
        answer = chat_completion(CHAT_SYSTEM, user_msg)
        refs = [
            {"titulo": h["titulo"], "categoria": h["categoria"], "sheet": h["sheet"], "score": h["score"]}
            for h in hits
        ]
        return {"answer": answer, "references": refs}
    
    def answer_with_memory(self, question: str, memory_summary: str = ""):
        context, hits = self.pipeline.build_context(question, memory_summary, config.TOP_K)
        user_msg = CHAT_USER_TEMPLATE.format(question=question, context=context or "(sin contexto)")
        answer = chat_completion(CHAT_SYSTEM, user_msg)
        refs = [{"titulo": h["titulo"], "categoria": h["categoria"], "sheet": h["sheet"], "score": h["score"]} for h in hits]
        return {"answer": answer, "references": refs}
