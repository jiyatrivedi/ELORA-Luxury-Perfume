"""
email_service.py — ELORA Order Confirmation Email
Sends a branded HTML email via Gmail SMTP using credentials
loaded exclusively from environment variables (never hardcoded).
"""

import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# HTML email template
# ---------------------------------------------------------------------------
def _build_html(order: dict, items: list) -> str:
    """Build a premium ELORA-branded HTML order confirmation email."""

    # ---- Items rows ----
    rows_html = ""
    for item in items:
        rows_html += f"""
        <tr>
          <td style="padding:14px 20px;border-bottom:1px solid #1e1a18;
                     font-family:'Georgia',serif;font-size:15px;
                     color:#f0ebe3;">
            {item['product_name']}
          </td>
          <td style="padding:14px 20px;border-bottom:1px solid #1e1a18;
                     font-size:13px;color:#7a7068;text-align:center;">
            {item['quantity']}
          </td>
          <td style="padding:14px 20px;border-bottom:1px solid #1e1a18;
                     font-size:13px;color:#c9a96e;text-align:right;">
            ${int(item['unit_price'])}
          </td>
          <td style="padding:14px 20px;border-bottom:1px solid #1e1a18;
                     font-size:13px;font-weight:600;color:#e8d5aa;text-align:right;">
            ${int(item['subtotal'])}
          </td>
        </tr>"""

    # ---- Full template ----
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1.0"/>
  <title>Your ELORA Order — {order['order_number']}</title>
</head>
<body style="margin:0;padding:0;background-color:#09080a;
             font-family:'Helvetica Neue',Arial,sans-serif;">

  <!-- Outer wrapper -->
  <table width="100%" cellpadding="0" cellspacing="0"
         style="background-color:#09080a;padding:40px 20px;">
    <tr>
      <td align="center">

        <!-- Email card -->
        <table width="600" cellpadding="0" cellspacing="0"
               style="max-width:600px;width:100%;background-color:#100e0e;
                      border:1px solid rgba(201,169,110,0.18);">

          <!-- ===== HEADER ===== -->
          <tr>
            <td style="padding:0;">
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td style="height:3px;background:linear-gradient(90deg,#c9a96e,#8a6e40,transparent);"></td>
                </tr>
              </table>
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td align="center"
                      style="padding:44px 40px 36px;
                             border-bottom:1px solid rgba(201,169,110,0.14);">
                    <p style="margin:0;font-family:'Georgia',serif;
                               font-size:28px;font-weight:400;
                               letter-spacing:0.55em;color:#c9a96e;
                               text-transform:uppercase;">ELORA</p>
                    <p style="margin:10px 0 0;font-size:11px;font-weight:400;
                               letter-spacing:0.28em;text-transform:uppercase;
                               color:#4a4440;">Luxury Fragrance</p>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- ===== HERO CONFIRMATION ===== -->
          <tr>
            <td style="padding:44px 40px 32px;text-align:center;
                       border-bottom:1px solid rgba(201,169,110,0.10);">
              <!-- Checkmark icon -->
              <div style="display:inline-block;width:60px;height:60px;
                           border-radius:50%;border:1px solid rgba(201,169,110,0.3);
                           background:rgba(201,169,110,0.07);
                           text-align:center;line-height:60px;margin-bottom:22px;">
                <span style="font-size:22px;color:#c9a96e;">&#10003;</span>
              </div>
              <p style="margin:0 0 6px;font-size:11px;font-weight:400;
                         letter-spacing:0.38em;text-transform:uppercase;
                         color:#c9a96e;">Order Confirmed</p>
              <h1 style="margin:0 0 14px;font-family:'Georgia',serif;
                          font-size:30px;font-weight:400;color:#f0ebe3;
                          letter-spacing:0.02em;line-height:1.2;">
                Thank you, {order['full_name'].split()[0]}.
              </h1>
              <p style="margin:0;font-size:13px;font-weight:300;
                         color:#7a7068;line-height:1.8;max-width:380px;
                         display:inline-block;">
                Your order has been received and is being prepared with care.
                A signature ELORA experience awaits you.
              </p>
            </td>
          </tr>

          <!-- ===== ORDER META ===== -->
          <tr>
            <td style="padding:0;">
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td width="33%" align="center"
                      style="padding:22px 16px;border-right:1px solid rgba(201,169,110,0.10);
                             border-bottom:1px solid rgba(201,169,110,0.10);">
                    <p style="margin:0 0 5px;font-size:9px;letter-spacing:0.3em;
                               text-transform:uppercase;color:#4a4440;">Order Number</p>
                    <p style="margin:0;font-size:13px;color:#c9a96e;
                               font-family:'Georgia',serif;letter-spacing:0.05em;">
                      {order['order_number']}
                    </p>
                  </td>
                  <td width="33%" align="center"
                      style="padding:22px 16px;border-right:1px solid rgba(201,169,110,0.10);
                             border-bottom:1px solid rgba(201,169,110,0.10);">
                    <p style="margin:0 0 5px;font-size:9px;letter-spacing:0.3em;
                               text-transform:uppercase;color:#4a4440;">Order Date</p>
                    <p style="margin:0;font-size:13px;color:#f0ebe3;">
                      {order['created_at'][:10]}
                    </p>
                  </td>
                  <td width="33%" align="center"
                      style="padding:22px 16px;
                             border-bottom:1px solid rgba(201,169,110,0.10);">
                    <p style="margin:0 0 5px;font-size:9px;letter-spacing:0.3em;
                               text-transform:uppercase;color:#4a4440;">Status</p>
                    <p style="margin:0;font-size:13px;color:#6ec98a;
                               text-transform:capitalize;">
                      {order['status']}
                    </p>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- ===== ORDERED ITEMS ===== -->
          <tr>
            <td style="padding:32px 40px 0;">
              <p style="margin:0 0 18px;font-size:9px;letter-spacing:0.32em;
                         text-transform:uppercase;color:#c9a96e;
                         padding-bottom:10px;
                         border-bottom:1px solid rgba(201,169,110,0.18);">
                Ordered Items
              </p>
            </td>
          </tr>
          <tr>
            <td style="padding:0 40px;">
              <table width="100%" cellpadding="0" cellspacing="0">
                <!-- Table header -->
                <tr style="background:rgba(201,169,110,0.04);">
                  <th style="padding:10px 20px;font-size:9px;letter-spacing:0.25em;
                              text-transform:uppercase;color:#4a4440;
                              text-align:left;font-weight:500;">Product</th>
                  <th style="padding:10px 20px;font-size:9px;letter-spacing:0.25em;
                              text-transform:uppercase;color:#4a4440;
                              text-align:center;font-weight:500;">Qty</th>
                  <th style="padding:10px 20px;font-size:9px;letter-spacing:0.25em;
                              text-transform:uppercase;color:#4a4440;
                              text-align:right;font-weight:500;">Unit Price</th>
                  <th style="padding:10px 20px;font-size:9px;letter-spacing:0.25em;
                              text-transform:uppercase;color:#4a4440;
                              text-align:right;font-weight:500;">Subtotal</th>
                </tr>
                {rows_html}
              </table>
            </td>
          </tr>

          <!-- ===== ORDER TOTAL ===== -->
          <tr>
            <td style="padding:0 40px 32px;">
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td style="padding:18px 20px 0;
                              border-top:1px solid rgba(201,169,110,0.18);">
                    <table width="100%" cellpadding="0" cellspacing="0">
                      <tr>
                        <td style="font-size:9px;letter-spacing:0.3em;
                                   text-transform:uppercase;color:#7a7068;">
                          Order Total
                        </td>
                        <td align="right"
                            style="font-family:'Georgia',serif;font-size:22px;
                                   font-weight:400;color:#c9a96e;">
                          ${int(order['total'])}
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- ===== DELIVERY ADDRESS ===== -->
          <tr>
            <td style="padding:0 40px 36px;">
              <table width="100%" cellpadding="0" cellspacing="0"
                     style="background:rgba(9,8,10,0.6);
                            border:1px solid rgba(201,169,110,0.10);">
                <tr>
                  <td style="padding:20px 24px;">
                    <p style="margin:0 0 14px;font-size:9px;letter-spacing:0.32em;
                               text-transform:uppercase;color:#c9a96e;">
                      Delivery Address
                    </p>
                    <p style="margin:0;font-family:'Georgia',serif;font-size:16px;
                               font-weight:400;color:#e8d5aa;font-style:italic;
                               margin-bottom:6px;">
                      {order['full_name']}
                    </p>
                    <p style="margin:0;font-size:13px;color:#7a7068;line-height:1.8;">
                      {order['address']}<br/>
                      {order['city']}, {order['state']} &mdash; {order['pincode']}<br/>
                      <span style="color:#4a4440;">{order['phone']}</span>
                    </p>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- ===== DIVIDER ===== -->
          <tr>
            <td style="padding:0 40px;">
              <div style="height:1px;background:rgba(201,169,110,0.10);"></div>
            </td>
          </tr>

          <!-- ===== FOOTER ===== -->
          <tr>
            <td align="center"
                style="padding:32px 40px 40px;">
              <p style="margin:0 0 6px;font-family:'Georgia',serif;
                         font-size:14px;letter-spacing:0.4em;color:#4a4440;
                         text-transform:uppercase;">ELORA</p>
              <p style="margin:0 0 16px;font-size:11px;color:#2e2a28;
                         letter-spacing:0.15em;">
                Crafted for those who leave an impression.
              </p>
              <p style="margin:0;font-size:11px;color:#2e2a28;">
                ELORA Atelier, Ahmedabad, Gujarat, India &nbsp;&middot;&nbsp;
                concierge@eloraperfum.example
              </p>
              <p style="margin:14px 0 0;font-size:10px;color:#2e2a28;">
                &copy; 2026 ELORA. All rights reserved.
              </p>
            </td>
          </tr>

          <!-- Bottom gold border -->
          <tr>
            <td style="height:2px;
                       background:linear-gradient(90deg,transparent,#8a6e40,#c9a96e,#8a6e40,transparent);">
            </td>
          </tr>

        </table>
        <!-- /Email card -->

      </td>
    </tr>
  </table>

</body>
</html>"""

    return html


# ---------------------------------------------------------------------------
# Plain-text fallback
# ---------------------------------------------------------------------------
def _build_plain(order: dict, items: list) -> str:
    lines = [
        "ELORA — Order Confirmation",
        "=" * 40,
        f"Order Number : {order['order_number']}",
        f"Order Date   : {order['created_at'][:10]}",
        f"Status       : {order['status']}",
        "",
        "ORDERED ITEMS",
        "-" * 40,
    ]
    for item in items:
        lines.append(
            f"  {item['product_name']:<20} x{item['quantity']}  "
            f"${int(item['unit_price'])} each = ${int(item['subtotal'])}"
        )
    lines += [
        "-" * 40,
        f"  ORDER TOTAL: ${int(order['total'])}",
        "",
        "DELIVERY ADDRESS",
        "-" * 40,
        f"  {order['full_name']}",
        f"  {order['address']}",
        f"  {order['city']}, {order['state']} — {order['pincode']}",
        f"  {order['phone']}",
        "",
        "© 2026 ELORA. All rights reserved.",
        "ELORA Atelier, Ahmedabad, Gujarat, India",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Public send function
# ---------------------------------------------------------------------------
def send_order_confirmation(order: dict, items: list) -> bool:
    """
    Send an order confirmation email to order['email'].

    Reads SMTP credentials from environment variables:
        MAIL_SERVER    (default: smtp.gmail.com)
        MAIL_PORT      (default: 587)
        MAIL_USERNAME  — your Gmail address
        MAIL_PASSWORD  — your Gmail App Password (16 chars, no spaces)

    Returns True on success, False on failure.
    Never raises — the order is already saved before this is called.
    """
    mail_server   = os.environ.get("MAIL_SERVER",   "smtp.gmail.com")
    mail_port     = int(os.environ.get("MAIL_PORT", "587"))
    mail_username = os.environ.get("MAIL_USERNAME", "")
    mail_password = os.environ.get("MAIL_PASSWORD", "")

    if not mail_username or not mail_password:
        logger.warning(
            "Email not sent: MAIL_USERNAME or MAIL_PASSWORD not configured. "
            "Add them to your .env file."
        )
        return False

    recipient = order.get("email", "")
    if not recipient:
        logger.warning("Email not sent: order has no recipient email.")
        return False

    subject = f"Your ELORA Order is Confirmed — {order['order_number']}"

    # Build MIME message (multipart: plain + HTML)
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"ELORA Parfum <{mail_username}>"
    msg["To"]      = recipient

    plain_part = MIMEText(_build_plain(order, items), "plain", "utf-8")
    html_part  = MIMEText(_build_html(order, items),  "html",  "utf-8")

    # RFC 2046: last part wins — HTML is preferred
    msg.attach(plain_part)
    msg.attach(html_part)

    try:
        with smtplib.SMTP(mail_server, mail_port, timeout=10) as server:
            server.ehlo()
            server.starttls()          # upgrade to TLS
            server.ehlo()
            server.login(mail_username, mail_password)
            server.sendmail(mail_username, [recipient], msg.as_string())

        logger.info("Order confirmation email sent to %s (order %s)",
                    recipient, order["order_number"])
        return True

    except smtplib.SMTPAuthenticationError:
        logger.error(
            "Email send failed — SMTP authentication error. "
            "Check MAIL_USERNAME and MAIL_PASSWORD in your .env file. "
            "Make sure you are using a Gmail App Password, not your account password."
        )
    except smtplib.SMTPException as exc:
        logger.error("Email send failed — SMTP error: %s", exc)
    except TimeoutError:
        logger.error("Email send failed — SMTP connection timed out.")
    except OSError as exc:
        logger.error("Email send failed — network error: %s", exc)

    return False
