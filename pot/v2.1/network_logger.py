from scapy.all import *
import os

output_directory = "tcp_streams"
os.system("rm -rf tcp_streams")
os.makedirs(output_directory, exist_ok=True)


def packet_callback(packet):
    src = (packet[IP].src, str(packet[TCP].sport))
    dst = (packet[IP].dst, str(packet[TCP].dport))

    host = [src, dst][src == ("172.17.0.2", "6379")]

    filename = "_".join(host)

    print("Saving new packet to", filename)

    pcap_filename = os.path.join(output_directory, f"{filename}.pcap")
    wrpcap(pcap_filename, packet, append=True)


print("sniff sniff sniff")
sniff(filter="tcp", iface="docker0", prn=packet_callback)
