from dotenv import load_dotenv
import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from langchain.callbacks import get_openai_callback


def main():
   
    st.set_page_config(page_title="Ask your PDF")

     # Set a header logo with a PNG file
    # st.image("path/to/your/logo.png", width=200)  # Replace with the path to your logo file
    st.image("./cuboulder.png")

    st.header("Ask your PDF 💬")

    
   
    

    # upload file
    pdf = st.file_uploader("Upload your PDF", type="pdf")
    
    # check for file format, if not pdf show error message
    if pdf is not None:
      pdf_reader = PdfReader(pdf)
      text = ""
      for page in pdf_reader.pages:
        text += page.extract_text()
    
      st.write(text[:100])
  
      # show user input
      user_question = st.text_input("Ask a question about your PDF:")
      if user_question:
        print(user_question)
        response = user_question.upper()
           
        st.write(response)
    

if __name__ == '__main__':
    main()
