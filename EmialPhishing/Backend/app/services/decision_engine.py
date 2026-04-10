from typing import Dict, Tuple
import logging
from app.config.settings import settings
from app.services.ml_service import MLService
from app.services.osint_service import OSINTService

logger = logging.getLogger(__name__)


class DecisionEngine:
    def __init__(self):
        self.ml_service = MLService()
        self.osint_service = OSINTService()
        self.osint_weight = settings.osint_weight
        self.ml_weight = settings.ml_weight
        self.high_risk_threshold = settings.high_risk_threshold
        self.low_risk_threshold = settings.low_risk_threshold
    
    def analyze_email(self, text: str, headers: Dict = None) -> Dict:
        """Perform hybrid analysis combining ML and OSINT."""
        try:
            # Get ML prediction
            ml_result = self.ml_service.predict(text)
            
            # Get OSINT analysis
            osint_result = self.osint_service.analyze_email(text, headers)
            
            # Make final decision
            final_decision, confidence, stage, reason = self._make_final_decision(
                ml_result, osint_result
            )
            
            return {
                'final_decision': final_decision,
                'confidence': confidence,
                'stage': stage,
                'reason': reason,
                'ml_analysis': ml_result,
                'osint_analysis': osint_result
            }
            
        except Exception as e:
            logger.error(f"Error in decision engine: {e}")
            return {
                'final_decision': 'Error',
                'confidence': 0.0,
                'stage': 'Error',
                'reason': f'Analysis failed: {str(e)}',
                'ml_analysis': {},
                'osint_analysis': {}
            }
    
    def _make_final_decision(
        self, 
        ml_result: Dict, 
        osint_result: Dict
    ) -> Tuple[str, float, str, str]:
        """Make final decision based on ML and OSINT results."""
        
        # Handle ML errors
        if ml_result.get('prediction') == 'Error':
            return 'Error', 0.0, 'Error', 'ML prediction failed'
        
        # Extract ML probability for phishing
        ml_phishing_prob = ml_result.get('probabilities', {}).get('phishing', 0.0)
        
        # Extract OSINT risk score and trust status
        osint_errored = 'error' in osint_result
        osint_risk_score = osint_result.get('risk_score', 0.0)
        is_trusted_domain = osint_result.get('is_trusted', False)

        # ── Rule 1: Verified Trusted Domains (The "Boss" Veto) ───────────────
        # If the domain is whitelisted (Google, Amazon etc.) AND passed auth, 
        # we trust it's legitimate even if ML is suspicious of the body text.
        if is_trusted_domain:
            return 'Legitimate', 0.99, 'OSINT', f"Verified Trusted Domain: {osint_result.get('analysis', {}).get('headers', {}).get('domain')}"

        # ── Rule 2: If OSINT errored, fall back to ML only ───────────────────
        if osint_errored:
            if ml_phishing_prob >= 0.5:
                return 'Phishing', ml_phishing_prob, 'ML', self._generate_ml_reason(ml_result, 'phishing')
            else:
                return 'Legitimate', 1.0 - ml_phishing_prob, 'ML', self._generate_ml_reason(ml_result, 'legitimate')

        # ── Rule 3: High-Confidence AI Protection (Hybrid Consensus) ─────────
        # If AI is EXTREMELY sure (>90%) and domain is NOT trusted, don't let 
        # a low OSINT score override it. The domain might just be new.
        if ml_phishing_prob >= 0.9:
            return 'Phishing', ml_phishing_prob, 'ML', f"Critical: High-confidence AI detection ({ml_phishing_prob:.1%})"

        # ── Rule 4: OSINT confident HIGH risk → Phishing ─────────────────────
        if osint_risk_score >= self.high_risk_threshold:
            return 'Phishing', min(osint_risk_score + 0.1, 1.0), 'OSINT', self._generate_osint_reason(osint_result, 'high')

        # ── Rule 5: OSINT confident LOW risk → Legitimate ────────────────────
        # Trust OSINT for known low risk that isn't overridden by high-conf ML
        if osint_risk_score <= self.low_risk_threshold:
            return 'Legitimate', max(1.0 - osint_risk_score - 0.1, 0.5), 'OSINT', self._generate_osint_reason(osint_result, 'low')

        # ── Rule 6: Middle range → Hybrid weighted decision ───────────────────
        combined_score = (ml_phishing_prob * self.ml_weight) + (osint_risk_score * self.osint_weight)

        if combined_score >= 0.5:
            decision = 'Phishing'
            confidence = combined_score
            stage = 'Hybrid'
            reason = self._generate_hybrid_reason(ml_result, osint_result, 'phishing')
        elif combined_score <= 0.3:
            decision = 'Legitimate'
            confidence = 1.0 - combined_score
            stage = 'Hybrid'
            reason = self._generate_hybrid_reason(ml_result, osint_result, 'legitimate')
        else:
            # ML tie-breaker
            if ml_phishing_prob >= 0.5:
                decision = 'Phishing'
                confidence = ml_phishing_prob
                stage = 'ML'
                reason = self._generate_ml_reason(ml_result, 'phishing')
            else:
                decision = 'Legitimate'
                confidence = 1.0 - ml_phishing_prob
                stage = 'ML'
                reason = self._generate_ml_reason(ml_result, 'legitimate')

        return decision, confidence, stage, reason
    
    def _generate_osint_reason(self, osint_result: Dict, level: str) -> str:
        """Generate reason for OSINT-based decision."""
        reasons = osint_result.get('reasons', [])
        
        if level == 'high':
            if osint_result.get('suspicious_urls', 0) > 0:
                return f"High risk: {osint_result['suspicious_urls']} suspicious URLs detected"
            elif osint_result.get('spam_indicators', 0) > 3:
                return f"High risk: {osint_result['spam_indicators']} spam indicators found"
            elif osint_result.get('phishing_indicators', 0) > 2:
                return f"High risk: {osint_result['phishing_indicators']} phishing keywords detected"
            else:
                return "High risk: Multiple suspicious patterns detected"
        else:
            return f"Low risk: Risk score {osint_result.get('risk_score', 0):.2f} below threshold"
    
    def _generate_ml_reason(self, ml_result: Dict, decision: str) -> str:
        """Generate reason for ML-based decision."""
        confidence = ml_result.get('confidence', 0.0)
        probabilities = ml_result.get('probabilities', {})
        
        if decision == 'phishing':
            return f"ML model predicts phishing with {confidence:.2%} confidence"
        else:
            return f"ML model predicts legitimate with {confidence:.2%} confidence"
    
    def _generate_hybrid_reason(
        self, 
        ml_result: Dict, 
        osint_result: Dict, 
        decision: str
    ) -> str:
        """Generate reason for hybrid decision."""
        ml_confidence = ml_result.get('confidence', 0.0)
        osint_risk = osint_result.get('risk_score', 0.0)
        
        key_factors = []
        
        # Identify key factors
        if osint_result.get('suspicious_urls', 0) > 0:
            key_factors.append(f"{osint_result['suspicious_urls']} suspicious URLs")
        
        if osint_result.get('spam_indicators', 0) > 2:
            key_factors.append(f"{osint_result['spam_indicators']} spam indicators")
        
        if osint_result.get('phishing_indicators', 0) > 1:
            key_factors.append(f"{osint_result['phishing_indicators']} phishing keywords")
        
        if ml_confidence > 0.8:
            key_factors.append(f"high ML confidence ({ml_confidence:.1%})")
        
        if not key_factors:
            if decision == 'phishing':
                key_factors.append("moderate ML and OSINT risk indicators")
            else:
                key_factors.append("low ML and OSINT risk indicators")
        
        factors_str = ", ".join(key_factors[:3])  # Limit to top 3 factors
        
        if decision == 'phishing':
            return f"Hybrid analysis indicates phishing due to: {factors_str}"
        else:
            return f"Hybrid analysis indicates legitimate email: {factors_str}"
    
    def get_decision_thresholds(self) -> Dict:
        """Get current decision thresholds."""
        return {
            'osint_weight': self.osint_weight,
            'ml_weight': self.ml_weight,
            'high_risk_threshold': self.high_risk_threshold,
            'low_risk_threshold': self.low_risk_threshold
        }
    
    def update_thresholds(
        self, 
        osint_weight: float = None,
        ml_weight: float = None,
        high_risk_threshold: float = None,
        low_risk_threshold: float = None
    ):
        """Update decision thresholds."""
        if osint_weight is not None:
            self.osint_weight = osint_weight
        if ml_weight is not None:
            self.ml_weight = ml_weight
        if high_risk_threshold is not None:
            self.high_risk_threshold = high_risk_threshold
        if low_risk_threshold is not None:
            self.low_risk_threshold = low_risk_threshold
        
        logger.info("Decision thresholds updated")
