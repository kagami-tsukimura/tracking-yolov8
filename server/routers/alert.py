# flake8: noqa: E402
import os
import sys
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request
from sqlalchemy.orm import Session

parent_dir = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(parent_dir)

from cruds import alert as alert_cruds
from dependencies import Dependencies

dependencies = Dependencies()
DBDependency = dependencies.get_db_dependency()

router = APIRouter(prefix="/alert", tags=["alert"])
