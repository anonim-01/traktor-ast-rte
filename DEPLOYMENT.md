# 🚀 Cloudflare Deployment Kılavuzu

Bu belge, Flask uygulamanızı Cloudflare'e deploy etmek için gerekli tüm adımları içerir.

## ⚠️ ÖNEMLİ UYARI

**Python Flask uygulamaları doğrudan Cloudflare Workers'ta ÇALIŞMAZ!** Cloudflare Workers JavaScript/TypeScript runtime kullanır.

### 📋 Deployment Seçenekleri

#### 1️⃣ **Önerilen: Geleneksel Hosting + Cloudflare CDN**
```bash
# VPS, Heroku, Railway, Render vb. platformlarda host edin
# Cloudflare DNS ile bağlayın (CDN, DDoS koruması, Analytics)
```

#### 2️⃣ **Cloudflare Pages (Statik)**
```bash
# Sadece statik dosyaları (HTML, CSS, JS) host eder
# Backend için ayrı bir API sunucusu gerekir
```

#### 3️⃣ **Cloudflare Pages Functions (JavaScript/TypeScript)**
```bash
# Flask uygulamanızı JavaScript'e port edin
# Veya API endpoint'lerini Pages Functions ile yazın
```

---

## 🎯 Önerilen Deployment: Traditional VPS + Cloudflare

### Adım 1: VPS/Cloud Provider Seçin
- **DigitalOcean** - Başlangıç için ideal ($6/ay)
- **AWS EC2** - Ölçeklenebilir
- **Google Cloud Run** - Serverless Python
- **Railway** - Kolay deployment
- **Render** - Ücretsiz tier

### Adım 2: Sunucu Kurulumu

```bash
# Ubuntu 22.04 örneği
sudo apt update && sudo apt upgrade -y

# Python 3.11 kurulumu
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.11 python3.11-venv python3-pip -y

# Nginx kurulumu
sudo apt install nginx -y

# Supervisor kurulumu (process manager)
sudo apt install supervisor -y
```

### Adım 3: Uygulama Deployment

```bash
# Proje klasörünü oluştur
sudo mkdir -p /var/www/traktor-ast-rte
sudo chown -R $USER:$USER /var/www/traktor-ast-rte

# Projeyi klonla
cd /var/www/traktor-ast-rte
git clone https://github.com/anonim-01/traktor-ast-rte.git .

# Virtual environment oluştur
python3.11 -m venv venv
source venv/bin/activate

# Bağımlılıkları yükle
pip install -r requirements.txt

# Environment değişkenlerini ayarla
cp .env.example .env
nano .env  # Değerleri düzenleyin
```

### Adım 4: Gunicorn ile Servis Oluşturma

```bash
# Gunicorn yükle
pip install gunicorn

# Gunicorn config dosyası oluştur
nano gunicorn_config.py
```

**gunicorn_config.py:**
```python
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 5
errorlog = "/var/log/gunicorn/error.log"
accesslog = "/var/log/gunicorn/access.log"
loglevel = "info"
```

### Adım 5: Supervisor Yapılandırması

```bash
sudo nano /etc/supervisor/conf.d/traktor-ast-rte.conf
```

**traktor-ast-rte.conf:**
```ini
[program:traktor-ast-rte]
command=/var/www/traktor-ast-rte/venv/bin/gunicorn -c gunicorn_config.py main:app
directory=/var/www/traktor-ast-rte
user=www-data
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/traktor-ast-rte/err.log
stdout_logfile=/var/log/traktor-ast-rte/out.log
```

```bash
# Log klasörlerini oluştur
sudo mkdir -p /var/log/traktor-ast-rte
sudo mkdir -p /var/log/gunicorn
sudo chown -R www-data:www-data /var/log/traktor-ast-rte
sudo chown -R www-data:www-data /var/log/gunicorn

# Supervisor'ı yeniden başlat
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start traktor-ast-rte
```

### Adım 6: Nginx Yapılandırması

```bash
sudo nano /etc/nginx/sites-available/traktor-ast-rte
```

**traktor-ast-rte:**
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # IP Engelleme (BTK)
    deny 185.67.32.0/22;
    deny 185.67.35.0/24;

    # Client max body size
    client_max_body_size 10M;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # Static files
    location /assets/ {
        alias /var/www/traktor-ast-rte/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Proxy to Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_buffering off;
    }
}
```

```bash
# Site'ı aktif et
sudo ln -s /etc/nginx/sites-available/traktor-ast-rte /etc/nginx/sites-enabled/

# Test et
sudo nginx -t

# Nginx'i yeniden başlat
sudo systemctl restart nginx
```

### Adım 7: Cloudflare DNS Yapılandırması

1. **Cloudflare Dashboard**'a gidin
2. Domain ekleyin veya mevcut domainizi seçin
3. **DNS Records** bölümüne gidin
4. A Record ekleyin:
   ```
   Type: A
   Name: @ (veya subdomain)
   Content: VPS_IP_ADRESI
   Proxy status: Proxied (turuncu bulut) ✅
   TTL: Auto
   ```

### Adım 8: SSL/TLS Yapılandırması

1. Cloudflare Dashboard → **SSL/TLS**
2. **Encryption mode**: Full (strict) seçin
3. Sunucuda Let's Encrypt kurun:

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

#### Alternatif: Self-Signed SSL Sertifikası (Development/Test)

Eğer Let's Encrypt kullanmak istemiyorsanız, self-signed sertifika oluşturabilirsiniz:

```bash
# SSL sertifika dizini oluştur
sudo mkdir -p /var/www/traktor-ast-rte/certs

# Self-signed sertifika oluştur
sudo openssl req -x509 -newkey rsa:4096 -keyout /var/www/traktor-ast-rte/certs/key.pem -out /var/www/traktor-ast-rte/certs/cert.pem -days 365 -nodes -subj "/C=TR/ST=Istanbul/L=Istanbul/O=Traktor/CN=your-domain.com"

# Dosya izinlerini ayarla
sudo chmod 600 /var/www/traktor-ast-rte/certs/key.pem
sudo chmod 644 /var/www/traktor-ast-rte/certs/cert.pem
sudo chown www-data:www-data /var/www/traktor-ast-rte/certs/*
```

**Güvenlik Notu:** Self-signed sertifikalar production ortamında kullanılmamalıdır. Sadece development/test amaçlıdır.

### Adım 9: Cloudflare Ayarları (Opsiyonel)

#### Security
- **WAF** (Web Application Firewall) aktif
- **DDoS Protection** otomatik
- **Rate Limiting**: 100 req/min per IP

#### Speed
- **Auto Minify**: HTML, CSS, JS ✅
- **Brotli Compression** ✅
- **HTTP/3** ✅
- **Caching Level**: Standard

#### Firewall Rules
```
BTK IP Engelleme:
(ip.src in {185.67.32.0/22 185.67.35.0/24}) → Block
```

---

## 🔒 Güvenlik Kontrol Listesi

- [ ] `.env` dosyası güvenli şekilde saklanıyor
- [ ] `FLASK_SECRET_KEY` güçlü ve benzersiz
- [ ] Cloudflare API token güncellendi
- [ ] Database dosyası web'den erişilebilir değil
- [ ] HTTPS zorunlu (HTTP → HTTPS redirect)
- [ ] BTK IP aralıkları engellendi
- [ ] Admin paneli şifresi güçlü
- [ ] Firewall aktif (UFW)
- [ ] Fail2ban kurulu (brute-force koruması)

---

## 📊 İzleme ve Bakım

### Log İzleme
```bash
# Uygulama logları
sudo tail -f /var/log/traktor-ast-rte/out.log
sudo tail -f /var/log/traktor-ast-rte/err.log

# Gunicorn logları
sudo tail -f /var/log/gunicorn/access.log
sudo tail -f /var/log/gunicorn/error.log

# Nginx logları
sudo tail -f /var/nginx/access.log
sudo tail -f /var/nginx/error.log
```

### Güncelleme
```bash
cd /var/www/traktor-ast-rte
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo supervisorctl restart traktor-ast-rte
```

### Yedekleme
```bash
# Database yedekleme
sudo cp /var/www/traktor-ast-rte/db.sqlite3 /backup/db-$(date +%Y%m%d).sqlite3

# Tam yedek
sudo tar -czf /backup/traktor-$(date +%Y%m%d).tar.gz /var/www/traktor-ast-rte
```

---

## 🆘 Sorun Giderme

### Uygulama Çalışmıyor
```bash
# Servis durumunu kontrol et
sudo supervisorctl status traktor-ast-rte

# Logları incele
sudo tail -100 /var/log/traktor-ast-rte/err.log

# Manuel başlatma (debug)
cd /var/www/traktor-ast-rte
source venv/bin/activate
python main.py
```

### Nginx Hataları
```bash
# Config testi
sudo nginx -t

# Nginx yeniden başlat
sudo systemctl restart nginx

# Port dinleme kontrolü
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :8000
```

### Cloudflare Bağlantı Sorunları
- SSL/TLS mode'u kontrol edin (Full strict olmalı)
- Origin server IP doğru mu kontrol edin
- Cloudflare cache'i temizleyin (Purge Everything)

---

## 📞 Destek

Herhangi bir sorun yaşarsanız:
1. Logları kontrol edin
2. GitHub Issues'da sorun açın
3. Cloudflare Community Forum

---

## 🔄 Alternatif: Docker Deployment

Eğer Docker kullanmak isterseniz:

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "-c", "gunicorn_config.py", "main:app"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./db.sqlite3:/app/db.sqlite3
      - ./logs:/app/logs
    environment:
      - FLASK_ENV=production
    restart: unless-stopped
```

---

## ✅ Production Checklist

### Deployment Öncesi
- [ ] Tüm testler geçiyor
- [ ] Environment değişkenleri ayarlandı
- [ ] Database migrate edildi
- [ ] Static dosyalar toplandi
- [ ] SSL sertifikası kuruldu

### Deployment Sonrası
- [ ] Ana sayfa açılıyor
- [ ] Admin paneli çalışıyor
- [ ] IP engelleme aktif
- [ ] Loglar düzgün kaydediliyor
- [ ] HTTPS zorunlu
- [ ] Performance testi yapıldı

---

**📅 Son Güncelleme:** 17 Kasım 2025
**🎯 Platform:** Ubuntu 22.04 + Nginx + Gunicorn + Cloudflare
