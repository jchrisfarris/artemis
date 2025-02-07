import uuid

from django.db.utils import IntegrityError

from artemisdb.artemisdb.consts import ComponentType
from artemisdb.artemisdb.models import Component, Dependency, License, RepoComponentScan, Scan
from artemislib.logging import Logger
from utils.plugin import Result

logger = Logger(__name__)


def process_sbom(result: Result, scan: Scan):
    for graph in result.details:
        for direct in graph:
            process_dependency(direct, scan, None)


def process_dependency(dep: dict, scan: Scan, parent: Dependency):
    component = get_component(dep["name"], dep["version"], scan, dep.get("type"))

    # Keep a copy of the license objects so they only have to be retrieved from the DB once
    license_obj_cache = {}

    licenses = []
    for license in dep["licenses"]:
        license_id = license["license_id"].lower()
        if license_id not in license_obj_cache:
            # If we don't have a local copy of the license object get it from the DB
            license_obj_cache[license_id], _ = License.objects.get_or_create(
                license_id=license_id, defaults={"name": license["name"]}
            )

        # Add the license object to the list for this component
        licenses.append(license_obj_cache[license_id])

    # Update the component's set of licenses
    if licenses:
        component.licenses.set(licenses)

    try:
        dependency = Dependency(
            label=component.label, component=component, scan=scan, source=dep["source"], parent=parent
        )
        dependency.save()
    except IntegrityError as e:
        logger.error("Unable to create dependency record %s (error: %s)", dependency, str(e))
        return

    for child in dep["deps"]:
        process_dependency(dep=child, scan=scan, parent=dependency)


def get_component(name: str, version: str, scan: Scan, component_type: str = None) -> Component:
    label = str(uuid.uuid4()).replace("-", "")  # Dash is not in the allowed character set for ltree labels
    component, created = Component.objects.get_or_create(
        name=name, version=version, defaults={"label": label, "component_type": component_type}
    )

    if not created and component.component_type in [None, ComponentType.UNKNOWN.value] and component_type is not None:
        # Update the component type if not already set
        component.component_type = component_type.lower()
        component.save()

    # Get the component/repo mapping, creating it if necessary. This mapping is maintained so that the SBOM
    # components API can do efficient filtering based on user scope or last scan time. Previously we used
    # the path through the dependency and scan tables for this but it was unusable in practice due to the
    # size of those tables.
    component_repo, created = RepoComponentScan.objects.get_or_create(
        repo=scan.repo, component=component, defaults={"scan": scan}
    )
    if not created:
        # Update the scan to point to this latest scan. We're only tracking the latest scan right now
        # for filtering on when a component was last seen.
        component_repo.scan = scan
        component_repo.save()

    return component
