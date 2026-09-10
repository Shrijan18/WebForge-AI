from pydantic import BaseModel, Field


class DesignSystem(BaseModel):

    color_palette: dict = Field(default_factory=dict)

    typography: dict = Field(default_factory=dict)

    layout: dict = Field(default_factory=dict)

    spacing: list[str] = Field(default_factory=list)

    border_radius: str = ""

    shadows: str = ""

    motion: list[str] = Field(default_factory=list)

    imagery: str = ""


class WebsitePlan(BaseModel):

    website_name: str

    website_type: str

    generation_level: str = "intermediate"

    pages: list[str]

    features: list[str]

    database: bool

    authentication: bool

    theme: str

    description: str

    target_audience: str = ""

    primary_goal: str = ""

    content_strategy: list[str] = Field(default_factory=list)

    image_assets: list[dict] = Field(default_factory=list)

    design_system: DesignSystem = Field(default_factory=DesignSystem)