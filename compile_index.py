import re
import os
import json

print("Rebuilding index.html from source HTML files...")

# File paths
script_dir = os.path.dirname(os.path.abspath(__file__))
index_path = os.path.join(script_dir, "index.html")
cv_path = os.path.join(script_dir, "curriculum_vitae.html")
res_path = os.path.join(script_dir, "research.html")
pub_path = os.path.join(script_dir, "publication.html")
links_path = os.path.join(script_dir, "links.html")
comments_path = os.path.join(script_dir, "comments.json")

# Obfuscate Rivian & Autonomy/AI Team references for previewing site
OBFUSCATE_EMPLOYER = True

# Load static comments from comments.json
static_comments = []
if os.path.exists(comments_path):
    try:
        with open(comments_path, 'r', encoding='utf-8') as f:
            static_comments = json.load(f)
    except Exception as e:
        print(f"Warning: Could not read comments.json: {e}")

static_comments_js = json.dumps(static_comments, ensure_ascii=False)


# Month mapping
months = {
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
    'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12,
    'january': 1, 'february': 2, 'march': 3, 'april': 4, 'june': 6,
    'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12
}

# Image mappings based on title substring
image_mappings = {
    "Conversational 3D Virtual Human": "ico3d",
    "Interactive Conversational": "ico3d",
    "Struggle Determination": "struggle",
    "Are you Struggling": "struggle",
    "psychometric scale": "methods_in_psy22",
    "Delphi technique": "methods_in_psy22",
    "Face-SSD": "face_ssd",
    "Metaphoric Hand Gestures": "metaphoric_gestures",
    "3D Finger CAPE": "finger_cape",
    "Clicking Action and Position": "finger_cape",
    "Iris Recognition System": "iris_recognition",
    "Eyelid Localization": "eyelid_localization",
    "Map2Thought": "map2thought",
    "CoMapGS": "comapgs",
    "VSCHH 2023": "iccvw23_vschh",
    "View Synthesis Challenge of Human Heads": "iccvw23_vschh",
    "ILSH": "iccvw23_ilsh",
    "Imperial Light-Stage Head": "iccvw23_ilsh",
    "Message Passing Framework": "message_passing",
    "EPIC-Tent": "epic_tent",
    "Camping Tent Assembly": "epic_tent",
    "SmileNet": "smilenet",
    "Face Landmark Detection": "face_landmark",
    "Random Forest-based Metaphoric": "random_forest",
    "Observe and Understand Hands": "random_forest",
    "Video-based Object Recognition": "object_recognition",
    "Smart Wristband": "smart_wristband",
    "Smart Glasses": "3dui14",
    "Collaboration Framework in Egocentric": "ic_URAI15",
    "Unified Visual Perception Model for Context-aware Augmented Reality": "ismar13_uvpm",
    "Unified Visual Perception Model": "kjmr14",
    "touch points detection for hand-plane": "khci14",
    "Touch Points Detection for Hand-Plane": "khci14",
    "SA-ResGS": "sa_resgs",
    "Stroke-based Semi-automatic ROI": "hcii2011",
    "Local Feature Descriptors for 3D Object Recognition": "isuvr2012",
    "mARGraphy": "isuvr2011",
    "QR Code Data Representation": "iarsm11",
    "Unified Context-aware Augmented Application Framework": "isuvr2010",
    "Adaptive Lip Feature Point Detection": "entertainment09",
    "Eyelid Detection": "IEEK07",
    "Touchless Finger Vein Recognition": "JIPS08",
    "Hough Transform-Based Semi-Automatic Vertex Detection Algorithm": "KIISE10",
    "Focusing on Digilog Miniatures": "IEIE12",
    "Complementary Feature-point-based": "KIISE12",
    "Contactless Hand Posture Estimation": "KSBE14",
    "multiple objects localization and recognition": "HCI_Korea_2013",
    "RGB-D image feature point extraction and description method": "KCC12"
}

# Helper to clean text and fix malformed href whitespace
def clean_html(text):
    if not text:
        return ""
    # 1. Clean href URLs of any internal whitespace
    def clean_href(m):
        url = re.sub(r'\s+', '', m.group(1))
        return f'href="{url}"'
    text = re.sub(r'href="([^"]*)"', clean_href, text)
    # 2. Collapse all whitespaces and newlines
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def standardize_cv_date(date_str):
    if not date_str:
        return ""
    # Remove surrounding brackets if any
    date_str = date_str.strip('[] ')
    # Replace present with Present
    date_str = re.sub(r'\bpresent\b', 'Present', date_str, flags=re.IGNORECASE)
    
    # Split by dash
    parts = date_str.split('-')
    cleaned_parts = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        # Extract all numbers or 'Present'
        if part.lower() == 'present':
            cleaned_parts.append('Present')
        else:
            # Find all numbers/words
            tokens = re.findall(r'[a-zA-Z0-9]+', part)
            if tokens:
                # If the first token is a 4-digit number (year) or similar
                if tokens[0].isdigit() and len(tokens[0]) == 4:
                    cleaned_parts.append(".".join(tokens))
                else:
                    cleaned_parts.append(" ".join(tokens))
            else:
                cleaned_parts.append(part)
    return " - ".join(cleaned_parts)

def simplify_venue(venue_str, year):
    if not venue_str:
        return ""
    v_upper = venue_str.upper()
    yr_str = ""
    
    # Check for Findings
    if "FINDINGS" in v_upper:
        if "CVPR" in v_upper:
            return f"CVPR Findings{yr_str}"
        if "EMNLP" in v_upper:
            return f"EMNLP Findings{yr_str}"
        if "ACL" in v_upper:
            return f"ACL Findings{yr_str}"
            
    # Check for workshops
    if "WORKSHOP" in v_upper or "WORKSHOPS" in v_upper:
        if "CVPR" in v_upper:
            return f"CVPR Workshop{yr_str}"
        if "ICCV" in v_upper:
            return f"ICCV Workshop{yr_str}"
        if "ECCV" in v_upper:
            return f"ECCV Workshop{yr_str}"
            
    # Regular conferences / journals
    if "CVPR" in v_upper:
        return f"CVPR{yr_str}"
    if "ICCV" in v_upper:
        return f"ICCV{yr_str}"
    if "ECCV" in v_upper:
        return f"ECCV{yr_str}"
    if "IJCV" in v_upper or "INTERNATIONAL JOURNAL OF COMPUTER VISION" in v_upper:
        return f"IJCV{yr_str}"
    if "CVIU" in v_upper or "COMPUTER VISION AND IMAGE UNDERSTANDING" in v_upper:
        return f"CVIU{yr_str}"
    if "TVCG" in v_upper or "VISUALIZATION AND COMPUTER GRAPHICS" in v_upper:
        return f"IEEE TVCG{yr_str}"
    if "THMS" in v_upper or "HUMAN-MACHINE SYSTEMS" in v_upper:
        return f"IEEE THMS{yr_str}"
    if "ICRA" in v_upper or "ROBOTICS AND AUTOMATION" in v_upper:
        return f"ICRA{yr_str}"
    if "ISUVR" in v_upper or "UBIQUITOUS VIRTUAL REALITY" in v_upper:
        return f"ISUVR{yr_str}"
    if "IEEE VR" in v_upper or "VIRTUAL REALITY" in v_upper:
        return f"IEEE VR{yr_str}"
    if "HCII" in v_upper or "HUMAN-COMPUTER INTERACTION" in v_upper:
        return f"HCII{yr_str}"
    if "URAI" in v_upper or "UBIQUITOUS ROBOTS AND AMBIENT INTELLIGENCE" in v_upper:
        return f"URAI{yr_str}"
    if "3DUI" in v_upper or "3D USER INTERFACES" in v_upper:
        return f"3DUI{yr_str}"
    if "ISMAR" in v_upper or ("MIXED" in v_upper and "REALITY" in v_upper):
        return f"ISMAR{yr_str}"
    if "EDUTAINMENT" in v_upper:
        return f"Edutainment{yr_str}"
    if "ARXIV" in v_upper:
        return f"arXiv{yr_str}"
    if "APMR" in v_upper:
        return f"APMR{yr_str}"
    if "KJMR" in v_upper:
        return f"KJMR{yr_str}"
    if "METHODS IN PSYCHOLOGY" in v_upper:
        return f"Methods in Psychology{yr_str}"
    if "IPIU" in v_upper or "영상처리 및 이해" in v_upper:
        return f"IPIU{yr_str}"
    if "IJCAS" in v_upper or "CONTROL, AUTOMATION, AND SYSTEMS" in v_upper:
        return f"IJCAS{yr_str}"
    if "PATTERN RECOGNITION LETTERS" in v_upper:
        return f"Pattern Recognition Letters{yr_str}"
    if "BERC BIOMETRICS" in v_upper or "BERC WORKSHOP" in v_upper:
        return f"BERC Workshop{yr_str}"
        
    # Domestic matches
    if "방송공학회지" in v_upper:
        return f"방송공학회지{yr_str}"
    if "정보과학회논문지" in v_upper or "JOURNAL OF KIISE" in v_upper:
        return f"정보과학회논문지{yr_str}"
    if "전자공학회지" in v_upper:
        return f"전자공학회지{yr_str}"
    if "대한전자공학회" in v_upper:
        return f"대한전자공학회논문지{yr_str}"
    if "정보처리학회" in v_upper:
        return f"정보처리학회논문지{yr_str}"
    if "HCI KOREA" in v_upper:
        return f"HCI Korea{yr_str}"
    if "KIISE" in v_upper:
        if "WINTER" in v_upper or "동계" in v_upper:
            return f"KIISE Winter Conference{yr_str}"
        if "AUTUMN" in v_upper or "FALL" in v_upper or "추계" in v_upper:
            return f"KIISE Autumn Conference{yr_str}"
        return f"KIISE Conference{yr_str}"
    if "KSC" in v_upper or "동계학술" in v_upper:
        return f"한국정보과학회(KIISE){yr_str}"
    if "추계학술" in v_upper:
        return f"한국정보과학회 추계학술회{yr_str}"
    if "KCC" in v_upper or "KOREA COMPUTER CONGRESS" in v_upper or ("정보과학회" in v_upper and ("학술" in v_upper or "CONGRESS" in v_upper)):
        return f"KCC{yr_str}"
        
    cleaned = venue_str
    cleaned = re.sub(r',?\s*(vol|no|pp|issue|pages|page)\.?\s*\d+.*$', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r',?\s*\d+\s*(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec).*$', '', cleaned, flags=re.IGNORECASE)
    if year > 0:
        cleaned = re.sub(r'\b' + str(year) + r'\b', '', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip(' ,.')
    return cleaned

def parse_korean_raw(korean_raw, year):
    if not korean_raw:
        return "", "", ""
    
    # Standardize quotes
    cleaned = korean_raw.strip()
    cleaned = cleaned.replace('&ldquo;', '“').replace('&rdquo;', '”')
    cleaned = cleaned.replace('&lsquo;', '‘').replace('&rsquo;', '’')
    cleaned = cleaned.replace('“', '"').replace('”', '"')
    
    # Try to find title in double quotes
    title_match = re.search(r'"([^"]+)"', cleaned)
    if title_match:
        korean_title = title_match.group(1).strip().rstrip(' ,.')
        escaped_title = re.escape(title_match.group(1))
        parts = re.split(r'"' + escaped_title + r'"', cleaned)
        korean_authors = parts[0].rstrip(',. ').strip()
        korean_venue = parts[1].lstrip(',. ').strip() if len(parts) > 1 else ""
    else:
        # Fallback if no quotes
        korean_title = cleaned
        korean_authors = ""
        korean_venue = ""
        
    return korean_title, korean_authors, korean_venue

def extract_special_notes(venue_full):
    if not venue_full:
        return []
    notes = []
    # 1. Best Paper / Poster / Presentation Award
    award_match = re.findall(r'(Best\s+(?:Paper|Poster|Presentation)\s+Award!?)', venue_full, re.IGNORECASE)
    for award in award_match:
        notes.append(award)
        
    # 2. Other notes in parentheses
    def find_balanced_parentheses(text):
        results = []
        stack = []
        start = -1
        for idx, char in enumerate(text):
            if char == '(':
                if not stack:
                    start = idx
                stack.append(char)
            elif char == ')':
                if stack:
                    stack.pop()
                    if not stack:
                        results.append(text[start+1:idx])
        return results

    parenthesis_matches = find_balanced_parentheses(venue_full)
    for content in parenthesis_matches:
        content_lower = content.lower()
        if any(kw in content_lower for kw in ["long paper", "invited", "presented in", "oral", "award", "excellent paper", "best paper", "best presentation", "tutorial"]):
            parts = content.split(',')
            for p in parts:
                p_strip = p.strip()
                p_lower = p_strip.lower()
                if "also to appear" in p_lower:
                    continue
                if p_strip:
                    notes.append(p_strip)
                    
    # 3. Oral presentation
    if "oral presentation" in venue_full.lower() and not any("oral" in n.lower() for n in notes):
        notes.append("Oral Presentation")
        
    # De-duplicate notes while preserving order
    seen = set()
    unique_notes = []
    for n in notes:
        norm = n.strip().lower().rstrip('!')
        if norm not in seen:
            seen.add(norm)
            unique_notes.append(n)
            
    return unique_notes

def parse_news():
    news = [
        {"date": "2026.06.15", "desc": "Joined the Autonomy & AI team at Rivian as a staff ML engineer."},
        {"date": "2026.06.11", "desc": "Invited talk at EECS, Queen Mary University of London."},
        {"date": "2026.02.20", "desc": "Paper accepted to IEEE/CVF CVPR (Findings), Denver, CO, USA. [<a href=\"https://arxiv.org/abs/2601.11442\" target=\"_blank\" rel=\"nofollow\">arXiv</a>]"},
        {"date": "2025.11.24", "desc": "Paper accepted to Springer IJCV. [<a href=\"https://ico3d.github.io\" target=\"_blank\" rel=\"nofollow\">Project</a>] [<a href=\"https://rdcu.be/e7aVe\" target=\"_blank\" rel=\"nofollow\">IJCV-SharedIt-PDF</a>] [<a href=\"https://doi.org/10.1007/s11263-025-02725-8\" target=\"_blank\" rel=\"nofollow\">article</a>] [<a href=\"https://youtu.be/meONZbaZzco\" target=\"_blank\" rel=\"nofollow\">demo</a>]"},
        {"date": "2025.08.11", "desc": "Paper accepted to Springer IJCV. [<a href=\"https://links.springernature.com/f/a/O_nwydZKF7aRtpDTP0zSIw~~/AABE5hA~/wUM5Un7EOfBSo52aHffXzodTFgsDInAvwUptFPRbPiRcaVG1I23K1rK9TSFi88I0k0omyBmlCQj0n_5Tm8nScZ8pgOdpOF3PRdjI5XKF6oPDnSKYg8SQeJLVuixL9ZAjgMaFv-YI37Rszq5olRpjxXemtJueedZoeAajQlIbT5qJnFJWBIf3Tgzvw9lU9udfCl0aeNDgH0gvK82U80wzisM8tQvozA4WDAHdifhfXPtd7Bd-uuv06Z9CSfClZiiLy5-gjrqshPzoWzTYeeE3wGgqYLp1sUCYtNrwalaCFYQ~\" target=\"_blank\" rel=\"nofollow\">article</a>]"},
        {"date": "2025.02.26", "desc": "Paper accepted to IEEE/CVF CVPR, Nashville, TN, USA. [<a href=\"https://youngkyoonjang.github.io/projects/comapgs/\" target=\"_blank\" rel=\"nofollow\">Project</a>] [<a href=\"http://arxiv.org/abs/2503.20998\" target=\"_blank\" rel=\"nofollow\">arXiv</a>] [<a href=\"https://openaccess.thecvf.com/content/CVPR2025/html/Jang_CoMapGS_Covisibility_Map-based_Gaussian_Splatting_for_Sparse_Novel_View_Synthesis_CVPR_2025_paper.html\" target=\"_blank\" rel=\"nofollow\">open access</a>]"},
        {"date": "2024.12.12", "desc": "Invited talk at the Department of AI, Korea University, South Korea."},
        {"date": "2024.12.02", "desc": "Invited talk at the Graduate School of AI, POSTECH, South Korea."},
        {"date": "2023.10.09", "desc": "The ILSH-VSCHH CodaLab challenges are now open for new [<a href=\"https://codalab.lisn.upsaclay.fr/competitions/16058\" rel=\"nofollow\" target=\"_blank\">Validation</a>] and [<a href=\"https://codalab.lisn.upsaclay.fr/competitions/14427\" rel=\"nofollow\" target=\"_blank\">Test</a>] submissions."},
        {"date": "2023.10.02", "desc": "Released the ILSH dataset and VSCHH 2023 challenge papers at [<a href=\"https://openaccess.thecvf.com/ICCV2023_workshops/RHWC\" rel=\"nofollow\" target=\"_blank\">ICCVW 2023</a>]."},
        {"date": "2023.05.15", "desc": "Launched the 'To NeRF or not to NeRF: VSCHH Challenge' at ICCV 2023. [<a href=\"https://sites.google.com/view/vschh/home\" rel=\"nofollow\" target=\"_blank\">WS</a>] [<a href=\"https://codalab.lisn.upsaclay.fr/competitions/13273\" rel=\"nofollow\" target=\"_blank\">CodaLab</a>]"},
        {"date": "2022.11.01", "desc": "Joined the 3D Vision Team at Huawei Noah's Ark Lab as a Senior Research Scientist."},
        {"date": "2022.06.10", "desc": "Invited talk at the Global Mentoring Program, KIST-UST, South Korea."},
        {"date": "2022.06.06", "desc": "Joined the R&D team at Disguise as a Software Engineer (Founding Research Specialist)."},
        {"date": "2022.05.26", "desc": "Released the Message Passing Framework source code at ICRA 2022. [<a href=\"https://github.com/youngkyoonjang/MessagePassingFramework\" rel=\"nofollow\" target=\"_blank\">Code</a>]"},
        {"date": "2022.02.15", "desc": "Invited talk at the Graduate School of Culture Technology, KAIST, South Korea."},
        {"date": "2022.01.31", "desc": "Paper accepted to IEEE ICRA, Philadelphia, USA. [<a href=\"https://sites.google.com/view/mpf-hri\" rel=\"nofollow\" target=\"_blank\">Project</a>] [<a href=\"https://github.com/youngkyoonjang/MessagePassingFramework\" rel=\"nofollow\" target=\"_blank\">Code</a>] [<a href=\"https://ieeexplore.ieee.org/document/9812439\" target=\"_blank\" rel=\"nofollow\">pdf</a>]"},
        {"date": "2022.01.14", "desc": "Invited talk at Mokpo Hongil High School, South Korea."},
        {"date": "2021.07.22", "desc": "Invited talk at the HCI Research Center, Dankook University, South Korea."},
        {"date": "2021.05.11", "desc": "Joined the Personal Robotics Lab in the ISN Group at Imperial College London as a Research Associate."},
        {"date": "2020.10.29", "desc": "Invited talk at Facebook Reality Labs, Redmond, USA."},
        {"date": "2020.08.10", "desc": "Released the EPIC-Tent 2019 dataset and annotations. [<a href=\"https://youtu.be/MGqT6J6JJ4I\" target=\"_blank\" rel=\"nofollow\">Teaser Video</a>] [<a href=\"https://data.bris.ac.uk/data/dataset/2ite3tu1u53n42hjfh3886sa86\" target=\"_blank\" rel=\"nofollow\">Dataset</a>] [<a href=\"https://github.com/youngkyoonjang/EPIC_Tent2019\" target=\"_blank\" rel=\"nofollow\">Annotation</a>]"},
        {"date": "2019.10.08", "desc": "Invited to serve as a Conference Track Area Chair for <a href=\"http://www.ieeevr.org/2020/\" rel=\"nofollow\" target=\"_blank\">IEEE VR 2020</a>."},
        {"date": "2019.08.21", "desc": "Workshop paper accepted to the IEEE ICCV Workshop on EPIC, Seoul, South Korea. [<a href=\"https://sites.google.com/view/epic-tent\" rel=\"nofollow\" target=\"_blank\">Project</a>]"},
        {"date": "2019.01.31", "desc": "Paper accepted to Elsevier CVIU. [<a href=\"https://sites.google.com/view/face-ssd/home\" rel=\"nofollow\" target=\"_blank\">Project</a>]"},
        {"date": "2018.11.15", "desc": "Invited to serve as a Conference Track Area Chair for <a href=\"http://ieeevr.org/2019/\" rel=\"nofollow\" target=\"_blank\">IEEE VR 2019</a>."},
        {"date": "2018.05.21", "desc": "Joined the Visual Information Laboratory at the University of Bristol as a Senior Research Associate (Postdoc)."},
        {"date": "2017.11.02", "desc": "Gave an invited lecture at the Computer Laboratory, University of Cambridge, UK."},
        {"date": "2017.08.25", "desc": "Workshop paper accepted to the IEEE ICCV Workshop on AMFG, Venice, Italy. [<a href=\"https://sites.google.com/view/sensingfeeling/\" rel=\"nofollow\" target=\"_blank\">Project</a>]"},
        {"date": "2017.08.03", "desc": "Invited talk at the Augmented Reality Research Center, KAIST, South Korea."},
        {"date": "2017.08.01", "desc": "Invited talk at the Intelligent Image Processing Research Center, KETI, South Korea."},
        {"date": "2016.08.08", "desc": "Paper accepted to IEEE Transactions on Human-Machine Systems. [<a href=\"https://sites.google.com/site/fingergesture/fui/\" rel=\"nofollow\" target=\"_blank\">Project</a>]"},
        {"date": "2016.07.01", "desc": "Won the Best Poster Award at the IEEE CVPR 2016 Workshop on HANDS, Las Vegas, USA (sponsored by Facebook/Oculus and Purdue University)."},
        {"date": "2016.07.01", "desc": "Poster presentation at the IEEE CVPR 2016 Workshop on HANDS, Las Vegas, NV, USA."},
        {"date": "2016.05.23", "desc": "Joined the MMV Group at Queen Mary University of London as a Postdoctoral Researcher."},
        {"date": "2016.05.04", "desc": "Invited talk at the Graduate School of Culture Technology, KAIST, South Korea."},
        {"date": "2016.04.29", "desc": "Invited talk at the College of Information and Communication Engineering, Daegu University, South Korea."},
        {"date": "2016.04.26", "desc": "Invited talk at the Realistic Information Platform Research Center, KETI, South Korea."},
        {"date": "2016.04.25", "desc": "Won the Best Presentation Award at APMR 2016, Andong, South Korea."},
        {"date": "2016.04.02", "desc": "Invited talk at NamDoHakSuk (NDHS), South Korea."},
        {"date": "2016.02.01", "desc": "Invited talk at the Max Planck Institute for Informatics, Germany."},
        {"date": "2015.12.18", "desc": "Invited talk at Mokpo Hongil High School, South Korea."},
        {"date": "2015.12.17", "desc": "Invited talk at the VTouch Research Group, VTouch Inc., South Korea."},
        {"date": "2015.11.12", "desc": "Gave an invited lecture for the GSCT Course (GCT555: 3D Interaction Design), KAIST, South Korea."},
        {"date": "2015.10.15", "desc": "Invited talk at the Korea Electric Power Research Institute, KEPCO, South Korea."},
        {"date": "2015.09.06", "desc": "Updated full CV and research statement."},
        {"date": "2015.08.20", "desc": "Launched the website."}
    ]
    if OBFUSCATE_EMPLOYER:
        for item in news:
            item["desc"] = item["desc"].replace("Autonomy & AI team at Rivian", "XXX team at YYY")
            item["desc"] = item["desc"].replace("Autonomy & AI Team at Rivian", "XXX Team at YYY")
            item["desc"] = item["desc"].replace("Rivian", "YYY")
    return news


def parse_publications():
    with open(pub_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # We want to extract 5 sections
    sections_def = [
        ("International Journal (SCI, SCIE)", "int-journal"),
        ("Domestic Journal (in Korean)", "dom-journal"),
        ("International Conference", "int-conference"),
        ("Domestic Conference (in Korean)", "dom-conference"),
        ("ETC (poster:1, arXiv:1, workshop:3, demo:0)", "etc-pub")
    ]
    
    all_pubs = []
    
    for title, cat in sections_def:
        # Search for header
        escaped_title = re.escape(title)
        # Match <DIV><STRONG><span style="color: #393939">...</span></STRONG></DIV>
        pattern = r'<DIV><STRONG><span style="color: #393939">' + escaped_title + r'</span></STRONG></DIV>.*?<UL>(.*?)</UL>'
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if not match:
            # Try general matching
            pattern = escaped_title + r'.*?<UL>(.*?)</UL>'
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            
        if match:
            li_html = match.group(1)
            # Find all LIs
            lis = re.findall(r'<li>(.*?)</li>', li_html, re.DOTALL | re.IGNORECASE)
            for li in lis:
                li = li.strip()
                if not li:
                    continue
                
                # Extract original Korean version if present in comment
                korean_raw = None
                comment_match = re.search(r'<!--\s*(.*?)\s*-->', li, re.DOTALL)
                if comment_match:
                    korean_raw = comment_match.group(1).strip()
                    li_clean = re.sub(r'<!--\s*(.*?)\s*-->', '', li, flags=re.DOTALL).strip()
                else:
                    li_clean = li
                
                # Extract links
                links = []
                a_tags = re.findall(r'<a\s+href="[^"]*".*?>.*?</a>', li_clean, re.DOTALL)
                for a in a_tags:
                    # Give it the badge class
                    badge_a = a.replace('href=', 'class="badge" href=')
                    links.append(badge_a)
                
                # Clean LI of links and their brackets
                cleaned = li_clean
                cleaned = re.sub(r'\[?\s*<a\s+href="[^"]*".*?>.*?</a>\s*\]?', '', cleaned, flags=re.DOTALL)
                
                # Replace HTML quote entities with standard curly quotes
                cleaned = cleaned.replace('&ldquo;', '“').replace('&rdquo;', '”')
                cleaned = cleaned.replace('&lsquo;', '‘').replace('&rsquo;', '’')
                
                # Find title in quotes
                title_match = re.search(r'["“](.*?)["”]', cleaned, re.DOTALL)
                if title_match:
                    pub_title = title_match.group(1).strip()
                    escaped_pub_title = re.escape(pub_title)
                    parts = re.split(r'["“]' + escaped_pub_title + r'["”]', cleaned, flags=re.DOTALL)
                    pub_title = clean_html(pub_title)
                    authors = clean_html(parts[0]).rstrip(',').strip()
                    venue = clean_html(parts[1]).lstrip(',').strip() if len(parts) > 1 else ""
                else:
                    pub_title = clean_html(cleaned)
                    authors = ""
                    venue = ""
                
                authors = clean_html(authors).rstrip(',').strip()
                venue = clean_html(venue).rstrip('.').strip().lstrip(',').strip()
                links_html = clean_html(" ".join(links))
                
                # Assign sort key (year, month)
                text_to_search = venue + " " + pub_title + " " + li_clean
                ym_match = re.search(r'(20\d{2})\.(0[1-9]|1[0-2])', text_to_search)
                if ym_match:
                    year, month = int(ym_match.group(1)), int(ym_match.group(2))
                else:
                    year_match = re.search(r'(20\d{2}|19\d{2})', text_to_search)
                    year = int(year_match.group(1)) if year_match else 0
                    
                    if year == 0:
                        short_yr = re.search(r'(URAI|ISUVR|HCII|CVPRW|ICCVW|3DUI)(\d{2})', text_to_search)
                        if short_yr:
                            year = 2000 + int(short_yr.group(2))
                        else:
                            any_yr = re.search(r'(\d{4})', text_to_search)
                            year = int(any_yr.group(1)) if any_yr else 2010
                            
                    month = 1
                    for mname, mval in months.items():
                        if re.search(r'\b' + mname + r'\b', text_to_search.lower()):
                            month = mval
                            break
                
                venue_full = venue
                # Simplify venue name
                venue = simplify_venue(venue, year)
                
                # Check image prefix
                image_prefix = None
                if "multi-layered random forest" in pub_title.lower():
                    image_prefix = "multi-layered_random_forest"
                elif "symbolic hand gesture" in pub_title.lower():
                    image_prefix = "symbolic_hand_gesture"
                else:
                    for keyword, prefix in image_mappings.items():
                        if keyword.lower() in pub_title.lower() or keyword.lower() in venue_full.lower():
                            image_prefix = prefix
                            break
                
                # Extract special notes
                special_notes = extract_special_notes(venue_full)
                
                all_pubs.append({
                    'category': cat,
                    'title': pub_title,
                    'authors': authors,
                    'venue': venue,
                    'venue_full': venue_full,
                    'links_html': links_html,
                    'image_prefix': image_prefix,
                    'special_notes': special_notes,
                    'date': (year, month),
                    'korean_raw': korean_raw,
                    'raw': li_clean
                })
        else:
            print(f"Warning: Section '{title}' not found in publication.html!")
            
    # Sort descending with custom key to group gesture papers together
    def get_sort_key(pub):
        title = pub['title'].lower()
        if "metaphoric hand gestures" in title:
            return (2017, 2, 3)
        elif "multi-layered random forest" in title:
            return (2017, 2, 2)
        elif "symbolic hand gesture" in title:
            return (2017, 2, 1)
        elif "static-dynamic gesture" in title:
            return (2015, 4, 2)
        elif "3d finger cape" in title:
            return (2015, 4, 1)
        elif "video-based object recognition" in title:
            return (2015, 4, 0)
        elif "smart wristband" in title:
            return (2014, 6, 2)
        elif "smart glasses" in title:
            return (2014, 6, 1)
        return (pub['date'][0], pub['date'][1], 0)
        
    all_pubs.sort(key=get_sort_key, reverse=True)
    return all_pubs

def parse_patents():
    with open(pub_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    categories = [
        ("International Patent (registered)", "int-patent"),
        ("Domestic Patent (in Korean) (registered)", "dom-patent-registered"),
        ("Domestic Patent (in Korean) (pending)", "dom-patent-pending"),
        ("Software Registration (in Korean)", "sw-registration")
    ]
    
    patents_data = {}
    
    for title, cat in categories:
        escaped_title = re.escape(title)
        pattern = r'<DIV><STRONG><span style="color: #393939">' + escaped_title + r'</span></STRONG></DIV>.*?<UL>(.*?)</UL>'
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            li_html = match.group(1)
            lis = re.findall(r'<li>(.*?)</li>', li_html, re.DOTALL | re.IGNORECASE)
            patents_data[cat] = [clean_html(li) for li in lis if li.strip()]
        else:
            patents_data[cat] = []
            
    return patents_data

def parse_cv_details():
    with open(cv_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # We want to extract Academic Activities, Volunteer, Teaching, Awards, Scholarships
    def extract_section_lis(section_title):
        escaped = re.escape(section_title)
        # Search for title tag
        pattern = r'<strong>' + escaped + r'</strong>.*?<UL>(.*?)</UL>'
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if not match:
            pattern = escaped + r'.*?<UL>(.*?)</UL>'
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            lis = re.findall(r'<li>(.*?)</li>', match.group(1), re.DOTALL | re.IGNORECASE)
            return [clean_html(li) for li in lis if li.strip()]
        return []
        
    # Honors and Awards has Scholarship and Awards subsections
    awards_match = re.search(r'Awards</strong></div>.*?<UL>(.*?)</UL>', content, re.DOTALL | re.IGNORECASE)
    awards = [clean_html(li) for li in re.findall(r'<li>(.*?)</li>', awards_match.group(1), re.DOTALL | re.IGNORECASE)] if awards_match else []
    
    scholarships_match = re.search(r'Scholarship.*?</div>.*?<UL>(.*?)</UL>', content, re.DOTALL | re.IGNORECASE)
    scholarships = [clean_html(li) for li in re.findall(r'<li>(.*?)</li>', scholarships_match.group(1), re.DOTALL | re.IGNORECASE)] if scholarships_match else []
    
    cv_data = {
        'activities': extract_section_lis("Academic Activities"),
        'volunteers': extract_section_lis("Volunteer Experiences"),
        'teaching': extract_section_lis("Teaching Experiences"),
        'awards': awards,
        'scholarships': scholarships
    }
    return cv_data

def parse_research_projects():
    with open(res_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Find all DIV elements with style="font-size: 14pt" (or similar)
    # The project wrapper ends at the next DIV with font-size 14pt or the end of section
    # Let's extract them by splitting by DIV tags
    parts = re.split(r'(<DIV><span style="font-size: 14pt">|<DIV><span style="font-size: 14pt;?">|<div[^>]*><span style="font-size: 14pt">|<div[^>]*><span style="font-size: 14pt;?">)', content, flags=re.IGNORECASE)
    
    projects = []
    # Index 0 is the header, subsequent elements are the dividers and their contents
    for idx in range(1, len(parts), 2):
        divider = parts[idx]
        block = parts[idx+1]
        
        # Split block at </section> or wrapper end to prevent bleeding
        block_clean = block.split('</section>')[0].split('</div>\n    </div>\n    </table>')[0]
        
        # Parse title
        title_match = re.search(r'<strong>(.*?)</strong>', block_clean, re.DOTALL | re.IGNORECASE)
        if not title_match:
            continue
        title = clean_html(title_match.group(1))
        
        # Clean title of tags
        title_clean = re.sub(r'<.*?>', '', title)
        
        # Rest of the block is description. We clean it of wrapper tags
        desc = block_clean[title_match.end():].strip()
        # remove closing tags
        desc = re.sub(r'^</span>\s*</DIV>\s*', '', desc, flags=re.IGNORECASE)
        desc = re.sub(r'^\s*</div>\s*', '', desc)
        desc = clean_html(desc)
        
        # Try to find target image prefix for project based on title keywords
        image_prefix = None
        for keyword, prefix in image_mappings.items():
            if keyword.lower() in title_clean.lower():
                image_prefix = prefix
                break
                
        projects.append({
            'title': title,
            'title_clean': title_clean,
            'desc': desc,
            'image_prefix': image_prefix
        })
        
    return projects

def parse_resources_links():
    with open(links_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # We want to extract sections under links.html
    # Links sections are separated by <h3> or <DIV><STRONG>
    # Let's find sections like "Computer Vision Groups", "Computer Vision Journals", "Resource & Code & Dataset" etc.
    link_sections = []
    
    pattern = r'<DIV><STRONG><span style="color: #393939">(.*?)</span></STRONG></DIV>.*?<UL>(.*?)</UL>'
    matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
    for title, list_html in matches:
        lis = re.findall(r'<li>(.*?)</li>', list_html, re.DOTALL | re.IGNORECASE)
        link_sections.append({
            'title': title.strip(),
            'links': [clean_html(li) for li in lis if li.strip()]
        })
        
    return link_sections


def generate_academic_timeline_html():
    html = []
    
    # 1. Academic Leadership Section
    html.append('                <!-- Academic Leadership Section -->')
    html.append('                <div class="reviewer-title">Academic Leadership</div>')
    html.append('                <div class="reviewer-section">')
    
    # Organiser Row
    html.append('                  <div class="reviewer-row">')
    html.append('                    <div class="reviewer-category">Organiser</div>')
    html.append('                    <div class="reviewer-venues">')
    html.append('                      <span class="reviewer-item tooltip-container"><a href="https://sites.google.com/view/vschh/home" target="_blank" rel="nofollow"><span class="venue-name">ICCVW</span> <span class="venue-years">2023</span></a><span class="tooltip-text">Organiser of To NeRF or not to NeRF: VSCHH @ ICCV 2023</span></span>, ')
    html.append('                      <span class="reviewer-item tooltip-container"><a href="https://old.uvrlab.org/isuvr/2015/main.html" target="_blank" rel="nofollow"><span class="venue-name">ISUVR* (General Chair)</span> <span class="venue-years">2015</span></a><span class="tooltip-text">General chair, International Symposium on Ubiquitous Virtual Reality</span></span>, ')
    html.append('                      <span class="reviewer-item tooltip-container"><a href="https://old.uvrlab.org/isuvr/2013/main.html" target="_blank" rel="nofollow"><span class="venue-name">ISUVR* (Organizing Chair)</span> <span class="venue-years">2013</span></a><span class="tooltip-text">Organizing chair, International Symposium on Ubiquitous Virtual Reality</span></span>, ')
    html.append('                      <span class="reviewer-item tooltip-container"><a href="https://old.uvrlab.org/isuvr/2012/index.html" target="_blank" rel="nofollow"><span class="venue-name">ISUVR* (Student Volunteer Chair)</span> <span class="venue-years">2012</span></a><span class="tooltip-text">Student volunteer chair, International Symposium on Ubiquitous Virtual Reality</span></span>')
    html.append('                    </div>')
    html.append('                  </div>')
    
    # Area Chair Row
    html.append('                  <div class="reviewer-row">')
    html.append('                    <div class="reviewer-category">Area Chair</div>')
    html.append('                    <div class="reviewer-venues">')
    html.append('                      <span class="reviewer-item tooltip-container"><a href="https://ieeevr.org/2020/" target="_blank" rel="nofollow"><span class="venue-name">IEEE VR</span> <span class="venue-years">2020</span></a><span class="tooltip-text">Area Chair, IEEE Conference on Virtual Reality and 3D User Interfaces; Conference Papers Category</span></span>, ')
    html.append('                      <span class="reviewer-item tooltip-container"><a href="https://ieeevr.org/2019/" target="_blank" rel="nofollow"><span class="venue-name">IEEE VR</span> <span class="venue-years">2019</span></a><span class="tooltip-text">Area Chair, IEEE Conference on Virtual Reality and 3D User Interfaces; Conference Papers Category</span></span>')
    html.append('                    </div>')
    html.append('                  </div>')
    
    html.append('                </div>')
    
    html.append('                <div class="academic-footnote">')
    html.append('                  * ISUVR was a vibrant international symposium driven by dedicated doctoral researchers, primarily from KAIST, in collaboration with peers from various domestic and international academic institutions. Replicating the rigorous peer-review and program design of major international conferences, the symposium invited global submissions and featured keynote and invited academic speakers from world-renowned institutions, including CMU, Columbia University, Georgia Tech, Imperial College London, MSR, EPFL, USC, DFKI, and Fraunhofer institute IPSI. The initiative fundamentally functioned to cultivate academic leadership and establish a premier network for emerging leaders in the AR/VR community.')
    html.append('                </div>')
    
    # 2. Reviewer & Program Committee Service Section
    html.append('                <!-- Reviewer & Program Committee Fields List -->')
    html.append('                <div class="reviewer-title">Reviewer Service</div>')
    html.append('                <div class="reviewer-section">')
    
    # CV / ML Row
    html.append('                  <div class="reviewer-row">')
    html.append('                    <div class="reviewer-category">CV / ML</div>')
    html.append('                    <div class="reviewer-venues">')
    html.append('                      <span class="reviewer-item tooltip-container"><span class="venue-name">ECCV</span> <span class="venue-years">(2026 - Present)</span><span class="tooltip-text">Reviewer for European Conference on Computer Vision</span></span>, ')
    html.append('                      <span class="reviewer-item tooltip-container"><span class="venue-name">IJCV</span> <span class="venue-years">(2023 - Present)</span><span class="tooltip-text">Review for International Journal of Computer Vision</span></span>, ')
    html.append('                      <span class="reviewer-item tooltip-container"><span class="venue-name">CVPR</span> <span class="venue-years">(2020 - Present)</span><span class="tooltip-text">Reviewer for IEEE/CVF Computer Vision and Pattern Recognition</span></span>, ')
    html.append('                      <span class="reviewer-item tooltip-container"><span class="venue-name">Pattern Recognition</span> <span class="venue-years">(2019 - Present)</span><span class="tooltip-text">Review for Pattern Recognition</span></span>, ')
    html.append('                      <span class="reviewer-item tooltip-container"><span class="venue-name">BMVC</span> <span class="venue-years">(2017 - 2019)</span><span class="tooltip-text">Technical Program Committee, British Machine Vision Conference</span></span>, ')
    html.append('                      <span class="reviewer-item tooltip-container"><span class="venue-name">CVPRW/ICCVW/ECCVW TPC</span> <span class="venue-years">(2016 - 2019)</span><span class="tooltip-text">Technical Program Committee for CVPR/ICCV/ECCV Workshops (HANDS, EPIC)</span></span>, ')
    html.append('                      <span class="reviewer-item tooltip-container"><span class="venue-name">IVC</span> <span class="venue-years">(2016 - 2018)</span><span class="tooltip-text">Review for Image and Vision Computing</span></span>')
    html.append('                    </div>')
    html.append('                  </div>')
    
    # AR / VR Row
    html.append('                  <div class="reviewer-row">')
    html.append('                    <div class="reviewer-category">AR / VR</div>')
    html.append('                    <div class="reviewer-venues">')
    html.append('                      <span class="reviewer-item tooltip-container"><span class="venue-name">IEEE TVCG</span> <span class="venue-years">(2016 - Present)</span><span class="tooltip-text">Review for IEEE Transactions on Visualization and Computer Graphics</span></span>, ')
    html.append('                      <span class="reviewer-item tooltip-container"><span class="venue-name">Augmented Human</span> <span class="venue-years">(2016)</span><span class="tooltip-text">Reviewer for Augmented Human International Conference</span></span>, ')
    html.append('                      <span class="reviewer-item tooltip-container"><span class="venue-name">ISMAR</span> <span class="venue-years">(2011 - 2015)</span><span class="tooltip-text">Review for IEEE International Symposium on Mixed and Augmented Reality</span></span>')
    html.append('                    </div>')
    html.append('                  </div>')
    
    # Human-Machine Interaction Row
    html.append('                  <div class="reviewer-row">')
    html.append('                    <div class="reviewer-category">Human-Machine Interaction</div>')
    html.append('                    <div class="reviewer-venues">')
    html.append('                      <span class="reviewer-item tooltip-container"><span class="venue-name">Ent. Computing</span> <span class="venue-years">(2022)</span><span class="tooltip-text">Review for Entertainment Computing</span></span>, ')
    html.append('                      <span class="reviewer-item tooltip-container"><span class="venue-name">IEEE FG</span> <span class="venue-years">(2017 - 2018)</span><span class="tooltip-text">Technical Program Committee, IEEE Conference on Automatic Face and Gesture Recognition</span></span>, ')
    html.append('                      <span class="reviewer-item tooltip-container"><span class="venue-name">Sensors</span> <span class="venue-years">(2017)</span><span class="tooltip-text">Review for Sensors (ISSN 1424-8220)</span></span>, ')
    html.append('                      <span class="reviewer-item tooltip-container"><span class="venue-name">KING Computing</span> <span class="venue-years">(2015)</span><span class="tooltip-text">Review for Korean Institute of Next Generation Computing</span></span>, ')
    html.append('                      <span class="reviewer-item tooltip-container"><span class="venue-name">IJRA (Robotics/Auto)</span> <span class="venue-years">(2009)</span><span class="tooltip-text">Review for International Journal of Robotics and Automation</span></span>')
    html.append('                    </div>')
    html.append('                  </div>')
    
    html.append('                </div>')
    
    return "\n".join(html)


def standardize_all_publication_images():
    papers_dir = os.path.join(script_dir, "images/papers")
    if not os.path.exists(papers_dir):
        print(f"Directory {papers_dir} not found. Skipping auto-standardization of images.")
        return
    try:
        from PIL import Image
    except ImportError:
        print("PIL/Pillow not installed. Skipping auto-standardization of images.")
        return
        
    print("Auto-standardizing publication images (fit without distortion, transparent padding)...")
    for filename in os.listdir(papers_dir):
        if not filename.endswith('.png'):
            continue
        file_path = os.path.join(papers_dir, filename)
        try:
            img = Image.open(file_path)
            img_w, img_h = img.size
            
            target_w = 400
            target_h = 250
            
            # If already correct size, skip
            if img_w == target_w and img_h == target_h:
                continue
                
            # Convert to RGBA for transparent padding
            img = img.convert('RGBA')
            
            # Calculate new size keeping aspect ratio
            ratio = min(target_w / img_w, target_h / img_h)
            new_w = int(img_w * ratio)
            new_h = int(img_h * ratio)
            
            img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
            # Create a transparent background canvas
            new_img = Image.new('RGBA', (target_w, target_h), (0, 0, 0, 0))
            
            # Paste the resized image in the center
            offset_x = (target_w - new_w) // 2
            offset_y = (target_h - new_h) // 2
            new_img.paste(img_resized, (offset_x, offset_y))
            
            # Save back as PNG
            new_img.save(file_path, 'PNG')
            print(f"  Auto-standardized {filename} from {img_w}x{img_h} to {target_w}x{target_h}")
        except Exception as e:
            print(f"  Error processing {filename}: {e}")


# Run parsers
news_list = parse_news()
publications_list = parse_publications()
patents_list = parse_patents()
cv_details = parse_cv_details()
projects_list = parse_research_projects()
links_list = parse_resources_links()

# Auto-standardize publication images to standard size
standardize_all_publication_images()

print(f"Parsed {len(news_list)} News items.")
print(f"Parsed {len(publications_list)} Publications.")
print(f"Parsed {len(projects_list)} Research Projects.")
print(f"Parsed {len(links_list)} Links sections.")


# Generate HTML
html_out = []

# Header
header_tmpl = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="chrome=1">
    <title>Youngkyoon Jang | Portfolio</title>
    <meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no">
    <meta name="description" content="Personal portfolio of Youngkyoon Jang - Staff ML Engineer at Rivian. Specialized in 3D Vision, Neural Rendering, and Human sensing technologies.">
    <meta name="keywords" content="Youngkyoon Jang, Computer Vision, 3D Vision, Neural Rendering, 3DGS, NeRF, Human Robot Interaction, Researcher Portfolio">
    
    <!-- Modern Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,300;0,400;0,700;1,400;1,700&display=swap" rel="stylesheet">
    
    <!-- Main Stylesheet -->
    <link rel="stylesheet" href="stylesheets/styles.css">
  </head>
  <body class="dark-theme">

    <!-- Floating Theme Switcher -->
    <button id="theme-toggle" class="floating-theme-btn" aria-label="Toggle Theme">
      <!-- Sun Icon -->
      <svg class="sun-icon" viewBox="0 0 24 24"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>
      <!-- Moon Icon -->
      <svg class="moon-icon" viewBox="0 0 24 24"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
    </button>

    <!-- Main Container (Jon Barron Style 1-Column) -->
    <div class="page-container">
      
      <!-- HEADER / PROFILE SECTION -->
      <header class="profile-header">
        <div class="profile-avatar-area">
          <div class="profile-frame">
            <img class="profile-img" src="images/YoungkyoonJang.png" alt="Youngkyoon Jang">
          </div>
          <div class="rivian-logo-container" style="display: flex; justify-content: center; margin-top: 12px;">
            <img src="images/rivian_logo.svg" class="logo-dark" alt="Rivian Icon" style="width: 80px; height: auto;">
            <img src="images/rivian_logo_black.svg" class="logo-light" alt="Rivian Icon" style="width: 80px; height: auto;">
          </div>
        </div>
        
        <div class="profile-info-area">
          <h1 class="profile-name">Youngkyoon Jang</h1>
          <p class="bio-paragraph">
            I am a staff ML engineer on the Autonomy & AI Team at <a href="https://rivian.com/" target="_blank">Rivian</a> (London), where I work on perception for 3D vision and closed-loop simulation. I received my Ph.D. from <a href="http://www.kaist.ac.kr/html/en/" target="_blank">KAIST</a> in 2015, advised by <a href="https://scholar.google.com/citations?user=s3Z4Q1oAAAAJ&hl=en" target="_blank">Woontack Woo</a> (KAIST) and co-advised by <a href="https://sites.google.com/view/tkkim/" target="_blank">Tae-Kyun Kim</a> (Imperial College London).
          </p>
          <p class="bio-paragraph">
            My research explores visual sensing technologies aiming to make interactions between humans and autonomous systems more intuitive in real-world environments. My expertise covers core technical challenges in computer vision and machine learning, focusing on 3D vision, pattern recognition, AR/VR, and human-machine interaction, with publications in top venues such as CVPR, ICCV, IJCV, CVIU, PRL, ISMAR, IEEE VR, TVCG, ICRA, THMS, 3DUI, and HCII.
          </p>
          
          <div class="social-links-row" style="margin-top: 24px;">
            <a href="#" class="tooltip-container" id="email-link" onclick="event.preventDefault(); navigator.clipboard.writeText('youngkyoonjang@gmail.com'); showToast('Copied email to clipboard!');">
              <svg class="social-icon" viewBox="0 0 24 24"><path d="M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/></svg>
              Email
              <span class="tooltip-text">youngkyoonjang@gmail.com (Click to copy)</span>
            </a>
            <a href="files/yjang_cv.pdf" target="_blank">
              <svg class="social-icon" viewBox="0 0 24 24"><path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/></svg>
              CV
            </a>
            <a href="files/yjang_bio.txt" target="_blank">
              <svg class="social-icon" viewBox="0 0 24 24"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>
              Bio
            </a>
            <a href="http://scholar.google.com/citations?user=yQiSin8AAAAJ&hl=en" target="_blank">
              <svg class="social-icon" viewBox="0 0 24 24"><path d="M12 3L1 9l11 6 9-4.91V17h2V9L12 3zM5.89 12.55v2.79c0 1.95 2.74 3.53 6.11 3.53s6.11-1.58 6.11-3.53v-2.79l-6.11 3.33-6.11-3.33z"/></svg>
              Scholar
            </a>
            <a href="https://twitter.com/YoungkyoonJang" target="_blank">
              <svg class="social-icon" viewBox="0 0 24 24"><path d="M22.46 6c-.77.35-1.6.58-2.46.69.88-.53 1.56-1.37 1.88-2.38-.83.5-1.75.85-2.72 1.05C18.37 4.5 17.26 4 16 4c-2.35 0-4.27 1.92-4.27 4.29 0 .34.04.67.11.98C8.28 9.09 5.11 7.38 3 4.79c-.37.63-.58 1.37-.58 2.15 0 1.48.75 2.78 1.9 3.55-.7 0-1.36-.2-1.94-.53v.05c0 2.05 1.46 3.75 3.39 4.14-.36.1-.73.15-1.12.15-.27 0-.54-.03-.8-.08.54 1.68 2.1 2.9 3.95 2.93-1.45 1.13-3.27 1.8-5.25 1.8-.34 0-.68-.02-1-.06C3.9 20.35 6.16 21 8.58 21c7.88 0 12.2-6.53 12.2-12.2 0-.19 0-.37-.01-.56.84-.6 1.56-1.36 2.13-2.23z"/></svg>
              Twitter
            </a>
            <a href="https://github.com/youngkyoonjang" target="_blank">
              <svg class="social-icon" viewBox="0 0 24 24"><path d="M12 2C6.477 2 2 6.477 2 12c0 4.42 2.865 8.167 6.839 9.49.5.092.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.603-3.369-1.34-3.369-1.34-.454-1.156-1.11-1.462-1.11-1.462-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.831.092-.646.35-1.086.636-1.336-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.203 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.579.688.481C19.137 20.164 22 16.418 22 12c0-5.52-4.477-10-10-10z"/></svg>
              GitHub
            </a>
            <a href="https://www.linkedin.com/pub/youngkyoon-jang/12/ab/511" target="_blank">
              <svg class="social-icon" viewBox="0 0 24 24"><path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.32 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.79M6.88 8.56a1.68 1.68 0 0 0 1.68-1.68c0-.93-.75-1.69-1.68-1.69a1.69 1.69 0 0 0-1.69 1.69c0 .93.76 1.68 1.69 1.68m1.39 9.94v-8.37H5.5v8.37h2.77z"/></svg>
              LinkedIn
            </a>
          </div>
        </div>
      </header>

      <main class="main-flow">

        <!-- ================= LATEST NEWS ================= -->
        <section class="flow-section" id="news-section">
          <h2 class="section-title">News</h2>
          <ul class="news-bullet-list">
"""
if OBFUSCATE_EMPLOYER:
    header_tmpl = header_tmpl.replace(
        '<meta name="description" content="Personal portfolio of Youngkyoon Jang - Staff ML Engineer at Rivian. Specialized in 3D Vision, Neural Rendering, and Human sensing technologies.">',
        '<meta name="description" content="Personal portfolio of Youngkyoon Jang - Staff ML Engineer at YYY. Specialized in 3D Vision, Neural Rendering, and Human sensing technologies.">'
    )
    header_tmpl = header_tmpl.replace(
        '<div class="rivian-logo-container" style="display: flex; justify-content: center; margin-top: 12px;">\n            <img src="images/rivian_logo.svg" class="logo-dark" alt="Rivian Icon" style="width: 80px; height: auto;">\n            <img src="images/rivian_logo_black.svg" class="logo-light" alt="Rivian Icon" style="width: 80px; height: auto;">\n          </div>',
        '<div class="rivian-logo-container" style="display: flex; justify-content: center; margin-top: 12px;">\n            <div class="logo-obfuscated" style="font-family: \'Lato\', sans-serif; font-weight: 900; font-size: 1.6rem; letter-spacing: 0.05em; color: var(--text-primary); text-transform: uppercase;">YYY</div>\n          </div>'
    )
    header_tmpl = header_tmpl.replace(
        'I am a staff ML engineer on the Autonomy & AI Team at <a href="https://rivian.com/" target="_blank">Rivian</a> (London)',
        'I am a staff ML engineer on the XXX Team at YYY (London)'
    )

html_out.append(header_tmpl)

# Ingest default news (top 5)
for idx, news in enumerate(news_list):
    if idx == 5:
        html_out.append(f"""          </ul>
          
          <div id="news-details" class="extendable-content">
            <ul class="news-bullet-list" style="margin-top: 10px;">
""")
    html_out.append(f"""              <li>
                <span class="news-date">{news['date']}</span>
                <span class="news-desc">{news['desc']}</span>
              </li>
""")

if len(news_list) > 5:
    html_out.append("""            </ul>
          </div>
          
          <div class="btn-container" style="margin-top: 12px;">
            <button class="extend-btn" data-target="news-details">
              <span>Show Older News</span>
              <svg class="arrow-icon" viewBox="0 0 24 24"><path d="M7 10l5 5 5-5z"/></svg>
            </button>
          </div>
""")
else:
    html_out.append("""          </ul>
""")
html_out.append("""        </section>
""")

# ================= PUBLICATIONS SECTION =================
html_out.append("""
        <!-- ================= PUBLICATIONS ================= -->
        <section class="flow-section" id="publications-section">
          <div class="section-header-row" style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--border-color); padding-bottom: 6px; margin-bottom: 24px; flex-wrap: wrap; gap: 12px;">
            <div style="display: flex; align-items: baseline; gap: 10px; flex-wrap: wrap;">
              <h2 class="section-title" style="border-bottom: none; margin-bottom: 0; padding-bottom: 0;">Publications</h2>
              <span style="font-size: 0.78rem; color: var(--text-secondary); font-weight: 400;">(* indicates equal contribution, <sup>†</sup> indicates corresponding author)</span>
            </div>
            <div class="pub-filters">
              <button class="filter-btn active" data-filter="all">All</button>
              <button class="filter-btn" data-filter="all-inc-domestic">All (+Kor)</button>
              <button class="filter-btn" data-filter="int-journal">Int'l Journals</button>
              <button class="filter-btn" data-filter="int-conference">Int'l Confs</button>
              <button class="filter-btn" data-filter="dom-journal">Kor Journals</button>
              <button class="filter-btn" data-filter="dom-conference">Kor Confs</button>
              <button class="filter-btn" data-filter="etc-pub">Other</button>
            </div>
          </div>

          <div class="publications-flow" id="publications-flow-container">
""")

for pub in publications_list:
    cat = pub['category']
    title = pub['title']
    authors = pub['authors']
    venue = pub['venue']
    venue_full = pub.get('venue_full', '')
    links = pub['links_html']
    prefix = pub['image_prefix']
    
    # Highlight the user's name in authors list (bold instead of underlined)
    authors = authors.replace("<u>", "").replace("</u>", "").strip()
    
    # Check if last author (corresponding author)
    authors_stripped = authors.rstrip('., ')
    is_last = (authors_stripped.endswith("Youngkyoon Jang") or 
               authors_stripped.endswith("Young Kyoon Jang") or 
               authors_stripped.endswith("Youngkyoon Jang*") or 
               authors_stripped.endswith("Young Kyoon Jang*"))
               
    if is_last:
        if "Youngkyoon Jang*" in authors or "Young Kyoon Jang*" in authors:
            authors = authors.replace("Youngkyoon Jang*", "<strong>Youngkyoon Jang*<sup>†</sup></strong>")
            authors = authors.replace("Young Kyoon Jang*", "<strong>Youngkyoon Jang*<sup>†</sup></strong>")
        else:
            authors = authors.replace("Youngkyoon Jang", "<strong>Youngkyoon Jang<sup>†</sup></strong>")
            authors = authors.replace("Young Kyoon Jang", "<strong>Youngkyoon Jang<sup>†</sup></strong>")
    else:
        if "Youngkyoon Jang*" in authors or "Young Kyoon Jang*" in authors:
            authors = authors.replace("Youngkyoon Jang*", "<strong>Youngkyoon Jang*</strong>")
            authors = authors.replace("Young Kyoon Jang*", "<strong>Youngkyoon Jang*</strong>")
        else:
            authors = authors.replace("Youngkyoon Jang", "<strong>Youngkyoon Jang</strong>")
            authors = authors.replace("Young Kyoon Jang", "<strong>Youngkyoon Jang</strong>")
    
    is_domestic = cat in ['dom-journal', 'dom-conference']
    lang_badge_html = '<span class="pub-lang-badge">in Korean</span>' if is_domestic else ""
    
    if prefix:
        entry_class = f"pub-entry {cat}"
        # Determine the thumbnail filename extension (prefer gif if it exists, otherwise png)
        if "multi-layered_random_forest" in prefix or "symbolic_hand_gesture" in prefix:
            thumb_ext = "gif"
            thumb_prefix = "metaphoric_gestures"
        else:
            thumb_ext = "gif" if os.path.exists(f"images/papers/{prefix}_thumbnail.gif") else "png"
            thumb_prefix = prefix
        media_html = f"""
            <div class="entry-media">
              <img src="images/papers/{prefix}_representative.png" class="representative-img" alt="{title} Representative">
              <img src="images/papers/{thumb_prefix}_thumbnail.{thumb_ext}" class="first-page-img" alt="{title} Thumbnail">
            </div>"""
    else:
        entry_class = f"pub-entry {cat} no-image-entry"
        media_html = """
            <div class="entry-media no-video">
              <div class="paper-placeholder-icon">
                <svg viewBox="0 0 24 24">
                  <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z" />
                </svg>
              </div>
            </div>"""
            
    if "metaphoric hand gestures" in title.lower() or "multi-layered random forest" in title.lower() or "smart wristband" in title.lower() or "unified visual perception model and its application" in title.lower():
        entry_class += " no-border-bottom"
            
    if is_domestic:
        entry_class += " hidden"
            
    special_notes = pub.get('special_notes', [])
    special_note_html = ""
    if special_notes:
        badge_htmls = []
        for note in special_notes:
            is_award = any(kw in note.lower() for kw in ["award", "best paper", "excellent paper", "best presentation"])
            badge_class = "pub-note-badge award-highlight" if is_award else "pub-note-badge"
            badge_htmls.append(f'<span class="{badge_class}">{note}</span>')
        special_note_html = "".join(badge_htmls)

    year = pub['date'][0]
    year_str = f", <strong>{year}</strong>" if year > 0 else ""
    if venue_full and venue_full != venue:
        venue_html = f'<div class="pub-venue tooltip-container" style="display: inline-block;"><strong>{venue}</strong>{year_str}<span class="tooltip-text">{venue_full}</span></div>'
    else:
        venue_html = f'<div class="pub-venue" style="display: inline-block;"><strong>{venue}</strong>{year_str}</div>'
            
    korean_raw = pub.get('korean_raw')
    if korean_raw:
        korean_raw_bold = korean_raw.replace("<u>", "<strong>").replace("</u>", "</strong>")
        title_html = f'<span class="tooltip-container">{title}<span class="tooltip-text" style="width: 450px; text-align: left; font-family: sans-serif;">{korean_raw_bold}</span></span>'
    else:
        title_html = title

    html_out.append(f"""
          <div class="{entry_class}">
            {media_html}
            <div class="entry-info">
              <div class="pub-title">{title_html}</div>
              <div class="pub-authors">{authors}</div>
              <div class="pub-venue-row" style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                {venue_html}
                {lang_badge_html}
                {special_note_html}
              </div>
              {f'<div class="pub-links">{links}</div>' if links else ''}
            </div>
          </div>""")

html_out.append("""
          </div>
        </section>
""")


# ================= RESEARCH PROJECTS SECTION =================
html_out.append("""
        <!-- ================= RESEARCH PROJECTS ================= -->
        <section class="flow-section" id="research-section">
          <h2 class="section-title">Research Projects</h2>
          <div class="publications-flow">
""")

for idx, proj in enumerate(projects_list):
    if idx == 5:
        html_out.append(f"""          </div>
          
          <div id="projects-details" class="extendable-content">
            <div class="publications-flow" style="margin-top: 24px;">
""")
    
    prefix = proj['image_prefix']
    if prefix:
        # Determine the thumbnail filename extension (prefer gif if it exists, otherwise png)
        thumb_ext = "gif" if os.path.exists(f"images/papers/{prefix}_thumbnail.gif") else "png"
        media_html = f"""
              <div class="entry-media">
                <img src="images/papers/{prefix}_representative.png" class="representative-img" alt="{proj['title_clean']} Overview">
                <img src="images/papers/{prefix}_thumbnail.{thumb_ext}" class="first-page-img" alt="{proj['title_clean']} Thumbnail">
              </div>"""
    else:
        media_html = """
              <div class="entry-media no-video">
                <div class="paper-placeholder-icon">
                  <svg viewBox="0 0 24 24">
                    <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z" />
                  </svg>
                </div>
              </div>"""
              
    html_out.append(f"""
            <div class="pub-entry">
              {media_html}
              <div class="entry-info">
                <div class="pub-title">{proj['title']}</div>
                <div class="pub-venue" style="font-weight: 400; font-size: 0.85rem; margin-top: 4px;">{proj['desc']}</div>
              </div>
            </div>""")

if len(projects_list) > 5:
    html_out.append("""            </div>
          </div>
          
          <div class="btn-container" style="margin-top: 12px;">
            <button class="extend-btn" data-target="projects-details">
              <span>Show All Projects</span>
              <svg class="arrow-icon" viewBox="0 0 24 24"><path d="M7 10l5 5 5-5z"/></svg>
            </button>
          </div>
""")
else:
    html_out.append("""          </div>
""")
html_out.append("""        </section>
""")


# ================= C.V. / EXPERIENCE SECTION =================
# We read Experience list from index_orig or curriculum_vitae
with open(cv_path, 'r', encoding='utf-8') as f:
    cv_raw_content = f.read()
    
# Experiences
exp_match = re.search(r'Research Experiences</strong></span></div>.*?<ul>(.*?)</ul>', cv_raw_content, re.DOTALL | re.IGNORECASE)
exp_lis = re.findall(r'<li>(.*?)</li>', exp_match.group(1), re.DOTALL | re.IGNORECASE) if exp_match else []

html_out.append("""
        <!-- ================= C.V. & EXPERIENCE ================= -->
        <section class="flow-section" id="cv-section">
          <h2 class="section-title">Professional Appointments</h2>
""")

logo_map = {
    "rivian": ("rivian_logo.svg", "Rivian"),
    "huawei": ("Huawei_logo.png", "Huawei Noah's Ark"),
    "disguise": ("disguise-logo-stack.png", "Disguise"),
    "bristol": ("bristol_logo.png", "Bristol"),
    "queen mary": ("qmul_logo.png", "QMUL"),
    "qmul": ("qmul_logo.png", "QMUL"),
    "cambridge": ("cambridge_logo.png", "Cambridge"),
    "imperial": ("Imperial_logo.jpg", "Imperial College"),
    "icl": ("Imperial_logo.jpg", "Imperial College"),
    "kaist": ("kaist_logo.jpg", "KAIST"),
    "gist": ("gist_logo.png", "GIST")
}

timeline_html = []
timeline_html.append('          <div class="timeline-compact-bar">')

# Sort chronologically (left to right)
def get_start_date(item):
    m_date = re.match(r'^\s*\[(.*?)\]\s*:\s*(.*)', item)
    if not m_date:
        return (9999, 12, 31)
    d_str = m_date.group(1).strip()
    parts = d_str.split('-')
    start_str = parts[0].strip()
    nums = re.findall(r'\d+', start_str)
    y = int(nums[0]) if len(nums) >= 1 else 2008
    m_val = int(nums[1]) if len(nums) >= 2 else 1
    d = int(nums[2]) if len(nums) >= 3 else 1
    return (y, m_val, d)

# Parse nodes first to calculate horizontal positions
def parse_date_range(date_str):
    date_str = date_str.strip('[] ')
    parts = date_str.split('-')
    start_str = parts[0].strip()
    
    # Parse start
    start_nums = re.findall(r'\d+', start_str)
    sy = int(start_nums[0]) if len(start_nums) >= 1 else 2008
    sm = int(start_nums[1]) if len(start_nums) >= 2 else 1
    sd = int(start_nums[2]) if len(start_nums) >= 3 else 1
    
    # Parse end
    if len(parts) > 1:
        end_str = parts[1].strip()
        if "present" in end_str.lower():
            end_val = 2027.0
        else:
            end_nums = re.findall(r'\d+', end_str)
            ey = int(end_nums[0]) if len(end_nums) >= 1 else sy
            em = int(end_nums[1]) if len(end_nums) >= 2 else 12
            ed = int(end_nums[2]) if len(end_nums) >= 3 else 28
            end_val = ey + (em - 1) / 12.0 + (ed - 1) / 365.0
    else:
        ey, em, ed = sy, sm, sd
        end_val = ey + (em - 1) / 12.0 + (ed - 1) / 365.0
        
    start_val = sy + (sm - 1) / 12.0 + (sd - 1) / 365.0
    return start_val, end_val

parsed_nodes = []
for idx, li in enumerate(exp_lis):
    m = re.match(r'^\s*\[(.*?)\]\s*:\s*(.*)', li)
    if not m:
        continue
    date_str = m.group(1).strip()
    desc = m.group(2).strip()
    
    desc_clean = clean_html(desc)
    desc_lower = desc_clean.lower()
    
    logo_file = "gist_logo.png"
    employer_name = "GIST"
    for kw, (logo, name) in logo_map.items():
        if re.search(r'\b' + re.escape(kw) + r'\b', desc_lower) or (kw == "queen mary" and kw in desc_lower):
            logo_file = logo
            employer_name = name
            break
            
    parts = desc_clean.split(',')
    role = parts[0].strip()
    
    full_desc = re.sub(r'<.*?>', '', desc_clean)
    date_display = standardize_cv_date(date_str)
    
    if OBFUSCATE_EMPLOYER:
        role = role.replace("Autonomy & AI Team", "XXX Team").replace("Autonomy & AI team", "XXX team").replace("Rivian", "YYY")
        employer_name = employer_name.replace("Rivian", "YYY")
        full_desc = full_desc.replace("Autonomy & AI Team", "XXX Team").replace("Autonomy & AI team", "XXX team").replace("Rivian", "YYY")

    # Extract start year
    yr_match = re.search(r'(20\d{2}|19\d{2})', date_str)
    year = yr_match.group(1) if yr_match else ""
    
    start_val, end_val = parse_date_range(date_str)
    
    # Classify track: visits/collab vs main career
    is_visit = ("visit" in desc_lower or "visitor" in desc_lower or "collaborator" in desc_lower or "intern" in desc_lower)
    track = "track-visits" if is_visit else "track-career"
    
    if "rivian" in logo_file:
        if OBFUSCATE_EMPLOYER:
            logo_img_html = '<div style="font-size: 11px; font-weight: 800; color: #111; font-family: \'Lato\', sans-serif;">YYY</div>'
        else:
            logo_img_html = '<img src="images/rivian_logo_stack.svg" alt="Rivian">'
    else:
        logo_img_html = f'<img src="images/{logo_file}" alt="{employer_name}">'
        
    parsed_nodes.append({
        'cv_index': idx,
        'start_val': start_val,
        'end_val': end_val,
        'date_str': date_str,
        'date_display': date_display,
        'year': year,
        'role': role,
        'employer_name': employer_name,
        'full_desc': full_desc,
        'logo_img_html': logo_img_html,
        'track': track
    })

# Compute raw percentage positions based on chronology (2008.0 to 2027.0)
TIMELINE_START = 2008.0
TIMELINE_END = 2027.0

for n in parsed_nodes:
    mid_val = (n['start_val'] + n['end_val']) / 2.0
    raw_pct = (mid_val - TIMELINE_START) / (TIMELINE_END - TIMELINE_START) * 100.0
    n['pct'] = raw_pct

# Group by track and sort chronologically
career_nodes = [n for n in parsed_nodes if n['track'] == 'track-career']
visit_nodes = [n for n in parsed_nodes if n['track'] == 'track-visits']

career_nodes.sort(key=lambda x: x['start_val'])
visit_nodes.sort(key=lambda x: x['start_val'])

# Force minimum separation of 4.5% between same-track nodes
def resolve_collisions(nodes, min_distance=4.5, min_bound=2.0, max_bound=98.0):
    n = len(nodes)
    if n <= 1:
        return
    for _ in range(1000):
        # Forward pass
        for i in range(n - 1):
            if nodes[i+1]['pct'] - nodes[i]['pct'] < min_distance:
                overlap = min_distance - (nodes[i+1]['pct'] - nodes[i]['pct'])
                if i == 0:
                    nodes[i+1]['pct'] += overlap
                else:
                    nodes[i]['pct'] -= overlap / 2.0
                    nodes[i+1]['pct'] += overlap / 2.0
        # Clamp
        for i in range(n):
            nodes[i]['pct'] = max(min_bound, min(max_bound, nodes[i]['pct']))
            
        # Backward pass
        for i in range(n - 1, 0, -1):
            if nodes[i]['pct'] - nodes[i-1]['pct'] < min_distance:
                overlap = min_distance - (nodes[i]['pct'] - nodes[i-1]['pct'])
                if i == n - 1:
                    nodes[i-1]['pct'] -= overlap
                else:
                    nodes[i]['pct'] += overlap / 2.0
                    nodes[i-1]['pct'] -= overlap / 2.0
        # Clamp
        for i in range(n):
            nodes[i]['pct'] = max(min_bound, min(max_bound, nodes[i]['pct']))

resolve_collisions(career_nodes)
resolve_collisions(visit_nodes)

# Combine and sort by horizontal position
all_final_nodes = career_nodes + visit_nodes
all_final_nodes.sort(key=lambda x: x['pct'])

# Assign unique IDs and calculate duration bar percentages
for idx, n in enumerate(all_final_nodes):
    n['id'] = f"node-{idx}"
    
    start_pct = (n['start_val'] - TIMELINE_START) / (TIMELINE_END - TIMELINE_START) * 100.0
    end_pct = (n['end_val'] - TIMELINE_START) / (TIMELINE_END - TIMELINE_START) * 100.0
    
    n['start_pct'] = max(2.0, min(98.0, start_pct))
    n['end_pct'] = max(2.0, min(98.0, end_pct))
    n['width_pct'] = max(1.5, n['end_pct'] - n['start_pct'])

# Render background grid lines and ruler years first
timeline_html.append('            <div class="timeline-ruler-axis"></div>')
ruler_years = [2008, 2010, 2012, 2014, 2016, 2018, 2020, 2022, 2024, 2026]
for yr in ruler_years:
    pct = (yr - TIMELINE_START) / (TIMELINE_END - TIMELINE_START) * 100.0
    timeline_html.append(f'''
            <div class="timeline-grid-line" style="left: {pct:.2f}%;"></div>
            <div class="timeline-ruler-tick" style="left: {pct:.2f}%;"></div>
            <div class="timeline-grid-year" style="left: {pct:.2f}%;">{yr}</div>''')

# Render Ph.D. division line (August 2015)
phd_val = 2015.0 + (8 - 1) / 12.0
phd_pct = (phd_val - TIMELINE_START) / (TIMELINE_END - TIMELINE_START) * 100.0
timeline_html.append(f'''
            <div class="timeline-phd-division" style="left: {phd_pct:.2f}%;">
              <div class="timeline-phd-line"></div>
              <div class="timeline-phd-label left">&larr; Pre-doctoral Appointments</div>
              <div class="timeline-phd-label right">Postdoctoral & Academic/Industrial Leadership &rarr;</div>
            </div>''')

# First render all duration bars (so they draw behind the nodes and stems)
for n in all_final_nodes:
    timeline_html.append(f'''
            <div class="timeline-duration-bar {n['track']}" data-duration-id="{n['id']}" style="left: {n['start_pct']:.2f}%; width: {n['width_pct']:.2f}%;"></div>''')

# Then render all nodes with their stems
for n in all_final_nodes:
    timeline_html.append(f'''
            <div class="timeline-node {n['track']}" data-node-id="{n['id']}" style="left: {n['pct']:.2f}%; --mobile-order: {n['cv_index']};">
              <div class="timeline-node-logo">
                {n['logo_img_html']}
              </div>
              <div class="timeline-node-year">{n['year']}</div>
              <div class="timeline-stem"></div>
              <div class="timeline-tooltip">
                <strong>{n['role']}</strong><br>
                <span style="color: var(--text-secondary); font-size: 0.68rem;">{n['employer_name']} &bull; {n['date_display']}</span>
                <hr style="border: none; border-top: 1px solid rgba(255, 255, 255, 0.1); margin: 6px 0;">
                {n['full_desc']}
              </div>
              <div class="timeline-node-desc-mobile">
                <span style="font-weight: 600;">{n['date_display']}</span>: {n['full_desc']}
              </div>
            </div>
    ''')

timeline_html.append('          </div>')
timeline_html.append('        </section>')

html_out.append("\n".join(timeline_html))

html_out.append("""
        <!-- ================= ACADEMIC ACTIVITIES ================= -->
        <section class="flow-section" id="academic-activities-section">
          <h2 class="section-title">Academic Activities</h2>
          <div class="academic-activities-content">
""" + generate_academic_timeline_html() + """
          </div>
        </section>
""")

html_out.append("""          
        <!-- ================= C.V. ACCORDIONS ================= -->
        <section class="flow-section" id="cv-accordions-section">
          <div class="extend-section-wrapper" style="margin-top: 0;">
            
            <!-- Accordion: Honors & Awards -->
            <div class="cv-subsection">
              <button class="extend-btn" data-target="cv-awards">
                <span>Show Honors & Awards</span>
                <svg class="arrow-icon" viewBox="0 0 24 24"><path d="M7 10l5 5 5-5z"/></svg>
              </button>
              <div id="cv-awards" class="extendable-content">
                <ul class="cv-bullets" style="margin-top: 12px;">
""")
for item in cv_details['awards']:
    html_out.append(f"                  <li>{item}</li>\n")
html_out.append("""                </ul>
              </div>
            </div>

            <!-- Accordion: Scholarships -->
            <div class="cv-subsection">
              <button class="extend-btn" data-target="cv-scholarships">
                <span>Show Scholarships</span>
                <svg class="arrow-icon" viewBox="0 0 24 24"><path d="M7 10l5 5 5-5z"/></svg>
              </button>
              <div id="cv-scholarships" class="extendable-content">
                <ul class="cv-bullets" style="margin-top: 12px;">
""")
for item in cv_details['scholarships']:
    html_out.append(f"                  <li>{item}</li>\n")
html_out.append("""                </ul>
              </div>
            </div>



            <!-- Accordion: Teaching Experiences -->
            <div class="cv-subsection">
              <button class="extend-btn" data-target="cv-teaching">
                <span>Show Teaching Experiences</span>
                <svg class="arrow-icon" viewBox="0 0 24 24"><path d="M7 10l5 5 5-5z"/></svg>
              </button>
              <div id="cv-teaching" class="extendable-content">
                <ul class="cv-bullets" style="margin-top: 12px;">
""")
for item in cv_details['teaching']:
    html_out.append(f"                  <li>{item}</li>\n")
html_out.append("""                </ul>
              </div>
            </div>

            <!-- Accordion: Volunteer Experiences -->
            <div class="cv-subsection">
              <button class="extend-btn" data-target="cv-volunteers">
                <span>Show Volunteer Experiences</span>
                <svg class="arrow-icon" viewBox="0 0 24 24"><path d="M7 10l5 5 5-5z"/></svg>
              </button>
              <div id="cv-volunteers" class="extendable-content">
                <ul class="cv-bullets" style="margin-top: 12px;">
""")
for item in cv_details['volunteers']:
    html_out.append(f"                  <li>{item}</li>\n")
html_out.append("""                </ul>
              </div>
            </div>

          </div>
        </section>
""")


# ================= PATENTS & SOFTWARE SECTION =================
html_out.append("""
        <!-- ================= PATENTS & SOFTWARE ================= -->
        <section class="flow-section" id="patents-section">
          <h2 class="section-title">Patents & Software Registrations</h2>
          <div class="extend-section-wrapper" style="margin-top: 0;">

            <!-- Accordion: International Patents -->
            <div class="cv-subsection">
              <button class="extend-btn" data-target="patents-int">
                <span>Show International Patents (registered)</span>
                <svg class="arrow-icon" viewBox="0 0 24 24"><path d="M7 10l5 5 5-5z"/></svg>
              </button>
              <div id="patents-int" class="extendable-content">
                <ul class="patents-bullet-list" style="margin-top: 12px;">
""")
for item in patents_list['int-patent']:
    html_out.append(f"                  <li>{item}</li>\n")
html_out.append("""                </ul>
              </div>
            </div>

            <!-- Accordion: Domestic Patents (registered) -->
            <div class="cv-subsection">
              <button class="extend-btn" data-target="patents-dom-reg">
                <span>Show Domestic Patents (registered)</span>
                <svg class="arrow-icon" viewBox="0 0 24 24"><path d="M7 10l5 5 5-5z"/></svg>
              </button>
              <div id="patents-dom-reg" class="extendable-content">
                <ul class="patents-bullet-list" style="margin-top: 12px;">
""")
for item in patents_list['dom-patent-registered']:
    html_out.append(f"                  <li>{item}</li>\n")
html_out.append("""                </ul>
              </div>
            </div>

            <!-- Accordion: Domestic Patents (pending) -->
            <div class="cv-subsection">
              <button class="extend-btn" data-target="patents-dom-pend">
                <span>Show Domestic Patents (pending)</span>
                <svg class="arrow-icon" viewBox="0 0 24 24"><path d="M7 10l5 5 5-5z"/></svg>
              </button>
              <div id="patents-dom-pend" class="extendable-content">
                <ul class="patents-bullet-list" style="margin-top: 12px;">
""")
for item in patents_list['dom-patent-pending']:
    html_out.append(f"                  <li>{item}</li>\n")
html_out.append("""                </ul>
              </div>
            </div>

            <!-- Accordion: Software Registrations -->
            <div class="cv-subsection">
              <button class="extend-btn" data-target="patents-sw">
                <span>Show Software Registrations</span>
                <svg class="arrow-icon" viewBox="0 0 24 24"><path d="M7 10l5 5 5-5z"/></svg>
              </button>
              <div id="patents-sw" class="extendable-content">
                <ul class="patents-bullet-list" style="margin-top: 12px;">
""")
for item in patents_list['sw-registration']:
    html_out.append(f"                  <li>{item}</li>\n")
html_out.append("""                </ul>
              </div>
            </div>

          </div>
        </section>
""")


# ================= RESOURCES & LINKS SECTION =================
html_out.append("""
        <!-- ================= RESOURCES & LINKS ================= -->
        <section class="flow-section" id="links-section">
          <h2 class="section-title">Resources & Links</h2>
          <div class="cv-subsection">
            <button class="extend-btn" data-target="links-accordion">
              <span>Show All Resources & Links</span>
              <svg class="arrow-icon" viewBox="0 0 24 24"><path d="M7 10l5 5 5-5z"/></svg>
            </button>
            <div id="links-accordion" class="extendable-content">
              <div class="links-flow-grid" style="margin-top: 24px;">
""")

for sec in links_list:
    html_out.append(f"""                <div class="link-flow-card">
                  <h3>{sec['title']}</h3>
                  <ul class="flow-styled-links">
""")
    for link in sec['links']:
        html_out.append(f"                    <li>{link}</li>\n")
    html_out.append("""                  </ul>
                </div>
""")

html_out.append("""              </div>
            </div>
          </div>
        </section>

      </main>

      <!-- SIMPLE FOOTER -->
      <footer class="simple-footer">
        <p>&copy; 2026 Youngkyoon Jang. All rights reserved.</p>
        <p>Theme inspired by bmild &amp; jonbarron.</p>
      </footer>

    </div>

    <!-- JS Logic -->
    <script>
      function showToast(message) {
        let toast = document.getElementById('custom-toast');
        if (!toast) {
          toast = document.createElement('div');
          toast.id = 'custom-toast';
          toast.style.position = 'fixed';
          toast.style.bottom = '24px';
          toast.style.left = '50%';
          toast.style.transform = 'translateX(-50%)';
          toast.style.background = 'rgba(30, 30, 35, 0.9)';
          toast.style.color = '#fff';
          toast.style.padding = '10px 20px';
          toast.style.borderRadius = '8px';
          toast.style.border = '1px solid rgba(255, 255, 255, 0.1)';
          toast.style.backdropFilter = 'blur(10px)';
          toast.style.fontSize = '0.85rem';
          toast.style.boxShadow = '0 8px 30px rgba(0,0,0,0.3)';
          toast.style.zIndex = '1000';
          toast.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
          toast.style.opacity = '0';
          document.body.appendChild(toast);
        }
        toast.innerText = message;
        toast.style.opacity = '1';
        toast.style.transform = 'translateX(-50%) translateY(-10px)';
        setTimeout(() => {
          toast.style.opacity = '0';
          toast.style.transform = 'translateX(-50%)';
        }, 2500);
      }

      document.addEventListener('DOMContentLoaded', () => {
        // Theme toggle
        const themeToggle = document.getElementById('theme-toggle');
        themeToggle.addEventListener('click', () => {
          if (document.body.classList.contains('dark-theme')) {
            document.body.classList.replace('dark-theme', 'light-theme');
            localStorage.setItem('theme', 'light');
          } else {
            document.body.classList.replace('light-theme', 'dark-theme');
            localStorage.setItem('theme', 'dark');
          }
        });
        
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'light') {
          document.body.classList.replace('dark-theme', 'light-theme');
        } else {
          document.body.classList.add('dark-theme');
        }

        // Expandable content
        const extendBtns = document.querySelectorAll('.extend-btn');
        extendBtns.forEach(btn => {
          btn.addEventListener('click', () => {
            const targetId = btn.getAttribute('data-target');
            const target = document.getElementById(targetId);
            btn.classList.toggle('active');
            target.classList.toggle('expanded');
            
            const textSpan = btn.querySelector('span');
            if (textSpan) {
              const currentText = textSpan.innerText;
              if (currentText.includes('Show')) {
                textSpan.innerText = currentText.replace('Show', 'Hide');
              } else if (currentText.includes('Hide')) {
                textSpan.innerText = currentText.replace('Hide', 'Show');
              }
            }
          });
        });

        // Publications Filter
        const filterBtns = document.querySelectorAll('.filter-btn');
        const pubEntries = document.querySelectorAll('#publications-flow-container .pub-entry');
        
        filterBtns.forEach(btn => {
          btn.addEventListener('click', () => {
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            const filter = btn.getAttribute('data-filter');
            pubEntries.forEach(entry => {
              if (filter === 'all') {
                if (entry.classList.contains('dom-journal') || entry.classList.contains('dom-conference')) {
                  entry.classList.add('hidden');
                } else {
                  entry.classList.remove('hidden');
                }
              } else if (filter === 'all-inc-domestic') {
                entry.classList.remove('hidden');
              } else {
                if (entry.classList.contains(filter)) {
                  entry.classList.remove('hidden');
                } else {
                  entry.classList.add('hidden');
                }
              }
            });
          });
        });

        // Mobile Tooltips support
        const tooltips = document.querySelectorAll('.tooltip-container');
        tooltips.forEach(tooltip => {
          tooltip.addEventListener('click', (e) => {
            e.stopPropagation();
            // Close other tooltips
            tooltips.forEach(t => {
              if (t !== tooltip) t.classList.remove('active');
            });
            tooltip.classList.toggle('active');
          });
        });
        
        // Close tooltips when clicking anywhere else
        document.addEventListener('click', () => {
          tooltips.forEach(t => t.classList.remove('active'));
        });

        // Highlight matching duration bar when hovering over a logo
        const timelineNodes = document.querySelectorAll('.timeline-node');
        timelineNodes.forEach(node => {
          const nodeId = node.getAttribute('data-node-id');
          const durationBar = document.querySelector(`.timeline-duration-bar[data-duration-id="${nodeId}"]`);
          if (durationBar) {
            node.addEventListener('mouseenter', () => {
              durationBar.classList.add('highlight');
            });
            node.addEventListener('mouseleave', () => {
              durationBar.classList.remove('highlight');
            });
          }
        });
      });
    </script>

    <!-- ==========================================
         Floating Feedback Widget (Self-Contained)
         ========================================== -->
    <style>
      .feedback-fab {
        position: fixed;
        bottom: 24px;
        right: 24px;
        z-index: 9999;
        background: var(--bg-secondary);
        border: 1px solid var(--border-color);
        color: var(--text-primary);
        padding: 10px 16px;
        border-radius: 50px;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.85rem;
        font-family: inherit;
        font-weight: 600;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
      }
      .feedback-fab:hover {
        transform: translateY(-3px);
        border-color: var(--accent-color);
        box-shadow: 0 6px 20px rgba(var(--accent-color-rgb), 0.25);
      }
      .feedback-fab-icon {
        font-size: 1.05rem;
      }
      .feedback-card {
        position: fixed;
        bottom: 80px;
        right: 24px;
        width: 320px;
        max-height: 480px;
        z-index: 9999;
        border: 1px solid var(--border-color);
        border-radius: 16px;
        box-shadow: var(--shadow-lg), 0 8px 32px rgba(0, 0, 0, 0.12);
        display: flex;
        flex-direction: column;
        overflow: hidden;
        font-family: inherit;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        transform: translateY(15px);
        opacity: 0;
        pointer-events: none;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
      }
      body.dark-theme .feedback-card {
        background: rgba(30, 41, 59, 0.9);
        border-color: rgba(255, 255, 255, 0.1);
      }
      body.light-theme .feedback-card {
        background: rgba(255, 255, 255, 0.9);
        border-color: rgba(0, 0, 0, 0.08);
      }
      .feedback-card.show {
        transform: translateY(0);
        opacity: 1;
        pointer-events: auto;
      }
      .feedback-header {
        padding: 12px 16px;
        border-bottom: 1px solid var(--border-color);
        display: flex;
        align-items: center;
        justify-content: space-between;
      }
      .feedback-header h3 {
        font-size: 0.95rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0;
      }
      .feedback-close-btn {
        background: none;
        border: none;
        color: var(--text-secondary);
        font-size: 1.2rem;
        cursor: pointer;
        line-height: 1;
        padding: 2px;
        transition: color 0.2s;
      }
      .feedback-close-btn:hover {
        color: var(--text-primary);
      }
      .feedback-body {
        display: flex;
        flex-direction: column;
        overflow-y: auto;
      }
      .feedback-desc {
        padding: 12px 16px 4px 16px;
        font-size: 0.75rem;
        color: var(--text-secondary);
        line-height: 1.4;
      }
      .feedback-comments-section {
        padding: 8px 16px;
      }
      .feedback-comments-section h4 {
        font-size: 0.75rem;
        font-weight: 700;
        color: var(--text-secondary);
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
      }
      .feedback-comments-list {
        display: flex;
        flex-direction: column;
        gap: 8px;
        max-height: 160px;
        overflow-y: auto;
        padding-right: 2px;
      }
      .feedback-comment-item {
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        padding: 8px 10px;
        border-radius: 10px;
        font-size: 0.75rem;
        line-height: 1.4;
        animation: feedbackSlideIn 0.25s ease;
      }
      @keyframes feedbackSlideIn {
        from { opacity: 0; transform: translateY(4px); }
        to { opacity: 1; transform: translateY(0); }
      }
      .feedback-comment-meta {
        display: flex;
        justify-content: space-between;
        margin-bottom: 2px;
        font-weight: 600;
        color: var(--accent-color);
      }
      .feedback-comment-time {
        font-weight: normal;
        color: var(--text-secondary);
        font-size: 0.65rem;
      }
      .feedback-comment-text {
        color: var(--text-primary);
        word-break: break-all;
      }
      .feedback-empty-state {
        text-align: center;
        color: var(--text-secondary);
        font-size: 0.75rem;
        padding: 16px 0;
        font-style: italic;
      }
      .feedback-form {
        padding: 12px 16px 16px 16px;
        display: flex;
        flex-direction: column;
        gap: 8px;
        border-top: 1px solid var(--border-color);
      }
      .feedback-input {
        width: 100%;
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        color: var(--text-primary);
        padding: 7px 10px;
        border-radius: 8px;
        font-size: 0.75rem;
        font-family: inherit;
        outline: none;
        transition: border-color 0.2s, box-shadow 0.2s;
      }
      .feedback-input:focus {
        border-color: var(--accent-color);
        box-shadow: 0 0 0 2px rgba(var(--accent-color-rgb), 0.15);
      }
      .feedback-textarea {
        resize: none;
      }
      .feedback-submit-btn {
        width: 100%;
        background: var(--accent-color);
        color: #ffffff;
        border: none;
        padding: 8px;
        border-radius: 8px;
        font-size: 0.8rem;
        font-weight: 600;
        cursor: pointer;
        font-family: inherit;
        transition: background 0.2s, transform 0.1s;
      }
      .feedback-submit-btn:hover {
        background: var(--accent-hover);
      }
      .feedback-submit-btn:active {
        transform: scale(0.98);
      }
      .feedback-view-all-btn {
        background: none;
        border: none;
        color: var(--accent-color);
        font-size: 0.75rem;
        font-weight: 600;
        cursor: pointer;
        padding: 4px 0 0 0;
        margin-top: 4px;
        display: none;
        align-items: center;
        gap: 4px;
        font-family: inherit;
        transition: color 0.2s;
        text-decoration: underline;
      }
      .feedback-view-all-btn:hover {
        color: var(--accent-hover);
      }
      @media (max-width: 480px) {
        .feedback-fab {
          bottom: 16px;
          right: 16px;
          padding: 8px 12px;
          font-size: 0.8rem;
        }
        .feedback-card {
          bottom: 68px;
          right: 16px;
          width: calc(100vw - 32px);
          max-height: 380px;
        }
      }
    </style>

    <button id="feedback-fab" class="feedback-fab" aria-label="Leave feedback(피드백)">
      <span class="feedback-fab-icon">💬</span>
      <span class="feedback-fab-text">Feedback(피드백)</span>
    </button>

    <div id="feedback-card" class="feedback-card">
      <div class="feedback-header">
        <h3>Feedback(피드백) 💬</h3>
        <button id="feedback-close-btn" class="feedback-close-btn" aria-label="Close">&times;</button>
      </div>
      <div class="feedback-body">
        <p class="feedback-desc">Feel free to leave any suggestions or comments to improve the website!</p>
        
        <div class="feedback-comments-section">
          <h4>Recent Feedback</h4>
          <div id="feedback-comments-list" class="feedback-comments-list">
            <!-- Dynamically populated -->
          </div>
          <button id="feedback-view-all-btn" class="feedback-view-all-btn">View All</button>
        </div>

        <form id="feedback-form" class="feedback-form">
          <input type="text" id="feedback-name-input" class="feedback-input" placeholder="Name / Nickname" required maxlength="20">
          <textarea id="feedback-text-input" class="feedback-input feedback-textarea" placeholder="Type your feedback here (max 150 chars)..." required maxlength="150" rows="3"></textarea>
          <button type="submit" class="feedback-submit-btn">Submit</button>
        </form>
      </div>
    </div>

    <script>
      document.addEventListener('DOMContentLoaded', () => {
        const fab = document.getElementById('feedback-fab');
        const card = document.getElementById('feedback-card');
        const closeBtn = document.getElementById('feedback-close-btn');
        const form = document.getElementById('feedback-form');
        const list = document.getElementById('feedback-comments-list');
        const viewAllBtn = document.getElementById('feedback-view-all-btn');
        let showAll = false;

        // Toggle card open/close
        fab.addEventListener('click', (e) => {
          e.stopPropagation();
          card.classList.toggle('show');
        });

        closeBtn.addEventListener('click', (e) => {
          e.stopPropagation();
          card.classList.remove('show');
        });

        // Close on clicking outside card
        document.addEventListener('click', (e) => {
          if (!card.contains(e.target) && e.target !== fab && !fab.contains(e.target)) {
            card.classList.remove('show');
          }
        });

        // Fetch & render comments
        const staticComments = """ + static_comments_js + """;

        function getLocalComments() {
          try {
            let comments = JSON.parse(localStorage.getItem('yj_feedback_comments')) || [];
            // Clean up any legacy test comments containing 'Antigravity'
            const cleaned = comments.filter(c => c.name && !c.name.includes('Antigravity'));
            if (cleaned.length !== comments.length) {
              localStorage.setItem('yj_feedback_comments', JSON.stringify(cleaned));
            }
            return cleaned;
          } catch(e) {
            return [];
          }
        }

        function saveLocalComment(comment) {
          const comments = getLocalComments();
          comments.unshift(comment); // Add new comment to beginning
          localStorage.setItem('yj_feedback_comments', JSON.stringify(comments));
        }

        function renderComments() {
          const localComments = getLocalComments();
          
          // Deduplicate comments with the same name and text (e.g. from previous local caching)
          const mergedComments = [];
          const seenKeys = new Set();
          [...localComments, ...staticComments].forEach(c => {
            const key = `${c.name || ''}|${c.text || ''}`;
            if (!seenKeys.has(key)) {
              seenKeys.add(key);
              mergedComments.push(c);
            }
          });
          
          const allComments = mergedComments;
          list.innerHTML = '';
          
          if (allComments.length === 0) {
            list.innerHTML = '<div class="feedback-empty-state">No feedback yet. Be the first! 😊</div>';
            viewAllBtn.style.display = 'none';
            return;
          }

          if (allComments.length > 3) {
            viewAllBtn.style.display = 'inline-block';
            viewAllBtn.textContent = showAll ? 'Show Less' : 'View All';
          } else {
            viewAllBtn.style.display = 'none';
          }

          // Show only latest 3 or all depending on state
          const commentsToRender = showAll ? allComments : allComments.slice(0, 3);
          commentsToRender.forEach(c => {
            const item = document.createElement('div');
            item.className = 'feedback-comment-item';
            
            const meta = document.createElement('div');
            meta.className = 'feedback-comment-meta';
            
            const nameSpan = document.createElement('span');
            nameSpan.textContent = c.name || 'Anonymous';
            
            const timeSpan = document.createElement('span');
            timeSpan.className = 'feedback-comment-time';
            timeSpan.textContent = c.time || '';
            
            meta.appendChild(nameSpan);
            meta.appendChild(timeSpan);
            
            const textDiv = document.createElement('div');
            textDiv.className = 'feedback-comment-text';
            textDiv.textContent = c.text || '';
            
            item.appendChild(meta);
            item.appendChild(textDiv);
            list.appendChild(item);
          });
        }

        viewAllBtn.addEventListener('click', (e) => {
          e.stopPropagation();
          showAll = !showAll;
          renderComments();
        });

        // Handle form submission
        form.addEventListener('submit', (e) => {
          e.preventDefault();
          const nameInput = document.getElementById('feedback-name-input');
          const textInput = document.getElementById('feedback-text-input');
          
          const name = nameInput.value.trim();
          const text = textInput.value.trim();
          
          if (!name || !text) return;

          // Cute formatting for time
          const now = new Date();
          const timeStr = `${now.getMonth() + 1}/${now.getDate()} ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;

          const comment = { name, text, time: timeStr };
          saveLocalComment(comment);
          renderComments();

          // Reset inputs
          nameInput.value = '';
          textInput.value = '';
        });

        // Initialize comments on load
        renderComments();
      });
    </script>
  </body>
</html>
""")

# Save generated index.html
with open(index_path, 'w', encoding='utf-8') as f:
    f.write("".join(html_out))

# Bio text obfuscation handling
bio_src = os.path.join(script_dir, "files/yjang_bio_src.txt")
bio_dest = os.path.join(script_dir, "files/yjang_bio.txt")

if not os.path.exists(bio_src) and os.path.exists(bio_dest):
    import shutil
    shutil.copyfile(bio_dest, bio_src)
    print("Created backup of original bio at files/yjang_bio_src.txt")

if os.path.exists(bio_src):
    with open(bio_src, 'r', encoding='utf-8') as f:
        bio_content = f.read()
    
    if OBFUSCATE_EMPLOYER:
        bio_content = bio_content.replace("Autonomy & AI team", "XXX team")
        bio_content = bio_content.replace("Autonomy & AI Team", "XXX Team")
        bio_content = bio_content.replace("Rivian", "YYY")
        print("Obfuscated bio content loaded from source backup.")
    else:
        print("Original bio content loaded from source backup.")
        
    with open(bio_dest, 'w', encoding='utf-8') as f:
        f.write(bio_content)
    print("Saved files/yjang_bio.txt")

status_str = "obfuscated" if OBFUSCATE_EMPLOYER else "original"
print(f"Successfully compiled and saved index.html ({status_str} mode)!")
