from typing import List
from typing import Dict
from typing import Any
from typing import Optional
from pydantic import BaseModel
from pydantic import ConfigDict


class RecipeNodeParameterDataset(BaseModel):
    type: str
    label: str


class RecipeNodeParameter(BaseModel):
    model_config = ConfigDict(strict=False, arbitrary_types_allowed=True)

    fields: Optional[List[str] | Any] = None
    dataset: Optional[RecipeNodeParameterDataset] = None


class RecipeNode(BaseModel):
    action: str
    parameters: RecipeNodeParameter


class Recipe(BaseModel):

    model_config = ConfigDict(strict=False, arbitrary_types_allowed=True)

    nodes: Dict[str, RecipeNode]
