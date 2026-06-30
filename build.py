import os
import re
import json

def format_inline_markdown(text):
    # Convert code highlights: `code` -> <span class="code-highlight">code</span>
    text = re.sub(r'`([^`\n]+)`', r'<span class="code-highlight">\1</span>', text)
    
    # Convert bold: **text** -> <span class="emphasis-bold">text</span>
    text = re.sub(r'\*\*([^*]+)\*\*', r'<span class="emphasis-bold">\1</span>', text)
    
    # Convert italics: *text* -> <em>text</em>
    text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
    
    return text

def extract_pills(text):
    # Extract [tech-pill: ...] blocks
    pills = []
    matches = re.findall(r'\[tech-pill:\s*([^\]]+)\]', text)
    for m in matches:
        pills.append(m.strip())
    # Remove the [tech-pill: ...] blocks from the text
    text_clean = re.sub(r'\s*\[tech-pill:\s*[^\]]+\]', '', text)
    return text_clean.strip(), pills

def compile_markdown_to_html(body_text, video_url):
    lines = body_text.split('\n')
    output = []
    
    in_code_block = False
    code_block_lang = ""
    code_lines = []
    
    in_list = False
    stack = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # 1. Code Blocks
        if stripped.startswith('```'):
            if in_code_block:
                # Close code block
                code_content = "\n".join(code_lines)
                code_content = code_content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                output.append(f'<pre><code class="language-{code_block_lang}">{code_content}</code></pre>')
                in_code_block = False
                code_lines = []
            else:
                in_code_block = True
                code_block_lang = stripped[3:].strip()
            i += 1
            continue
            
        if in_code_block:
            code_lines.append(line)
            i += 1
            continue
            
        # 2. Custom Container Blocks (:::)
        if stripped.startswith(':::'):
            parts = stripped.split(maxsplit=2)
            if len(parts) > 1:
                # Open container
                container_type = parts[1]
                args = parts[2] if len(parts) > 2 else ""
                
                if in_list:
                    output.append("</ul>")
                    in_list = False
                
                if container_type == 'challenge':
                    output.append('<div class="challenge-solution-card">')
                    output.append('    <div class="card-tag tag-challenge">The Challenge</div>')
                    stack.append('div')
                elif container_type == 'solution':
                    output.append('<div class="challenge-solution-card">')
                    output.append('    <div class="card-tag tag-solution">The Solution</div>')
                    stack.append('div')
                elif container_type == 'refinement':
                    output.append(f'    <div class="card-tag tag-refinement">{args}</div>')
                elif container_type == 'arch-diagram':
                    output.append('<div class="arch-diagram">')
                    stack.append('div')
                elif container_type == 'arch-column':
                    output.append('    <div class="arch-column">')
                    output.append(f'        <h4>{args}</h4>')
                    stack.append('arch-column')
                elif container_type == 'asset-gallery':
                    output.append('<div class="asset-gallery">')
                    stack.append('div')
                elif container_type == 'asset-card':
                    card_parts = args.split(maxsplit=1)
                    img_file = card_parts[0]
                    label = card_parts[1] if len(card_parts) > 1 else ""
                    output.append('    <div class="asset-card">')
                    output.append(f'        <img src="{img_file}" alt="{label}">')
                    output.append(f'        <div class="asset-label">{label}</div>')
                    output.append('    </div>')
                elif container_type == 'node-container':
                    output.append('<div class="node-container">')
                    stack.append('div')
                elif container_type == 'node':
                    is_primary = False
                    node_args = args
                    if node_args.startswith('primary '):
                        is_primary = True
                        node_args = node_args[8:]
                    
                    title_part, val_part = node_args.split('|', 1) if '|' in node_args else (node_args, "")
                    class_attr = 'class="node primary"' if is_primary else 'class="node"'
                    output.append(f'    <div {class_attr}>')
                    output.append(f'        <div class="node-title">{title_part.strip()}</div>')
                    if val_part:
                        output.append(f'        <div class="node-value">{val_part.strip()}</div>')
                    output.append('    </div>')
                elif container_type == 'node-arrow':
                    output.append('    <div class="node-arrow">➔</div>')
                elif container_type == 'node-sub-list':
                    output.append('    <div class="node-sub-list">')
                    stack.append('node-sub-list')
                elif container_type == 'polish-grid':
                    output.append('<div class="polish-grid">')
                    stack.append('div')
                elif container_type == 'polish-card':
                    output.append('    <div class="polish-card">')
                    output.append(f'        <h4>{args}</h4>')
                    stack.append('div')
                elif container_type == 'video-card':
                    v_parts = args.split(maxsplit=1)
                    cover = v_parts[0]
                    v_title = v_parts[1] if len(v_parts) > 1 else ""
                    output.append(f'        <a href="{video_url}" target="_blank" rel="noopener noreferrer" class="video-link-card" style="background-image: linear-gradient(rgba(0, 0, 0, 0.4), rgba(0, 0, 0, 0.4)), url(\'{cover}\');">')
                    output.append('            <div class="play-btn-overlay">')
                    output.append('                <svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>')
                    output.append('            </div>')
                    output.append('            <div class="video-card-title">')
                    output.append(f'                <span>{v_title}</span>')
                    output.append('                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="opacity: 0.8;"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6M15 3h6v6M10 14L21 3"/></svg>')
                    output.append('            </div>')
                    output.append('        </a>')
            else:
                # Close container
                if in_list:
                    output.append("</ul>")
                    in_list = False
                if stack:
                    tag = stack.pop()
                    if tag == 'arch-column':
                        output.append('    </div>')
                    elif tag == 'node-sub-list':
                        output.append('    </div>')
                    else:
                        output.append(f'</{tag}>')
            i += 1
            continue
            
        # Horizontal Rule / Section Divider
        if stripped == '---':
            if in_list:
                output.append("</ul>")
                in_list = False
            output.append('<hr class="section-divider">')
            i += 1
            continue
            
        # 3. Lists
        if stripped.startswith('- ') or stripped.startswith('* '):
            item_text = stripped[2:]
            item_text = format_inline_markdown(item_text)
            
            # Check if we are inside a node-sub-list
            if stack and stack[-1] == 'node-sub-list':
                output.append(f'        <div class="node-sub-item">{item_text}</div>')
            else:
                if not in_list:
                    output.append("<ul>")
                    in_list = True
                
                # Sub-items or teammate items
                if '[Teammate System]' in item_text or '[Teammate]' in item_text:
                    output.append(f'    <li class="sub-item">{item_text}</li>')
                else:
                    output.append(f'    <li>{item_text}</li>')
                
            i += 1
            continue
        elif in_list and stripped == "":
            next_list = False
            for k in range(i+1, len(lines)):
                if lines[k].strip() == "":
                    continue
                if lines[k].strip().startswith('- ') or lines[k].strip().startswith('* '):
                    next_list = True
                break
            if not next_list:
                output.append("</ul>")
                in_list = False
            
        # 4. Headings
        if stripped.startswith('### '):
            h_text = stripped[4:]
            h_text, pills = extract_pills(h_text)
            pills_html = " ".join([f'<span class="tech-pill">{p}</span>' for p in pills])
            output.append(f'<h3>{h_text} {pills_html}</h3>')
            i += 1
            continue
        elif stripped.startswith('## '):
            output.append(f'<h2>{stripped[3:]}</h2>')
            i += 1
            continue
        elif stripped.startswith('# '):
            # We don't render `# Title` in the main body because it is already handled in the hero
            # However, if there are headers like `# 1. Project Vision`, render them as `<h2>` elements to match styles.
            header_content = stripped[2:]
            output.append(f'<h2>{header_content}</h2>')
            i += 1
            continue
            
        # 5. Paragraphs
        if stripped != "":
            para_lines = []
            while i < len(lines) and lines[i].strip() != "" and not lines[i].strip().startswith('```') and not lines[i].strip().startswith(':::') and not lines[i].strip().startswith('- ') and not lines[i].strip().startswith('* ') and not lines[i].strip().startswith('#'):
                para_lines.append(lines[i].strip())
                i += 1
            
            para_text = " ".join(para_lines)
            para_text = format_inline_markdown(para_text)
            output.append(f'<p>\n    {para_text}\n</p>')
            continue
            
        i += 1
        
    return "\n".join(output)

def compile_case_study(md_path, template_html):
    print(f"Compiling {md_path}...")
    with open(md_path, 'r', encoding='utf-8') as f:
        file_content = f.read()
        
    parts = file_content.split('---', 2)
    if len(parts) < 3:
        raise ValueError(f"Invalid format in {md_path}. Ensure it has double '---' enclosing a JSON frontmatter.")
        
    metadata = json.loads(parts[1].strip())
    body_markdown = parts[2].strip()
    
    # Process metadata variables
    title = metadata.get("title", "")
    subtitle = metadata.get("subtitle", "")
    theme = metadata.get("theme", "")
    meta_title = metadata.get("meta_title", "")
    meta_description = metadata.get("meta_description", "")
    cover_image = metadata.get("cover_image", "")
    video_url = metadata.get("video_url", "")
    
    # Title formatting (horns for El Pollo Diablo)
    if title == "EL POLLO DIABLO":
        title_html = '<span class="glitch-text-wrap"><svg class="devil-horn horn-left" viewBox="0 0 50 100"><path d="M 35 75 C 15 55 10 30 20 15 C 25 30 37 50 40 75 Z" fill="currentColor" /></svg>EL POLLO DIABLO<svg class="devil-horn horn-right" viewBox="0 0 50 100"><path d="M 15 75 C 35 55 40 30 30 15 C 25 30 13 50 10 75 Z" fill="currentColor" /></svg></span>'
    else:
        title_html = title
        
    # Generate meta-grid HTML
    meta_items_html = []
    for item in metadata.get("meta_items", []):
        meta_items_html.append(f'''            <div class="meta-item">
                <div class="meta-label">{item.get("label", "")}</div>
                <div class="meta-value">{item.get("value", "")}</div>
            </div>''')
    meta_grid_html = "\n".join(meta_items_html)
    
    # Generate video button HTML if URL is provided
    video_button_html = ""
    if video_url:
        video_button_html = f'''        <a href="{video_url}" target="_blank" rel="noopener noreferrer" class="cs-video-btn">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" style="display:inline-block; vertical-align:middle; margin-right:4px;"><path d="M8 5v14l11-7z"/></svg>
            Watch Gameplay Video
        </a>'''
        
    # Compile body markdown content
    body_content_html = compile_markdown_to_html(body_markdown, video_url)
    
    # Replace placeholders in template
    output_html = template_html
    output_html = output_html.replace("{{ META_TITLE }}", meta_title)
    output_html = output_html.replace("{{ META_DESCRIPTION }}", meta_description)
    output_html = output_html.replace("{{ COVER_IMAGE }}", cover_image)
    output_html = output_html.replace("{{ THEME }}", theme)
    output_html = output_html.replace("{{ TITLE_HTML }}", title_html)
    output_html = output_html.replace("{{ GLITCH_TITLE }}", title)
    output_html = output_html.replace("{{ SUBTITLE }}", subtitle)
    output_html = output_html.replace("{{ META_GRID_HTML }}", meta_grid_html)
    output_html = output_html.replace("{{ VIDEO_BUTTON_HTML }}", video_button_html)
    output_html = output_html.replace("{{ TITLE }}", title)
    output_html = output_html.replace("{{ BODY_CONTENT }}", body_content_html)
    
    # Write output HTML file in the root directory
    filename = os.path.basename(md_path).replace('.md', '.html')
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output_html)
        
    print(f"Generated {filename}")

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(root_dir, 'templates', 'case-study-template.html')
    
    if not os.path.exists(template_path):
        print(f"Error: Template not found at {template_path}")
        return
        
    with open(template_path, 'r', encoding='utf-8') as f:
        template_html = f.read()
        
    case_studies_dir = os.path.join(root_dir, 'case_studies')
    if not os.path.exists(case_studies_dir):
        print(f"Creating case_studies directory at {case_studies_dir}")
        os.makedirs(case_studies_dir)
        return
        
    compiled_any = False
    for filename in os.listdir(case_studies_dir):
        if filename.endswith('.md'):
            md_path = os.path.join(case_studies_dir, filename)
            try:
                compile_case_study(md_path, template_html)
                compiled_any = True
            except Exception as e:
                print(f"Error compiling {filename}: {e}")
                
    if not compiled_any:
        print("No markdown files found in case_studies/ folder to compile.")

if __name__ == '__main__':
    main()
