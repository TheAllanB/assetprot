"""
DMCA notice generation service (SRP + OCP + DIP).

SRP: This module only handles DMCA notice text generation.
OCP: New notice formats can be added by creating new DMCAGenerator implementations.
DIP: Callers depend on the DMCAGenerator protocol.
"""

from datetime import datetime
from typing import Any


class StandardDMCAGenerator:
    """
    Standard DMCA takedown notice generator (OCP — implements DMCAGenerator protocol).

    LSP: Can be substituted with any other DMCAGenerator implementation
    (e.g., EuropeanGDPRNoticeGenerator, JapaneseCopyrightNoticeGenerator).
    """

    def generate(self, violation: Any) -> str:
        """Generate a standard DMCA takedown notice for a violation."""
        return f"""DMCA Takedown Notice

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


# Default generator instance
_default_generator = StandardDMCAGenerator()


def generate_dmca_notice(violation: Any, generator: StandardDMCAGenerator | None = None) -> str:
    """
    Generate a DMCA notice using the given generator (DIP).

    Defaults to StandardDMCAGenerator if none provided.
    """
    gen = generator or _default_generator
    return gen.generate(violation)