"""
Experiment
├── detection_objective
├── excitation_objective
├── detection_angle
├── z_motion
└── Channel(s)
    ├── detector
    ├── detector_roi
    ├── em_filters
    ├── ex_waves
    ├── ex_power
    └── Image(s)
        ├── timestamp
        ├── dx
        ├── dy
        ├── dz
        ├── stage_position
        ├── position_name
        └── tile_index
"""

from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Union, Tuple, List
from uuid import UUID, uuid4


class UnitsLength(Enum):
    pm = -12
    nm = -9
    µm = -6
    mm = -3
    cm = -2
    dm = -1
    m = 0
    dam = 1
    hm = 2
    km = 3
    Mm = 6
    Gm = 9


class UnitsTime(Enum):
    ps = -12
    ns = -9
    us = -6
    ms = -3
    cs = -2
    ds = -1
    s = 0
    das = 1
    hs = 2
    ks = 3
    Ms = 6
    Gs = 9


class Immersion(Enum):
    oil = 1
    water = 2
    waterdipping = 3
    air = 4
    multi = 5
    glycerol = 6
    other = 7


class FilterType(Enum):
    bp = "bandpass"
    sp = "shortpass"
    lp = "longpass"


class ZMotion(Enum):
    sample_xy = 1
    sample_z = 2
    detection_obj = 3


@dataclass
class Filter:
    center: float
    bandwidth: float
    units: UnitsLength = UnitsLength.nm
    part: Optional[str] = None
    type: FilterType = FilterType.bp
    manufacturer: Optional[str] = None


@dataclass
class Laser:
    wavelength: float
    part: Optional[str] = None
    serial_number: Optional[str] = None
    manufacturer: Optional[str] = None


@dataclass
class Image:
    timestamp: Optional[datetime] = None
    dx: float = 1
    dy: float = 1
    dz: float = 1
    stage_position: Optional[tuple] = None  # (x, y, z)
    position_name: Optional[str] = None
    tile_index: Optional[tuple] = None  # (X, Y, Z)  # if part of a tile scan


@dataclass
class Channel:
    images: List[Image]
    detector: Optional[str] = None  # serial number
    # left, top, right, bottom
    detector_roi: Optional[Tuple[int, int, int, int]] = None
    # barrier filter(s) for this channel
    em_filters: List[Filter] = field(default_factory=list)
    ex_waves: List[Union[Filter, Laser]] = field(default_factory=list)
    ex_power: Optional[float] = None


@dataclass
class Objective:
    na: float
    nominal_magnification: Optional[float] = None
    calibrated_magnification: Optional[float] = None
    immersion: Immersion = Immersion.air
    lot_number: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    working_distance: Optional[float] = field(
        default=None, metadata={"units": UnitsLength.µm}
    )
    id: UUID = field(default_factory=uuid4, init=False, repr=False)


@dataclass
class Environment:
    temperature: Optional[float] = None
    medium: Optional[str] = None


@dataclass
class Experiment:
    # some of this stuff might belong in "Channel"
    channels: List[Channel] = field(default_factory=list)
    operator: Optional[str] = None
    sample: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    sample_holder: Optional[str] = None
    detection_objective: Optional[Objective] = None
    excitation_objective: Optional[Objective] = None
    # relative to the axis of Z motion
    detection_angle: float = 0.0
    z_motion: ZMotion = ZMotion.detection_obj
    environment: Optional[Environment] = None


@dataclass
class SIMChannel(Channel):
    angles: List[float] = field(default_factory=list)
    nphases: int = 5
    linespacing: Optional[float] = None
    is_linear: bool = True


@dataclass
class SIMExperiment(Experiment):
    channels: List[SIMChannel] = field(default_factory=list)


# Specific to LLS/MOSAIC
# timestamp_fpga = datetime
# slm_pattern
# dm_pattern
# sample_chamber
# microscope_layout
# microscope_mode
# scan_type
# imaging_mode
