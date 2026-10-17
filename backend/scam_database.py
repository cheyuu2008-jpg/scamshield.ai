"""
ScamShield AI - Preloaded Realistic Test Cases & Threat Intelligence Feed
Used for instant 1-click demonstration, testing, and scam awareness quizzes.
"""

SAMPLE_SCAMS = [
    {
        "id": "bank_smishing",
        "title": "Chase Bank Security Alert",
        "category": "SMS / Smishing",
        "type": "text",
        "badge": "Financial Phishing",
        "content": "CHASE ALERT: We detected an unauthorized debit charge of $1,429.50 on your debit card. If this was not you, please verify your identity immediately to prevent account suspension: https://chase-security-verify-auth.xyz/login?ref=9102"
    },
    {
        "id": "package_delivery",
        "title": "USPS Undelivered Package",
        "category": "SMS / Smishing",
        "type": "text",
        "badge": "Postal Delivery Scam",
        "content": "USPS Notification: Your package could not be delivered on 10/17 due to an incomplete delivery address. Please update your address and pay the $1.99 redelivery fee within 24 hours: https://usps-redelivery-tracking.top/parcel/confirm"
    },
    {
        "id": "tech_support",
        "title": "Geek Squad / Windows Defender Invoice",
        "category": "Email / BEC",
        "type": "email",
        "badge": "Tech Support Extortion",
        "content": "GEEK SQUAD INVOICE #89211\n\nDear Customer,\nYour annual auto-renewal subscription for Windows Defender Total Shield has been processed for $499.00 from your checking account. If you did not authorize this charge, call our Fraud Prevention Helpline immediately at 1-800-412-9843 to cancel and receive a full refund. Please do not ignore, as charges will be finalized within 2 hours."
    },
    {
        "id": "hi_mom",
        "title": "'Hi Mom' Family Emergency",
        "category": "SMS / Impersonation",
        "type": "text",
        "badge": "Social Engineering",
        "content": "Hi mom! I dropped my phone in the water and it's completely broken. This is my temporary new number. Can you please do me a huge favor? I need to pay an urgent medical bill right now but my banking app is locked on this device. Can you wire $850 to this Zelle or Apple Gift Card? Please don't tell dad yet, I'll pay you back tonight!"
    },
    {
        "id": "crypto_bait",
        "title": "Crypto Doubling Giveaway",
        "category": "Social Media / Crypto",
        "type": "text",
        "badge": "Crypto Doubler Fraud",
        "content": "🚀 CELEBRATION GIVEAWAY! Elon Musk & Tesla are distributing 5,000 BTC to celebrate the new update! Send 0.1 BTC to 0.5 BTC to the official wallet address below and you will immediately receive 2x back guaranteed! Over 80% already claimed. Visit https://tesla-btc-giveaway-official.click before timer runs out!"
    },
    {
        "id": "irs_call",
        "title": "IRS Law Enforcement Arrest Threat",
        "category": "Call Transcript",
        "type": "call",
        "badge": "Government Impersonation",
        "content": "This is Officer Mark Davis calling from the Federal Legal Department of the Internal Revenue Service. An active arrest warrant has been issued in your name due to fraudulent tax evasion. Stay on the line right now. Do not hang up the phone or local county sheriff will arrive at your door within 45 minutes. You must immediately purchase four $500 Target gift cards or crypto to settle this legal fine."
    },
    {
        "id": "legit_bank",
        "title": "Legitimate Bank 2FA Alert (Clean Control)",
        "category": "Safe Message Example",
        "type": "text",
        "badge": "Clean Message",
        "content": "Wells Fargo: Your one-time verification code is 492019. This code expires in 10 minutes. Wells Fargo will NEVER call or text you asking for this code. Do not share it with anyone."
    }
]

AWARENESS_QUIZ = [
    {
        "id": 1,
        "scenario": "You get a text: 'Netflix: Your payment failed. Update your card at netflix-billing-update.top to prevent immediate cancellation.'",
        "options": [
            "Click the link immediately so my family's show isn't interrupted",
            "Reply with 'STOP' to unsubscribe",
            "Ignore the text and log in directly to Netflix.com or open the official Netflix app to check billing"
        ],
        "correctIndex": 2,
        "explanation": "Scammers use fake urgent payment notices with suspicious domains (.top). Always check your account status directly in the official app or official site."
    },
    {
        "id": 2,
        "scenario": "A tech support caller says your computer has 50 dangerous viruses and asks you to install AnyDesk so they can clean it for free.",
        "options": [
            "Hang up immediately — legitimate companies never call out of the blue asking for remote access",
            "Allow remote access since they offer to fix it for free",
            "Pay their cancellation fee using Apple Gift Cards"
        ],
        "correctIndex": 0,
        "explanation": "Never allow unsolicited callers remote access to your computer. They use remote software to steal passwords, lock files, or manipulate your bank screens."
    },
    {
        "id": 3,
        "scenario": "A message from an unknown number says: 'Hi Mum, I lost my phone and wallet. Can you wire $400 for emergency train tickets?'",
        "options": [
            "Wire the money immediately via Zelle",
            "Call your child's original phone number or call another family member/friend to verify first",
            "Send them your credit card photo"
        ],
        "correctIndex": 1,
        "explanation": "The 'Hi Mum / Hi Dad' scam exploits panic. Always call your child on their established number or contact someone who is with them before sending funds."
    }
]

TRENDING_THREATS = [
    {
        "title": "AI Voice Cloning 'Kidnapping' Scams",
        "severity": "HIGH",
        "surge": "+140% this quarter",
        "description": "Criminals scrape 3-second audio clips from social media to clone family members' voices pleading for emergency bail money."
    },
    {
        "title": "Smishing Postal / Toll Road Fee Links",
        "severity": "CRITICAL",
        "surge": "+220% this month",
        "description": "Texts claiming unpaid $2.50 highway toll fines or missed USPS parcels with links ending in .top and .xyz."
    },
    {
        "title": "Crypto 'Pig Butchering' (Sha Zhu Pan)",
        "severity": "CRITICAL",
        "surge": "+95% this year",
        "description": "Scammers build romantic or friendly relationships over weeks before steering victims into rigged crypto trading platforms."
    },
    {
        "title": "QR Code Phishing (Quishing)",
        "severity": "MEDIUM",
        "surge": "+65% this quarter",
        "description": "Fake QR code stickers placed on public parking meters directing drivers to credential-stealing copycat payment portals."
    }
]
