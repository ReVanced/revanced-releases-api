from app.dependencies import load_config

config: dict = load_config()

class Socials:
    
    """Implements the code infrastructure for the socials page."""
    
    async def get_socials(self) -> dict:
        """Get socials from config.toml.
        
        Returns:
            dict: A dictionary containing socials from config.toml
        """
        
        socials: dict = config['socials']
        
        return socials
