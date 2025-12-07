# 🔐 TASK-008: Security Hardening
## WAF + Vulnerability Scanning + Compliance + SOC2 Preparation

**Дата:** 7 декабря 2025, 18:20 MSK  
**статус:** 🔵 READY FOR ASSIGNMENT  
**Команда:** SECURITY Team  
**Ответственные:** Alexander Z. (Security Lead), Mikhail V. (AppSec), Roman S. (Infrastructure Security)  
**Начало:** 23 декабря 2025, 09:00 MSK  
**Дедлайн:** 27 декабря 2025, 17:00 MSK  
**Приоритет:** 🔴 **CRITICAL**  
**Дни:** 5 дней (Security Audit & Hardening)

---

## 🎯 ЦЕЛИ

1. **Web Application Firewall (WAF)** - Protect API endpoints
2. **Vulnerability Scanning** - Container + Code scanning
3. **Compliance Audit** - OWASP + NIST
4. **SOC2 Preparation** - Security policies
5. **Penetration Testing** - Red team simulation

---

## 📋 ПОДЗАДАЧИ

### Подзадача 1: WAF Setup

**Cloudflare WAF Configuration:**

```bash
# 1. Enable WAF rules
- OWASP ModSecurity core rule set
- Rate limiting (100 req/min per IP)
- Geographic blocking (if needed)
- Bot management

# 2. Custom rules
- Block SQL injection patterns
- Block XSS attempts
- Block path traversal
- Block XXE attacks

# 3. Logging
- Log all blocked requests
- Monitor false positives
- Setup alerts for patterns
```

**Success Criteria:**
- [ ] WAF rules active
- [ ] Rate limiting enforced
- [ ] False positive rate <1%
- [ ] Blocked attacks logged
- [ ] Team alerted on patterns

### Подзадача 2: Container Security Scanning

**Trivy scanning:**

```bash
# 1. Scan Docker images
trivy image super-brain-api:latest
trivy image super-brain-bot:latest
trivy image super-brain-batch:latest

# 2. Scan K8s cluster
trivy kubernetes --namespace production

# 3. Generate reports
trivy image --format json super-brain-api:latest > scan-report.json
```

**Criteria:**
- [ ] 0 critical vulnerabilities
- [ ] <5 high vulnerabilities
- [ ] All high-risk fixed
- [ ] Scanning automated in CI/CD
- [ ] Weekly scheduled scans

### Подзадача 3: Code Security Scanning (SAST)

**Semgrep + SonarQube:**

```bash
# 1. Semgrep scan
semgrep --config p/security-audit --json api/
semgrep --config p/owasp-top-ten bot/

# 2. SonarQube scan
sonar-scanner \
  -Dsonar.projectKey=super-brain \
  -Dsonar.sources=. \
  -Dsonar.host.url=https://sonar.example.com
```

**Findings Priority:**
- [ ] Critical: SQL injection patterns
- [ ] Critical: Hardcoded secrets
- [ ] High: Insecure crypto
- [ ] High: XSS vulnerabilities
- [ ] Medium: Error handling

### Подзадача 4: Dependency Scanning

**Snyk + OWASP Dependency-Check:**

```bash
# 1. Snyk scan
snyk test --json > snyk-report.json
snyk container test super-brain-api:latest

# 2. Check requirements
pip-audit requirements.txt

# 3. Check npm
npm audit
```

**Success Criteria:**
- [ ] All critical deps patched
- [ ] No outdated versions
- [ ] Automated scanning in CI
- [ ] Weekly vulnerability checks
- [ ] SLA for patches: <7 days for critical

### Подзадача 5: Compliance Audit

**OWASP Top 10 Check:**

```
1. Broken Access Control
   - [ ] RBAC implemented
   - [ ] JWT validation
   - [ ] Rate limiting

2. Cryptographic Failures
   - [ ] TLS 1.2+ enforced
   - [ ] Secrets encrypted
   - [ ] No hardcoded creds

3. Injection
   - [ ] SQL injection: Parameterized queries
   - [ ] Command injection: Input sanitization
   - [ ] Template injection: Escaping

4. Insecure Design
   - [ ] Threat modeling done
   - [ ] Security by default
   - [ ] Limits enforced

5. Security Misconfiguration
   - [ ] Default passwords changed
   - [ ] Unnecessary features disabled
   - [ ] Updated security patches

6. Vulnerable & Outdated Components
   - [ ] Dependencies scanned
   - [ ] No EOL libraries
   - [ ] Versions patched

7. Authentication Failures
   - [ ] MFA ready
   - [ ] Password policy enforced
   - [ ] Session timeout set

8. Software & Data Integrity Failures
   - [ ] Signed releases
   - [ ] Integrity checks
   - [ ] Secure CI/CD

9. Logging & Monitoring Failures
   - [ ] All access logged
   - [ ] Alerts configured
   - [ ] Log retention policy

10. SSRF
    - [ ] URL validation
    - [ ] Protocol whitelist
    - [ ] No file:// access
```

### Подзадача 6: SOC2 Preparation

**Security Policies:**

```
1. Access Control Policy
   - [ ] Least privilege principle
   - [ ] MFA requirement
   - [ ] Access reviews (quarterly)
   - [ ] Offboarding procedures

2. Data Protection Policy
   - [ ] Encryption at rest
   - [ ] Encryption in transit
   - [ ] Data classification
   - [ ] PII handling

3. Incident Response Plan
   - [ ] Detection procedures
   - [ ] Escalation path
   - [ ] Containment steps
   - [ ] Post-incident review

4. Change Management
   - [ ] Change request process
   - [ ] Approval workflow
   - [ ] Testing requirement
   - [ ] Rollback procedure

5. Backup & Disaster Recovery
   - [ ] Daily backups
   - [ ] Off-site storage
   - [ ] RTO < 4 hours
   - [ ] RPO < 1 hour

6. Risk Assessment
   - [ ] Annual risk assessment
   - [ ] Threat analysis
   - [ ] Mitigation plans
   - [ ] Residual risk tracking

7. Employee Training
   - [ ] Annual security training
   - [ ] Phishing simulations
   - [ ] Code security training
   - [ ] Attestation/sign-off

8. Vendor Management
   - [ ] Vendor assessments
   - [ ] NDA/SLAs signed
   - [ ] Regular audits
   - [ ] Incident notification
```

### Подзадача 7: Penetration Testing

**Red Team Simulation:**

```bash
# Scope: 97v.ru production

# 1. External testing
- Port scanning
- DNS enumeration
- SSL/TLS analysis
- Web app scanning (Burp)

# 2. Internal testing (if approved)
- Network segmentation test
- Privilege escalation attempts
- Data exfiltration simulation
- Lateral movement test

# 3. Social engineering (optional)
- Phishing simulation
- Pretext calls
- Physical security test

# Success: No critical vulns should be exploitable
```

**Report Requirements:**
- [ ] Executive summary
- [ ] Findings categorized (Critical/High/Medium/Low)
- [ ] Proof of concepts
- [ ] Remediation recommendations
- [ ] Verification testing

---

## 🧪 CHECKLIST

### День 1-2 (23-24 Dec): WAF & Scanning
- [ ] WAF configured and tested
- [ ] Container scanning results
- [ ] Code scanning results
- [ ] Dependency audit complete
- [ ] Vulnerabilities triaged

### День 3 (25 Dec): Compliance Audit
- [ ] OWASP checklist 100% complete
- [ ] Findings documented
- [ ] Remediation plans created
- [ ] Timeline for fixes

### День 4 (26 Dec): SOC2 Prep
- [ ] All policies documented
- [ ] Approval workflows set
- [ ] Training materials ready
- [ ] Baseline established

### День 5 (27 Dec): Penetration Testing
- [ ] Pentest completed
- [ ] Report generated
- [ ] Findings triaged
- [ ] Remediation timeline set

---

## 📄 REPORTING

**File:** `TASKS/TASK-008-SECURITY-HARDENING-COMPLETED.md`

**Include:**
- WAF configuration & testing results
- Vulnerability scan summaries (Trivy, Semgrep, Snyk)
- OWASP compliance checklist
- SOC2 policy documentation
- Penetration test findings
- Remediation plan with timeline
- Executive summary
- Recommendations for continuous security

---

## 🔗 RESOURCES

- OWASP: https://owasp.org
- SOC2: https://www.aicpa.org/soc2
- CIS Benchmarks: https://www.cisecurity.org
- NIST: https://csrc.nist.gov

---

**Status:** 🔵 READY FOR ASSIGNMENT  
**Team:** SECURITY (Alexander Z., Mikhail V., Roman S.)  
**Duration:** 5 days  
**Critical:** Yes  
**Note:** Final task before v1.0 release