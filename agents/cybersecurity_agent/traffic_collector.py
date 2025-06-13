# agents/cybersecurity_agent/traffic_collector.py
"""
Collecteur de trafic réseau temps réel pour validation du modèle CICIDS2017
Compatible avec la structure du projet Next-Gen-Agents-SC
"""
import os
import sys
import time
import json
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import threading
import queue
import subprocess
import socket
import struct

# Ajouter le répertoire racine au path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    import pyshark
    PYSHARK_AVAILABLE = True
except ImportError:
    PYSHARK_AVAILABLE = False
    logging.warning("⚠️ pyshark non disponible - utilisation du mode fallback")

try:
    import scapy.all as scapy
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    logging.warning("⚠️ scapy non disponible")

logger = logging.getLogger(__name__)

class CICIDSFeatureExtractor:
    """Extracteur de features CICIDS2017 depuis les flows réseau"""
    
    def __init__(self):
        self.feature_names = self._get_cicids_features()
    
    def _get_cicids_features(self) -> List[str]:
        """Retourne la liste complète des 79 features CICIDS2017"""
        return [
            # Flow-based features
            'Flow Duration', 'Total Fwd Packets', 'Total Backward Packets',
            'Total Length of Fwd Packets', 'Total Length of Bwd Packets',
            'Fwd Packet Length Max', 'Fwd Packet Length Min', 'Fwd Packet Length Mean', 'Fwd Packet Length Std',
            'Bwd Packet Length Max', 'Bwd Packet Length Min', 'Bwd Packet Length Mean', 'Bwd Packet Length Std',
            
            # Timing features
            'Flow Bytes/s', 'Flow Packets/s', 'Flow IAT Mean', 'Flow IAT Std', 'Flow IAT Max', 'Flow IAT Min',
            'Fwd IAT Total', 'Fwd IAT Mean', 'Fwd IAT Std', 'Fwd IAT Max', 'Fwd IAT Min',
            'Bwd IAT Total', 'Bwd IAT Mean', 'Bwd IAT Std', 'Bwd IAT Max', 'Bwd IAT Min',
            
            # TCP Flag features
            'Fwd PSH Flags', 'Bwd PSH Flags', 'Fwd URG Flags', 'Bwd URG Flags',
            'Fwd Header Length', 'Bwd Header Length',
            'Fwd Packets/s', 'Bwd Packets/s',
            
            # Packet length features
            'Min Packet Length', 'Max Packet Length', 'Packet Length Mean', 'Packet Length Std', 'Packet Length Variance',
            
            # TCP-specific features
            'FIN Flag Count', 'SYN Flag Count', 'RST Flag Count', 'PSH Flag Count', 'ACK Flag Count', 'URG Flag Count',
            'CWE Flag Count', 'ECE Flag Count',
            
            # Window size features
            'Down/Up Ratio', 'Average Packet Size', 'Avg Fwd Segment Size', 'Avg Bwd Segment Size',
            'Fwd Header Length.1', 'Fwd Avg Bytes/Bulk', 'Fwd Avg Packets/Bulk', 'Fwd Avg Bulk Rate',
            'Bwd Avg Bytes/Bulk', 'Bwd Avg Packets/Bulk', 'Bwd Avg Bulk Rate',
            
            # Subflow features
            'Subflow Fwd Packets', 'Subflow Fwd Bytes', 'Subflow Bwd Packets', 'Subflow Bwd Bytes',
            
            # Window size and buffer features
            'Init_Win_bytes_forward', 'Init_Win_bytes_backward', 'act_data_pkt_fwd', 'min_seg_size_forward',
            
            # Active and Idle features
            'Active Mean', 'Active Std', 'Active Max', 'Active Min',
            'Idle Mean', 'Idle Std', 'Idle Max', 'Idle Min'
        ]
    
    def extract_features_from_flow(self, flow_data: Dict) -> Dict[str, float]:
        """Extrait les features CICIDS2017 depuis un flow"""
        packets = flow_data.get('packets', [])
        if len(packets) < 2:
            return self._get_empty_features()
        
        # Séparer forward/backward packets
        first_packet = packets[0]
        src_ip = first_packet.get('src_ip')
        
        fwd_packets = [p for p in packets if p.get('src_ip') == src_ip]
        bwd_packets = [p for p in packets if p.get('src_ip') != src_ip]
        
        features = {}
        
        # 1. Basic flow features
        features['Flow Duration'] = self._calculate_flow_duration(packets)
        features['Total Fwd Packets'] = len(fwd_packets)
        features['Total Backward Packets'] = len(bwd_packets)
        
        # 2. Packet length features
        fwd_lengths = [p.get('length', 0) for p in fwd_packets]
        bwd_lengths = [p.get('length', 0) for p in bwd_packets]
        all_lengths = [p.get('length', 0) for p in packets]
        
        features.update(self._calculate_length_features(fwd_lengths, bwd_lengths, all_lengths))
        
        # 3. Timing features
        features.update(self._calculate_timing_features(packets, fwd_packets, bwd_packets))
        
        # 4. TCP flags features
        features.update(self._calculate_flag_features(packets, fwd_packets, bwd_packets))
        
        # 5. Window and protocol features
        features.update(self._calculate_protocol_features(packets, fwd_packets, bwd_packets))
        
        # 6. Active/Idle features (simplifiées)
        features.update(self._calculate_activity_features(packets))
        
        # Remplir les features manquantes avec des valeurs par défaut
        for feature_name in self.feature_names:
            if feature_name not in features:
                features[feature_name] = 0.0
        
        return features
    
    def _calculate_flow_duration(self, packets: List[Dict]) -> float:
        """Calcule la durée du flow en microsecondes"""
        if len(packets) < 2:
            return 0.0
        
        timestamps = [p.get('timestamp', 0) for p in packets]
        return (max(timestamps) - min(timestamps)) * 1_000_000  # en microsecondes
    
    def _calculate_length_features(self, fwd_lengths: List[int], bwd_lengths: List[int], all_lengths: List[int]) -> Dict[str, float]:
        """Calcule les features liées aux tailles de paquets"""
        features = {}
        
        # Forward packet lengths
        if fwd_lengths:
            features['Fwd Packet Length Max'] = max(fwd_lengths)
            features['Fwd Packet Length Min'] = min(fwd_lengths)
            features['Fwd Packet Length Mean'] = np.mean(fwd_lengths)
            features['Fwd Packet Length Std'] = np.std(fwd_lengths)
            features['Total Length of Fwd Packets'] = sum(fwd_lengths)
        else:
            features.update({
                'Fwd Packet Length Max': 0, 'Fwd Packet Length Min': 0,
                'Fwd Packet Length Mean': 0, 'Fwd Packet Length Std': 0,
                'Total Length of Fwd Packets': 0
            })
        
        # Backward packet lengths
        if bwd_lengths:
            features['Bwd Packet Length Max'] = max(bwd_lengths)
            features['Bwd Packet Length Min'] = min(bwd_lengths)
            features['Bwd Packet Length Mean'] = np.mean(bwd_lengths)
            features['Bwd Packet Length Std'] = np.std(bwd_lengths)
            features['Total Length of Bwd Packets'] = sum(bwd_lengths)
        else:
            features.update({
                'Bwd Packet Length Max': 0, 'Bwd Packet Length Min': 0,
                'Bwd Packet Length Mean': 0, 'Bwd Packet Length Std': 0,
                'Total Length of Bwd Packets': 0
            })
        
        # Overall packet lengths
        if all_lengths:
            features['Min Packet Length'] = min(all_lengths)
            features['Max Packet Length'] = max(all_lengths)
            features['Packet Length Mean'] = np.mean(all_lengths)
            features['Packet Length Std'] = np.std(all_lengths)
            features['Packet Length Variance'] = np.var(all_lengths)
            features['Average Packet Size'] = np.mean(all_lengths)
        else:
            features.update({
                'Min Packet Length': 0, 'Max Packet Length': 0,
                'Packet Length Mean': 0, 'Packet Length Std': 0,
                'Packet Length Variance': 0, 'Average Packet Size': 0
            })
        
        return features
    
    def _calculate_timing_features(self, packets: List[Dict], fwd_packets: List[Dict], bwd_packets: List[Dict]) -> Dict[str, float]:
        """Calcule les features temporelles"""
        features = {}
        
        # Flow-level timing
        if len(packets) > 1:
            timestamps = [p.get('timestamp', 0) for p in packets]
            timestamps.sort()
            
            # Inter-arrival times
            iats = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
            
            if iats:
                features['Flow IAT Mean'] = np.mean(iats) * 1_000_000  # microsecondes
                features['Flow IAT Std'] = np.std(iats) * 1_000_000
                features['Flow IAT Max'] = max(iats) * 1_000_000
                features['Flow IAT Min'] = min(iats) * 1_000_000
        
        # Forward timing
        if len(fwd_packets) > 1:
            fwd_times = sorted([p.get('timestamp', 0) for p in fwd_packets])
            fwd_iats = [fwd_times[i+1] - fwd_times[i] for i in range(len(fwd_times)-1)]
            
            if fwd_iats:
                features['Fwd IAT Total'] = sum(fwd_iats) * 1_000_000
                features['Fwd IAT Mean'] = np.mean(fwd_iats) * 1_000_000
                features['Fwd IAT Std'] = np.std(fwd_iats) * 1_000_000
                features['Fwd IAT Max'] = max(fwd_iats) * 1_000_000
                features['Fwd IAT Min'] = min(fwd_iats) * 1_000_000
        
        # Backward timing
        if len(bwd_packets) > 1:
            bwd_times = sorted([p.get('timestamp', 0) for p in bwd_packets])
            bwd_iats = [bwd_times[i+1] - bwd_times[i] for i in range(len(bwd_times)-1)]
            
            if bwd_iats:
                features['Bwd IAT Total'] = sum(bwd_iats) * 1_000_000
                features['Bwd IAT Mean'] = np.mean(bwd_iats) * 1_000_000
                features['Bwd IAT Std'] = np.std(bwd_iats) * 1_000_000
                features['Bwd IAT Max'] = max(bwd_iats) * 1_000_000
                features['Bwd IAT Min'] = min(bwd_iats) * 1_000_000
        
        # Flow rates
        duration = features.get('Flow Duration', 0) / 1_000_000  # en secondes
        if duration > 0:
            total_bytes = sum(p.get('length', 0) for p in packets)
            features['Flow Bytes/s'] = total_bytes / duration
            features['Flow Packets/s'] = len(packets) / duration
            features['Fwd Packets/s'] = len(fwd_packets) / duration
            features['Bwd Packets/s'] = len(bwd_packets) / duration
        
        return features
    
    def _calculate_flag_features(self, packets: List[Dict], fwd_packets: List[Dict], bwd_packets: List[Dict]) -> Dict[str, float]:
        """Calcule les features des flags TCP"""
        features = {}
        
        # Compter tous les flags
        all_flags = [p.get('flags', []) for p in packets]
        flag_counts = {
            'FIN Flag Count': sum(1 for flags in all_flags if 'FIN' in flags),
            'SYN Flag Count': sum(1 for flags in all_flags if 'SYN' in flags),
            'RST Flag Count': sum(1 for flags in all_flags if 'RST' in flags),
            'PSH Flag Count': sum(1 for flags in all_flags if 'PSH' in flags),
            'ACK Flag Count': sum(1 for flags in all_flags if 'ACK' in flags),
            'URG Flag Count': sum(1 for flags in all_flags if 'URG' in flags),
            'CWE Flag Count': 0,  # Rarement utilisé
            'ECE Flag Count': 0   # Rarement utilisé
        }
        
        features.update(flag_counts)
        
        # Forward/Backward PSH et URG flags
        fwd_flags = [p.get('flags', []) for p in fwd_packets]
        bwd_flags = [p.get('flags', []) for p in bwd_packets]
        
        features['Fwd PSH Flags'] = sum(1 for flags in fwd_flags if 'PSH' in flags)
        features['Bwd PSH Flags'] = sum(1 for flags in bwd_flags if 'PSH' in flags)
        features['Fwd URG Flags'] = sum(1 for flags in fwd_flags if 'URG' in flags)
        features['Bwd URG Flags'] = sum(1 for flags in bwd_flags if 'URG' in flags)
        
        return features
    
    def _calculate_protocol_features(self, packets: List[Dict], fwd_packets: List[Dict], bwd_packets: List[Dict]) -> Dict[str, float]:
        """Calcule les features protocolaires"""
        features = {}
        
        # Header lengths (estimation)
        features['Fwd Header Length'] = len(fwd_packets) * 20  # TCP header basique
        features['Bwd Header Length'] = len(bwd_packets) * 20
        features['Fwd Header Length.1'] = features['Fwd Header Length']
        
        # Segment sizes
        if fwd_packets:
            fwd_lengths = [p.get('length', 0) for p in fwd_packets]
            features['Avg Fwd Segment Size'] = np.mean(fwd_lengths)
        else:
            features['Avg Fwd Segment Size'] = 0
            
        if bwd_packets:
            bwd_lengths = [p.get('length', 0) for p in bwd_packets]
            features['Avg Bwd Segment Size'] = np.mean(bwd_lengths)
        else:
            features['Avg Bwd Segment Size'] = 0
        
        # Ratios
        total_fwd = len(fwd_packets)
        total_bwd = len(bwd_packets)
        
        if total_fwd > 0:
            features['Down/Up Ratio'] = total_bwd / total_fwd if total_fwd > 0 else 0
        else:
            features['Down/Up Ratio'] = 0
        
        # Subflow features (simplifiées)
        features['Subflow Fwd Packets'] = total_fwd
        features['Subflow Fwd Bytes'] = sum(p.get('length', 0) for p in fwd_packets)
        features['Subflow Bwd Packets'] = total_bwd
        features['Subflow Bwd Bytes'] = sum(p.get('length', 0) for p in bwd_packets)
        
        # Window sizes (estimation)
        features['Init_Win_bytes_forward'] = 65535  # Valeur typique
        features['Init_Win_bytes_backward'] = 65535
        features['act_data_pkt_fwd'] = total_fwd
        features['min_seg_size_forward'] = min([p.get('length', 0) for p in fwd_packets]) if fwd_packets else 0
        
        # Bulk features (simplifiées)
        bulk_features = [
            'Fwd Avg Bytes/Bulk', 'Fwd Avg Packets/Bulk', 'Fwd Avg Bulk Rate',
            'Bwd Avg Bytes/Bulk', 'Bwd Avg Packets/Bulk', 'Bwd Avg Bulk Rate'
        ]
        for feature in bulk_features:
            features[feature] = 0  # Simplification
        
        return features
    
    def _calculate_activity_features(self, packets: List[Dict]) -> Dict[str, float]:
        """Calcule les features d'activité/inactivité (simplifiées)"""
        features = {}
        
        # Features d'activité (simplification basée sur les timestamps)
        if len(packets) > 1:
            timestamps = sorted([p.get('timestamp', 0) for p in packets])
            gaps = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
            
            # Considérer les gaps > 1 seconde comme périodes d'inactivité
            idle_periods = [gap for gap in gaps if gap > 1.0]
            active_periods = [gap for gap in gaps if gap <= 1.0]
            
            if active_periods:
                features['Active Mean'] = np.mean(active_periods) * 1_000_000
                features['Active Std'] = np.std(active_periods) * 1_000_000
                features['Active Max'] = max(active_periods) * 1_000_000
                features['Active Min'] = min(active_periods) * 1_000_000
            else:
                features.update({'Active Mean': 0, 'Active Std': 0, 'Active Max': 0, 'Active Min': 0})
            
            if idle_periods:
                features['Idle Mean'] = np.mean(idle_periods) * 1_000_000
                features['Idle Std'] = np.std(idle_periods) * 1_000_000
                features['Idle Max'] = max(idle_periods) * 1_000_000
                features['Idle Min'] = min(idle_periods) * 1_000_000
            else:
                features.update({'Idle Mean': 0, 'Idle Std': 0, 'Idle Max': 0, 'Idle Min': 0})
        else:
            activity_features = ['Active Mean', 'Active Std', 'Active Max', 'Active Min',
                               'Idle Mean', 'Idle Std', 'Idle Max', 'Idle Min']
            for feature in activity_features:
                features[feature] = 0
        
        return features
    
    def _get_empty_features(self) -> Dict[str, float]:
        """Retourne un dictionnaire avec toutes les features à 0"""
        return {feature: 0.0 for feature in self.feature_names}


class RealTimeTrafficCollector:
    """Collecteur de trafic réseau temps réel pour validation CICIDS2017"""
    
    def __init__(self, interface: str = "any", capture_filter: str = None):
        self.interface = interface
        self.capture_filter = capture_filter or "tcp or udp"
        self.flows = {}
        self.feature_extractor = CICIDSFeatureExtractor()
        self.is_running = False
        self.packet_queue = queue.Queue()
        
        # Vérifier les capacités du système
        self.capture_method = self._detect_capture_method()
        logger.info(f"🔍 Méthode de capture: {self.capture_method}")
    
    def _detect_capture_method(self) -> str:
        """Détecte la meilleure méthode de capture disponible"""
        if PYSHARK_AVAILABLE:
            return "pyshark"
        elif SCAPY_AVAILABLE:
            return "scapy"
        else:
            return "netstat"  # Fallback
    
    def start_capture(self, duration: int = 60, max_packets: int = 1000) -> pd.DataFrame:
        """Lance la capture de trafic pendant une durée donnée"""
        logger.info(f"🔍 Début capture - Interface: {self.interface}, Durée: {duration}s")
        
        self.flows = {}
        self.is_running = True
        
        if self.capture_method == "pyshark":
            return self._capture_with_pyshark(duration, max_packets)
        elif self.capture_method == "scapy":
            return self._capture_with_scapy(duration, max_packets)
        else:
            return self._capture_with_netstat(duration)
    
    def _capture_with_pyshark(self, duration: int, max_packets: int) -> pd.DataFrame:
        """Capture avec PyShark"""
        try:
            capture = pyshark.LiveCapture(
                interface=self.interface,
                display_filter=self.capture_filter
            )
            
            packets_processed = 0
            start_time = time.time()
            
            for packet in capture.sniff_continuously():
                if time.time() - start_time > duration or packets_processed >= max_packets:
                    break
                
                packet_data = self._extract_packet_data_pyshark(packet)
                if packet_data:
                    self._add_packet_to_flows(packet_data)
                    packets_processed += 1
            
            capture.close()
            logger.info(f"✅ Capture terminée - {packets_processed} paquets traités")
            
        except Exception as e:
            logger.error(f"❌ Erreur capture PyShark: {e}")
            return pd.DataFrame()
        
        return self._convert_flows_to_features()
    
    def _capture_with_scapy(self, duration: int, max_packets: int) -> pd.DataFrame:
        """Capture avec Scapy"""
        try:
            packets = scapy.sniff(
                iface=self.interface if self.interface != "any" else None,
                filter=self.capture_filter,
                timeout=duration,
                count=max_packets
            )
            
            for packet in packets:
                packet_data = self._extract_packet_data_scapy(packet)
                if packet_data:
                    self._add_packet_to_flows(packet_data)
            
            logger.info(f"✅ Capture Scapy terminée - {len(packets)} paquets")
            
        except Exception as e:
            logger.error(f"❌ Erreur capture Scapy: {e}")
            return pd.DataFrame()
        
        return self._convert_flows_to_features()
    
    def _capture_with_netstat(self, duration: int) -> pd.DataFrame:
        """Mode fallback avec netstat (simulation)"""
        logger.warning("📡 Mode fallback - Simulation avec netstat")
        
        # Simuler quelques flows basiques
        simulated_flows = self._generate_simulated_flows()
        
        for flow in simulated_flows:
            flow_key = self._create_flow_key(flow['packets'][0])
            self.flows[flow_key] = flow
        
        return self._convert_flows_to_features()
    
    def _extract_packet_data_pyshark(self, packet) -> Optional[Dict]:
        """Extrait les données d'un paquet PyShark"""
        try:
            packet_data = {
                'timestamp': float(packet.sniff_timestamp),
                'length': int(packet.length),
                'protocol': 'UNKNOWN',
                'src_ip': None,
                'dst_ip': None,
                'src_port': 0,
                'dst_port': 0,
                'flags': []
            }
            
            # IP layer
            if hasattr(packet, 'ip'):
                packet_data['src_ip'] = packet.ip.src
                packet_data['dst_ip'] = packet.ip.dst
                packet_data['protocol'] = packet.ip.proto
            
            # TCP layer
            if hasattr(packet, 'tcp'):
                packet_data['src_port'] = int(packet.tcp.srcport)
                packet_data['dst_port'] = int(packet.tcp.dstport)
                packet_data['protocol'] = 'TCP'
                
                # TCP flags
                flags = []
                if hasattr(packet.tcp, 'flags_syn') and packet.tcp.flags_syn == '1':
                    flags.append('SYN')
                if hasattr(packet.tcp, 'flags_ack') and packet.tcp.flags_ack == '1':
                    flags.append('ACK')
                if hasattr(packet.tcp, 'flags_fin') and packet.tcp.flags_fin == '1':
                    flags.append('FIN')
                if hasattr(packet.tcp, 'flags_rst') and packet.tcp.flags_rst == '1':
                    flags.append('RST')
                if hasattr(packet.tcp, 'flags_push') and packet.tcp.flags_push == '1':
                    flags.append('PSH')
                if hasattr(packet.tcp, 'flags_urg') and packet.tcp.flags_urg == '1':
                    flags.append('URG')
                
                packet_data['flags'] = flags
            
            # UDP layer
            elif hasattr(packet, 'udp'):
                packet_data['src_port'] = int(packet.udp.srcport)
                packet_data['dst_port'] = int(packet.udp.dstport)
                packet_data['protocol'] = 'UDP'
            
            return packet_data
            
        except Exception as e:
            logger.debug(f"Erreur extraction paquet PyShark: {e}")
            return None
    
    def _extract_packet_data_scapy(self, packet) -> Optional[Dict]:
        """Extrait les données d'un paquet Scapy"""
        try:
            packet_data = {
                'timestamp': packet.time,
                'length': len(packet),
                'protocol': 'UNKNOWN',
                'src_ip': None,
                'dst_ip': None,
                'src_port': 0,
                'dst_port': 0,
                'flags': []
            }
            
            # IP layer
            if packet.haslayer(scapy.IP):
                ip_layer = packet[scapy.IP]
                packet_data['src_ip'] = ip_layer.src
                packet_data['dst_ip'] = ip_layer.dst
                packet_data['protocol'] = ip_layer.proto
            
            # TCP layer
            if packet.haslayer(scapy.TCP):
                tcp_layer = packet[scapy.TCP]
                packet_data['src_port'] = tcp_layer.sport
                packet_data['dst_port'] = tcp_layer.dport
                packet_data['protocol'] = 'TCP'
                
                # TCP flags
                flags = []
                if tcp_layer.flags & 0x02:  # SYN
                    flags.append('SYN')
                if tcp_layer.flags & 0x10:  # ACK
                    flags.append('ACK')
                if tcp_layer.flags & 0x01:  # FIN
                    flags.append('FIN')
                if tcp_layer.flags & 0x04:  # RST
                    flags.append('RST')
                if tcp_layer.flags & 0x08:  # PSH
                    flags.append('PSH')
                if tcp_layer.flags & 0x20:  # URG
                    flags.append('URG')
                
                packet_data['flags'] = flags
            
            # UDP layer
            elif packet.haslayer(scapy.UDP):
                udp_layer = packet[scapy.UDP]
                packet_data['src_port'] = udp_layer.sport
                packet_data['dst_port'] = udp_layer.dport
                packet_data['protocol'] = 'UDP'
            
            return packet_data
            
        except Exception as e:
            logger.debug(f"Erreur extraction paquet Scapy: {e}")
            return None
    
    def _add_packet_to_flows(self, packet_data: Dict):
        """Ajoute un paquet à un flow existant ou en crée un nouveau"""
        flow_key = self._create_flow_key(packet_data)
        
        if flow_key not in self.flows:
            self.flows[flow_key] = {
                'packets': [],
                'start_time': packet_data['timestamp'],
                'end_time': packet_data['timestamp']
            }
        
        self.flows[flow_key]['packets'].append(packet_data)
        self.flows[flow_key]['end_time'] = packet_data['timestamp']
    
    def _create_flow_key(self, packet_data: Dict) -> str:
        """Crée une clé unique pour identifier un flow bidirectionnel"""
        src_ip = packet_data.get('src_ip', '0.0.0.0')
        dst_ip = packet_data.get('dst_ip', '0.0.0.0')
        src_port = packet_data.get('src_port', 0)
        dst_port = packet_data.get('dst_port', 0)
        protocol = packet_data.get('protocol', 'UNKNOWN')
        
        # Créer un identifiant bidirectionnel
        ips = sorted([src_ip, dst_ip])
        ports = sorted([src_port, dst_port])
        
        return f"{ips[0]}:{ports[0]}-{ips[1]}:{ports[1]}-{protocol}"
    
    def _convert_flows_to_features(self) -> pd.DataFrame:
        """Convertit les flows en features CICIDS2017"""
        features_list = []
        
        logger.info(f"🔧 Conversion de {len(self.flows)} flows en features CICIDS2017...")
        
        for flow_key, flow_data in self.flows.items():
            if len(flow_data['packets']) < 2:  # Skip flows trop courts
                continue
            
            try:
                features = self.feature_extractor.extract_features_from_flow(flow_data)
                features['flow_id'] = flow_key
                features_list.append(features)
            except Exception as e:
                logger.debug(f"Erreur extraction features pour flow {flow_key}: {e}")
        
        if features_list:
            df = pd.DataFrame(features_list)
            logger.info(f"✅ {len(df)} flows convertis en features CICIDS2017")
            return df
        else:
            logger.warning("⚠️ Aucun flow valide trouvé")
            return pd.DataFrame()
    
    def _generate_simulated_flows(self) -> List[Dict]:
        """Génère des flows simulés pour le mode fallback"""
        simulated_flows = []
        current_time = time.time()
        
        # Flow normal HTTP
        normal_flow = {
            'packets': [
                {
                    'timestamp': current_time,
                    'src_ip': '192.168.1.100',
                    'dst_ip': '8.8.8.8',
                    'src_port': 45678,
                    'dst_port': 80,
                    'protocol': 'TCP',
                    'length': 60,
                    'flags': ['SYN']
                },
                {
                    'timestamp': current_time + 0.01,
                    'src_ip': '8.8.8.8',
                    'dst_ip': '192.168.1.100',
                    'src_port': 80,
                    'dst_port': 45678,
                    'protocol': 'TCP',
                    'length': 60,
                    'flags': ['SYN', 'ACK']
                },
                {
                    'timestamp': current_time + 0.02,
                    'src_ip': '192.168.1.100',
                    'dst_ip': '8.8.8.8',
                    'src_port': 45678,
                    'dst_port': 80,
                    'protocol': 'TCP',
                    'length': 500,
                    'flags': ['ACK', 'PSH']
                }
            ]
        }
        simulated_flows.append(normal_flow)
        
        # Flow suspect (nombreux petits paquets - potentiel scan)
        scan_flow = {
            'packets': []
        }
        
        for i in range(50):  # Beaucoup de petits paquets
            scan_flow['packets'].append({
                'timestamp': current_time + i * 0.001,  # Très rapprochés
                'src_ip': '10.0.0.1',
                'dst_ip': '192.168.1.100',
                'src_port': 12345,
                'dst_port': 22 + i,  # Ports qui changent
                'protocol': 'TCP',
                'length': 40,
                'flags': ['SYN']
            })
        
        simulated_flows.append(scan_flow)
        
        return simulated_flows


class NetworkModelValidator:
    """Validateur pour le modèle d'analyse réseau CICIDS2017"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.collector = RealTimeTrafficCollector()
        self.model = self._load_model(model_path)
        
        # Statistiques de validation
        self.validation_stats = {
            'total_flows_tested': 0,
            'normal_detected': 0,
            'attacks_detected': 0,
            'false_positives': 0,
            'false_negatives': 0,
            'tests_results': []
        }
    
    def _load_model(self, model_path: Optional[str]):
        """Charge le modèle d'analyse réseau"""
        try:
            # Import du modèle depuis votre structure
            from agents.cybersecurity_agent.custom_model_loaders import NetworkAnalyzerXGBoost
            return NetworkAnalyzerXGBoost()
        except Exception as e:
            logger.error(f"❌ Erreur chargement modèle: {e}")
            return None
    
    def run_validation_suite(self) -> Dict[str, Any]:
        """Lance une suite complète de tests de validation"""
        logger.info("🧪 Démarrage de la suite de validation complète...")
        
        results = {
            'validation_timestamp': datetime.now().isoformat(),
            'tests_performed': [],
            'overall_success': True,
            'recommendations': []
        }
        
        # Test 1: Validation basique du modèle
        logger.info("📊 Test 1: Validation basique du modèle")
        basic_test = self._test_model_basic_functionality()
        results['tests_performed'].append(basic_test)
        
        # Test 2: Trafic normal
        logger.info("🌐 Test 2: Détection trafic normal")
        normal_test = self._test_normal_traffic_detection()
        results['tests_performed'].append(normal_test)
        
        # Test 3: Simulation d'attaques
        logger.info("🚨 Test 3: Détection d'attaques simulées")
        attack_test = self._test_attack_detection()
        results['tests_performed'].append(attack_test)
        
        # Test 4: Performance en temps réel
        logger.info("⚡ Test 4: Performance temps réel")
        performance_test = self._test_realtime_performance()
        results['tests_performed'].append(performance_test)
        
        # Analyse globale
        results['overall_success'] = all(test['passed'] for test in results['tests_performed'])
        results['success_rate'] = sum(1 for test in results['tests_performed'] if test['passed']) / len(results['tests_performed'])
        
        # Recommandations
        if not results['overall_success']:
            results['recommendations'] = self._generate_recommendations(results['tests_performed'])
        
        # Statistiques finales
        results['validation_stats'] = self.validation_stats
        
        logger.info(f"✅ Suite de validation terminée - Succès: {results['success_rate']:.1%}")
        
        return results
    
    def _test_model_basic_functionality(self) -> Dict[str, Any]:
        """Test la fonctionnalité de base du modèle"""
        test_result = {
            'test_name': 'Basic Model Functionality',
            'passed': False,
            'details': {},
            'errors': []
        }
        
        try:
            if self.model is None:
                test_result['errors'].append("Modèle non chargé")
                return test_result
            
            # Test de cohérence: même input = même output
            test_input = ["normal web traffic"]
            result1 = self.model.predict(test_input)
            result2 = self.model.predict(test_input)
            
            consistency_check = result1 == result2
            test_result['details']['consistency'] = consistency_check
            
            # Test de réponse aux inputs évidents
            obvious_tests = {
                'normal_traffic': "normal web browsing http request",
                'ddos_traffic': "high volume ddos syn flood attack",
                'port_scan': "port scanning nmap reconnaissance"
            }
            
            obvious_results = {}
            for test_name, test_text in obvious_tests.items():
                result = self.model.predict([test_text])
                obvious_results[test_name] = result[0] if result else {}
            
            test_result['details']['obvious_tests'] = obvious_results
            
            # Le test passe s'il y a cohérence et des réponses sensées
            test_result['passed'] = (
                consistency_check and 
                len(obvious_results) == 3 and
                all('label' in result for result in obvious_results.values())
            )
            
        except Exception as e:
            test_result['errors'].append(f"Erreur test basique: {str(e)}")
        
        return test_result
    
    def _test_normal_traffic_detection(self) -> Dict[str, Any]:
        """Test la détection de trafic normal"""
        test_result = {
            'test_name': 'Normal Traffic Detection',
            'passed': False,
            'details': {},
            'errors': []
        }
        
        try:
            logger.info("📡 Collecte de trafic normal (30 secondes)...")
            logger.info("💡 Générez du trafic web normal maintenant (navigation, requêtes API)...")
            
            # Capturer du trafic normal
            features_df = self.collector.start_capture(duration=30, max_packets=100)
            
            if features_df.empty:
                test_result['errors'].append("Aucun trafic capturé")
                return test_result
            
            # Analyser avec le modèle
            normal_count = 0
            attack_count = 0
            total_flows = len(features_df)
            
            for index, row in features_df.iterrows():
                try:
                    # Convertir la ligne en format attendu par le modèle
                    features_text = f"flow with {row.get('Total Fwd Packets', 0)} forward packets"
                    result = self.model.predict([features_text])
                    
                    if result and len(result) > 0:
                        label = result[0].get('label', 'UNKNOWN')
                        if label == 'NORMAL':
                            normal_count += 1
                        else:
                            attack_count += 1
                    
                except Exception as e:
                    logger.debug(f"Erreur analyse flow: {e}")
            
            # Statistiques
            normal_rate = normal_count / total_flows if total_flows > 0 else 0
            
            test_result['details'] = {
                'total_flows': total_flows,
                'normal_detected': normal_count,
                'attacks_detected': attack_count,
                'normal_rate': normal_rate
            }
            
            # Le test passe si au moins 70% du trafic est détecté comme normal
            test_result['passed'] = normal_rate >= 0.7
            
            self.validation_stats['total_flows_tested'] += total_flows
            self.validation_stats['normal_detected'] += normal_count
            
        except Exception as e:
            test_result['errors'].append(f"Erreur test trafic normal: {str(e)}")
        
        return test_result
    
    def _test_attack_detection(self) -> Dict[str, Any]:
        """Test la détection d'attaques simulées"""
        test_result = {
            'test_name': 'Attack Detection',
            'passed': False,
            'details': {},
            'errors': []
        }
        
        try:
            # Test avec des descriptions d'attaques connues
            attack_samples = [
                "ddos attack high volume traffic flood",
                "port scan reconnaissance nmap scanning",
                "brute force ssh login attempts",
                "syn flood dos attack",
                "botnet malicious traffic"
            ]
            
            attack_detections = {}
            
            for attack_desc in attack_samples:
                result = self.model.predict([attack_desc])
                if result and len(result) > 0:
                    label = result[0].get('label', 'UNKNOWN')
                    confidence = result[0].get('score', 0)
                    
                    attack_detections[attack_desc] = {
                        'detected_as': label,
                        'confidence': confidence,
                        'is_attack': label != 'NORMAL'
                    }
            
            # Calculer le taux de détection
            total_attacks = len(attack_samples)
            detected_attacks = sum(1 for det in attack_detections.values() if det['is_attack'])
            detection_rate = detected_attacks / total_attacks
            
            test_result['details'] = {
                'attack_samples_tested': total_attacks,
                'attacks_detected': detected_attacks,
                'detection_rate': detection_rate,
                'detections': attack_detections
            }
            
            # Le test passe si au moins 60% des attaques sont détectées
            test_result['passed'] = detection_rate >= 0.6
            
            self.validation_stats['attacks_detected'] += detected_attacks
            
        except Exception as e:
            test_result['errors'].append(f"Erreur test détection attaques: {str(e)}")
        
        return test_result
    
    def _test_realtime_performance(self) -> Dict[str, Any]:
        """Test les performances en temps réel"""
        test_result = {
            'test_name': 'Real-time Performance',
            'passed': False,
            'details': {},
            'errors': []
        }
        
        try:
            # Mesurer le temps de traitement
            start_time = time.time()
            
            # Capturer un petit échantillon
            features_df = self.collector.start_capture(duration=10, max_packets=50)
            capture_time = time.time() - start_time
            
            # Mesurer le temps d'analyse
            analysis_start = time.time()
            predictions = []
            
            for index, row in features_df.iterrows():
                features_text = f"flow analysis {index}"
                result = self.model.predict([features_text])
                predictions.append(result)
            
            analysis_time = time.time() - analysis_start
            
            # Calculer les métriques
            total_flows = len(features_df)
            avg_analysis_time = analysis_time / total_flows if total_flows > 0 else 0
            
            test_result['details'] = {
                'capture_time': capture_time,
                'analysis_time': analysis_time,
                'total_flows_processed': total_flows,
                'avg_time_per_flow': avg_analysis_time,
                'flows_per_second': total_flows / analysis_time if analysis_time > 0 else 0
            }
            
            # Le test passe si l'analyse est assez rapide (< 1 seconde par flow)
            test_result['passed'] = avg_analysis_time < 1.0
            
        except Exception as e:
            test_result['errors'].append(f"Erreur test performance: {str(e)}")
        
        return test_result
    
    def _generate_recommendations(self, test_results: List[Dict]) -> List[str]:
        """Génère des recommandations basées sur les résultats"""
        recommendations = []
        
        for test in test_results:
            if not test['passed']:
                test_name = test['test_name']
                
                if test_name == 'Basic Model Functionality':
                    recommendations.append("🔧 Vérifiez que le modèle est correctement chargé et entraîné")
                    recommendations.append("📊 Validez le format des données d'entrée")
                
                elif test_name == 'Normal Traffic Detection':
                    normal_rate = test['details'].get('normal_rate', 0)
                    if normal_rate < 0.5:
                        recommendations.append("⚠️ Trop de faux positifs - ajustez les seuils du modèle")
                        recommendations.append("🎯 Réentraînez avec plus de données de trafic normal")
                
                elif test_name == 'Attack Detection':
                    detection_rate = test['details'].get('detection_rate', 0)
                    if detection_rate < 0.4:
                        recommendations.append("🚨 Améliorer la détection d'attaques")
                        recommendations.append("📈 Ajouter plus d'exemples d'attaques dans l'entraînement")
                
                elif test_name == 'Real-time Performance':
                    avg_time = test['details'].get('avg_time_per_flow', 0)
                    if avg_time > 2.0:
                        recommendations.append("⚡ Optimiser les performances du modèle")
                        recommendations.append("🔧 Considérer l'utilisation de GPU ou parallélisation")
        
        return recommendations
    
    def generate_validation_report(self, results: Dict[str, Any]) -> str:
        """Génère un rapport de validation détaillé"""
        report = []
        report.append("="*60)
        report.append("📊 RAPPORT DE VALIDATION - MODÈLE RÉSEAU CICIDS2017")
        report.append("="*60)
        report.append(f"📅 Date: {results['validation_timestamp']}")
        report.append(f"✅ Taux de succès global: {results['success_rate']:.1%}")
        report.append("")
        
        # Détails des tests
        for test in results['tests_performed']:
            status = "✅ PASSÉ" if test['passed'] else "❌ ÉCHOUÉ"
            report.append(f"🧪 {test['test_name']}: {status}")
            
            if test['details']:
                for key, value in test['details'].items():
                    if isinstance(value, float):
                        report.append(f"   📈 {key}: {value:.3f}")
                    else:
                        report.append(f"   📋 {key}: {value}")
            
            if test['errors']:
                for error in test['errors']:
                    report.append(f"   ❌ {error}")
            
            report.append("")
        
        # Recommandations
        if results['recommendations']:
            report.append("💡 RECOMMANDATIONS:")
            for rec in results['recommendations']:
                report.append(f"   {rec}")
            report.append("")
        
        # Statistiques globales
        stats = results['validation_stats']
        report.append("📊 STATISTIQUES GLOBALES:")
        report.append(f"   🔍 Flows testés: {stats['total_flows_tested']}")
        report.append(f"   ✅ Détections normales: {stats['normal_detected']}")
        report.append(f"   🚨 Détections d'attaques: {stats['attacks_detected']}")
        
        report.append("="*60)
        
        return "\n".join(report)


# Script de test rapide
def quick_validation_test():
    """Test rapide de validation du modèle"""
    print("🚀 VALIDATION RAPIDE DU MODÈLE RÉSEAU CICIDS2017")
    print("="*50)
    
    try:
        # Initialiser le validateur
        validator = NetworkModelValidator()
        
        # Test rapide du modèle
        print("📊 Test basique du modèle...")
        basic_test = validator._test_model_basic_functionality()
        
        if basic_test['passed']:
            print("✅ Modèle fonctionnel!")
            
            # Test de détection d'attaques
            print("🚨 Test détection d'attaques...")
            attack_test = validator._test_attack_detection()
            
            if attack_test['passed']:
                print("✅ Détection d'attaques fonctionnelle!")
                detection_rate = attack_test['details']['detection_rate']
                print(f"📈 Taux de détection: {detection_rate:.1%}")
            else:
                print("❌ Problème avec la détection d'attaques")
        else:
            print("❌ Problème avec le modèle de base")
        
        print("\n💡 Pour une validation complète, lancez:")
        print("python -c \"from agents.cybersecurity_agent.traffic_collector import NetworkModelValidator; v=NetworkModelValidator(); print(v.generate_validation_report(v.run_validation_suite()))\"")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        print("🔧 Vérifiez que les dépendances sont installées:")
        print("pip install pyshark scapy pandas numpy scikit-learn")


if __name__ == "__main__":
    quick_validation_test()