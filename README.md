# Stmermaid AI Editor

Stmermaid is a powerful, AI-driven Mermaid.js diagram editor built with Streamlit and powered by Google Gemini AI. It allows users to create, modify, and preview Mermaid diagrams through natural language instructions or manual editing.

## Features

- **AI-Powered Generation**: Simply describe the diagram you want, and the Gemini AI will generate the Mermaid code for you.
- **Image-to-Diagram Conversion**: Paste an image of a diagram from your clipboard, and the AI will analyze it to generate the corresponding Mermaid.js code.
- **Iterative Refinement**: Chat with the AI assistant to modify existing diagrams (e.g., "Add a new node", "Change the layout", "Make it more complex").
- **Live Preview**: Real-time rendering of Mermaid diagrams.
- **Configuration Sidebar**:
    - Adjust editor width.
    - Change Mermaid themes (default, neutral, dark, forest, base).
    - Toggle between classic and hand-drawn looks.
    - Switch layout engines (dagre, elk).
    - Customize edge curves (basis, step, linear, natural).
- **Export**: Download your generated diagrams as high-quality SVG files.
- **Manual Editor**: Direct access to the Mermaid code for fine-tuning.

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd stmermaid
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up your Environment Variables:
   Create a `.env` file in the root directory and add your Google Gemini API Key:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```

## Usage

Run the Streamlit application:
```bash
streamlit run app.py
```

## Technologies

- [Streamlit](https://streamlit.io/)
- [Mermaid.js](https://mermaid.js.org/)
- [Google Gemini API](https://ai.google.dev/)
- [python-dotenv](https://github.com/theskumar/python-dotenv)
- [streamlit-paste-button](https://github.com/ohtaman/streamlit-paste-button)