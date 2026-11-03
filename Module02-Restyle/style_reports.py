"""Keep the two generated evidence reports in the module's presentation style."""
import re

def style_report(raw, name):
    if name == 'defect-results.md':
        title, label = 'Integrity defects — actual query results', 'INTEGRITY RESULTS'
        headings = ['01 / Orphan job', '02 / Duplicate part identity',
                    '03a / Text price comparison', '03b / Numeric comparison',
                    '04 / Unknown installation date', '05 / List-based join']
        visual = '''![Five integrity defect categories verified against the legacy fixture](assets/integrity-defects.svg)

*The diagram summarizes the same fixture and queries documented below. A numeric cast repairs this comparison, not arbitrary price validation.*

'''
    else:
        title, label = 'Cardinality observations in the legacy fixture', 'CARDINALITY RESULTS'
        headings = ['01 / Jobs per machine', '02 / Jobs per technician',
                    '03 / Part tokens per job', '04 / Jobs per part']
        visual = ''
    body = raw.split('\n',1)[1].strip()
    i = 0
    def section(match):
        nonlocal i
        heading = headings[i]
        i += 1
        return f'### {heading}\n\n'+match.group(0)
    body = re.sub(r'```sql\n.*?```', section, body, flags=re.S)
    body = re.sub(r'(?m)^Measured execute \+ fetch: (\d+\.\d+ ms) \(one local run\)\.',
                  r'\nMeasured execute + fetch: **\1** *(one local run)*.', body)
    if name == 'cardinality-results.md':
        body = body.replace('Observed counts support intended relationships; they do not enforce future cardinality.',
                            'Observed counts support **intended relationships**; they *do not enforce future cardinality*.')
    header = f'<p align="center"><sub>DATABASES 2026 &nbsp; / &nbsp; MODULE 02 &nbsp; / &nbsp; {label}</sub></p>\n\n<h1 align="center">{title}</h1>\n\n'
    footer = '\n\n---\n\n<p align="center"><sub>MODULE 02 &nbsp; / &nbsp; DATA CONTRACTS AND LEGACY SCHEMAS</sub><br><a href="README.md">Module overview</a> &nbsp; · &nbsp; <a href="er-audit.md">ER audit</a> &nbsp; · &nbsp; <a href="../README.md">Portfolio</a></p>\n'
    return header + visual + body + footer
