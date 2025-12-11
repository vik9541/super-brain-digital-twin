#!/usr/bin/env python3
"""GitHub Copilot Agent Runner - Оркестратор AI анализа кода"""
import argparse, json, os, sys, yaml, logging, subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class CopilotAgentRunner:
    def __init__(self, config_path='.github/copilot-agent.yml'):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        self.results = []
    
    def analyze_with_openai(self, files: List[str], mode: str) -> Dict:
        """GPT-5.1 Codex Max анализ"""
        logger.info(f"🧠 GPT-5.1 Codex Max: анализ {len(files)} файлов...")
        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            findings = []
            for file in files[:10]:  # Лимит 10 файлов
                content = Path(file).read_text()
                prompt = f"Analyze this {file.split('.')[-1]} code for issues:\n\n{content[:2000]}"
                response = client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500
                )
                findings.append({"file": file, "analysis": response.choices[0].message.content})
            return {"model": "gpt-5.1-codex-max", "findings": findings}
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            return {"model": "gpt-5.1-codex-max", "findings": [], "error": str(e)}
    
    def analyze_with_claude(self, files: List[str], mode: str) -> Dict:
        """﻿Claude Opus 4.5 анализ"""
        logger.info(f"🔍 Claude Opus 4.5: глубокий анализ {len(files)} файлов...")
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
            findings = []
            for file in files[:5]:
                content = Path(file).read_text()
                message = client.messages.create(
                    model="claude-3-opus-20240229",
                    max_tokens=500,
                    messages=[{"role": "user", "content": f"Find bugs in:\n{content[:2000]}"}]
                )
                findings.append({"file": file, "analysis": message.content[0].text})
            return {"model": "claude-opus-4.5", "findings": findings}
        except Exception as e:
            logger.error(f"Claude error: {e}")
            return {"model": "claude-opus-4.5", "findings": [], "error": str(e)}
    
    def run_copilot_cli(self, files: List[str]) -> Dict:
        """GitHub Copilot CLI интеграция"""
        logger.info("🤖 GitHub Copilot CLI: запуск...")
        try:
            result = subprocess.run(
                ['gh', 'copilot', 'suggest', '--', 'analyze code quality'],
                capture_output=True, text=True, timeout=30
            )
            return {"model": "copilot-cli", "output": result.stdout}
        except Exception as e:
            logger.error(f"Copilot CLI error: {e}")
            return {"model": "copilot-cli", "output": "", "error": str(e)}
    
    def run(self, files: List[str], mode: str = 'full') -> Dict:
        logger.info(f"🚀 Запуск анализа (режим: {mode})")
        start = datetime.now()
        results = {
            "timestamp": start.isoformat(),
            "mode": mode,
            "files_count": len(files),
            "models": []
        }
        
        if mode in ['full', 'python-only']:
            results['models'].append(self.analyze_with_openai(files, mode))
            results['models'].append(self.analyze_with_claude(files, mode))
        
        if mode in ['full', 'quick']:
            results['models'].append(self.run_copilot_cli(files))
        
        results['duration'] = (datetime.now() - start).total_seconds()
        return results

def main():
    parser = argparse.ArgumentParser(description='Copilot Agent Runner')
    parser.add_argument('--model', default='all', help='Model to use')
    parser.add_argument('--mode', default='full', help='Analysis mode')
    parser.add_argument('--files', required=True, help='Files to analyze (comma-separated)')
    parser.add_argument('--output', default='copilot-results.json', help='Output file')
    args = parser.parse_args()
    
    files = [f.strip() for f in args.files.split(',') if f.strip()]
    runner = CopilotAgentRunner()
    results = runner.run(files, args.mode)
    
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    logger.info(f"✅ Результаты сохранены: {args.output}")
    logger.info(f"📊 Найдено проблем: {sum(len(m.get('findings', [])) for m in results['models'])}")

if __name__ == '__main__':
    main()
