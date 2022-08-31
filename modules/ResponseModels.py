import modules.ResponseFields as ResponseFields
from pydantic import BaseModel, create_model

"""Implements pydantic models and model generator for the API's responses."""

class ModelGenerator():
    
    """Generates a pydantic model from a dictionary."""
    
    def __make_model(self, v, name):
        # Parses a dictionary and creates a pydantic model from it.
        #
        # Args:
        #    v: key value
        #    name: key name
        #
        # Returns:
        #    pydantic.BaseModel: Generated pydantic model
        
        if type(v) is dict:
            return create_model(name, **{k: self.__make_model(v, k) for k, v in v.items()}), ...
        return None, v

    def generate(self, v: dict, name: str):
        
        """Returns a pydantic model from a dictionary.

        Args:
            v (Dict): JSON dictionary
            name (str): Model name

        Returns:
            pydantic.BaseModel: Generated pydantic model
        """
        return self.__make_model(v, name)[0]

class AppsResponseModel(BaseModel):
    """Implements the JSON response model for the /apps endpoint.

    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    
    apps: list[str]

class ToolsResponseModel(BaseModel):
    """Implements the JSON response model for the /tools endpoint.

    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    
    tools: list[ ResponseFields.ToolsResponseFields ]

class PatchesResponseModel(BaseModel):
    """Implements the JSON response model for the /patches endpoint.

    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    
    __root__: list[ ResponseFields.PatchesResponseFields ]