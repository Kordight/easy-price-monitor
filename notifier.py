"""
Email Notification Module for Easy Price Monitor

This module handles sending email alerts when significant price changes are detected.
Supports both SSL and STARTTLS SMTP connections, and can send to single or multiple
recipients. Formats alerts as HTML emails with product links and detailed price information.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from storage import get_product_url_by_id_mysql, get_shop_id_by_name_mysql
from utils import load_products


def send_email_alert(changes, smtp_config, email_from, email_to):
    """
    Sends email alerts for price changes.
    
    Supports both single and multiple recipients. Handles both SSL (port 465) and STARTTLS
    (other ports) SMTP connections. Formats alerts as HTML emails with product links and
    price change information.
    
    Args:
        changes: List of dictionaries containing price change information
        smtp_config: Dictionary with 'server', 'port', 'user', 'password' keys
        email_from: Sender email address
        email_to: Recipient email address (string) or list of recipient addresses
    """
    if not changes:
        return

    # Support both single string and list of recipients
    if isinstance(email_to, str):
        recipients = [email_to]
    else:
        recipients = email_to
    
    # Join recipients for the email header
    email_to_header = ", ".join(recipients)

    subject = "[Easy Price Monitor] Alert: Price Change Detected"
    changed_products = []
    changed_products_text = []

    # Build fallback map from products.json in case URL is missing
    try:
      products = load_products("products.json")
      url_fallback = {}
      for p in products:
        name = p.get("name")
        for s in p.get("shops", []):
          url_fallback[(name, s.get("name"))] = s.get("url")
    except Exception:
      url_fallback = {}

    for c in changes:
      try:
        # Prefer DB lookup when product_id present; otherwise use provided URL; finally fallback to products.json
        if 'product_id' in c:
          url = get_product_url_by_id_mysql(c['product_id'], get_shop_id_by_name_mysql(c['shop_name']))
        else:
          url = c.get('product_url', '')
        if not url:
          url = url_fallback.get((c.get('product_name'), c.get('shop_name')), '')

        # Normalize numeric fields safely for display and arrows
        try:
          price_diff_val = float(c.get('price_diff', 0) or 0)
        except Exception:
          price_diff_val = 0.0
        try:
          percent_val = float(c.get('percent_change', 0) or 0)
        except Exception:
          percent_val = 0.0
        arrow = '↑' if price_diff_val > 0 else '↓' if price_diff_val < 0 else '→'

        changed_products.append(
          f"<li><a href='{url}'>{c.get('product_name','(unknown)')}</a> at {c.get('shop_name','(unknown)')}: "
          f"(change: <b>{price_diff_val:+.2f} {c.get('currency','')}</b>, {percent_val:+.2f}% {arrow})"
          f"<br> Current price <b>{c.get('price','')}</b></li>"
        )
        changed_products_text.append(
          f"- {c.get('product_name','(unknown)')} at {c.get('shop_name','(unknown)')}: "
          f"{price_diff_val:+.2f} {c.get('currency','')} ({percent_val:+.2f}%), now {c.get('price','')}\n  {url}"
        )
      except Exception as item_err:
        # Best-effort: include minimal info even if some fields are missing
        changed_products.append(
          f"<li>{c.get('product_name','(unknown)')} at {c.get('shop_name','(unknown)')} (details unavailable)</li>"
        )
        changed_products_text.append(
          f"- {c.get('product_name','(unknown)')} at {c.get('shop_name','(unknown)')} (details unavailable)"
        )

    # Log how many items will be included
    try:
      from datetime import datetime as _dt
      print(f"[{_dt.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] Preparing email with {len(changed_products)} alert item(s)")
    except Exception:
      pass

    # Ensure the report never renders empty for recipients
    if not changed_products:
      changed_products.append("<li>No detailed items available. Check logs for filtering.</li>")
      changed_products_text.append("(No detailed items available. Check logs for filtering.)")
    changed_products = "".join(changed_products)
    changed_products_text = "\n".join(changed_products_text)

    msg = MIMEMultipart('alternative')
    msg["From"] = email_from
    msg["To"] = email_to_header
    msg["Subject"] = subject
    body = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Price Alert</title>
      <style>
        body {{
          margin: 0;
          padding: 0;
          background-color: #f5f8fa;
          font-family: Arial, sans-serif;
          -webkit-text-size-adjust: 100%;
        }}
        .container {{
          max-width: 600px;
          margin: 0 auto;
          background: #ffffff;
          border-radius: 8px;
          overflow: hidden;
          box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        }}
        .header {{
          background: #00A4BD;
          color: #ffffff;
          text-align: center;
          padding: 24px;
        }}
        .header h1 {{
          margin: 0;
          font-size: 24px;
        }}
        .content {{
          padding: 20px;
          color: #333333;
          font-size: 16px;
          line-height: 1.5;
        }}
        .content h2 {{
          font-size: 18px;
          margin-bottom: 12px;
          color: #00A4BD;
        }}
        .product-list li {{
          margin-bottom: 8px;
        }}
        .footer {{
          font-size: 12px;
          color: #888888;
          text-align: center;
          padding: 16px;
        }}
        @media only screen and (max-width: 600px) {{
          .header h1 {{
            font-size: 20px;
          }}
          .content {{
            font-size: 14px;
          }}
        }}
      </style>
    </head>
    <body>
      <div class="container">
        <div class="header">
          <h1>🔔 Price Change Detected</h1>
        </div>
        <div class="content">
          <h2>Easy Price Monitor found updates:</h2>
          <ul class="product-list">
            {changed_products}
          </ul>
          <p style="margin-top:20px;">
            Best regards,<br>
            <b>Easy Price Monitor</b><br>
            <span style="font-size:12px; color:#888;">This is an automated message, please do not reply.</span>
          </p>
        </div>
        <div class="footer">
          Generated by <a href="https://github.com/Kordight/Easy-Price-Monitor"> Easy Price Monitor </a>
        </div>
      </div>
    </body>
    </html>
    """

    # Attach plain text alternative and HTML with UTF-8 encoding
    text_body = (
      "Price Change Detected\n\n" +
      "Updates:\n" +
      changed_products_text +
      "\n\nBest regards,\nEasy Price Monitor\n"
    )
    msg.attach(MIMEText(text_body, "plain", "utf-8"))
    msg.attach(MIMEText(body, "html", "utf-8"))

    port = smtp_config["port"]
    
    host = smtp_config["server"]
    try:
        if port == 465:
            # SSL
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] Connecting to SMTP server {host}:{port} using SSL")
            with smtplib.SMTP_SSL(host, port) as smtp:
                smtp.login(smtp_config["user"], smtp_config["password"])
                smtp.send_message(msg, to_addrs=recipients)
        else:
            # STARTTLS
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] Connecting to SMTP server {host}:{port} using STARTTLS")
            with smtplib.SMTP(host, port) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
                smtp.login(smtp_config["user"], smtp_config["password"])
                smtp.send_message(msg, to_addrs=recipients)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] Email alert sent successfully to {email_to_header}")
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [ERROR] Failed to send email to {email_to_header}: {e}")


