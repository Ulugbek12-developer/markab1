BASE_PRICES = {
    "iPhone 11": 300, "iPhone 11 Pro": 400, "iPhone 11 Pro Max": 450,
    "iPhone 12": 400, "iPhone 12 Pro": 500, "iPhone 12 Pro Max": 550,
    "iPhone 13": 500, "iPhone 13 Pro": 650, "iPhone 13 Pro Max": 750,
    "iPhone 14": 650, "iPhone 14 Pro": 850, "iPhone 14 Pro Max": 950,
    "iPhone 15": 800, "iPhone 15 Pro": 1050, "iPhone 15 Pro Max": 1150,
    "iPhone 16": 1000, "iPhone 16 Pro": 1300, "iPhone 16 Pro Max": 1450,
    "iPhone 17 Pro Max": 1600
}

def calculate_phone_price(data):
    model = data.get('model', "")
    base = BASE_PRICES.get(model, 500)
    
    # Memory adjustments
    storage = str(data.get('storage', data.get('memory', "128GB")))
    if "256" in storage: base += 50
    elif "512" in storage: base += 100
    elif "1TB" in storage: base += 200
    
    # Battery adjustments
    try:
        battery_val = int(str(data.get('battery', 90)).replace('%', '').strip())
        if battery_val >= 90: pass
        elif battery_val >= 80: base -= 30
        elif battery_val >= 70: base -= 60
        else: base -= 100
    except: pass
    
    # Cycles
    try:
        cycles = int(data.get('cycles', 0))
        if cycles > 1000: base -= 50
        elif cycles > 500: base -= 30
    except: pass

    # Region adjustments
    region = str(data.get('region', "")).upper()
    if "CH/A" in region or "HN/A" in region: base -= 30
    elif "KH/A" in region or "J/A" in region: base -= 20
    elif "LL/A" in region or "ZA/A" in region: base += 20
    
    # Detailed Condition
    screen_cond = str(data.get('screen_condition', data.get('condition', ""))).lower()
    if any(x in screen_cond for x in ["chiziq", "scratch", "minor"]): base -= 30
    elif any(x in screen_cond for x in ["singan", "yorilgan", "cracked", "bad"]): base -= 150
    
    body_cond = str(data.get('body_condition', "")).lower()
    if any(x in body_cond for x in ["chiziq", "scratch", "minor"]): base -= 20
    elif any(x in body_cond for x in ["singan", "pachoq", "cracked", "bad"]): base -= 80
    
    # Box
    box = str(data.get('box', data.get('has_box', ''))).lower()
    if any(x in box for x in ["yo'q", "нет", "no", "false"]): base -= 30
    
    # Replaced parts deductions
    replaced_parts = data.get('replaced_parts', [])
    if "almashtirilmagan" not in replaced_parts and "none" not in [str(p).lower() for p in replaced_parts]:
        for part in replaced_parts:
            p = str(part).lower()
            if "ekran" in p or "display" in p: base -= 100
            elif "batareya" in p or "battery" in p: base -= 30
            elif "kamera" in p or "camera" in p: base -= 70
            elif "qopqoq" in p or "glass" in p or "housing" in p: base -= 40
            else: base -= 20
            
    # Defects deductions
    defects = data.get('defects', [])
    if "hammasi_ishlaydi" not in defects and "none" not in [str(d).lower() for d in defects]:
        for defect in defects:
            d = str(defect).lower()
            if "face" in d: base -= 150
            elif "true" in d: base -= 50
            elif "asosiy" in d or "back" in d: base -= 100
            elif "old" in d or "front" in d: base -= 60
            elif "wifi" in d: base -= 80
            else: base -= 30

    return int(base) # Returns price in dollars (e.g. 850)
