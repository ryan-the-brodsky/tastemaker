from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any, Dict
from datetime import datetime
import uuid

from db_config import Base


# SQLAlchemy Models

class UserModel(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    subscription_tier = Column(String, default="free", nullable=False, server_default="free")
    subscription_updated_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    sessions = relationship("ExtractionSessionModel", back_populates="user", cascade="all, delete-orphan")


class ExtractionSessionModel(Base):
    __tablename__ = "extraction_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    phase = Column(String, default="color_exploration")  # Start with color selection
    brand_colors = Column(Text, nullable=True)
    project_description = Column(Text, nullable=True)  # User's project context for AI generation
    comparison_count = Column(Integer, default=0)
    confidence_score = Column(Float, default=0.0)
    # NEW: Established preferences as JSON for progressive incorporation
    # Format: {"backgroundColor": "#667eea", "borderRadius": "8px", ...}
    established_preferences = Column(Text, nullable=True)
    # Chosen color palette (JSON): {primary, secondary, accent, accentSoft, background}
    chosen_colors = Column(Text, nullable=True)
    # Chosen typography (JSON): {heading, body, style}
    chosen_typography = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Component Studio progress tracking (JSON)
    studio_progress = Column(Text, nullable=True)

    user = relationship("UserModel", back_populates="sessions")
    comparisons = relationship("ComparisonResultModel", back_populates="session", cascade="all, delete-orphan")
    rules = relationship("StyleRuleModel", back_populates="session", cascade="all, delete-orphan")
    skills = relationship("GeneratedSkillModel", back_populates="session", cascade="all, delete-orphan")
    studio_choices = relationship("ComponentStudioChoiceModel", back_populates="session", cascade="all, delete-orphan")


class ComparisonResultModel(Base):
    __tablename__ = "comparison_results"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("extraction_sessions.id", ondelete="CASCADE"), nullable=False)
    comparison_id = Column(Integer, nullable=False)
    component_type = Column(String, nullable=False)
    phase = Column(String, nullable=False)
    option_a_styles = Column(Text, nullable=False)
    option_b_styles = Column(Text, nullable=False)
    choice = Column(String, nullable=False)  # Legacy: single choice for backwards compat
    decision_time_ms = Column(Integer)
    # NEW: Multi-question responses as JSON array
    # Format: [{"category": "color", "property": "backgroundColor", "choice": "a"}, ...]
    question_responses = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("ExtractionSessionModel", back_populates="comparisons")


class StyleRuleModel(Base):
    __tablename__ = "style_rules"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("extraction_sessions.id", ondelete="CASCADE"), nullable=False)
    rule_id = Column(String, nullable=False)
    component_type = Column(String, nullable=True)
    property = Column(String, nullable=False)
    operator = Column(String, nullable=False)
    value = Column(Text, nullable=False)
    severity = Column(String, default="warning")
    confidence = Column(Float)
    source = Column(String, nullable=False)
    message = Column(String)
    is_modified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # NEW: Interactive UX rule fields
    rule_category = Column(String, default="STATIC")  # STATIC|TEMPORAL|BEHAVIORAL|SPATIAL|PATTERN
    timing_constraint_ms = Column(Integer, nullable=True)  # For temporal rules (Doherty threshold)
    count_property = Column(String, nullable=True)  # For counting rules (Hick's/Miller's)
    zone_definition = Column(JSON, nullable=True)  # For spatial rules (thumb zones)
    pattern_indicators = Column(JSON, nullable=True)  # For dark pattern detection

    session = relationship("ExtractionSessionModel", back_populates="rules")


class GeneratedSkillModel(Base):
    __tablename__ = "generated_skills"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("extraction_sessions.id", ondelete="CASCADE"), nullable=False)
    skill_name = Column(String, nullable=False)
    file_path = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("ExtractionSessionModel", back_populates="skills")


class ComponentStudioChoiceModel(Base):
    """Stores per-component, per-dimension choices from the Component Studio."""
    __tablename__ = "component_studio_choices"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("extraction_sessions.id", ondelete="CASCADE"), nullable=False)
    component_type = Column(String, nullable=False)      # "button"
    dimension = Column(String, nullable=False)            # "border_radius"
    selected_option_id = Column(String, nullable=False)   # "rounded"
    selected_value = Column(String, nullable=False)       # "8px"
    fine_tuned_value = Column(String, nullable=True)      # "12px" (if slider-adjusted)
    css_property = Column(String, nullable=False)         # "borderRadius"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    session = relationship("ExtractionSessionModel", back_populates="studio_choices")


# NEW: Interactive UX audit models for video/replay analysis

class InteractionRecordingModel(Base):
    """Stores metadata about uploaded videos or Playwright replays for UX auditing."""
    __tablename__ = "interaction_recordings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("extraction_sessions.id", ondelete="CASCADE"), nullable=False)
    source_type = Column(String, nullable=False)  # "video" | "playwright"
    source_path = Column(String, nullable=True)  # Path to uploaded video file
    duration_ms = Column(Integer, nullable=True)  # Total duration in milliseconds
    frame_count = Column(Integer, default=0)  # Number of extracted frames
    status = Column(String, default="pending")  # pending|processing|completed|failed
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    session = relationship("ExtractionSessionModel")
    frames = relationship("InteractionFrameModel", back_populates="recording", cascade="all, delete-orphan")
    temporal_metrics = relationship("TemporalMetricModel", back_populates="recording", cascade="all, delete-orphan")


class InteractionFrameModel(Base):
    """Stores individual frames extracted from recordings with Claude-extracted values."""
    __tablename__ = "interaction_frames"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    recording_id = Column(String, ForeignKey("interaction_recordings.id", ondelete="CASCADE"), nullable=False)
    frame_number = Column(Integer, nullable=False)  # Sequential frame number
    timestamp_ms = Column(Integer, nullable=False)  # Timestamp in the recording
    frame_path = Column(String, nullable=False)  # Path to extracted frame image
    extracted_values = Column(JSON, nullable=True)  # Claude-extracted values from frame
    extraction_status = Column(String, default="pending")  # pending|completed|failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    recording = relationship("InteractionRecordingModel", back_populates="frames")


class TemporalMetricModel(Base):
    """Stores calculated temporal metrics between frames for Doherty threshold etc."""
    __tablename__ = "temporal_metrics"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    recording_id = Column(String, ForeignKey("interaction_recordings.id", ondelete="CASCADE"), nullable=False)
    metric_type = Column(String, nullable=False)  # response_time, animation_duration, state_transition
    start_frame_id = Column(String, ForeignKey("interaction_frames.id"), nullable=False)
    end_frame_id = Column(String, ForeignKey("interaction_frames.id"), nullable=False)
    duration_ms = Column(Integer, nullable=False)  # Measured duration
    details = Column(JSON, nullable=True)  # Additional context (what changed, etc.)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    recording = relationship("InteractionRecordingModel", back_populates="temporal_metrics")
    start_frame = relationship("InteractionFrameModel", foreign_keys=[start_frame_id])
    end_frame = relationship("InteractionFrameModel", foreign_keys=[end_frame_id])


# Pydantic Schemas

# Auth Schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    subscription_tier: str = "free"

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    access_token: str
    user: UserResponse


# Session Schemas
class SessionCreate(BaseModel):
    name: str
    brand_colors: Optional[List[str]] = None
    project_description: Optional[str] = None  # User's project context for AI


class SessionResponse(BaseModel):
    id: str
    name: str
    phase: str
    brand_colors: Optional[str] = None
    project_description: Optional[str] = None
    comparison_count: int
    confidence_score: float
    # NEW: Established preferences for progressive incorporation display
    established_preferences: Optional[dict] = None
    # Chosen color palette from color_exploration phase
    chosen_colors: Optional[dict] = None
    # Chosen typography from typography_exploration phase
    chosen_typography: Optional[dict] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SessionDetailResponse(SessionResponse):
    comparisons: List["ComparisonResultResponse"] = []
    rules: List["StyleRuleResponse"] = []


# Comparison Schemas
class ComparisonOption(BaseModel):
    id: str
    styles: dict


# NEW: Multi-question schemas
class ComparisonQuestion(BaseModel):
    """A single question about a style property difference."""
    category: str  # "typography", "color", "shape", "spacing"
    property: str  # "backgroundColor", "fontWeight", etc.
    question_text: str  # "Which background color appeals to you?"
    option_a_value: str  # The value in option A
    option_b_value: str  # The value in option B


class ComparisonResponse(BaseModel):
    comparison_id: int
    component_type: str
    phase: str
    option_a: ComparisonOption
    option_b: ComparisonOption
    context: str
    # NEW: Multi-question support
    questions: Optional[List[ComparisonQuestion]] = None
    generation_method: Optional[str] = None  # "claude_api" or "deterministic"


class QuestionAnswer(BaseModel):
    """User's answer to a single question."""
    category: str
    property: str
    choice: str  # "a", "b", "none"


class ComparisonChoice(BaseModel):
    choice: str  # "a", "b", "none" - legacy single choice for backwards compat
    decision_time_ms: int
    # NEW: Multi-question answers
    answers: Optional[List[QuestionAnswer]] = None


class ComparisonResultResponse(BaseModel):
    id: str
    comparison_id: int
    component_type: str
    phase: str
    choice: str
    decision_time_ms: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SessionProgress(BaseModel):
    comparison_count: int
    phase: str
    confidence_score: float
    next_phase: Optional[str] = None
    # NEW: Return updated established preferences for UI display
    established_preferences: Optional[dict] = None


# Rule Schemas
class RuleCreate(BaseModel):
    statement: str
    component: Optional[str] = None


class RuleUpdate(BaseModel):
    value: Optional[Any] = None
    severity: Optional[str] = None
    message: Optional[str] = None


class StyleRuleResponse(BaseModel):
    id: str
    rule_id: str
    component_type: Optional[str] = None
    property: str
    operator: str
    value: str
    severity: str
    confidence: Optional[float] = None
    source: str
    message: Optional[str] = None
    is_modified: bool
    created_at: datetime
    # NEW: Interactive UX rule fields
    rule_category: Optional[str] = "STATIC"  # STATIC|TEMPORAL|BEHAVIORAL|SPATIAL|PATTERN
    timing_constraint_ms: Optional[int] = None
    count_property: Optional[str] = None
    zone_definition: Optional[Dict] = None
    pattern_indicators: Optional[List[str]] = None

    class Config:
        from_attributes = True


# Interactive Audit Schemas
class InteractionRecordingResponse(BaseModel):
    id: str
    session_id: str
    source_type: str
    duration_ms: Optional[int] = None
    frame_count: int
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class InteractionFrameResponse(BaseModel):
    id: str
    recording_id: str
    frame_number: int
    timestamp_ms: int
    extracted_values: Optional[Dict] = None
    extraction_status: str

    class Config:
        from_attributes = True


class TemporalMetricResponse(BaseModel):
    id: str
    recording_id: str
    metric_type: str
    start_frame_id: str
    end_frame_id: str
    duration_ms: int
    details: Optional[Dict] = None

    class Config:
        from_attributes = True


class VideoAuditRequest(BaseModel):
    session_id: str


class ReplayAuditRequest(BaseModel):
    session_id: str
    playwright_script: str  # JSON script or URL to replay


class InteractiveAuditResult(BaseModel):
    recording_id: str
    total_frames: int
    temporal_violations: List[Dict]
    spatial_violations: List[Dict]
    behavioral_violations: List[Dict]
    pattern_violations: List[Dict]
    summary: Dict


# Skill Schemas
class SkillGenerateResponse(BaseModel):
    skill_id: str
    download_url: str
    preview: dict


# Component Studio Schemas
class DimensionOption(BaseModel):
    id: str
    label: str
    value: str

class FineTuneConfig(BaseModel):
    min: float
    max: float
    step: float
    unit: str

class DimensionDefinition(BaseModel):
    key: str
    label: str
    css_property: str
    options: List[DimensionOption]
    fine_tune: Optional[FineTuneConfig] = None
    order: int

class ComponentDimensionsResponse(BaseModel):
    component_type: str
    component_label: str
    dimensions: List[DimensionDefinition]

class DimensionChoiceSubmit(BaseModel):
    dimension: str          # "border_radius"
    selected_option_id: str # "rounded"
    selected_value: str     # "8px"
    css_property: str       # "borderRadius"
    fine_tuned_value: Optional[str] = None  # "12px" if slider-adjusted

class ComponentStateResponse(BaseModel):
    component_type: str
    choices: Dict[str, Dict[str, Any]]  # dimension_key -> {option_id, value, fine_tuned_value, css_property}

class StudioProgressResponse(BaseModel):
    current_component: Optional[str] = None
    current_dimension_index: int = 0
    completed_components: List[str] = []
    total_components: int = 12
    checkpoint_approvals: List[str] = []
    pending_checkpoint: Optional[str] = None
    is_complete: bool = False

class CheckpointData(BaseModel):
    checkpoint_id: str
    label: str
    description: str
    mockup_type: str
    components: List[str]
    component_styles: Dict[str, Dict[str, str]]  # component_type -> {css_property: value}
    colors: Optional[Dict] = None
    typography: Optional[Dict] = None

class LockComponentResponse(BaseModel):
    success: bool
    next_component: Optional[str] = None
    trigger_checkpoint: Optional[str] = None
    is_studio_complete: bool = False


# Update forward refs
SessionDetailResponse.model_rebuild()
