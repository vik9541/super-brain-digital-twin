#!/usr/bin/env python3
"""Report Generator - Генератор визуальных HTML отчетов по результатам аудита"""
import argparse, json, sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 Copilot Agent Audit Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white;
                      border-radius: 16px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); padding: 40px; }}
        h1 {{ color: #2d3748; font-size: 2.5em; margin-bottom: 10px; }}
        .meta {{ color: #718096; margin-bottom: 30px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                 gap: 20px; margin: 30px 0; }}
        .stat-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                     color: white; padding: 20px; border-radius: 12px; text-align: center; }}
        .stat-number {{ font-size: 2.5em; font-weight: bold; margin: 10px 0; }}
        .model-section {{ background: #f7fafc; padding: 25px; border-radius: 12px;
                         margin: 20px 0; border-left: 4px solid #667eea; }}
        .finding {{ background: white; padding: 15px; margin: 10px 0; border-radius: 8px;
                   border-left: 4px solid #f56565; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .finding.error {{ border-color: #f56565; }}
        .finding.warning {{ border-color: #ed8936; }}
        .finding.info {{ border-color: #4299e1; }}
        .badge {{ display: inline-block; padding: 4px 12px; border-radius: 12px;
                 font-size: 0.85em; font-weight: 600; margin-right: 8px; }}
        .badge.error {{ background: #fed7d7; color: #c53030; }}
        .badge.warning {{ background: #feebc8; color: #c05621; }}
        .badge.info {{ background: #bee3f8; color: #2c5282; }}
        footer {{ text-align: center; margin-top: 40px; color: #a0aec0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 GitHub Copilot Agent - Отчет по аудиту</h1>
        <div class="meta">
            <p>📅 {timestamp}</p>
            <p>📊 Режим: {mode} | 📁 Файлов: {files_count}</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div>🔴 Критичные</div>
                <div class="stat-number">{critical}</div>
            </div>
            <div class="stat-card">
                <div>🟠 Ошибки</div>
                <div class="stat-number">{errors}</div>
            </div>
            <div class="stat-card">
                <div>🟡 Предупреждения</div>
                <div class="stat-number">{warnings}</div>
            </div>
        </div>
        
        {models_html}
        
        <footer>
            <p>Сгенерировано GitHub Copilot Agent Runner v1.0</p>
        </footer>
    </div>
</body>
</html>
'''

def generate_html_report(results: Dict, output_path: str = 'audit-report.html'):
    """HTML отчет с визуализацией"""
    critical = errors = warnings = 0
    models_html = ''
    
    for model in results.get('models', []):
        model_name = model.get('model', 'Unknown')
        findings = model.get('findings', [])
        
        models_html += f'<div class="model-section"><h2>🧠 {model_name}</h2>'
        
        if isinstance(findings, list):
            for finding in findings:
                if isinstance(finding, dict):
                    severity = 'info'
                    if 'error' in str(finding).lower(): 
                        severity = 'error'
                        errors += 1
                    elif 'warning' in str(finding).lower(): 
                        severity = 'warning'
                        warnings += 1
                    
                    models_html += f'''<div class="finding {severity}">
                        <span class="badge {severity}">{severity.upper()}</span>
                        <strong>{finding.get('file', 'N/A')}</strong>
                        <p>{finding.get('analysis', str(finding))[:200]}...</p>
                    </div>'''
        
        if model.get('error'):
            models_html += f'<div class="finding error">❌ Error: {model["error"]}</div>'
        
        models_html += '</div>'
    
    html = HTML_TEMPLATE.format(
        timestamp=results.get('timestamp', datetime.now().isoformat()),
        mode=results.get('mode', 'full'),
        files_count=results.get('files_count', 0),
        critical=critical,
        errors=errors,
        warnings=warnings,
        models_html=models_html
    )
    
    Path(output_path).write_text(html, encoding='utf-8')
    print(f'✅ Отчет сохранен: {output_path}')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True, help='JSON results file')
    parser.add_argument('--output', default='audit-report.html')
    parser.add_argument('--format', default='html', choices=['html', 'markdown'])
    args = parser.parse_args()
    
    with open(args.input) as f:
        results = json.load(f)
    
    if args.format == 'html':
        generate_html_report(results, args.output)
    else:
        print(f'⚠️ Format {args.format} not yet implemented')

if __name__ == '__main__':
    main()
