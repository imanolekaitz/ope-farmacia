import fitz
import json
import re

def extract_questions_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text() + "\n"
        
    questions = []
    matches = re.finditer(r'(?:^|\n)(\d+)\.\s+(.*?)(?=\n\d+\.\s+|\Z)', full_text, re.DOTALL)
    
    extracted_nums = []
    
    for match in matches:
        q_num = match.group(1)
        q_block = match.group(2).strip()
        
        options = {}
        correct_answer = ""
        
        opt_matches = list(re.finditer(r'\(([a-d])\)\s+(.*?)(?=\n\([a-d]\)|\Z)', q_block, re.DOTALL))
        
        if not opt_matches:
            continue
            
        q_text = q_block[:opt_matches[0].start()].strip().replace('\n', ' ')
        
        for p in opt_matches:
            letter = p.group(1).upper()
            opt_content = p.group(2).strip()
            
            clean_str = re.sub(r'[-\s\n\r]', '', opt_content).lower()
            
            if "(correcta)" in clean_str:
                correct_answer = letter
                # remove (Correcta) and its variants from text
                opt_text = re.sub(r'\(Cor[-\s\n\r]*recta\)', '', opt_content, flags=re.IGNORECASE).strip()
            else:
                opt_text = re.sub(r'\(Incor[-\s\n\r]*recta\)', '', opt_content, flags=re.IGNORECASE).strip()
            
            options[letter] = opt_text.replace('\n', ' ')
            
        if options and correct_answer:
            q_text_with_num = f"{q_num}. {q_text}"
            questions.append({
                "pregunta": q_text_with_num,
                "opciones": options,
                "respuestaCorrecta": correct_answer
            })
            extracted_nums.append(int(q_num))
            
    return questions, extracted_nums

pdf_path = r"g:\Mi unidad\Antigravity\Programa OPE Farmacia\Data\PREGUNTAS_BATERIA_COMÚN_CATEGORÍAS_C2_C3_D_y_E_soluciones.pdf"
json_path = r"g:\Mi unidad\Antigravity\Programa OPE Farmacia\data\preguntas_comunes.json"

questions, nums = extract_questions_from_pdf(pdf_path)

with open(json_path, "w", encoding="utf-8") as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)

print(f"Extracted {len(questions)} questions")
missing = [i for i in range(1, 301) if i not in nums]
print("Missing:", missing)
