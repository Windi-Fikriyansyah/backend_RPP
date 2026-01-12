import httpx
from io import BytesIO
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
import math
import urllib.parse

class PPTService:
    THEMES = {
        "Ceria": {
            "primary": "#FF9F43",
            "secondary": "#FECA57",
            "accent": "#FF6B6B",
            "text": "#2D3436",
            "bg": "#FFFFFF"
        },
        "Formal": {
            "primary": "#2E86DE",
            "secondary": "#54A0FF",
            "accent": "#222F3E",
            "text": "#2D3436",
            "bg": "#FFFFFF"
        },
        "Alam": {
            "primary": "#10AC84",
            "secondary": "#1DD1A1",
            "accent": "#006266",
            "text": "#2D3436",
            "bg": "#FFFFFF"
        },
        "Pastel": {
            "primary": "#FF9FF3",
            "secondary": "#FDCB6E",
            "accent": "#A29BFE",
            "text": "#2D3436",
            "bg": "#F9F9F9"
        }
    }

    @staticmethod
    def hex_to_rgb(hex_code):
        hex_code = hex_code.lstrip('#')
        return RGBColor(*(int(hex_code[i:i+2], 16) for i in (0, 2, 4)))

    @staticmethod
    def add_decorations(slide, theme_colors):
        # Top-right accent circle
        circle = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(9), Inches(-0.5), Inches(1.5), Inches(1.5))
        circle.fill.solid()
        circle.fill.fore_color.rgb = theme_colors["secondary"]
        circle.line.fill.background()

        # Bottom-left accent line
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(-0.2), Inches(7.2), Inches(3), Inches(0.1))
        line.fill.solid()
        line.fill.fore_color.rgb = theme_colors["primary"]
        line.line.fill.background()

    @staticmethod
    def auto_fit_text(text_frame, max_font_size=24, min_font_size=12):
        # Simple auto-shrink logic
        char_count = sum(len(p.text) for p in text_frame.paragraphs)
        if char_count > 200:
            size = min_font_size
        elif char_count > 100:
            size = max_font_size - 6
        else:
            size = max_font_size
        
        for p in text_frame.paragraphs:
            p.font.size = Pt(size)

    @classmethod
    async def generate_ppt(cls, json_data: dict) -> BytesIO:
        prs = Presentation()
        prs.slide_width = Inches(10)
        prs.slide_height = Inches(7.5)
        
        theme_name = json_data.get("theme", "Formal")
        theme = cls.THEMES.get(theme_name, cls.THEMES["Formal"])
        colors = {k: cls.hex_to_rgb(v) for k, v in theme.items()}

        # 1. Title Slide
        slide_layout = prs.slide_layouts[6] # Blank
        slide = prs.slides.add_slide(slide_layout)
        
        # Background color for title slide
        background = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        background.fill.solid()
        background.fill.fore_color.rgb = colors["primary"]
        background.line.fill.background()

        # Title
        title_box = slide.shapes.add_textbox(Inches(1), Inches(2.5), Inches(8), Inches(2))
        tf = title_box.text_frame
        p = tf.paragraphs[0]
        p.text = json_data.get("judul_materi", "Materi Ajar").upper()
        p.font.bold = True
        p.font.size = Pt(44)
        p.font.color.rgb = RGBColor(255, 255, 255)
        p.alignment = PP_ALIGN.CENTER

        # 2. Content Slides
        for i, slide_info in enumerate(json_data.get("slides", [])):
            layout_type = slide_info.get("layout_type", "split")
            slide = prs.slides.add_slide(prs.slide_layouts[6]) # Blank
            cls.add_decorations(slide, colors)

            if layout_type == "highlight":
                # Solid Primary BG
                bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
                bg.fill.solid()
                bg.fill.fore_color.rgb = colors["primary"]
                bg.line.fill.background()

                text_box = slide.shapes.add_textbox(Inches(1), Inches(2.5), Inches(8), Inches(3))
                tf = text_box.text_frame
                tf.word_wrap = True
                p = tf.paragraphs[0]
                p.text = slide_info.get("judul_slide", "")
                p.font.bold = True
                p.font.size = Pt(48)
                p.font.color.rgb = RGBColor(255, 255, 255)
                p.alignment = PP_ALIGN.CENTER

            elif layout_type == "big_image":
                keyword = slide_info.get("keyword_visual", "education")
                encoded_keyword = urllib.parse.quote(keyword)
                img_url = f"https://loremflickr.com/1280/960/{encoded_keyword}"
                fallback_url = f"https://picsum.photos/1280/960"
                
                try:
                    print(f"DEBUG: Fetching Big Image for keyword: {keyword}")
                    async with httpx.AsyncClient() as client:
                        # Try primary
                        response = await client.get(img_url, timeout=15, follow_redirects=True)
                        if response.status_code != 200:
                            print(f"DEBUG: Primary image failed ({response.status_code}), trying fallback...")
                            response = await client.get(fallback_url, timeout=15, follow_redirects=True)
                        
                        print(f"DEBUG: Big Image Response Status: {response.status_code}")
                        if response.status_code == 200:
                            img_bytes = BytesIO(response.content)
                            slide.shapes.add_picture(img_bytes, 0, 0, width=prs.slide_width)
                        else:
                            print(f"DEBUG: Failed to fetch Big Image even with fallback. Status: {response.status_code}")
                except Exception as img_err:
                    print(f"DEBUG: Error fetching Big Image: {img_err}")

                # Translucent overlay
                overlay = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(5), prs.slide_width, Inches(2.5))
                overlay.fill.solid()
                overlay.fill.fore_color.rgb = RGBColor(0, 0, 0)
                # Note: python-pptx doesn't support alpha easily, but we can use a dark fill
                
                text_box = slide.shapes.add_textbox(Inches(0.5), Inches(5.2), Inches(9), Inches(2))
                tf = text_box.text_frame
                p = tf.paragraphs[0]
                p.text = slide_info.get("judul_slide", "")
                p.font.bold = True
                p.font.size = Pt(32)
                p.font.color.rgb = RGBColor(255, 255, 255)

            else: # split (default)
                # Left: Text
                title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.5), Inches(5), Inches(1))
                t_tf = title_box.text_frame
                t_p = t_tf.paragraphs[0]
                t_p.text = slide_info.get("judul_slide", "Slide")
                t_p.font.bold = True
                t_p.font.size = Pt(32)
                t_p.font.color.rgb = colors["primary"]

                content_box = slide.shapes.add_textbox(Inches(0.5), Inches(1.5), Inches(4.5), Inches(5))
                tf = content_box.text_frame
                tf.word_wrap = True
                
                for point in slide_info.get("konten", []):
                    p = tf.add_paragraph()
                    p.text = f"• {point}"
                    p.font.color.rgb = colors["text"]
                    p.space_after = Pt(12)
                
                cls.auto_fit_text(tf)

                # Right: Image
                keyword = slide_info.get("keyword_visual", "education")
                encoded_keyword = urllib.parse.quote(keyword)
                img_url = f"https://loremflickr.com/800/800/{encoded_keyword}"
                fallback_url = f"https://picsum.photos/800/800"
                try:
                    print(f"DEBUG: Fetching Split Image for keyword: {keyword}")
                    async with httpx.AsyncClient() as client:
                        response = await client.get(img_url, timeout=15, follow_redirects=True)
                        if response.status_code != 200:
                            print(f"DEBUG: Primary image failed ({response.status_code}), trying fallback...")
                            response = await client.get(fallback_url, timeout=15, follow_redirects=True)

                        print(f"DEBUG: Split Image Response Status: {response.status_code}")
                        if response.status_code == 200:
                            img_bytes = BytesIO(response.content)
                            # Add picture and maintain aspect ratio roughly
                            slide.shapes.add_picture(img_bytes, Inches(5.5), Inches(1.5), width=Inches(4))
                        else:
                            print(f"DEBUG: Failed to fetch Split Image even with fallback. Status: {response.status_code}")
                except Exception as img_err:
                    print(f"DEBUG: Error fetching Split Image: {img_err}")

        # Save to memory
        ppt_output = BytesIO()
        prs.save(ppt_output)
        ppt_output.seek(0)
        return ppt_output
