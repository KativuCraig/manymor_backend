"""
Two-Factor Authentication (2FA) utilities using TOTP (Time-based One-Time Password)
Works with Google Authenticator, Microsoft Authenticator, Authy, etc.
"""
import pyotp
import qrcode
from io import BytesIO
import base64
from django.conf import settings


def generate_2fa_secret():
    """Generate a new TOTP secret key for a user"""
    return pyotp.random_base32()


def get_totp_uri(user, secret):
    """
    Generate TOTP URI for QR code generation
    
    Args:
        user: User instance
        secret: TOTP secret key
        
    Returns:
        URI string for TOTP provisioning
    """
    company_name = getattr(settings, 'COMPANY_NAME', 'ManyMor')
    return pyotp.totp.TOTP(secret).provisioning_uri(
        name=user.email,
        issuer_name=company_name
    )


def generate_qr_code(data):
    """
    Generate QR code image from data
    
    Args:
        data: String data to encode in QR code
        
    Returns:
        Base64 encoded PNG image
    """
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_base64}"


def verify_totp_code(secret, code):
    """
    Verify a TOTP code against a secret
    
    Args:
        secret: TOTP secret key
        code: 6-digit code from authenticator app
        
    Returns:
        Boolean indicating if code is valid
    """
    totp = pyotp.TOTP(secret)
    # Allow a window of ±1 time period (30 seconds) for clock drift
    return totp.verify(code, valid_window=1)


def get_backup_codes(count=8):
    """
    Generate backup codes for 2FA recovery
    
    Args:
        count: Number of backup codes to generate
        
    Returns:
        List of backup codes
    """
    import secrets
    import string
    
    codes = []
    for _ in range(count):
        # Generate 8-character alphanumeric code
        code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        # Format as XXXX-XXXX
        formatted_code = f"{code[:4]}-{code[4:]}"
        codes.append(formatted_code)
    
    return codes
