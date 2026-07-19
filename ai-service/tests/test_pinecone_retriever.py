import unittest
from unittest.mock import MagicMock, patch
from app.rag.retriever import KnowledgeRetriever
from app.retrievers.faiss_retriever import FAISSRetriever
from app.retrievers.pinecone_retriever import PineconeRetriever

class TestPineconeRetrieverSwitch(unittest.TestCase):
    @patch("app.core.config.VECTOR_STORE", "faiss")
    def test_selects_faiss_retriever_by_default(self):
        retriever = KnowledgeRetriever()
        self.assertEqual(retriever.vector_store_type, "faiss")
        self.assertIsInstance(retriever.active_retriever, FAISSRetriever)

    @patch("app.core.config.VECTOR_STORE", "pinecone")
    @patch("app.services.pinecone_service.PineconeService.initialize", return_value=True)
    def test_selects_pinecone_retriever_when_configured(self, mock_init):
        retriever = KnowledgeRetriever()
        self.assertEqual(retriever.vector_store_type, "pinecone")
        self.assertIsInstance(retriever.active_retriever, PineconeRetriever)

    @patch("app.core.config.VECTOR_STORE", "pinecone")
    @patch("app.services.pinecone_service.PineconeService.query_vectors")
    @patch("app.rag.embedding.EmbeddingEngine.get_query_embedding")
    @patch("app.services.pinecone_service.PineconeService.initialize", return_value=True)
    def test_pinecone_retrieval_formatting(self, mock_init, mock_embed, mock_query):
        mock_embed.return_value = [0.1] * 384
        mock_query.return_value = [
            {
                "id": "chunk-001",
                "score": 0.85,
                "metadata": {
                    "text": "Cook the paneer cubes.",
                    "source": "recipes",
                    "title": "Paneer Butter Masala",
                    "chunk_id": "chunk-001"
                }
            }
        ]
        
        retriever = KnowledgeRetriever()
        chunks = retriever.retrieve("paneer")
        
        self.assertEqual(len(chunks), 1)
        chunk = chunks[0]
        self.assertEqual(chunk["chunk_id"], "chunk-001")
        self.assertEqual(chunk["source"], "recipes")
        self.assertEqual(chunk["title"], "Paneer Butter Masala")
        self.assertEqual(chunk["content"], "Cook the paneer cubes.")
        self.assertEqual(chunk["score"], 0.8500)
