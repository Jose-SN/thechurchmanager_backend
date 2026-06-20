"""
Seed the Full Service Production Template with 22 checklist items.

Usage:
    py -3 -m app.checklist.seed --team-id <uuid> --organization-id <uuid>
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import uuid

from app.checklist.constants import DEFAULT_SVC_META
from app.checklist.models import ChecklistItem, ChecklistTemplate
from app.db.session import get_session_factory, init_sqlalchemy, close_sqlalchemy

logger = logging.getLogger(__name__)

FULL_SERVICE_ITEMS = [
    ("Mixer powered on", "[audio] Audio System", 0, True),
    ("Wireless mic batteries checked", "[audio] Audio System", 1, True),
    ("Podium microphone tested", "[audio] Audio System", 2, True),
    ("In-ear monitors checked", "[audio] Audio System", 3, True),
    ("Stage monitor levels set", "[audio] Audio System", 4, True),
    ("Playback/laptop audio routed", "[audio] Audio System", 5, True),
    ("Recording feed armed", "[audio] Audio System", 6, False),
    ("Backup audio source ready", "[audio] Audio System", 7, False),
    ("Main camera powered on", "[video] Camera & Stream", 8, True),
    ("Stream software running", "[video] Camera & Stream", 9, True),
    ("Slide/projection software connected", "[video] Camera & Stream", 10, True),
    ("Stream destination verified", "[video] Camera & Stream", 11, True),
    ("Lighting preset loaded", "[video] Camera & Stream", 12, True),
    ("Backup camera ready", "[video] Camera & Stream", 13, False),
    ("Recording storage checked", "[video] Camera & Stream", 14, False),
    ("Stage cleared of hazards", "[stage] Stage Safety", 15, True),
    ("Cable runs taped down", "[stage] Stage Safety", 16, True),
    ("Emergency exits unobstructed", "[stage] Stage Safety", 17, True),
    ("Props and furniture set", "[stage] Stage Safety", 18, True),
    ("Worship team briefed", "[stage] Stage Safety", 19, True),
    ("Communion/elements prepared", "[stage] Stage Safety", 20, False),
    ("Post-service reset plan confirmed", "[stage] Stage Safety", 21, False),
]


async def seed(team_id: uuid.UUID, organization_id: uuid.UUID, created_by: str = "seed-script") -> uuid.UUID:
    await init_sqlalchemy()
    session_factory = get_session_factory()
    try:
        async with session_factory() as session:
            template = ChecklistTemplate(
                organization_id=organization_id,
                team_id=team_id,
                name="Full Service Production Template",
                description="Complete Sunday service checklist covering audio, video, and stage safety.",
                is_active=True,
                created_by=created_by,
            )
            session.add(template)
            await session.flush()
            for title, description, order, is_required in FULL_SERVICE_ITEMS:
                session.add(
                    ChecklistItem(
                        template_id=template.id,
                        title=title,
                        description=description,
                        order=order,
                        is_required=is_required,
                    )
                )
            await session.commit()
            logger.info("Seeded template %s with %s items", template.id, len(FULL_SERVICE_ITEMS))
            logger.info("Default notes metadata: %s", DEFAULT_SVC_META)
            return template.id
    finally:
        await close_sqlalchemy()


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed Full Service Production checklist template")
    parser.add_argument("--team-id", required=True)
    parser.add_argument("--organization-id", required=True)
    parser.add_argument("--created-by", default="seed-script")
    args = parser.parse_args()
    template_id = asyncio.run(
        seed(
            uuid.UUID(args.team_id),
            uuid.UUID(args.organization_id),
            args.created_by,
        )
    )
    print(f"Seeded template id: {template_id}")


if __name__ == "__main__":
    main()
