from datetime import datetime


def generate_dmca_notice(violation) -> str:
    notice = f"""DMCA Takedown Notice

Date: {datetime.now().strftime('%B %d, %Y')}

To: Content Removal Team

Subject: DMCA Notice of Copyright Infringement

Dear Sir/Madam,

I am writing to notify you of a copyright infringement concerning content that is hosted on your platform.

VIOLATION DETAILS:
- URL: {violation.discovered_url}
- Platform: {violation.platform}
- Detection Date: {violation.detected_at.strftime('%B %d, %Y')}
- Confidence Score: {violation.confidence:.1%}

We believe this content is being made available without our authorization. We are the rightful owners or authorized representatives of the copyright holder.

STATEMENT OF GOOD FAITH:
I have a good faith belief that the use of the copyrighted material described above is not authorized by the copyright owner, its agent, or the law.

ACCURACY STATEMENT:
I swear, under penalty of perjury, that the information in this notification is accurate and that I am authorized to act on behalf of the copyright owner.

REQUESTED ACTION:
We request that you immediately remove or disable access to the infringing material and take appropriate action against the account holder.

Please contact us to confirm the action taken.

Sincerely,
GUARDIAN Content Protection Team
"""
    return notice