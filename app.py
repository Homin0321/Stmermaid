import html
import os
import re

import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
from google import genai
from streamlit_paste_button import paste_image_button

load_dotenv()
st.set_page_config(layout="wide", page_title="Stmermaid")

# --- 1. Constants & Default Data ---
MODEL_OPTIONS = [
    "gemini-3-flash-preview",
    "gemini-3.1-pro-preview",
]

DEFAULT_DIAGRAM = """flowchart LR
    A[Hard edge] -->|Link text| B(Round edge)
    B --> C{Decision}
    C -->|One| D[Result one]
    C -->|Two| E[Result two]
"""

INITIAL_FRONTMATTER = "---\nconfig:\n  theme: default\n  look: classic\n  layout: dagre\n  flowchart:\n    curve: basis\n---\n"

# --- 2. Session State Initialization ---
# We initialize these only once to prevent resets during reruns
if "mermaid_code" not in st.session_state:
    st.session_state.mermaid_code = f"{INITIAL_FRONTMATTER}{DEFAULT_DIAGRAM}"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "config_theme" not in st.session_state:
    st.session_state.config_theme = "default"

if "config_look" not in st.session_state:
    st.session_state.config_look = "classic"

if "config_layout" not in st.session_state:
    st.session_state.config_layout = "dagre"

if "config_curve" not in st.session_state:
    st.session_state.config_curve = "basis"


# --- 3. Helper Functions ---
def update_code_from_sidebar():
    """Update the mermaid code based on sidebar inputs, preserving the diagram body."""
    current_code = st.session_state.mermaid_code
    frontmatter_pattern = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
    match = frontmatter_pattern.match(current_code)

    if match:
        body = current_code[match.end() :]
    else:
        body = current_code

    new_frontmatter = "---\nconfig:\n"
    new_frontmatter += f"  theme: {st.session_state.config_theme}\n"
    new_frontmatter += f"  look: {st.session_state.config_look}\n"
    new_frontmatter += f"  layout: {st.session_state.config_layout}\n"
    new_frontmatter += "  flowchart:\n"
    new_frontmatter += f"    curve: {st.session_state.config_curve}\n"
    new_frontmatter += "---\n"

    st.session_state.mermaid_code = new_frontmatter + body


def clear_chat():
    """Callback for New Chat button to clear messages without resetting the diagram."""
    st.session_state.messages = []


# --- 4. Sidebar UI ---
st.sidebar.title("Stmermaid AI Editor")

# Layout adjustment - Using a key ensures this survives reruns
editor_width_ratio = st.sidebar.slider(
    "Editor Width",
    min_value=1,
    max_value=9,
    value=4,
    help="Adjust the width of the editor column relative to the preview column (Total: 10).",
    key="editor_width_slider",
)
col1_width = editor_width_ratio
col2_width = 10 - col1_width

# Settings Expander
with st.sidebar.expander("Diagram Configuration", expanded=False):
    st.selectbox(
        "Select Mermaid Theme",
        options=["default", "neutral", "dark", "forest", "base"],
        key="config_theme",
        on_change=update_code_from_sidebar,
    )

    st.selectbox(
        "Select Mermaid Look",
        options=["classic", "handDrawn"],
        key="config_look",
        on_change=update_code_from_sidebar,
    )

    st.selectbox(
        "Layout Engine",
        options=["dagre", "elk"],
        key="config_layout",
        on_change=update_code_from_sidebar,
    )

    st.selectbox(
        "Edge Curve (Flowchart)",
        options=["basis", "step", "linear", "natural"],
        key="config_curve",
        on_change=update_code_from_sidebar,
    )

st.sidebar.selectbox(
    "Select Model", options=MODEL_OPTIONS, index=0, key="selected_model"
)

# --- Image to Diagram Feature & Chat Controls ---
with st.sidebar:
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        paste_result = paste_image_button(
            label="Paste Image",
            background_color="#C0C0C0",
            hover_background_color="#666666",
            errors="ignore",
            key="paste_image_btn",
        )
    with btn_col2:
        st.button("New Chat", use_container_width=True, on_click=clear_chat)

if paste_result.image_data is not None:
    st.sidebar.image(
        paste_result.image_data,
        caption="Pasted Diagram Image",
        use_container_width=True,
    )
    if st.sidebar.button("Convert to Diagram", use_container_width=True):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            st.sidebar.error("Please set GEMINI_API_KEY in your .env file.")
        else:
            with st.sidebar.status("AI is analyzing the image..."):
                try:
                    client = genai.Client(api_key=api_key)
                    system_prompt = (
                        "You are a Mermaid.js expert. Your task is to extract the diagram from the provided image and generate the corresponding Mermaid diagram code.\n"
                        "Instructions:\n"
                        "1. Analyze the structure, nodes, connections, text, and overall flow in the diagram image.\n"
                        "2. Provide the complete, accurate Mermaid code inside a markdown code block starting with ```mermaid.\n"
                        "3. Ensure the code is valid syntax.\n"
                        "4. Do not include extra explanation outside the code block unless necessary."
                    )

                    contents = [
                        "Please carefully convert this diagram image into Mermaid.js code.",
                        paste_result.image_data,
                    ]

                    response = client.models.generate_content(
                        model=st.session_state.selected_model,
                        contents=contents,
                        config={"system_instruction": system_prompt},
                    )

                    full_response = response.text
                    mermaid_pattern = re.compile(r"```mermaid\n(.*?)\n```", re.DOTALL)
                    match = mermaid_pattern.search(full_response)

                    if match:
                        generated_code = match.group(1).strip()
                        chat_display_text = mermaid_pattern.sub(
                            "", full_response
                        ).strip()

                        # Preserve current style configurations via frontmatter
                        new_frontmatter = "---\nconfig:\n"
                        new_frontmatter += f"  theme: {st.session_state.config_theme}\n"
                        new_frontmatter += f"  look: {st.session_state.config_look}\n"
                        new_frontmatter += (
                            f"  layout: {st.session_state.config_layout}\n"
                        )
                        new_frontmatter += "  flowchart:\n"
                        new_frontmatter += (
                            f"    curve: {st.session_state.config_curve}\n"
                        )
                        new_frontmatter += "---\n"

                        st.session_state.mermaid_code = new_frontmatter + generated_code
                    else:
                        chat_display_text = full_response

                    st.session_state.messages.append(
                        {
                            "role": "user",
                            "content": "🖼️ Uploaded an image for diagram conversion.",
                        }
                    )
                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": "I have extracted the diagram from the image.\n\n"
                            + chat_display_text,
                        }
                    )
                    st.rerun()

                except Exception as e:
                    st.sidebar.error(f"Error calling Gemini API: {e}")


# Chat History
st.sidebar.subheader("AI Assistant")
chat_container = st.sidebar.container(height=250)
for message in st.session_state.messages:
    with chat_container.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input & Logic
if prompt := st.sidebar.chat_input("Ask for changes..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with chat_container.chat_message("user"):
        st.markdown(prompt)

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.sidebar.error("Please set GEMINI_API_KEY in your .env file.")
    else:
        with st.sidebar.status("AI is thinking..."):
            try:
                client = genai.Client(api_key=api_key)
                system_prompt = (
                    "You are a Mermaid.js expert. Your task is to generate or modify Mermaid diagram code based on user requests.\n"
                    "Instructions:\n"
                    "1. Briefly explain what you changed or created.\n"
                    "2. Provide the complete, updated Mermaid code inside a markdown code block starting with ```mermaid.\n"
                    "3. Ensure the code is valid and includes requested changes.\n"
                    "4. Preserve YAML frontmatter if present, unless asked to change it."
                )

                history_context = "\n".join(
                    [f"{m['role']}: {m['content']}" for m in st.session_state.messages]
                )
                user_content = f"Current Mermaid Code:\n{st.session_state.mermaid_code}\n\nRecent History:\n{history_context}\n\nUser Request: {prompt}"

                response = client.models.generate_content(
                    model=st.session_state.selected_model,
                    contents=user_content,
                    config={"system_instruction": system_prompt},
                )

                full_response = response.text
                mermaid_pattern = re.compile(r"```mermaid\n(.*?)\n```", re.DOTALL)
                match = mermaid_pattern.search(full_response)

                if match:
                    generated_code = match.group(1).strip()
                    chat_display_text = mermaid_pattern.sub("", full_response).strip()
                    st.session_state.mermaid_code = generated_code
                else:
                    chat_display_text = full_response

                st.session_state.messages.append(
                    {"role": "assistant", "content": chat_display_text}
                )
                st.rerun()

            except Exception as e:
                st.sidebar.error(f"Error calling Gemini API: {e}")

# Footer link in sidebar
st.sidebar.markdown("[Mermaid Documentation](https://mermaid.js.org/intro/)")

# --- 5. Main Content ---
col1, col2 = st.columns([col1_width, col2_width])

with col1:
    # Text area bound to mermaid_code session state
    st.text_area(
        "Mermaid Code Input",
        key="mermaid_code",
        height=800,
        label_visibility="collapsed",
    )

with col2:
    final_code = st.session_state.mermaid_code

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{ margin: 0; font-family: sans-serif; position: relative; }}
        #error {{
            color: #721c24;
            background-color: #f8d7da;
            border-color: #f5c6cb;
            padding: .75rem 1.25rem;
            margin-bottom: 1rem;
            border: 1px solid transparent;
            border-radius: .25rem;
            font-family: monospace;
            white-space: pre-wrap;
            display: none;
        }}
        .header-container {{
            display: flex;
            justify-content: flex-end;
            padding: 10px;
            min-height: 28px;
        }}
        #download-btn {{
            padding: 6px 12px;
            background-color: #C0C0C0;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            display: none;
            opacity: 0.6;
            transition: opacity 0.2s;
        }}
        #download-btn:hover {{
            opacity: 1;
        }}
    </style>
    </head>
    <body>

    <div class="header-container">
        <button id="download-btn">Download SVG</button>
    </div>
    <div id="error"></div>
    <pre class="mermaid" id="mermaid-graph">{html.escape(final_code)}</pre>

    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';

        mermaid.initialize({{
            startOnLoad: false,
            suppressErrorRendering: true
        }});

        const element = document.getElementById('mermaid-graph');
        const errorElement = document.getElementById('error');
        const downloadBtn = document.getElementById('download-btn');

        async function renderDiagram() {{
            try {{
                const code = element.textContent;
                await mermaid.parse(code);
                await mermaid.run({{ nodes: [element] }});
                errorElement.style.display = 'none';
                downloadBtn.style.display = 'block';
            }} catch (error) {{
                console.error('Mermaid Error:', error);
                element.innerHTML = '';
                errorElement.textContent = error.str || error.message || 'Syntax Error';
                errorElement.style.display = 'block';
                downloadBtn.style.display = 'none';
            }}
        }}

        downloadBtn.addEventListener('click', () => {{
            const svg = element.querySelector('svg');
            if (!svg) return;

            const serializer = new XMLSerializer();
            let source = serializer.serializeToString(svg);

            if(!source.includes('xmlns="http://www.w3.org/2000/svg"')){{
                source = source.replace(/^<svg/, '<svg xmlns="http://www.w3.org/2000/svg"');
            }}
            if(!source.includes('xmlns:xlink="http://www.w3.org/1999/xlink"')){{
                source = source.replace(/^<svg/, '<svg xmlns:xlink="http://www.w3.org/1999/xlink"');
            }}

            source = '<?xml version="1.0" standalone="no"?>\\r\\n' + source;
            const url = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(source);

            const downloadLink = document.createElement("a");
            downloadLink.href = url;
            downloadLink.download = "mermaid-diagram.svg";
            document.body.appendChild(downloadLink);
            downloadLink.click();
            document.body.removeChild(downloadLink);
        }});

        renderDiagram();
    </script>
    </body>
    </html>
    """

    components.html(html_code, height=800, scrolling=True)
