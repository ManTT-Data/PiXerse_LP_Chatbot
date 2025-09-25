# !/usr/bin/env python
# Copyright (C) 2025 HRForce
#
# All rights reserved.
# @link hrforce.ai
#
# __author__ = "henry@hrforce.ai"
# __date__ = "2025-06-11 11:20:06"
#

from sqlalchemy.orm import DeclarativeBase

from core.db.meta import meta


class Base(DeclarativeBase):
    """Base for all models."""

    metadata = meta