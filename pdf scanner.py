import pdfplumber
import re
import json
import os

# 1. Paths to your PDFs
QUESTION_PDF = "Download_70th_BPSC_Prelims_Question_Paper_2024_PDF_compressed_eab2d89d8d7a21924dc20a6d7531dd14.pdf"
ANSWER_KEY_PDF = "NB-2025-01-17-02.pdf"

# 2. Extract text from both PDFs
def extract_text(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

print("🕮 Extracting question paper text...")
q_text = extract_text(QUESTION_PDF)

print("🕮 Extracting answer key text...")
a_text = extract_text(ANSWER_KEY_PDF)

# 3. Parse the answer key into a dict: { qno: 'A'|'B'|'C'|'D' }
answer_pattern = re.compile(r"(\d{1,3})\s*([ABCD])")
answers = dict()
for m in answer_pattern.finditer(a_text):
    qno = int(m.group(1))
    ans = m.group(2)
    # In the key PDF, each set appears. We assume Set E is first or filter if needed.
    answers[qno] = ans

print(f"✔ Loaded {len(answers)} answer entries.")

# 4. Parse questions and options
#    Assumes questions numbered "1. Question text" and options "A. opt\nB. opt\n..."
question_blocks = re.split(r"\n(?=\d{1,3}\.)", q_text)
questions = []
for block in question_blocks:
    head = block.strip().split("\n",1)
    if len(head)<2: continue
    # Extract Q number
    m = re.match(r"(\d{1,3})\.\s*(.*)", head[0])
    if not m: continue
    qno = int(m.group(1))
    qrest = m.group(2) + "\n" + head[1]

    # Split into question vs options
    parts = re.split(r"\n(?=[ABCD]\.)", qrest)
    if len(parts)<2: continue
    qtext = parts[0].strip()
    opts = []
    for opt_line in parts[1:]:
        m2 = re.match(r"([ABCD])\.\s*(.*)", opt_line.strip())
        if m2:
            opts.append(m2.group(2).strip())
    # Skip if we didn't parse 4 options
    if len(opts)!=4:
        continue

    questions.append({
        "id": qno,
        "question": qtext,
        "options": opts,
        "answer": answers.get(qno, ""),  # blank if missing
        "tag": ""  # placeholder
    })

print(f"✔ Parsed {len(questions)} questions with 4 options each.")

# 5. Tagging rules (customize these as needed)
def assign_tag(qtext):
    text = qtext.lower()
    if "century" in text or "ad" in text: return "Ancient History"
    if "dharma" in text or "mughal" in text: return "Medieval History"
    if "constitution" in text or "amendment" in text: return "Polity"
    if "budget" in text or "economy" in text: return "Economics"
    if any(w in text for w in ["atom", "density", "enzyme", "organ"]): return "Science"
    if any(w in text for w in ["puzzle", "aptitude", "ratio"]): return "Aptitude"
    if "bihar" in text: return "Bihar Special History"
    if any(w in text for w in ["election", "policy", "act", "commission"]): return "Current Affairs"
    # default
    return "General"

for q in questions:
    q["tag"] = assign_tag(q["question"])

# 6. Sort by question number and write JSON
questions = sorted(questions, key=lambda x: x["id"])
os.makedirs("questions", exist_ok=True)
with open("questions/2024.json","w",encoding="utf-8") as f:
    json.dump(questions, f, indent=2, ensure_ascii=False)

print("🎉 Done! Wrote", len(questions), "questions to questions/2024.json")
