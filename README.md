# jada-dos
Free Stress tester with http, tcp, udp, https methods (not intended for harm)
HTTP flood
python ultra_stress.py http://localhost:8080 -p http -t 128
TCP flood  
python ultra_stress.py localhost:8080 -p tcp -t 128
UDP flood
python ultra_stress.py localhost:8080 -p udp -t 256
# UDP is fastest
python ultra_stress.py target:port -p udp -t 512 -d 30
# For HTTP services
python ultra_stress.py http://target:port -p http -t 256 -d 60

TCP: 256 threads max

UDP: 512 threads max (UDP is lightweight)

HTTP: 128 threads max (more overhead)

HTTPS: 64 threads max (SSL overhead)

Custom payload size:
python ultra_stress.py localhost:8080 --payload-size 65500 -t 128

Mixed attack (alternates protocols):
python ultra_stress.py localhost:80 -p mixed -t 192 -d 120

HTTPS flood:
python ultra_stress.py https://localhost:8443 -p https -t 64 -d 45

UDP flood (fastest):
python ultra_stress.py 192.168.1.100:53 -p udp -t 512 -d 30

TCP SYN flood (raw TCP):
python ultra_stress.py localhost:8080 -p tcp -t 256 -d 60

Basic HTTP flood:
python ultra_stress.py http://localhost:8080 -t 128 -d 30
