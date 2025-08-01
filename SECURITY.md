# Security Guide 🔐

This document outlines the security measures implemented in the Doctor Appointment Bot project and provides guidelines for secure deployment and maintenance.

## 🔒 Security Architecture

### 1. Data Encryption
- **Local Development**: Sensitive data encrypted using Fernet (AES 128) with PBKDF2 key derivation
- **Production (Railway)**: Environment variables secured by Railway's encryption
- **Master Password**: PBKDF2 with 100,000 iterations and SHA-256

### 2. Environment Variables
```bash
# Required Environment Variables (Railway)
TELEGRAM_BOT_TOKEN=<encrypted_by_railway>
GOOGLE_CREDENTIALS=<encrypted_by_railway>
GOOGLE_SHEETS_ID=<encrypted_by_railway>
GOOGLE_CREDENTIALS_FILE=credentials.json
```

### 3. File Security
- All credential files excluded from version control
- Encrypted configuration files for local development
- Secure configuration loader with multiple fallbacks

## 🛡️ Security Features

### Encryption Utilities
- `encrypt_secrets.py`: Master encryption/decryption utility
- `secure_config.py`: Secure configuration loader
- `setup_railway_security.py`: Railway environment variable manager

### Access Control
- Master password protection for local encrypted files
- Railway platform security for production environment
- No hardcoded credentials in source code

### Data Protection
- Telegram Bot Token secured
- Google Service Account credentials encrypted
- Google Sheets ID protected
- API keys never exposed in logs

## 🚀 Deployment Security

### Railway Platform
1. **Environment Variables**: All sensitive data stored as encrypted environment variables
2. **Build Security**: No credentials in build logs or images
3. **Runtime Security**: Credentials loaded securely at runtime
4. **Network Security**: HTTPS/TLS for all communications

### GitHub Repository
1. **No Secrets**: All sensitive data excluded via .gitignore
2. **Clean History**: No credentials in commit history
3. **Secret Scanning**: GitHub's secret scanning enabled
4. **Access Control**: Repository access properly managed

## 📋 Security Checklist

### Initial Setup
- [ ] Install cryptography package: `pip install cryptography`
- [ ] Create encrypted configuration: `python encrypt_secrets.py --create-config`
- [ ] Set up Railway variables: `python setup_railway_security.py`
- [ ] Verify .gitignore excludes all credential files
- [ ] Test bot deployment with encrypted configuration

### Regular Maintenance
- [ ] Rotate Telegram Bot Token monthly
- [ ] Rotate Google Service Account credentials quarterly
- [ ] Monitor Railway deployment logs weekly
- [ ] Review access logs monthly
- [ ] Update security dependencies regularly

### Incident Response
- [ ] Have credential revocation procedure ready
- [ ] Maintain emergency contact list
- [ ] Document recovery procedures
- [ ] Test backup and restore procedures

## 🔧 Usage Instructions

### For Local Development

1. **Create Encrypted Configuration**:
```bash
python encrypt_secrets.py --create-config
```

2. **Run Bot with Encrypted Config**:
```python
from secure_config import SecureConfigLoader
config = SecureConfigLoader()
bot_token = config.get('TELEGRAM_BOT_TOKEN')
```

### For Railway Deployment

1. **Configure Environment Variables**:
```bash
python setup_railway_security.py
```

2. **Deploy Securely**:
```bash
railway up --detach
```

3. **Verify Deployment**:
```bash
railway logs
railway variables
```

## ⚠️ Security Warnings

### Never Do This
- ❌ Commit `.env` files to version control
- ❌ Hardcode API keys in source code  
- ❌ Share credentials via insecure channels
- ❌ Use weak master passwords
- ❌ Store credentials in plain text

### Always Do This
- ✅ Use environment variables for sensitive data
- ✅ Encrypt local configuration files
- ✅ Regularly rotate credentials
- ✅ Monitor access logs
- ✅ Keep security dependencies updated

## 🚨 Emergency Procedures

### If Credentials Are Compromised

1. **Immediate Actions**:
   - Revoke compromised Telegram Bot Token via BotFather
   - Disable Google Service Account in Google Cloud Console
   - Change Railway environment variables
   - Review access logs for unauthorized usage

2. **Recovery Steps**:
   - Generate new credentials
   - Update Railway environment variables
   - Test bot functionality
   - Monitor for suspicious activity

3. **Prevention**:
   - Analyze how compromise occurred
   - Implement additional security measures
   - Update security procedures
   - Train team on security best practices

## 📞 Support & Reporting

### Security Issues
- Report security vulnerabilities privately
- Use encrypted communication channels
- Provide detailed information about the issue
- Allow reasonable time for remediation

### Contact Information
- **Security Team**: [Secure contact method]
- **Emergency Contact**: [Emergency contact]
- **Railway Support**: [Railway support channel]

## 📚 Additional Resources

### Documentation
- [Railway Security Best Practices](https://docs.railway.app/reference/security)
- [Telegram Bot Security](https://core.telegram.org/bots/faq#security)
- [Google Cloud Security](https://cloud.google.com/security)

### Tools
- [Railway CLI](https://docs.railway.app/develop/cli)
- [Python Cryptography](https://cryptography.io/)
- [OWASP Security Guidelines](https://owasp.org/)

---

**Last Updated**: 2025-08-01  
**Version**: 1.0  
**Review Schedule**: Monthly

> 🔐 Security is everyone's responsibility. When in doubt, choose the more secure option.
