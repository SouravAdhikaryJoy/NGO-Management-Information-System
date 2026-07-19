import io

from fastapi import APIRouter, Depends, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session as DbSession

from app.api.errors import api_error
from app.database import get_db
from app.excel.import_templates import import_workbook, write_blank_template
from app.excel.reimport import reimport_master_timetable
from app.schemas.api import ImportResponse

router = APIRouter(tags=["import"])


@router.post("/import", response_model=ImportResponse)
async def import_excel(file: UploadFile, db: DbSession = Depends(get_db)):
    """Upload the master Excel workbook: validate every row, then upsert.
    Any validation error aborts the whole import and is reported per row."""
    content = await file.read()
    result = import_workbook(db, io.BytesIO(content))
    return result.as_dict()


@router.post("/import/edits")
async def import_manual_edits(file: UploadFile, db: DbSession = Depends(get_db)):
    """Re-import a manually edited MasterTimetable sheet (design doc section 7):
    each edited session is re-validated against all hard constraints; invalid
    edits are rejected row-by-row, valid ones applied, soft report refreshed."""
    content = await file.read()
    try:
        return reimport_master_timetable(db, io.BytesIO(content))
    except Exception as exc:
        raise api_error(400, "reimport_failed", f"could not process workbook: {exc}")


@router.get("/import/template")
def download_template():
    """Download a blank import workbook with every sheet and header row."""
    buffer = io.BytesIO()
    write_blank_template(buffer)
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=import_template.xlsx"},
    )
