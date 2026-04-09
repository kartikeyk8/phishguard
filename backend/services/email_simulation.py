"""
Email Simulation Service — sends real phishing training emails via smtplib
"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from backend.config import SMTP_EMAIL, SMTP_PASSWORD

TEMPLATES = {
    "beginner": {
        "from_name":  "PayPal Security",
        "from_addr":  "security@paypa1-alert.com",
        "subject":    "Your PayPal account has been limited!",
        "html": """<div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;border:1px solid #ddd">
  <div style="background:#003087;padding:20px;text-align:center">
    <h2 style="color:white;margin:0;font-size:24px">PayPal</h2>
  </div>
  <div style="padding:30px">
    <h3 style="color:#333">Your account has been limited</h3>
    <p>Dear {name},</p>
    <p>We have detected <strong>unusual activity</strong> on your PayPal account. Your account has been temporarily limited until you verify your information.</p>
    <p>Please click the button below to restore your account access immediately:</p>
    <div style="text-align:center;margin:30px 0">
      <a href="http://paypa1-secure-verify.com/restore" style="background:#0070ba;color:white;padding:14px 28px;text-decoration:none;border-radius:4px;font-size:16px;display:inline-block">Restore My Account</a>
    </div>
    <p style="color:#d93025"><strong>Warning:</strong> If you do not verify within 24 hours your account will be permanently suspended.</p>
    <p>PayPal Security Team</p>
  </div>
  <div style="background:#f5f5f5;padding:15px;text-align:center;font-size:11px;color:#888;border-top:1px solid #ddd">
    ⚠️ THIS IS A PHISHGUARD TRAINING EMAIL — This is a simulated phishing attempt for cybersecurity awareness training only. Do not click the link above.
  </div>
</div>""",
        "red_flags": [
            "Sender domain is paypa1-alert.com not paypal.com — digit 1 used instead of letter l",
            "Uses urgent threatening language to pressure you into acting fast",
            "Link goes to paypa1-secure-verify.com which is not PayPal's real domain",
            "Legitimate PayPal never asks you to click a link to restore your account",
        ]
    },
    "intermediate": {
        "from_name":  "IT Helpdesk",
        "from_addr":  "helpdesk@yourcompany-support.com",
        "subject":    "Mandatory password reset required by 5pm today",
        "html": """<div style="font-family:Calibri,Arial,sans-serif;max-width:600px;margin:0 auto;border:1px solid #ddd">
  <div style="background:#0078d4;padding:15px 20px">
    <h3 style="color:white;margin:0">IT Helpdesk — Security Notice</h3>
  </div>
  <div style="padding:25px">
    <p>Hi {name},</p>
    <p>Our security system has flagged your account for a <strong>mandatory password reset</strong> as part of our quarterly security compliance update.</p>
    <p>All employees must complete this by <strong>5:00 PM today</strong> or their account will be locked pending IT review.</p>
    <p>Please reset your password using the secure link below:</p>
    <div style="background:#f0f0f0;padding:12px;border-left:4px solid #0078d4;margin:20px 0;word-break:break-all">
      <a href="http://reset.yourcompany-support.com/reset?token=a8f3k2m9">http://reset.yourcompany-support.com/reset?token=a8f3k2m9</a>
    </div>
    <p>If you have any issues contact the helpdesk on ext. 4200.</p>
    <p>Regards,<br>IT Helpdesk Team</p>
  </div>
  <div style="background:#f5f5f5;padding:12px;text-align:center;font-size:11px;color:#888;border-top:1px solid #ddd">
    ⚠️ PHISHGUARD TRAINING EMAIL — Simulated phishing for awareness training only.
  </div>
</div>""",
        "red_flags": [
            "Sender domain is yourcompany-support.com — not your company's real domain",
            "Artificial urgency with a 5pm deadline to pressure immediate action",
            "Reset link goes to yourcompany-support.com not your actual company domain",
            "Real IT departments never send password reset links via email",
        ]
    },
    "advanced": {
        "from_name":  "James Harris — Barclays Mortgages",
        "from_addr":  "james.harris@barclays-mortgages.co.uk",
        "subject":    "Re: Your mortgage enquiry — urgent signature required",
        "html": """<div style="font-family:Georgia,serif;max-width:600px;margin:0 auto;border:1px solid #ddd">
  <div style="border-bottom:3px solid #00aeef;padding:15px 20px;background:#fff">
    <span style="font-size:20px;color:#00aeef;font-weight:bold">Barclays</span>
    <span style="font-size:12px;color:#666;margin-left:10px">Mortgage Services</span>
  </div>
  <div style="padding:25px">
    <p>Hi {name},</p>
    <p>Further to our call on Tuesday regarding your mortgage application, the updated agreement is now ready for your review and signature.</p>
    <p>Could you please sign and return by <strong>4:00 PM today</strong> to ensure we can lock in the rate we discussed before the end of the business day.</p>
    <div style="text-align:center;margin:25px 0">
      <a href="http://barclays-sign.docusign-secure.co.uk/d/abc123" style="background:#00aeef;color:white;padding:12px 24px;text-decoration:none;border-radius:3px;font-size:15px;display:inline-block">Review and Sign Document</a>
    </div>
    <p>Please do not hesitate to call me directly on 0207-555-0192 if you have any questions.</p>
    <p>Kind regards,<br><strong>James Harris</strong><br>Senior Mortgage Advisor | Barclays<br>Direct: 0207-555-0192<br>james.harris@barclays-mortgages.co.uk</p>
  </div>
  <div style="background:#f5f5f5;padding:12px;text-align:center;font-size:11px;color:#888;border-top:1px solid #ddd">
    ⚠️ PHISHGUARD TRAINING — Simulated spear phishing email for cybersecurity awareness training.
  </div>
</div>""",
        "red_flags": [
            "Sender domain is barclays-mortgages.co.uk — real Barclays uses barclays.co.uk",
            "DocuSign link goes to docusign-secure.co.uk not docusign.com",
            "Uses personal context from a real event to build false trust",
            "Phone number 0207-555-0192 in the email is attacker-controlled",
            "End of day urgency prevents you from verifying through official channels",
        ]
    }
}


def send_phishing_email(to_email: str, difficulty: str, user_name: str) -> dict:
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        return {"sent": False, "reason": "SMTP not configured"}

    template = TEMPLATES.get(difficulty, TEMPLATES["beginner"])

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = template["subject"]
        msg["From"]    = f"{template['from_name']} <{SMTP_EMAIL}>"
        msg["To"]      = to_email
        msg["Reply-To"] = template["from_addr"]

        html = template["html"].replace("{name}", user_name)
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.sendmail(SMTP_EMAIL, to_email, msg.as_string())

        return {
            "sent":      True,
            "to":        to_email,
            "subject":   template["subject"],
            "from_addr": template["from_addr"],
            "red_flags": template["red_flags"],
        }
    except Exception as e:
        return {"sent": False, "reason": str(e), "red_flags": template["red_flags"]}
