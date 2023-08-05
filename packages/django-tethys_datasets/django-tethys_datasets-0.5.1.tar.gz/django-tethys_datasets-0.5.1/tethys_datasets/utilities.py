from tethys_apps.base.app_base import TethysAppBase
from .models import DatasetService as DsModel, SpatialDatasetService as SdsModel


def initialize_engine_object(engine, endpoint, apikey=None, username=None, password=None):
    """
    Initialize a DatasetEngine object from a string that points at the engine class.
    """
    # Derive import parts from engine string
    engine_split = engine.split('.')
    module_string = '.'.join(engine_split[:-1])
    engine_class_string = engine_split[-1]

    # Import
    module = __import__(module_string, fromlist=[engine_class_string])
    EngineClass = getattr(module, engine_class_string)

    # Create Engine Object
    engine_instance = EngineClass(endpoint=endpoint,
                                  apikey=apikey,
                                  username=username,
                                  password=password)
    return engine_instance


def get_dataset_engine(name, app_class=None):
    """
    Get a dataset engine with the given name.

    Args:
      name (string): Name of the dataset engine to retrieve.
      app_class (class): The app class to include in the search for dataset engines.

    Returns:
      (DatasetEngine): A dataset engine object.
    """
    # If the app_class is given, check it first for a dataset engine
    app_dataset_services = None

    if app_class and issubclass(app_class, TethysAppBase):
        # Instantiate app class and retrieve dataset services list
        app = app_class()
        app_dataset_services = app.dataset_services()

    if app_dataset_services:
        # Search for match
        for app_dataset_service in app_dataset_services:

            # If match is found, initiate engine object
            if app_dataset_service.name == name:
                return initialize_engine_object(engine=app_dataset_service.engine,
                                                endpoint=app_dataset_service.endpoint,
                                                apikey=app_dataset_service.apikey,
                                                username=app_dataset_service.username,
                                                password=app_dataset_service.password)

    # If the dataset engine cannot be found in the app_class, check database for site-wide dataset engines
    site_dataset_services = DsModel.objects.all()

    if site_dataset_services:
        # Search for match
        for site_dataset_service in site_dataset_services:

            # If match is found initiate engine object
            if site_dataset_service.name == name:
                dataset_service_object = initialize_engine_object(engine=site_dataset_service.engine.encode('utf-8'),
                                                                  endpoint=site_dataset_service.endpoint,
                                                                  apikey=site_dataset_service.apikey,
                                                                  username=site_dataset_service.username,
                                                                  password=site_dataset_service.password)

                return dataset_service_object

    raise NameError('Could not find dataset service with name "{0}". Please check that dataset service with that name '
                    'exists in settings.py or in your app.py.'.format(name))


def get_spatial_dataset_engine(name, app_class=None):
    """
    Get a spatial dataset engine with the given name.

    Args:
      name (string): Name of the dataset engine to retrieve.
      app_class (class): The app class to include in the search for dataset engines.

    Returns:
      (SpatialDatasetEngine): A spatial dataset engine object.
    """
    # If the app_class is given, check it first for a dataset engine
    app_spatial_dataset_services = None

    if app_class and issubclass(app_class, TethysAppBase):
        # Instantiate app class and retrieve dataset services list
        app = app_class()
        app_spatial_dataset_services = app.spatial_dataset_services()

    if app_spatial_dataset_services:
        # Search for match
        for app_spatial_dataset_service in app_spatial_dataset_services:

            # If match is found, initiate engine object
            if app_spatial_dataset_service.name == name:
                return initialize_engine_object(engine=app_spatial_dataset_service.engine,
                                                endpoint=app_spatial_dataset_service.endpoint,
                                                apikey=app_spatial_dataset_service.apikey,
                                                username=app_spatial_dataset_service.username,
                                                password=app_spatial_dataset_service.password)

    # If the dataset engine cannot be found in the app_class, check database for site-wide dataset engines
    site_spatial_dataset_services = SdsModel.objects.all()

    if site_spatial_dataset_services:
        # Search for match
        for site_spatial_dataset_service in site_spatial_dataset_services:

            # If match is found initiate engine object
            if site_spatial_dataset_service.name == name:
                return initialize_engine_object(engine=site_spatial_dataset_service.engine.encode('utf-8'),
                                                endpoint=site_spatial_dataset_service.endpoint,
                                                apikey=site_spatial_dataset_service.apikey,
                                                username=site_spatial_dataset_service.username,
                                                password=site_spatial_dataset_service.password)


    raise NameError('Could not find spatial dataset service with name "{0}". Please check that dataset service with that name '
                    'exists in either the Admin Settings or in your app.py.'.format(name))







