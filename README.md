# CompareWise: Amazon Product Comparison Tool

CompareWise leverages advanced AI to revolutionize the way you compare Amazon products, delivering insights at the click of a button.

## Technologies Used

- **API**: Axesso Amazon Data Service for fetching product details.
- **RAG App & LLM Powered Assistant**: Utilizes the LLaMA Index and OpenAI's GPT-3.5-turbo for generating conversational AI responses.
- **Data Analytics/Visualization**: Employs Pandas for data manipulation and Streamlit for interactive data visualization.

## Problem Statement

In the vast ocean of products available on Amazon, finding the right product that meets all your criteria can be daunting. CompareWise aims to simplify this process by providing a detailed comparison between two products, based on their features, reviews, prices, and more, all through an intuitive AI-powered chat interface.

## How to Run

1. Ensure Python 3.8+ is installed.
2. Clone the repository and navigate into the project directory.
3. To run this app, follow these steps in your terminal:
```bash
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
streamlit run app.py
```
## Reflections

Developing CompareWise was both challenging and rewarding. It offered a hands-on experience with integrating various technologies to solve a real-world problem, emphasizing the power of AI in enhancing user experience.

### What I Learned

- Advanced API integration and data extraction techniques.
- The intricacies of developing a chatbot with state-of-the-art language models.
- Effective data visualization and UI design with Streamlit.

### Challenges Faced

- **JSON File Engine**: Navigating the complexities of loading and parsing JSON data for product details.
- **Multi-document Query**: Implementing an efficient way to query and compare data from multiple product documents within the chat interface.

CompareWise is not just a tool; it's a step towards making informed purchasing decisions easier and more accessible to everyone.

