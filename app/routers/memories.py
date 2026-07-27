from typing import Annotated, Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from fastapi import APIRouter, Depends, HTTPException, Response, status

from .. import oauth2, schemas
from ..database import get_session
from ..exceptions import MemAPIException
from ..models import Memory

router = APIRouter(
    prefix="/memories",
    tags=["memories"],
    dependencies=[Depends(oauth2.get_current_user)],
)


@router.post("/", response_model=schemas.MySchemaOut)
def create_memory(
    memory: schemas.MySchema,
    session: Annotated[Session, Depends(get_session)],
    id: int = Depends(oauth2.get_current_user),
):
    try:

        memory = Memory(title=memory.title, content=memory.content, owner_id=id)
        session.add(memory)
        session.commit()
        _ = memory.owner
        print(memory)
        return memory
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Memory already exists, Duplicates are not allowed.",
        )


@router.get("/", response_model=list[schemas.MySchemaOut])
def get_memorys(session: Annotated[Session, Depends(get_session)]):
    memorys = (
        session.execute(select(Memory).options(joinedload(Memory.owner)))
        .scalars()
        .all()
    )

    # print(">>>>>>>>>>>> Size of checkedin:", engine.pool.checkedin())
    # print(">>>>>>>>>>>> Size of checkedout:", engine.pool.checkedout())

    return memorys


@router.get("/current", response_model=list[schemas.MySchemaOut])
def get_memorys_current_user(
    session: Annotated[Session, Depends(get_session)],
    current_user: int = Depends(oauth2.get_current_user),
    Limit: int = 10,
    page: int = 1,
    search: Optional[str] = "",
):
    print(Limit)
    skip = (page - 1) * Limit
    memorys = (
        session.execute(
            select(Memory)
            .filter(Memory.title.contains(search))
            .filter(Memory.owner_id == current_user)
            .options(joinedload(Memory.owner))
            .limit(Limit)
            .offset(skip)
        )
        .scalars()
        .all()
    )
    return memorys


@router.get("/{id}", response_model=schemas.MySchemaOut)
def get_memory(
    session: Annotated[Session, Depends(get_session)],
    id: int,
    current_user: int = Depends(oauth2.get_current_user),
):
    memory = session.get(Memory, str(id))
    if memory.owner_id != int(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied, cannot view memorys of other users.",
        )
    if not memory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"memory with id: {id} not found",
        )
    return memory


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_memory(
    session: Annotated[Session, Depends(get_session)],
    id: int,
    current_user: int = Depends(oauth2.get_current_user),
):
    memory = session.get(Memory, str(id))
    if not memory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"memory with id: {id} not found",
        )
    if memory.owner_id != int(current_user):
        print(memory.owner_id, current_user)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied, Cannot Delete memorys of other users",
        )

    session.delete(memory)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.MySchemaOut)
def update_memory(
    updated_memory: schemas.MySchema,
    session: Annotated[Session, Depends(get_session)],
    id: int,
):
    memory = session.get(Memory, str(id))
    if not memory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"memory with id: {id} not found",
        )
    memory.title = updated_memory.title
    memory.content = updated_memory.content
    session.commit()
    print(memory)
    return memory
