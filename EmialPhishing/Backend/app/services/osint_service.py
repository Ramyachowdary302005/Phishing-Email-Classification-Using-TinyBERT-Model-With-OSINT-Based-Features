import re
import tldextract
import requests
import validators
from typing import List, Dict, Tuple
from urllib.parse import urlparse
import logging
from app.config.settings import settings

logger = logging.getLogger(__name__)


class OSINTService:
    def __init__(self):
        # Extended suspicious TLDs — many are used in phishing campaigns
        self.suspicious_tlds = [
            '.tk', '.ml', '.ga', '.cf', '.click', '.download', '.top',
            '.loan', '.win', '.xyz', '.gq', '.pw', '.cc', '.info',
            '.biz', '.ru', '.cn', '.work', '.online', '.site', '.buzz',
            '.live', '.icu', '.club', '.vip', '.monster', '.beauty'
        ]

        # URL shortener patterns
        self.suspicious_url_patterns = [
            r'bit\.ly', r'tinyurl\.com', r'short\.link', r'goo\.gl',
            r't\.co', r'ow\.ly', r'rb\.gy', r'cutt\.ly', r'is\.gd'
        ]

        # Spam indicators
        self.spam_keywords = [
            'free', 'winner', 'congratulations', 'claim', 'urgent', 'act now',
            'limited time', 'exclusive offer', 'click here', 'verify account',
            'suspended', 'security alert', 'payment required', 'invoice',
            'lottery', 'prize', 'reward', 'bonus', 'cash', 'money back',
            'dear customer', 'dear user', 'dear member'
        ]

        # Phishing keywords in email body
        self.phishing_keywords = [
            'verify', 'confirm', 'update', 'suspended', 'locked', 'security',
            'unusual activity', 'fraud', 'protect', 'immediate action',
            'account', 'password', 'login', 'signin', 'credentials',
            'expire', 'unauthorized', 'compromised', 'restore access'
        ]

        # Keywords suspicious in a DOMAIN — only action/security words, NOT brand names.
        # Brand names (amazon, google etc.) are checked separately via homograph detection.
        # If a domain IS 'amazon.in', seeing 'amazon' is EXPECTED and legitimate.
        self.suspicious_domain_keywords = [
            'secure', 'security', 'alert', 'verify', 'update',
            'account', 'login', 'signin', 'banking', 'payment', 'confirm',
            'wallet', 'webscr', 'ebayisapi'
        ]

        # Common brand names that are spoofed via homographs
        self.brand_names = [
            'amazon', 'paypal', 'microsoft', 'google', 'apple', 'netflix',
            'facebook', 'instagram', 'twitter', 'linkedin', 'ebay', 'bank'
        ]

        # Explicitly trusted domains (whitelist) — these will override ML if ML is uncertain
        self.trusted_domains = [
            'google.com', 'gmail.com', 'microsoft.com', 'outlook.com', 'live.com',
            'apple.com', 'icloud.com', 'amazon.com', 'amazon.in', 'paypal.com',
            'github.com', 'linkedin.com', 'twitter.com', 'facebook.com',
            'bankofamerica.com', 'chase.com', 'wellsfargo.com', 'hsbc.com'
        ]

        # Homograph character mappings (attacker uses these to spoof brands)
        self.homograph_map = {
            '0': 'o', '1': 'l', '3': 'e', '4': 'a', '5': 's',
            '6': 'g', '7': 't', '8': 'b', '9': 'g', '@': 'a'
        }

    # ─── Main Entry ──────────────────────────────────────────────────────────

    def analyze_email(self, text: str, headers: Dict = None) -> Dict:
        """Perform OSINT analysis on email content and headers."""
        try:
            risk_score = 0.0
            reasons = []

            # Extract URLs from body
            urls = self._extract_urls(text)
            url_analysis = self._analyze_urls(urls)

            # Extract emails from body
            emails = self._extract_emails(text)
            email_analysis = self._analyze_emails(emails)

            # Extract phones from body
            phones = self._extract_phones(text)
            phone_analysis = self._analyze_phones(phones)

            # Text content analysis
            text_analysis = self._analyze_text_content(text)

            # Header analysis (most important — checks sender domain)
            header_analysis = self._analyze_headers(headers) if headers else {'risk_score': 0.0, 'reasons': [], 'is_trusted': False}

            # Weighted risk score
            risk_score += url_analysis['risk_score'] * 0.30
            risk_score += email_analysis['risk_score'] * 0.15
            risk_score += phone_analysis['risk_score'] * 0.05
            risk_score += text_analysis['risk_score'] * 0.25
            risk_score += header_analysis.get('risk_score', 0.0) * 0.25

            # Collect reasons
            reasons.extend(header_analysis.get('reasons', []))
            if header_analysis.get('is_trusted'):
                reasons.append(f"✓ Verified Trusted Domain: {header_analysis.get('domain')}")

            reasons.extend(url_analysis['reasons'])
            reasons.extend(email_analysis['reasons'])
            reasons.extend(text_analysis['reasons'])
            reasons.extend(phone_analysis['reasons'])

            return {
                'risk_score': round(min(risk_score, 1.0), 4),
                'url_count': len(urls),
                'email_count': len(emails),
                'phone_count': len(phones),
                'suspicious_urls': url_analysis['suspicious_count'],
                'is_trusted': header_analysis.get('is_trusted', False),
                'suspicious_emails': email_analysis['suspicious_count'],
                'suspicious_phones': phone_analysis['suspicious_count'],
                'spam_indicators': text_analysis['spam_count'],
                'phishing_indicators': text_analysis['phishing_count'],
                'reasons': reasons[:10],
                'analysis': {
                    'urls': url_analysis,
                    'emails': email_analysis,
                    'phones': phone_analysis,
                    'text': text_analysis,
                    'headers': header_analysis
                }
            }

        except Exception as e:
            logger.error(f"Error in OSINT analysis: {e}")
            return {
                'risk_score': 0.0,
                'is_trusted': False,
                'reasons': [f'Analysis error: {str(e)}'],
                'error': str(e)
            }

    # ─── Extractors ──────────────────────────────────────────────────────────

    def _extract_urls(self, text: str) -> List[str]:
        url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
        return list(set(url_pattern.findall(text)))

    def _extract_emails(self, text: str) -> List[str]:
        pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        return list(set(pattern.findall(text)))

    def _extract_phones(self, text: str) -> List[str]:
        # Fixed regex: escaping dash correctly to avoid invalid range error
        pattern = re.compile(r'(\+?\d{1,3}[\s.\-]?)?\(?\d{3}\)?[\s.\-]?\d{3}[\s.\-]?\d{4}')
        return list(set(pattern.findall(text)))

    # ─── Homograph Detection ─────────────────────────────────────────────────

    def _normalize_homograph(self, domain: str) -> str:
        """Replace common homograph characters with their letter equivalents."""
        result = domain.lower()
        for char, replacement in self.homograph_map.items():
            result = result.replace(char, replacement)
        return result

    def _detect_homograph_spoofing(self, domain: str) -> Tuple[bool, str]:
        """
        Detect if a domain is spoofing a known brand using character substitution.
        e.g. amaz0n-security-alert.xyz -> normalized to 'amazon' brand match
        """
        # Get just the base domain (without TLD and subdomains)
        try:
            extracted = tldextract.extract(domain)
            base = extracted.domain.lower()
        except Exception:
            base = domain.lower()

        normalized = self._normalize_homograph(base)

        for brand in self.brand_names:
            # Exact brand name appears in normalized domain after substitution
            if brand in normalized and base != brand:
                return True, brand

        return False, ''

    # ─── Header Analysis (Sender Domain — THE MOST IMPORTANT CHECK) ──────────

    def _analyze_headers(self, headers: Dict) -> Dict:
        risk_score = 0.0
        reasons = []
        is_trusted = False
        domain = ""

        if not headers:
            return {'risk_score': 0.0, 'reasons': [], 'is_trusted': False, 'domain': ''}

        # ── Check SPF / DKIM / DMARC ──────────────────────────────────────
        if headers.get('spf', 'pass').lower() == 'fail':
            risk_score += 0.3
            reasons.append('SPF authentication failed')

        if headers.get('dkim', 'pass').lower() == 'fail':
            risk_score += 0.25
            reasons.append('DKIM authentication failed')

        if headers.get('dmarc', 'pass').lower() == 'fail':
            risk_score += 0.2
            reasons.append('DMARC authentication failed')

        # ── Analyze the From / Sender email address ────────────────────────
        sender_email = headers.get('from', '') or headers.get('sender', '')
        if sender_email and '@' in sender_email:
            local_part = sender_email.split('@')[0].lower()
            full_domain = sender_email.split('@')[1].lower()
            domain = full_domain

            # A. Check for Trusted Domain (whitelist)
            # Industry level: Trusted domains MUST pass SPF/DKIM to be actually trusted
            has_auth_failure = (headers.get('spf', 'pass').lower() == 'fail' or 
                                headers.get('dkim', 'pass').lower() == 'fail')
            
            if not has_auth_failure:
                for td in self.trusted_domains:
                    if full_domain == td or full_domain.endswith('.' + td):
                        is_trusted = True
                        break

            # 1. Check for suspicious local part (the part before @)
            # Only flag if TLD is ALSO suspicious — support@amazon.in is legitimate,
            # but support@amaz0n-alert.xyz is not.
            try:
                tld_check = tldextract.extract(full_domain)
                tld_suspicious = f'.{tld_check.suffix}' in self.suspicious_tlds
            except Exception:
                tld_suspicious = False

            if tld_suspicious:
                suspicious_local = ['support', 'admin', 'noreply', 'no-reply',
                                     'security', 'alert', 'verify', 'service', 'helpdesk']
                for s in suspicious_local:
                    if s in local_part:
                        risk_score += 0.15
                        reasons.append(f'Suspicious sender name: "{local_part}"')
                        break

            # 2. Check domain TLD
            try:
                extracted = tldextract.extract(full_domain)
                tld = f'.{extracted.suffix}'
                if tld in self.suspicious_tlds:
                    risk_score += 0.35
                    reasons.append(f'Suspicious sender TLD: {tld}')
            except Exception:
                pass

            # 3. Check for phishing keywords INSIDE domain name
            domain_base = full_domain.replace('-', ' ').replace('.', ' ')
            for kw in self.suspicious_domain_keywords:
                if kw in domain_base:
                    # Don't flag if it's a trusted domain
                    if not is_trusted:
                        risk_score += 0.2
                        reasons.append(f'Suspicious keyword in sender domain: "{kw}"')
                    break

            # 4. Detect homograph spoofing (amaz0n, paypa1, micros0ft etc.)
            spoofed, brand = self._detect_homograph_spoofing(full_domain)
            if spoofed:
                risk_score += 0.5
                reasons.append(f'Homograph spoofing detected: "{full_domain}" impersonates "{brand}"')

            # 5. Numeric-heavy domain (many phishing domains use random numbers)
            digits_in_domain = sum(c.isdigit() for c in full_domain)
            if digits_in_domain >= 4:
                risk_score += 0.2
                reasons.append(f'Numeric-heavy sender domain: {full_domain}')

            # 6. Hyphenated domain with >2 hyphens (red flag)
            if full_domain.count('-') >= 2:
                risk_score += 0.2
                reasons.append(f'Hyphenated sender domain (suspicious): {full_domain}')

        return {
            'risk_score': min(risk_score, 1.0),
            'reasons': reasons,
            'is_trusted': is_trusted,
            'domain': domain
        }

    # ─── URL Analysis ────────────────────────────────────────────────────────

    def _analyze_urls(self, urls: List[str]) -> Dict:
        risk_score = 0.0
        reasons = []
        suspicious_count = 0

        for url in urls:
            # Long URL
            if len(url) > 75:
                risk_score += 0.1
                reasons.append(f'Unusually long URL: {url[:50]}...')
                suspicious_count += 1

            # Check TLD
            try:
                extracted = tldextract.extract(url)
                tld = f'.{extracted.suffix}'
                if tld in self.suspicious_tlds:
                    risk_score += 0.25
                    reasons.append(f'Suspicious URL TLD: {tld}')
                    suspicious_count += 1

                # Homograph in URL domain
                spoofed, brand = self._detect_homograph_spoofing(extracted.domain)
                if spoofed:
                    risk_score += 0.4
                    reasons.append(f'Homograph in URL domain: impersonates "{brand}"')
                    suspicious_count += 1

                # Suspicious keywords in URL domain
                domain_base = extracted.domain.lower().replace('-', ' ')
                for kw in self.suspicious_domain_keywords:
                    if kw in domain_base and kw != extracted.domain:
                        risk_score += 0.15
                        reasons.append(f'Suspicious keyword in URL domain: "{kw}"')
                        break
            except Exception:
                pass

            # URL shortener
            for pattern in self.suspicious_url_patterns:
                if re.search(pattern, url, re.IGNORECASE):
                    risk_score += 0.15
                    reasons.append(f'URL shortener detected')
                    suspicious_count += 1
                    break

            # IP address in URL
            if re.search(r'http[s]?://\d+\.\d+\.\d+\.\d+', url):
                risk_score += 0.3
                reasons.append(f'Raw IP address in URL: {url}')
                suspicious_count += 1

        return {
            'risk_score': min(risk_score, 1.0),
            'suspicious_count': suspicious_count,
            'reasons': reasons
        }

    # ─── Email Address Body Analysis ─────────────────────────────────────────

    def _analyze_emails(self, emails: List[str]) -> Dict:
        risk_score = 0.0
        reasons = []
        suspicious_count = 0

        for email in emails:
            if '@' not in email:
                continue
            full_domain = email.split('@')[1].lower()
            try:
                ext = tldextract.extract(full_domain)
                if f'.{ext.suffix}' in self.suspicious_tlds:
                    risk_score += 0.2
                    reasons.append(f'Suspicious TLD in embedded email: .{ext.suffix}')
                    suspicious_count += 1
            except Exception:
                pass

        return {
            'risk_score': min(risk_score, 1.0),
            'suspicious_count': suspicious_count,
            'reasons': reasons
        }

    # ─── Phone Analysis ──────────────────────────────────────────────────────

    def _analyze_phones(self, phones: List[str]) -> Dict:
        risk_score = 0.0
        reasons = []
        suspicious_count = 0

        if phones:
            risk_score += 0.05 * len(phones)
            reasons.append(f'Phone numbers in email body: {len(phones)}')
            suspicious_count = len(phones)

        return {
            'risk_score': min(risk_score, 1.0),
            'suspicious_count': suspicious_count,
            'reasons': reasons
        }

    # ─── Text Content Analysis ───────────────────────────────────────────────

    def _analyze_text_content(self, text: str) -> Dict:
        risk_score = 0.0
        reasons = []
        spam_count = 0
        phishing_count = 0

        text_lower = text.lower()

        # Spam keywords
        for keyword in self.spam_keywords:
            if keyword in text_lower:
                spam_count += text_lower.count(keyword)
                risk_score += 0.05

        # Phishing keywords
        for keyword in self.phishing_keywords:
            if keyword in text_lower:
                phishing_count += text_lower.count(keyword)
                risk_score += 0.07

        # Urgency patterns
        urgency_patterns = [r'urgent', r'immediate', r'act now', r'limited time', r'expire', r'suspended']
        for pattern in urgency_patterns:
            if re.search(pattern, text_lower):
                risk_score += 0.1
                reasons.append(f'Urgency trigger: "{pattern}"')

        # Excessive capitalization
        if len(text) > 0 and sum(1 for c in text if c.isupper()) > len(text) * 0.3:
            risk_score += 0.15
            reasons.append('Excessive capitalization detected')

        # Excessive punctuation
        if text.count('!') > 3 or text.count('?') > 3:
            risk_score += 0.1
            reasons.append('Excessive punctuation detected')

        return {
            'risk_score': min(risk_score, 1.0),
            'spam_count': spam_count,
            'phishing_count': phishing_count,
            'reasons': reasons
        }
