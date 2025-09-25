# !/usr/bin/env python
# Copyright (C) 2025 HRForce
#
# All rights reserved.
# @link hrforce.ai
#
# __author__ = "man.tra@cvtot.vn"
# __date__ = "2025-09-24 11:26:49"
#

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from core.settings.base import settings

# Base for ORM models
Base = declarative_base()

DATABASE_URL = settings.DB_URL

engine = create_async_engine(DATABASE_URL, echo=False)

async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

meta = sa.MetaData()