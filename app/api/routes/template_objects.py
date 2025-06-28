
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from datetime import datetime, timezone
from app.api.deps import  SessionDep
from fastapi import status
from typing import List
from app.models import ObjectTemplate, ObjectTemplateRule, AttachmentFileStorage, Attachment , AttachmentLink

router = APIRouter(prefix="/template_objects", tags=["Template objects"])

@router.post("/", response_model=ObjectTemplate.Create, status_code=status.HTTP_201_CREATED)
def create_template_object(
    template_object: ObjectTemplate.Create,
    session: SessionDep,
):
    db_obj = ObjectTemplate(
        name=template_object.name,
        description=template_object.description,
        type=template_object.type,
        tags=template_object.tags,
        allowedComposition=template_object.allowedComposition,
        fabricant=template_object.fabricant,
        fournisseur=template_object.fournisseur,
        version=template_object.version,
        isLastVersion=template_object.isLastVersion,
        createdAt=datetime.now(timezone.utc),
        updatedAt=datetime.now(timezone.utc),
        is_deleted=False
    )
    session.add(db_obj)
    session.flush()  
    
    if template_object.rules:
        for rule_data in template_object.rules:
            rule = ObjectTemplateRule(
                object_template_id=db_obj.id,
                name=rule_data.name,
                value=rule_data.value,
                isLink=rule_data.isLink,
                link=rule_data.link,
                isFile=rule_data.isFile
            )
            session.add(rule)
    
    if template_object.attachments:
        for attachment_data in template_object.attachments:
            attachment = Attachment(
                object_template_id=db_obj.id,
                file_name=attachment_data.file_name,
                file_type=attachment_data.file_type,
                file_storage=attachment_data.file_storage,
                size_bytes=attachment_data.size_bytes,
                file_hash=attachment_data.file_hash,
                uploaded_at=datetime.now(timezone.utc),
                reference_count=attachment_data.reference_count,
                meta_data=attachment_data.meta_data,
                is_deleted=False
            )
            session.add(attachment)

    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

@router.get("/", response_model=List[ObjectTemplate.Read])
def read_template_objects(
    session: SessionDep,
):
    statement = select(ObjectTemplate).where(
        ObjectTemplate.is_deleted == False
    )
    results = session.exec(statement).all()
    return results

@router.get("/{template_object_id}", response_model=ObjectTemplate.Read)
def read_template_object(
    template_object_id: UUID,
    session: SessionDep,
):
    template_object = session.get(ObjectTemplate, template_object_id)
    if not template_object or template_object.is_deleted:
        raise HTTPException(status_code=404, detail="TemplateObject not found")
    return template_object

@router.patch("/{template_object_id}", response_model=ObjectTemplate.Read)
def update_template_object(
    template_object_id: UUID,
    template_object_update: ObjectTemplate.Update,
    session: SessionDep,
):
    db_obj = session.get(ObjectTemplate, template_object_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="TemplateObject not found")
    update_data = template_object_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_obj, key, value)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

@router.delete("/{template_object_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_template_object(
    template_object_id: UUID,
    session: SessionDep,
):
    db_obj = session.get(ObjectTemplate, template_object_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="TemplateObject not found")
    db_obj.is_deleted= True 
    session.add(db_obj)
    session.commit()

@router.get("/{template_object_id}/attachments", response_model=List[Attachment.Read])
def get_template_object_attachments(
    template_object_id: UUID,
    session: SessionDep,
):
    db_obj = session.get(ObjectTemplate, template_object_id)
    if not db_obj or db_obj.is_deleted:
        raise HTTPException(status_code=404, detail="TemplateObject not found")
    
    attachments = session.exec(
        select(Attachment).where(
            Attachment.object_template_id == template_object_id,
            Attachment.is_deleted == False
        )
    ).all()
    
    return attachments
@router.post("/{template_object_id}/attachments", response_model=Attachment.Read)
def add_attachment_to_template_object(
    template_object_id: UUID,
    attachment_data: Attachment.Create,
    session: SessionDep,
):
    db_obj = session.get(ObjectTemplate, template_object_id)
    if not db_obj or db_obj.is_deleted:
        raise HTTPException(status_code=404, detail="TemplateObject not found")
    file_storage_id = None
    if attachment_data.file_storage:
        file_storage_obj = AttachmentFileStorage(
            provider=attachment_data.file_storage.provider,
            path=attachment_data.file_storage.path,
            bucket=attachment_data.file_storage.bucket
        )
        session.add(file_storage_obj)
        session.flush()  
        file_storage_id = file_storage_obj.id

    attachment = Attachment(
        object_template_id=template_object_id,
        file_name=attachment_data.file_name,
        file_type=attachment_data.file_type,
        file_storage_id=file_storage_id,
        size_bytes=attachment_data.size_bytes,
        file_hash=attachment_data.file_hash,
        uploaded_at=datetime.now(timezone.utc),
        reference_count=attachment_data.reference_count,
        meta_data=attachment_data.meta_data,
        is_deleted=False
    )

    session.add(attachment)
    session.commit()
    session.refresh(attachment)
@router.patch("/{template_object_id}/attachments/{attachment_id}", response_model=Attachment.Read)
def update_attachment_of_template_object(
    template_object_id: UUID,
    attachment_id: UUID,
    attachment_update: Attachment.Update,
    session: SessionDep,
):
    db_obj = session.get(ObjectTemplate, template_object_id)
    if not db_obj or db_obj.is_deleted:
        raise HTTPException(status_code=404, detail="TemplateObject not found")

    attachment = session.get(Attachment, attachment_id)
    if not attachment or attachment.is_deleted or attachment.object_template_id != template_object_id:
        raise HTTPException(status_code=404, detail="Attachment not found")

    update_data = attachment_update.dict(exclude_unset=True)

    if "file_storage" in update_data and update_data["file_storage"]:
        file_storage_data = update_data.pop("file_storage")
        if attachment.file_storage_id:
            file_storage_obj = session.get(AttachmentFileStorage, attachment.file_storage_id)
            if file_storage_obj:
                for key, value in file_storage_data.items():
                    setattr(file_storage_obj, key, value)
                session.add(file_storage_obj)
        else:
            file_storage_obj = AttachmentFileStorage(**file_storage_data)
            session.add(file_storage_obj)
            session.flush()
            attachment.file_storage_id = file_storage_obj.id

    for key, value in update_data.items():
        setattr(attachment, key, value)

    session.add(attachment)
    session.commit()
    session.refresh(attachment)
    return attachment
