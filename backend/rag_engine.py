from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()

class RAGEngine:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=self.api_key
        )
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=self.api_key,
            temperature=0
        )

    def create_vector_store(self, chunks):
        vector_store = FAISS.from_texts(chunks, self.embeddings)
        return vector_store

    def get_qa_chain(self, vector_store, language="en"):
        from langchain_core.runnables import RunnablePassthrough
        from langchain_core.output_parsers import StrOutputParser
        
        prompt_template = """
        You are an intelligent multilingual document assistant.
        Answer the question strictly based on the provided context.
        If the answer is not in the context, respond exactly with:
        "I could not find this information in the uploaded document."
        
        Do not hallucinate or use external knowledge.
        
        Context: {context}
        Question: {question}
        
        Answer in {language}:"""
        
        prompt = ChatPromptTemplate.from_template(prompt_template)
        retriever = vector_store.as_retriever()
        
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
        
        # Creating a chain using LCEL
        rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough(), "language": lambda x: language}
            | prompt
            | self.llm
            | StrOutputParser()
        )
        
        # Wrapper to maintain compatibility with main.py
        class MiniQA:
            def invoke(self, query):
                res = rag_chain.invoke(query)
                return {"result": res}
                
        return MiniQA()

    def get_summary(self, text, style="Detailed Summary", language="en"):
        if not text or len(text.strip()) < 10:
            return "The document appears to be empty or contains too little text to summarize."
            
        print(f"Generating {style} in {language} for document ({len(text)} chars)...")
        
        style_prompts = {
            "Short Summary": "Generate a concise 2-3 sentence summary of the following text.",
            "Detailed Summary": "Generate a well-structured summary with Main Topic, Key Points, Important Insights, and a Final Conclusion.",
            "Bullet Points": "Summarize the following text using clear, informative bullet points.",
            "Explain Like I’m 5": "Explain the following text in very simple terms, as if you were explaining it to a 5-year-old."
        }
        
        # Trim text if it's excessively large for a single prompt
        summarization_text = text[:100000] if len(text) > 100000 else text
        
        prompt = f"""
        {style_prompts.get(style, style_prompts["Detailed Summary"])}
        The summary must be in {language}.
        
        Text:
        {summarization_text}
        
        Summary:"""
        
        try:
            print("Invoking Gemini-Flash for summary...")
            response = self.llm.invoke(prompt)
            print("Summary generation successful.")
            return response.content
        except Exception as e:
            print(f"Summarization error: {str(e)}")
            return f"An error occurred while generating the summary: {str(e)}"
