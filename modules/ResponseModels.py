import modules.ResponseFields as ResponseFields
from typing import Dict, Union, List
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

    def generate(self, v: Dict, name: str):
        
        """Returns a pydantic model from a dictionary.

        Args:
            v (Dict): JSON dictionary
            name (str): Model name

        Returns:
            pydantic.BaseModel: Generated pydantic model
        """
        return self.__make_model(v, name)[0]

class SupportedApps(BaseModel):
    """Implements the JSON response model for the /apps endpoint.

    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    
    apps: List[str]

class LatestTools(BaseModel):
    """Implements the JSON response model for the /tools endpoint.

    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    
    tools: List[ Dict[ ResponseFields.LatestToolsFields, str ] ]
    
    class Config:  
        use_enum_values = True
        
class SimplifiedPatches(BaseModel):
    """Implements the JSON response model for the /patches endpoint.

    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    
    patches: List[ Dict[ ResponseFields.SimplifiedPatchesFields, str ] ]
    
    class Config:  
        use_enum_values = True

class Patches(BaseModel):
    """_summary_

    Args:
        BaseModel (pydantic.BaseModel): BaseModel from pydantic
    """
    
    __root__ = List[ Dict[ str, Union[str, List[str], Dict, bool] ] ]