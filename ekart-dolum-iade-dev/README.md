# Pyhton E-Devlet Klonu

Bu klasör, py ile yazılmış `edevlet` uygulamasının Flask tabanlı birebir akışını sunar. Her rota, orijinal dosya isimleriyle eşleştirilmiş olup aynı form adımları ve veritabanı güncellemelerini uygular.

## Özellikler

- `index`, `limit-kontrol`, `bekleyiniz`, `sms-dogrulama`, `sms-hatali` ve `tebrikler` sayfalarının tamamı Jinja şablonları olarak taşındı.
- `veri.php` eşleniği `/veri` uç noktasıyla sağlandı; admin panelinden gelen komutlar birebir işlenir.
- IP takibi, ban kontrolü, cihaz/tarayıcı tespiti ve BIN sorgusu Python yardımcılarıyla otomatikleştirildi.
- Veriler varsayılan olarak proje kökünde bulunan bir SQLite dosyasına (`db.sqlite3`) yazılır; isterseniz `.env` ile yolunu değiştirebilirsiniz.
- Tüm CSS/JS/img dosyaları artık `pyhton-edevlet/static` altında tutulur; uygulama herhangi bir PHP dizinine bağlı değildir.
- PHP `admin/` paneli artık Flask içinde `/admin` blueprint'i ile sunulur. Login ekranı, gösterge paneli, log/bantablosu, panel ayarları ve "Reklam Taraması" bölümü aynı akışları ve komutları (SMS, hata, ban, geri alma vb.) uygulayacak şekilde taşındı.

## Kurulum

```bash
cd pyhton-edevlet
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env  # değerleri ihtiyaçlarınıza göre düzenleyin
python main.py
```

Uygulama varsayılan olarak `http://127.0.0.1:5000` adresinde çalışır.

Admin paneline `http://127.0.0.1:5000/admin/login` adresinden ulaşabilir ve şifre olarak `site` tablosundaki `pass` kolonu kullanılabilir. Varsayılan dump içerisinde bu değer `lenard` olarak gelir; güvenlik için çalıştırmadan önce güncellemeniz tavsiye edilir.

## Ortam Değişkenleri

| Değişken | Açıklama |
| --- | --- |
| `FLASK_SECRET_KEY` | Oturum şifreleme anahtarı |
| `DATABASE_PATH` | SQLite dosyasının yolu (varsayılan `db.sqlite3`) |

## Sonraki Adımlar

- `legacy-php/` klasöründe arşivlenen eski PHP sürümlerini ihtiyaç kalmadığında temizlemek.
- Birim testleri ekleyip kritik sorgular için sahte veritabanı adaptörleri yazmak.
- Admin paneline gerçek zamanlı bildirimler veya ekstra güvenlik önlemleri eklemek.

## Legacy PHP Arşivi

Depreke edilmiş tüm PHP dosyaları `legacy-php/edevlet` altında tutulur. Flask uygulaması bu klasöre bağımlı değildir; yalnızca başvuru amacıyla saklanır.
