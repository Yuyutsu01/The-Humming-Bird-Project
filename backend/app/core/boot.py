# Dynamic Module Bootstrap Registry Loader
import logging
import pkgutil
import importlib
from fastapi import FastAPI, APIRouter
from backend.app.modules.base import BaseModule

logger = logging.getLogger(__name__)

def bootstrap_modules(app: FastAPI) -> None:
    """
    Scans the backend/app/modules/ folder, dynamically imports any 'registry' files,
    instantiates discovered BaseModule subclasses, executes their initialize lifecycle hooks,
    and automatically registers their API routers to the FastAPI gateway.
    """
    logger.info("Starting dynamic module discovery process...")
    
    # Locate backend.app.modules package path
    try:
        import backend.app.modules as modules_pkg
        package_path = modules_pkg.__path__
    except Exception as e:
        logger.error(f"Failed to resolve modules package path: {e}", exc_info=True)
        return
        
    discovered_count = 0
    
    # Iterate through all direct subdirectories (packages) in the modules folder
    for _, module_name, ispkg in pkgutil.iter_modules(package_path):
        if not ispkg:
            continue
            
        logger.debug(f"Discovered module directory package: '{module_name}'. Attempting registry import...")
        
        try:
            # 1. Attempt to import registry.py from the discovered module sub-package
            registry_module_path = f"backend.app.modules.{module_name}.registry"
            registry_module = importlib.import_module(registry_module_path)
            
            # 2. Scan the registry module attributes to find subclasses of BaseModule
            module_class_found = False
            for attr_name in dir(registry_module):
                cls = getattr(registry_module, attr_name)
                
                # Check if this attribute is a class and a subclass of BaseModule (but not BaseModule itself)
                if (
                    isinstance(cls, type) 
                    and issubclass(cls, BaseModule) 
                    and cls is not BaseModule
                ):
                    logger.info(f"Found module registry class: '{cls.__name__}' inside module '{module_name}'.")
                    
                    # 3. Instantiate the module registry
                    module_instance = cls()
                    
                    # 4. Initialize module resources (DB tables, event subscriptions, adapters)
                    logger.info(f"Executing initialize() lifecycle hook for module: '{module_name}'...")
                    module_instance.initialize()
                    
                    # 5. Extract and mount the module router
                    router = module_instance.register_routes()
                    if isinstance(router, APIRouter):
                        from backend.app.core.config import settings
                        prefix = "" if router.prefix.startswith(settings.API_V1_STR) else settings.API_V1_STR
                        app.include_router(router, prefix=prefix)
                        logger.info(f"Mounted API router from module '{module_name}' with prefix '{prefix}' successfully.")
                    else:
                        logger.warning(f"Module '{module_name}' did not return a valid APIRouter instance from register_routes(). Skipping route registration.")
                        
                    module_class_found = True
                    discovered_count += 1
                    break
                    
            if not module_class_found:
                logger.warning(f"Discovered module folder '{module_name}' but found no valid BaseModule subclass in registry.py.")
                
        except ModuleNotFoundError as e:
            # Handle modules that don't have a registry.py or have internal import issues
            if f"registry" in str(e):
                logger.debug(f"Skipping module directory '{module_name}': registry.py not found.")
            else:
                logger.error(f"Failed to bootstrap module '{module_name}' due to internal missing imports: {e}", exc_info=True)
        except Exception as e:
            logger.error(f"Unexpected error encountered bootstrapping module '{module_name}': {e}", exc_info=True)

    logger.info(f"Module bootstrapping completed. Total successfully initialized modules: {discovered_count}")
