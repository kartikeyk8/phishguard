"""
URL Analysis Service — live URL breakdown using tldextract
"""
import tldextract
import validators
import re

SUSPICIOUS_TLDS = {".xyz",".tk",".ml",".ga",".cf",".gq",".top",".club",".online",".site",".icu"}
SUSPICIOUS_KEYWORDS = ["secure","verify","login","signin","account","update","confirm","banking",
                       "alert","support","helpdesk","reset","suspended","blocked","urgent","paypal",
                       "amazon","apple","microsoft","google","netflix","bank","hsbc","barclays"]
LEGIT_DOMAINS = {"google.com","gmail.com","microsoft.com","apple.com","paypal.com","netflix.com",
                 "amazon.com","amazon.co.uk","facebook.com","zoom.us","hsbc.co.uk","barclays.co.uk",
                 "gov.uk","hmrc.gov.uk","dhl.com","royalmail.com","instagram.com"}


def analyse_url(url: str) -> dict:
    if not url.startswith(("http://","https://")):
        url = "https://" + url

    if not validators.url(url):
        return {"error": "Invalid URL", "is_phishing": True, "confidence": "High"}

    ext        = tldextract.extract(url)
    subdomain  = ext.subdomain
    domain     = ext.domain
    suffix     = ext.suffix
    full_domain = f"{domain}.{suffix}"

    flags      = []
    risk_score = 0

    # HTTPS check
    uses_https = url.startswith("https://")
    if not uses_https:
        flags.append("No HTTPS — connection is not encrypted")
        risk_score += 1

    # Brand in subdomain check
    if full_domain in LEGIT_DOMAINS:
        if subdomain:
            flags.append(f"'{full_domain}' appears as a subdomain — the REAL domain is '{full_domain}' but with extra prefix controlled by attacker")
            risk_score += 3
    else:
        for legit in LEGIT_DOMAINS:
            legit_name = legit.split(".")[0]
            if legit_name in subdomain.lower() or legit_name in domain.lower():
                flags.append(f"'{legit_name}' appears in URL but real domain is '{full_domain}' — brand impersonation")
                risk_score += 4
                break

    # Suspicious TLD
    if f".{suffix}" in SUSPICIOUS_TLDS:
        flags.append(f"TLD '.{suffix}' is commonly used in phishing")
        risk_score += 2

    # Suspicious keywords
    found = [kw for kw in SUSPICIOUS_KEYWORDS if kw in domain.lower()]
    if found:
        flags.append(f"Domain contains suspicious keywords: {', '.join(found)}")
        risk_score += len(found)

    # Homograph detection
    for digit, letter in {"0":"o","1":"l","5":"s","3":"e"}.items():
        if digit in domain:
            flags.append(f"Domain contains '{digit}' possibly substituting for '{letter}' — homograph attack")
            risk_score += 3
            break

    # Deep subdomain
    if len(subdomain.split(".")) > 2:
        flags.append(f"Deep subdomain structure used to hide real domain")
        risk_score += 2

    if risk_score >= 5:
        verdict, confidence, is_phishing = "Phishing", "High", True
    elif risk_score >= 2:
        verdict, confidence, is_phishing = "Suspicious", "Medium", True
    else:
        verdict, confidence, is_phishing = "Likely Legitimate", "High", False

    explanation = f"The real domain is '{full_domain}'."
    if subdomain:
        explanation += f" Everything before it ('{subdomain}') is a subdomain that anyone can set to any brand name."
    if flags:
        explanation += f" Red flags: {'; '.join(flags[:2])}."

    return {
        "url": url,
        "breakdown": {
            "subdomain":   subdomain or "none",
            "domain":      domain,
            "suffix":      suffix,
            "full_domain": full_domain,
            "uses_https":  uses_https,
        },
        "flags":       flags,
        "risk_score":  risk_score,
        "verdict":     verdict,
        "confidence":  confidence,
        "is_phishing": is_phishing,
        "explanation": explanation,
    }
