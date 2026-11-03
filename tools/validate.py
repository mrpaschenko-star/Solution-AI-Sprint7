#!/usr/bin/env python3
"""Verify Sprint 7 structure, links, examples and generated calculations."""
from pathlib import Path
import json,re,subprocess,sys
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
EXPECTED={
'Task1':['README','initiatives','selection','formulations'],
'Task2':['README','flagship-passport','ocr-passport','extraction-passport','placement','model-evaluation'],
'Task3':['README','architecture','contracts','reliability-monitoring','security'],
'Task4':['README','assumptions','market-prices','tco','tco-results','pilot','recommendation'],
'Task5':['README','degradation']}
def main():
 errors=[]
 for task,names in EXPECTED.items():
  for name in names:
   path=ROOT/task/(name+'.md')
   if not path.exists() or path.stat().st_size<100:errors.append(f'Missing/empty {path}')
 for passport in (ROOT/'Task2').glob('*-passport.md'):
  text=passport.read_text()
  for n in range(6):
   if not re.search(r'^## '+str(n)+r'\.',text,re.M):errors.append(f'Passport section {n}: {passport.name}')
 initiatives=(ROOT/'Task1/initiatives.md').read_text()
 ids=re.findall(r'^\| (\d+) \|',initiatives,re.M)
 if ids!=list(map(str,range(1,19))):errors.append('Triage must cover initiatives 1–18 once')
 adrs=list((ROOT/'Task2/adr').glob('ADR-*.md'))
 if len(adrs)!=3:errors.append('Expected 3 ADRs')
 for adr in adrs:
  for title in ['Контекст','Жёсткие ограничения','Сравнительные критерии','Рассмотренные варианты','Решение','Допущения','Риски и что с ними делаем','План выхода','Триггеры пересмотра','История']:
   if '## '+title not in adr.read_text():errors.append(f'ADR field {title}: {adr.name}')
 sources=list(ROOT.glob('Task*/diagrams/*.puml'))
 if len(sources)!=5:errors.append('Expected 5 diagram sources')
 for source in sources:
  try:
   with Image.open(source.with_suffix('.png')) as img:
    if img.format!='PNG' or min(img.size)<100:errors.append(f'Invalid PNG {source.name}')
    img.verify()
  except (OSError,SyntaxError) as exc:errors.append(f'PNG missing/broken {source.name}: {exc}')
  for inc in re.findall(r'^!include\s+(.+)',source.read_text(),re.M):
   if not (source.parent/inc).exists():errors.append(f'Include missing {inc}')
 for path in ROOT.rglob('*.md'):
  for dest in re.findall(r'!?\[[^\]]*\]\(([^\n)]+)\)',path.read_text()):
   if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:',dest) or dest.startswith('#'):continue
   local=dest.split('#',1)[0].strip('<>')
   if local and not (path.parent/local).exists():errors.append(f'Broken link {path.relative_to(ROOT)}: {dest}')
 for block in re.findall(r'```json\n(.*?)\n```',(ROOT/'Task3/contracts.md').read_text(),re.S):
  try:json.loads(block)
  except json.JSONDecodeError as exc:errors.append(f'Contract example JSON: {exc}')
 for pattern in ('*.svg','*.drawio','*.mmd'):
  if list(ROOT.glob('Task*/**/'+pattern)):errors.append(f'Unexpected format {pattern}')
 if errors:raise SystemExit('\n'.join(errors))
 subprocess.run([sys.executable,str(ROOT/'tools/calculate_tco.py'),'--check'],check=True)
 print('PASS: 18 initiatives, 3 passports (0–5), 3 ADRs, 5 PlantUML/PNG pairs, local links, JSON examples, TCO reproducibility.')
 print('These are documentation checks, not model-quality or production tests.')
if __name__=='__main__':main()
