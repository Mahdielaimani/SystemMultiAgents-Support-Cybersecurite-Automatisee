def test_ddos_detection():
    """Test avec simulation DDoS"""
    
    # Utiliser hping3 pour simuler DDoS
    import subprocess
    
    print("🚨 Simulation DDoS avec hping3...")
    # SYN flood vers localhost
    cmd = "hping3 -S -p 80 -i u1000 127.0.0.1"
    process = subprocess.Popen(cmd.split(), stdout=subprocess.DEVNULL)
    
    # Capturer pendant l'attaque
    collector = RealTimeTrafficCollector()
    features = collector.start_capture(duration=15)
    
    process.terminate()
    
    # Analyser
    ddos_detected = False
    for _, row in features.iterrows():
        prediction = model.predict(row.values.reshape(1, -1))
        if "DDoS" in prediction or "DoS" in prediction:
            ddos_detected = True
            break
    
    print(f"✅ DDoS détecté: {ddos_detected}")
    assert ddos_detected, "DDoS non détecté!"

def test_port_scan_detection():
    """Test avec scan de ports"""
    print("🔍 Simulation scan de ports avec nmap...")
    
    # Scanner quelques ports
    cmd = "nmap -sS -F 127.0.0.1"
    process = subprocess.Popen(cmd.split(), stdout=subprocess.DEVNULL)
    
    collector = RealTimeTrafficCollector()
    features = collector.start_capture(duration=10)
    
    process.wait()
    
    # Vérifier détection
    scan_detected = False
    for _, row in features.iterrows():
        prediction = model.predict(row.values.reshape(1, -1))
        if "PortScan" in prediction:
            scan_detected = True
            break
    
    print(f"✅ Port scan détecté: {scan_detected}")
    return scan_detected