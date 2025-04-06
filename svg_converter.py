import streamlit as st
import base64
from io import BytesIO

class SVGConverter:
    @staticmethod
    def display_svg(svg_content):
        """
        Display SVG content in Streamlit with proper styling
        """
        # Add custom CSS for SVG container
        st.markdown("""
            <style>
            .svg-container {
                background-color: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin: 10px 0;
            }
            .svg-container svg {
                max-width: 100%;
                height: auto;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Wrap SVG in a container with custom styling
        svg_html = f"""
        <div class="svg-container">
            {svg_content}
        </div>
        """
        st.markdown(svg_html, unsafe_allow_html=True)
    
    @staticmethod
    def svg_to_base64(svg_content):
        """
        Convert SVG content to base64 for embedding in HTML
        """
        svg_bytes = svg_content.encode('utf-8')
        b64 = base64.b64encode(svg_bytes).decode('utf-8')
        return f"data:image/svg+xml;base64,{b64}"
    
    @staticmethod
    def create_interactive_svg(svg_content, click_handler=None):
        """
        Create an interactive SVG with click handlers
        """
        if click_handler:
            # Add JavaScript for click handling
            js_code = f"""
            <script>
                document.querySelectorAll('.interactive-element').forEach(element => {{
                    element.addEventListener('click', function(e) {{
                        {click_handler}
                    }});
                }});
            </script>
            """
            return f"{svg_content}{js_code}"
        return svg_content 