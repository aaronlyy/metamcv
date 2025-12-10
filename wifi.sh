#!/bin/bash
set -e

echo "Installiere benötigte Pakete ..."
sudo apt update
sudo apt install -y hostapd dnsmasq

echo "Deaktiviere Services vor Konfiguration ..."
sudo systemctl stop hostapd
sudo systemctl stop dnsmasq

echo "Konfiguriere dnsmasq ..."
sudo tee /etc/dnsmasq.conf >/dev/null <<EOF
interface=wlan0
dhcp-range=192.168.88.10,192.168.88.50,255.255.255.0,24h
EOF

echo "Konfiguriere statische IP für wlan0 ..."
sudo tee -a /etc/dhcpcd.conf >/dev/null <<EOF

interface wlan0
static ip_address=192.168.88.1/24
nohook wpa_supplicant
EOF

echo "Konfiguriere hostapd (Hotspot) ..."
sudo tee /etc/hostapd/hostapd.conf >/dev/null <<EOF
interface=wlan0
driver=nl80211
ssid=kuchenfi
hw_mode=g
channel=6
auth_algs=1
wmm_enabled=1
ignore_broadcast_ssid=0
EOF

echo "Trage hostapd Config Pfad ein ..."
sudo sed -i 's|#DAEMON_CONF=""|DAEMON_CONF="/etc/hostapd/hostapd.conf"|' /etc/default/hostapd

echo "Aktiviere Services ..."
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo systemctl enable dnsmasq

echo "Starte Services ..."
sudo systemctl restart dhcpcd
sudo systemctl start dnsmasq
sudo systemctl start hostapd

echo "Hotspot 'kuchenfi' wurde eingerichtet!"
