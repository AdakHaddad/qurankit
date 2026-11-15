#!/usr/bin/env python3
"""Generate comprehensive sample data for all extension adapters across all 114 surahs."""

import json
import random
from pathlib import Path

# Qur'anic metadata
SURAH_NAMES = {
    1: ("الفاتحة", "Al-Fatihah", 7, "Meccan"),
    2: ("البقرة", "Al-Baqarah", 286, "Medinan"),
    3: ("آل عمران", "Aal-Imran", 200, "Medinan"),
    4: ("النساء", "An-Nisa", 176, "Medinan"),
    5: ("المائدة", "Al-Maidah", 120, "Medinan"),
    6: ("الأنعام", "Al-An'am", 165, "Meccan"),
    7: ("الأعراف", "Al-A'raf", 206, "Meccan"),
    8: ("الأنفال", "Al-Anfal", 75, "Medinan"),
    9: ("التوبة", "At-Tawbah", 129, "Medinan"),
    10: ("يونس", "Yunus", 109, "Meccan"),
    11: ("هود", "Hud", 123, "Meccan"),
    12: ("يوسف", "Yusuf", 111, "Meccan"),
    13: ("الرعد", "Ar-Ra'd", 43, "Medinan"),
    14: ("إبراهيم", "Ibrahim", 52, "Meccan"),
    15: ("الحجر", "Al-Hijr", 99, "Meccan"),
    16: ("النحل", "An-Nahl", 128, "Meccan"),
    17: ("الإسراء", "Al-Isra", 111, "Meccan"),
    18: ("الكهف", "Al-Kahf", 110, "Meccan"),
    19: ("مريم", "Maryam", 98, "Meccan"),
    20: ("طه", "Ta-Ha", 135, "Meccan"),
    21: ("الأنبياء", "Al-Anbiya", 112, "Meccan"),
    22: ("الحج", "Al-Hajj", 78, "Medinan"),
    23: ("المؤمنون", "Al-Mu'minun", 118, "Meccan"),
    24: ("النور", "An-Nur", 64, "Medinan"),
    25: ("الفرقان", "Al-Furqan", 77, "Meccan"),
    26: ("الشعراء", "Ash-Shu'ara", 227, "Meccan"),
    27: ("النمل", "An-Naml", 93, "Meccan"),
    28: ("القصص", "Al-Qasas", 88, "Meccan"),
    29: ("العنكبوت", "Al-Ankabut", 69, "Meccan"),
    30: ("الروم", "Ar-Rum", 60, "Meccan"),
    31: ("لقمان", "Luqman", 34, "Meccan"),
    32: ("السجدة", "As-Sajdah", 30, "Meccan"),
    33: ("الأحزاب", "Al-Ahzab", 73, "Medinan"),
    34: ("سبأ", "Saba", 54, "Meccan"),
    35: ("فاطر", "Fatir", 45, "Meccan"),
    36: ("يس", "Ya-Sin", 83, "Meccan"),
    37: ("الصافات", "As-Saffat", 182, "Meccan"),
    38: ("ص", "Sad", 88, "Meccan"),
    39: ("الزمر", "Az-Zumar", 75, "Meccan"),
    40: ("غافر", "Ghafir", 85, "Meccan"),
    41: ("فصلت", "Fussilat", 54, "Meccan"),
    42: ("الشورى", "Ash-Shura", 53, "Meccan"),
    43: ("الزخرف", "Az-Zukhruf", 89, "Meccan"),
    44: ("الدخان", "Ad-Dukhan", 59, "Meccan"),
    45: ("الجاثية", "Al-Jathiyah", 37, "Meccan"),
    46: ("الأحقاف", "Al-Ahqaf", 35, "Meccan"),
    47: ("محمد", "Muhammad", 38, "Medinan"),
    48: ("الفتح", "Al-Fath", 29, "Medinan"),
    49: ("الحجرات", "Al-Hujurat", 18, "Medinan"),
    50: ("ق", "Qaf", 45, "Meccan"),
    51: ("الذاريات", "Adh-Dhariyat", 60, "Meccan"),
    52: ("الطور", "At-Tur", 49, "Meccan"),
    53: ("النجم", "An-Najm", 62, "Meccan"),
    54: ("القمر", "Al-Qamar", 55, "Meccan"),
    55: ("الرحمن", "Ar-Rahman", 78, "Meccan"),
    56: ("الواقعة", "Al-Waqiah", 96, "Meccan"),
    57: ("الحديد", "Al-Hadid", 29, "Medinan"),
    58: ("المجادلة", "Al-Mujadila", 22, "Medinan"),
    59: ("الحشر", "Al-Hashr", 24, "Medinan"),
    60: ("الممتحنة", "Al-Mumtahanah", 13, "Medinan"),
    61: ("الصف", "As-Saff", 14, "Medinan"),
    62: ("الجمعة", "Al-Jumu'ah", 11, "Medinan"),
    63: ("المنافقون", "Al-Munafiqun", 11, "Medinan"),
    64: ("التغابن", "At-Taghabun", 18, "Medinan"),
    65: ("الطلاق", "At-Talaq", 12, "Medinan"),
    66: ("التحريم", "At-Tahrim", 12, "Medinan"),
    67: ("الملك", "Al-Mulk", 30, "Meccan"),
    68: ("القلم", "Al-Qalam", 52, "Meccan"),
    69: ("الحاقة", "Al-Haqqah", 52, "Meccan"),
    70: ("المعارج", "Al-Ma'arij", 44, "Meccan"),
    71: ("نوح", "Nuh", 28, "Meccan"),
    72: ("الجن", "Al-Jinn", 28, "Meccan"),
    73: ("المزمل", "Al-Muzzammil", 20, "Meccan"),
    74: ("المدثر", "Al-Muddaththir", 56, "Meccan"),
    75: ("القيامة", "Al-Qiyamah", 40, "Meccan"),
    76: ("الإنسان", "Al-Insan", 31, "Medinan"),
    77: ("المرسلات", "Al-Mursalat", 50, "Meccan"),
    78: ("النبأ", "An-Naba", 40, "Meccan"),
    79: ("النازعات", "An-Nazi'at", 46, "Meccan"),
    80: ("عبس", "Abasa", 42, "Meccan"),
    81: ("التكوير", "At-Takwir", 29, "Meccan"),
    82: ("الانفطار", "Al-Infitar", 19, "Meccan"),
    83: ("المطففين", "Al-Mutaffifin", 36, "Meccan"),
    84: ("الانشقاق", "Al-Inshiqaq", 25, "Meccan"),
    85: ("البروج", "Al-Buruj", 22, "Meccan"),
    86: ("الطارق", "At-Tariq", 17, "Meccan"),
    87: ("الأعلى", "Al-A'la", 19, "Meccan"),
    88: ("الغاشية", "Al-Ghashiyah", 26, "Meccan"),
    89: ("الفجر", "Al-Fajr", 30, "Meccan"),
    90: ("البلد", "Al-Balad", 20, "Meccan"),
    91: ("الشمس", "Ash-Shams", 15, "Meccan"),
    92: ("الليل", "Al-Layl", 21, "Meccan"),
    93: ("الضحى", "Ad-Duha", 11, "Meccan"),
    94: ("الشرح", "Ash-Sharh", 8, "Meccan"),
    95: ("التين", "At-Tin", 8, "Meccan"),
    96: ("العلق", "Al-Alaq", 19, "Meccan"),
    97: ("القدر", "Al-Qadr", 5, "Meccan"),
    98: ("البينة", "Al-Bayyinah", 8, "Medinan"),
    99: ("الزلزلة", "Az-Zalzalah", 8, "Medinan"),
    100: ("العاديات", "Al-Adiyat", 11, "Meccan"),
    101: ("القارعة", "Al-Qari'ah", 11, "Meccan"),
    102: ("التكاثر", "At-Takathur", 8, "Meccan"),
    103: ("العصر", "Al-Asr", 3, "Meccan"),
    104: ("الهمزة", "Al-Humazah", 9, "Meccan"),
    105: ("الفيل", "Al-Fil", 5, "Meccan"),
    106: ("قريش", "Quraysh", 4, "Meccan"),
    107: ("الماعون", "Al-Ma'un", 7, "Meccan"),
    108: ("الكوثر", "Al-Kawthar", 3, "Meccan"),
    109: ("الكافرون", "Al-Kafirun", 6, "Meccan"),
    110: ("النصر", "An-Nasr", 3, "Medinan"),
    111: ("المسد", "Al-Masad", 5, "Meccan"),
    112: ("الإخلاص", "Al-Ikhlas", 4, "Meccan"),
    113: ("الفلق", "Al-Falaq", 5, "Meccan"),
    114: ("الناس", "An-Nas", 6, "Meccan"),
}

# Sample tafsir templates
TAFSIR_TEMPLATES = [
    ("linguistic", "Analysis of key Arabic terms and their linguistic nuances"),
    ("theological", "Theological implications and doctrinal points"),
    ("historical", "Historical context and reasons for revelation (asbab al-nuzul)"),
    ("comparative", "Comparative analysis with other verses"),
    ("legal", "Legal rulings derived from this verse"),
    ("spiritual", "Spiritual and ethical lessons"),
]

# Sample hadith collections
HADITH_COLLECTIONS = [
    ("sahih_bukhari", "صحيح البخاري"),
    ("sahih_muslim", "صحيح مسلم"),
    ("sunan_abu_dawood", "سنن أبي داود"),
    ("sunan_tirmidhi", "سنن الترمذي"),
    ("sunan_nasai", "سنن النسائي"),
    ("sunan_ibn_majah", "سنن ابن ماجه"),
]

# Sample qiraat
QIRAAT_LIST = [
    ("hafs_an_asim", "حفص عن عاصم", "Shatibiyyah"),
    ("warsh_an_nafi", "ورش عن نافع", "Tayyibah"),
    ("qaloon_an_nafi", "قالون عن نافع", "Tayyibah"),
    ("ad_duri_an_abi_amr", "الدوري عن أبي عمرو", "Shatibiyyah"),
    ("al_bazzi_an_ibn_kathir", "البزي عن ابن كثير", "Shatibiyyah"),
]

# Tajwid rules by category
TAJWID_RULES = [
    # Noon sakinah / tanwin
    ("ghunnah_noon_sakinah", "ghunnah", "Ghunnah for Noon Sakinah/Tanwin", "الغنة في النون الساكنة والتنوين", ["م", "ن", "ي", "و"]),
    ("idgham_yalmalun_ghunnah", "idgham", "Idgham with Ghunnah (Ya, Nun, Mim, Waw)", "إدغام مع الغنة", ["ي", "ن", "م", "و"]),
    ("idgham_yalmalun_no_ghunnah", "idgham", "Idgham without Ghunnah (Ra, Lam)", "إدغام بلا غنة", ["ر", "ل"]),
    ("ikhfa_haqiqi", "ikhfa", "Ikhfa Haqiqi (Real Concealment)", "الإخفاء الحقيقي", ["ت", "ث", "ج", "د", "ذ", "ز", "س", "ش", "ص", "ض", "ط", "ظ", "ف", "ق", "ك"]),
    ("izhar_halqi", "izhar", "Izhar Halqi (Throat Letters)", "الإظهار الحلق", ["ء", "ه", "ع", "ح", "غ", "خ"]),
    # Meem sakinah
    ("idgham_shafawi", "idgham", "Idgham Shafawi (Meem into Meem)", "الإدغام الشفوي", ["م"]),
    ("ikhfa_shafawi", "ikhfa", "Ikhfa Shafawi (Meem before Ba)", "الإخفاء الشفوي", ["ب"]),
    ("izhar_shafawi", "izhar", "Izhar Shafawi (Meem before other)", "الإظهار الشفوي", ["rest"]),
    # Madd
    ("madd_asli", "madd", "Madd Asli (Natural)", "المد الطبيعي", ["ا", "و", "ي"]),
    ("madd_far_i", "madd", "Madd Far'i (Secondary)", "المد الفرعي", ["hamza_after", "sukoon_after"]),
    ("madd_badal", "madd", "Madd Badal (Substitute)", "المد بدل", ["hamza_before"]),
    ("madd_lin", "madd", "Madd Lin (Soft)", "المد اللين", ["waw_ya_before_sukoon"]),
    # Qalqalah
    ("qalqalah_kubra", "qalqalah", "Qalqalah Kubra (Major)", "القلقلة الكبرى", ["ق", "ط", "ب", "ج", "د"]),
    ("qalqalah_sughra", "qalqalah", "Qalqalah Sughra (Minor)", "القلقلة الصغرى", ["ق", "ط", "ب", "ج", "د"]),
]

# Waqf signs
WAQF_TYPES = [
    ("waqf_tamm", "۝", "Waqf Tamm (Complete Stop)", "الوقف التام", "Complete meaning"),
    ("waqf_kafi", "۞", "Waqf Kafi (Sufficient Stop)", "الوقف الكافي", "Sufficient meaning"),
    ("waqf_hasan", "ۗ", "Waqf Hasan (Good Stop)", "الوقف الحسن", "Good meaning"),
    ("waqf_ghayr_kafi", "ۖ", "Waqf Ghayr Kafi (Insufficient)", "الوقف غير الكافي", "Insufficient meaning"),
    ("ibtida_jaiz", "", "Ibtida Jaiz (Permissible Start)", "الابتداء الجائز", "Permissible beginning"),
    ("ibtida_mustahabb", "", "Ibtida Mustahabb (Recommended Start)", "الابتداء المستحب", "Recommended beginning"),
]

def generate_tafsir_data():
    """Generate comprehensive tafsir sample data for all surahs."""
    output = []
    entry_id = 1
    
    for surah_num, (name_ar, name_en, ayah_count, revelation) in SURAH_NAMES.items():
        # Generate 1-3 entries per ayah for first 10 ayahs, then 1 per 5 ayahs
        max_ayahs = min(ayah_count, 20) if surah_num <= 10 else min(ayah_count, 10)
        
        for ayah in range(1, max_ayahs + 1):
            num_entries = random.randint(1, 3) if ayah <= 5 else 1
            
            for i in range(num_entries):
                cat, desc = random.choice(TAFSIR_TEMPLATES)
                source = random.choice(["ibn_kathir", "tabari", "qurtubi", "jalalayn", "saadi"])
                
                entry = {
                    "entry_id": f"{source}_{surah_num}_{ayah}_{i+1}",
                    "source_id": source,
                    "surah_number": surah_num,
                    "ayah_start": ayah,
                    "ayah_end": ayah,
                    "text_original": f"تفسير {name_ar} آية {ayah} من {source}: {desc}. هذا نص تجريبي للتوضيح فقط.",
                    "text_normalized": f"تفسير {name_ar} آية {ayah} من {source}: {desc}. هذا نص تجريبي للتوضيح فقط.",
                    "language": "ar",
                    "metadata_json": {"category": cat, "topic": f"ayah_{ayah}"}
                }
                output.append(entry)
                entry_id += 1
    
    return output

def generate_hadith_data():
    """Generate comprehensive hadith sample data."""
    output = []
    hadith_id = 1
    
    topics = [
        "wahy", "iman", "salah", "zakat", "sawm", "hajj", "jihad", "akhlaq",
        "tawhid", "dua", "tazkiyah", "sirah", "fiqh", "adab", "ruh"
    ]
    
    for collection_id, collection_name in HADITH_COLLECTIONS:
        # 20-50 hadith per collection
        num_hadith = random.randint(20, 50)
        
        for i in range(num_hadith):
            topic = random.choice(topics)
            book_num = random.randint(1, 97)
            
            entry = {
                "hadith_id": f"{collection_id}_{hadith_id}",
                "collection_id": collection_id,
                "book_number": book_num,
                "book_title": f"كتاب {topic}",
                "hadith_number": i + 1,
                "hadith_number_global": hadith_id,
                "text_original": f"حديث رقم {hadith_id} من {collection_name}: نص الحديث حول {topic}. هذا نص تجريبي.",
                "text_normalized": f"حديث رقم {hadith_id} من {collection_name}: نص الحديث حول {topic}. هذا نص تجريبي.",
                "language": "ar",
                "grade": random.choice(["sahih", "hasan", "da'if"]),
                "grade_source": collection_id.replace("sahih_", "").replace("sunan_", ""),
                "isnad": [f"راوٍ {j+1}" for j in range(random.randint(3, 6))],
                "metadata_json": {"topic": topic, "chapter": topic}
            }
            output.append(entry)
            hadith_id += 1
    
    return output

def generate_qiraat_data():
    """Generate qiraat sample data for key ayahs across surahs."""
    output = []
    
    # Key ayahs where qiraat differences are well-known
    key_ayahs = [
        (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7),
        (2, 1), (2, 2), (2, 10), (2, 255), (2, 256), (2, 285), (2, 286),
        (3, 1), (3, 18), (3, 19), (3, 26),
        (12, 2), (12, 3), (12, 4),
        (18, 1), (18, 9), (18, 10), (18, 110),
        (36, 1), (36, 2), (36, 3),
        (55, 1), (55, 13), (55, 28),
        (67, 1), (67, 2),
        (112, 1), (112, 2), (112, 3), (112, 4),
        (113, 1), (113, 2), (113, 3), (113, 4), (113, 5),
        (114, 1), (114, 2), (114, 3), (114, 4), (114, 5), (114, 6),
    ]
    
    diff_types = [
        ("madd", "Madd difference"),
        ("hamzah", "Hamzah difference"),
        ("imalah", "Imalah difference"),
        ("tasheel", "Tasheel difference"),
        ("rawm", "Rawm difference"),
        ("ishmam", "Ishmam difference"),
    ]
    
    for qiraat_id, qiraat_name, tariq in QIRAAT_LIST:
        for surah, ayah in key_ayahs:
            if surah > 114:
                continue
            surah_data = SURAH_NAMES.get(surah)
            if not surah_data or ayah > surah_data[2]:
                continue
                
            has_diff = random.random() < 0.3  # 30% have differences
            diffs = []
            if has_diff:
                diff_type, diff_desc = random.choice(diff_types)
                diffs.append({
                    "type": diff_type,
                    "position": random.randint(5, 30),
                    "detail": f"{diff_desc} in {qiraat_name}"
                })
            
            entry = {
                "reading_id": f"{qiraat_id}_{surah}_{ayah}",
                "qiraat_id": qiraat_id,
                "surah_number": surah,
                "ayah_number": ayah,
                "text_original": f"نص تجريبي للسورة {surah} الآية {ayah} برواية {qiraat_name}",
                "text_normalized": f"نص تجريبي للسورة {surah} الآية {ayah} برواية {qiraat_name}",
                "differences": diffs,
                "metadata_json": {"rawi": qiraat_name.split("_")[0], "tariq": tariq}
            }
            output.append(entry)
    
    return output

def generate_tajwid_data():
    """Generate comprehensive tajwid rules."""
    output = []
    
    # Add general rules
    for rule in TAJWID_RULES:
        rule_id, rule_type, name, name_ar, triggers = rule[0], rule[1], rule[2], rule[3], rule[4]
        entry = {
            "rule_id": rule_id,
            "rule_type": rule_type,
            "name": name,
            "name_arabic": name_ar,
            "description": f"Description of {name} tajwid rule.",
            "description_arabic": f"وصف قاعدة {name_ar} التجويدية.",
            "conditions": {"trigger_letters": triggers} if isinstance(triggers, list) else triggers,
            "examples": [
                {"surah": 1, "ayah": 1, "text": "بِسْمِ اللَّهِ", "highlight": "م"},
                {"surah": 2, "ayah": 10, "text": "فِي قُلُوبِهِم مَّرَضٌ", "highlight": "م م"},
            ],
            "priority": random.randint(5, 10),
            "metadata_json": {"category": rule_type}
        }
        output.append(entry)
    
    # Add specific ayah-level rules for first 10 surahs
    for surah_num in range(1, 11):
        surah_data = SURAH_NAMES[surah_num]
        for ayah in range(1, min(surah_data[2] + 1, 8)):
            rule_type = random.choice(["ghunnah", "idgham", "ikhfa", "izhar", "madd", "qalqalah"])
            entry = {
                "rule_id": f"{rule_type}_{surah_num}_{ayah}",
                "rule_type": rule_type,
                "name": f"{rule_type.title()} at {surah_num}:{ayah}",
                "name_arabic": f"{rule_type} في {surah_num}:{ayah}",
                "description": f"Specific {rule_type} application at {surah_num}:{ayah}",
                "description_arabic": f"تطبيق {rule_type} في {surah_num}:{ayah}",
                "conditions": {"surah": surah_num, "ayah": ayah},
                "examples": [{"surah": surah_num, "ayah": ayah, "text": "نص تجريبي", "highlight": "م"}],
                "priority": random.randint(1, 10),
                "metadata_json": {"category": rule_type, "specific_ayah": True}
            }
            output.append(entry)
    
    return output

def generate_waqf_data():
    """Generate comprehensive waqf data for all surahs."""
    output = []
    
    # Per-ayah waqf signs for first 10 surahs
    for surah_num in range(1, 11):
        surah_data = SURAH_NAMES[surah_num]
        
        for ayah in range(1, surah_data[2] + 1):
            # End of ayah - waqf tamm
            entry = {
                "rule_id": f"waqf_{surah_num}_{ayah}_tamm",
                "rule_type": "waqf_tamm",
                "name": f"Waqf Tamm at {surah_num}:{ayah}",
                "name_arabic": f"الوقف التام في {surah_num}:{ayah}",
                "description": f"Complete stop at end of ayah {ayah}",
                "description_arabic": f"الوقف التام في آخر الآية {ayah}",
                "conditions": {"position": "ayah_end", "completeness": "complete_meaning"},
                "surah_number": surah_num,
                "ayah_number": ayah,
                "word_position": -1,  # end
                "sign_character": "۝",
                "priority": 10,
                "metadata_json": {"category": "ayah_end"}
            }
            output.append(entry)
            
            # Add in-ayah waqf for longer ayahs (every ~5 words)
            if ayah <= 5:  # Only first few ayahs for demo
                for wp in [2, 4]:
                    if random.random() < 0.5:
                        waqf_type, char, name, name_ar, desc = random.choice(WAQF_TYPES[:-2])  # exclude ibtida
                        entry = {
                            "rule_id": f"waqf_{surah_num}_{ayah}_{wp}_{waqf_type}",
                            "rule_type": waqf_type,
                            "name": f"{name} at {surah_num}:{ayah} word {wp}",
                            "name_arabic": f"{name_ar} في {surah_num}:{ayah} كلمة {wp}",
                            "description": f"{desc} at word position {wp}",
                            "description_arabic": f"{desc} في موضع الكلمة {wp}",
                            "conditions": {"position": "in_ayah", "word_position": wp},
                            "surah_number": surah_num,
                            "ayah_number": ayah,
                            "word_position": wp,
                            "sign_character": char,
                            "priority": random.randint(5, 9),
                            "metadata_json": {"category": "in_ayah"}
                        }
                        output.append(entry)
        
        # Surah end
        entry = {
            "rule_id": f"waqf_{surah_num}_surah_end",
            "rule_type": "waqf_tamm",
            "name": f"Waqf Tamm at End of Surah {surah_num}",
            "name_arabic": f"الوقف التام في آخر سورة {surah_num}",
            "description": f"Complete stop at end of surah {surah_num}",
            "description_arabic": f"الوقف التام في آخر السورة {surah_num}",
            "conditions": {"position": "surah_end", "completeness": "complete_meaning"},
            "surah_number": surah_num,
            "ayah_number": surah_data[2],
            "word_position": -1,
            "sign_character": "۝",
            "priority": 10,
            "metadata_json": {"category": "surah_end"}
        }
        output.append(entry)
    
    # Ibtida (start) signs for first few surahs
    for surah_num in range(1, 6):
        for ayah in [1, 2]:
            ibtida_type, char, name, name_ar, desc = random.choice(WAQF_TYPES[-2:])
            entry = {
                "rule_id": f"ibtida_{surah_num}_{ayah}_{ibtida_type}",
                "rule_type": ibtida_type,
                "name": f"{name} at {surah_num}:{ayah}",
                "name_arabic": f"{name_ar} في {surah_num}:{ayah}",
                "description": f"{desc} at beginning of ayah {ayah}",
                "description_arabic": f"{desc} في بداية الآية {ayah}",
                "conditions": {"position": "ayah_start", "type": "permissible_start" if "jaiz" in ibtida_type else "recommended_start"},
                "surah_number": surah_num,
                "ayah_number": ayah,
                "word_position": 1,
                "sign_character": char,
                "priority": random.randint(5, 7),
                "metadata_json": {"category": "ibtida"}
            }
            output.append(entry)
    
    return output

def main():
    data_dir = Path(__file__).parent.parent / "data"
    
    print("Generating tafsir data...")
    tafsir_data = generate_tafsir_data()
    with open(data_dir / "tafsir" / "sample_tafsir.jsonl", "w", encoding="utf-8") as f:
        for entry in tafsir_data:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"  Generated {len(tafsir_data)} tafsir entries")
    
    print("Generating hadith data...")
    hadith_data = generate_hadith_data()
    with open(data_dir / "hadith" / "sample_hadith.jsonl", "w", encoding="utf-8") as f:
        for entry in hadith_data:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"  Generated {len(hadith_data)} hadith entries")
    
    print("Generating qiraat data...")
    qiraat_data = generate_qiraat_data()
    with open(data_dir / "qiraat" / "sample_qiraat.jsonl", "w", encoding="utf-8") as f:
        for entry in qiraat_data:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"  Generated {len(qiraat_data)} qiraat entries")
    
    print("Generating tajwid data...")
    tajwid_data = generate_tajwid_data()
    with open(data_dir / "tajwid" / "sample_tajwid.jsonl", "w", encoding="utf-8") as f:
        for entry in tajwid_data:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"  Generated {len(tajwid_data)} tajwid entries")
    
    print("Generating waqf data...")
    waqf_data = generate_waqf_data()
    with open(data_dir / "waqf" / "sample_waqf.jsonl", "w", encoding="utf-8") as f:
        for entry in waqf_data:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"  Generated {len(waqf_data)} waqf entries")
    
    print("\nAll sample data generated successfully!")

if __name__ == "__main__":
    main()
