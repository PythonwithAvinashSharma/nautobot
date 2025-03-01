from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Document, Conversation
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from nautobot.dcim.models import Device
from django.db.models import Q
from dotenv import load_dotenv
import os
import re
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatbotView(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(self):
        try:
            # Initialize embedding model
            self.embedding_model = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                encode_kwargs={'normalize_embeddings': True}
            )
            
            # Load environment variables
            load_dotenv(".env")
            
            # Configure Gemini
            google_api_key = os.getenv('GOOGLE_API_KEY')
            if not google_api_key:
                raise ValueError("Google API key not found")
            
            # Initialize Gemini
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-pro",
                temperature=0.3,
                google_api_key=google_api_key,
                request_timeout=60
            )
            
            # Initialize vector store
            self.setup_vector_store()
            
        except Exception as e:
            logger.error(f"Error initializing ChatbotView: {str(e)}")
            raise

    def setup_vector_store(self):
        """Setup FAISS vector store for document retrieval"""
        try:
            if os.path.exists("vectorstore.faiss"):
                self.vector_store = FAISS.load_local(
                    "vectorstore.faiss",
                    self.embedding_model,
                    allow_dangerous_deserialization=True
                )
                logger.info("Loaded existing vector store")
            else:
                # Load initial documents (e.g., manuals, FAQs, past conversations)
                documents = [
                    "Network troubleshooting guide.",
                    "How to configure Cisco devices?",
                    "Steps to identify faulty routers.",
                    "Latest firmware updates for network devices."
                ]
                self.vector_store = FAISS.from_texts(documents, self.embedding_model)
                self.vector_store.save_local("vectorstore.faiss")
                logger.info("Created new vector store with initial documents")

        except Exception as e:
            logger.error(f"Error setting up vector store: {str(e)}")
            raise

    def retrieve_context(self, user_query):
        """Retrieve relevant context from the FAISS vector store"""
        try:
            results = self.vector_store.similarity_search(user_query, k=3)  # Retrieve top 3 similar docs
            retrieved_docs = "\n".join([doc.page_content for doc in results])
            logger.info(f"Retrieved documents: {retrieved_docs}")
            return retrieved_docs
        except Exception as e:
            logger.error(f"Error retrieving documents from vector store: {str(e)}")
            return "No relevant documents found."

    def extract_query_params(self, message):
        message_lower = message.lower()
        params = {
            'location': None,
            'device_type': None
        }

        # Extract location (handle both "in" and "at")
        location_indicators = ["in", "at"]
        location_match = re.search(r"\b(?:in|at)\s+(\S+)", message_lower)
        if location_match:
            params['location'] = location_match.group(1).strip()
        type_match = re.search(r"type\s+(\S+)\s+(.+)", message_lower)

        # Extract device type
        if "type" in message_lower:
            type_parts = message_lower.split("type")
            if len(type_parts) > 1:
                device_type = type_parts[1].strip()
                type_parts = device_type.split()
                if len(type_parts) >= 2:
                    params['device_type'] = {
                        'manufacturer': type_parts[0],
                        'model': ' '.join(type_parts[1:])
                    }

        return params

    def query_database(self, user_message):
        """Query the database with proper foreign key handling"""
        try:
            # Extract query parameters
            params = self.extract_query_params(user_message)
            logger.info(f"Extracted params: {params}")
            
            # Build query
            query = Q()
            
            # Handle location query correctly
            if params['location']:
                query &= Q(location__name__iexact=params['location'].upper())
                logger.info(f"Querying location: {params['location']}")
            
            # Handle device type query correctly
            if params['device_type']:
                device_type = params['device_type']
                type_query = Q()
                if 'manufacturer' in device_type:
                    type_query &= Q(device_type__manufacturer__name__iexact=device_type['manufacturer'])
                if 'model' in device_type:
                    type_query &= Q(device_type__model__iexact=device_type['model'])
                query &= type_query
                logger.info(f"Querying device type: {device_type}")
            
            # Execute query
            devices = Device.objects.filter(query)
            
            if not devices.exists():
                return (f"No devices found matching your criteria. "
                    f"Location: {params['location'] or 'Not specified'}, "
                    f"Device Type: {params.get('device_type', 'Not specified')}")
            
            # Format response
            response_parts = ["Found the following devices:"]
            
            for device in devices:
                device_info = [
                    f"Name: {device.name or 'Unnamed'}",
                    f"Type: {device.device_type.manufacturer} {device.device_type.model}",
                    f"Status: {device.status}",
                    f"Role: {device.role}"
                ]
                response_parts.append(" | ".join(device_info))
            
            return "\n".join(response_parts)
            
        except Exception as e:
            logger.error(f"Error in query_database: {str(e)}")
            return f"An error occurred while querying the database: {str(e)}"

    def post(self, request):
        start_time = time.time()
        try:
            user_message = request.data.get("message", "")
            session_id = request.data.get("session_id", "default_session")

            if not user_message:
                return Response({"error": "Message cannot be empty", "session_id": session_id}, status=400)

            # Step 1: Retrieve relevant documents using FAISS
            rag_time = time.time()
            retrieved_context = self.retrieve_context(user_message)
            logger.info(f"RAG retrieval took {time.time() - rag_time:.2f} seconds")

            # Step 2: Extract query parameters and query DB if needed
            query_time = time.time()
            db_results_str = self.query_database(user_message)
            logger.info(f"Database query took {time.time() - query_time:.2f} seconds")

            # Step 3: Combine Retrieved Context & DB Data for LLM
            final_prompt = f"""
            You are a network assistant helping with infrastructure-related queries.

            Relevant documents retrieved:
            {retrieved_context}

            Database results (JSON format):
            {db_results_str}

            User's question:
            {user_message}

            Generate a well-structured response, ensuring it's concise and easy to read.
            """

            # Step 4: Get Response from LLM
            try:
                llm_time = time.time()
                response = self.llm.invoke(final_prompt)
                logger.info(f"LLM response took {time.time() - llm_time:.2f} seconds")

                # Convert LLM response into a better structure
                structured_response = {
                    "llm_response": response,
                    "database_results": db_results_str
                }

                # Save conversation history
                Conversation.objects.create(session_id=session_id, message=user_message, response=str(response))

                logger.info(f"Total request processing took {time.time() - start_time:.2f} seconds")
                return Response({"response": final_response, "session_id": session_id})

            except Exception as e:
                logger.error(f"Error generating AI response: {str(e)}")
                return Response({"response": db_results_str, "session_id": session_id})

        except Exception as e:
            logger.error(f"Error in post method: {str(e)}")
            return Response({"error": f"An error occurred: {str(e)}", "session_id": session_id})