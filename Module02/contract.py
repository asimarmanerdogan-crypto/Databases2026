"""Corrected maintenance contract; run with uv run python Module02/contract.py."""
from datetime import date
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import (CheckConstraint, Column, Date, ForeignKey, Integer,
                        MetaData, Numeric, String, Table, create_engine, event)
from sqlalchemy.schema import CreateTable

PositiveId = Annotated[int, Field(strict=True, ge=1)]
RequiredText = Annotated[str, Field(min_length=1)]


class ContractModel(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class Machine(ContractModel):
    machine_id: PositiveId
    machine_name: RequiredText
    serial_no: str = Field(pattern=r"^SN-.+$")
    site: RequiredText
    installed: date


class Technician(ContractModel):
    technician_id: PositiveId
    name: RequiredText


class Part(ContractModel):
    part_no: RequiredText
    description: RequiredText
    unit_price: Decimal = Field(ge=0, max_digits=9, decimal_places=2)


class MaintenanceJob(ContractModel):
    job_id: PositiveId
    machine_id: PositiveId
    technician_id: PositiveId
    done_on: date
    part_nos: list[RequiredText] = Field(default_factory=list)

    @field_validator("part_nos")
    @classmethod
    def no_duplicate_parts(cls, values):
        if len(values) != len(set(values)):
            raise ValueError("a job can list a part only once")
        return values


metadata = MetaData()
machine_t = Table("machine", metadata,
    Column("machine_id", Integer, primary_key=True),
    Column("machine_name", String, nullable=False, unique=True),
    Column("serial_no", String, nullable=False, unique=True),
    Column("site", String, nullable=False),
    Column("installed", Date, nullable=False),
    CheckConstraint("machine_id >= 1"),
    CheckConstraint("length(trim(machine_name)) > 0 AND length(trim(site)) > 0"),
    CheckConstraint("serial_no GLOB 'SN-?*'"),
)
technician_t = Table("technician", metadata,
    Column("technician_id", Integer, primary_key=True),
    Column("name", String, nullable=False),
    CheckConstraint("technician_id >= 1 AND length(trim(name)) > 0"),
)
part_t = Table("part", metadata,
    Column("part_no", String, primary_key=True, nullable=False),
    Column("description", String, nullable=False),
    Column("unit_price", Numeric(9, 2), nullable=False),
    CheckConstraint("length(trim(part_no)) > 0 AND length(trim(description)) > 0"),
    CheckConstraint("typeof(unit_price) IN ('integer','real') AND unit_price >= 0 AND unit_price <= 9999999.99 AND round(unit_price, 2) = unit_price"),
)
maint_job_t = Table("maint_job", metadata,
    Column("job_id", Integer, primary_key=True),
    Column("machine_id", Integer, ForeignKey("machine.machine_id"), nullable=False),
    Column("technician_id", Integer, ForeignKey("technician.technician_id"), nullable=False),
    Column("done_on", Date, nullable=False),
    CheckConstraint("job_id >= 1"),
)
job_part_t = Table("job_part", metadata,
    Column("job_id", Integer, ForeignKey("maint_job.job_id"), primary_key=True, nullable=False),
    Column("part_no", String, ForeignKey("part.part_no"), primary_key=True, nullable=False),
)


def make_engine():
    engine = create_engine("sqlite://")

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, _):
        connection.execute("PRAGMA foreign_keys=ON")

    metadata.create_all(engine)
    return engine


if __name__ == "__main__":
    engine = make_engine()
    for table in metadata.sorted_tables:
        print(str(CreateTable(table).compile(engine)).strip() + ";\n")
