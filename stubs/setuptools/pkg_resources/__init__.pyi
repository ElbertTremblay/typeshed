import importlib.abc
import types
import zipimport
from _typeshed import Incomplete
from abc import ABCMeta
from collections.abc import Callable, Generator, Iterable, Iterator, Sequence
from io import BytesIO
from re import Pattern
from typing import IO, Any, ClassVar, Protocol, TypeVar, overload, type_check_only
from typing_extensions import Literal, Self, TypeAlias

from ._vendored_packaging import requirements as packaging_requirements, version as packaging_version

_T = TypeVar("_T")
_D = TypeVar("_D", bound=Distribution)
_NestedStr: TypeAlias = str | Iterable[str | Iterable[Any]]
_InstallerType: TypeAlias = Callable[[Requirement], Distribution | None]
_EPDistType: TypeAlias = Distribution | Requirement | str
_MetadataType: TypeAlias = IResourceProvider | None
_PkgReqType: TypeAlias = str | Requirement
_DistFinderType: TypeAlias = Callable[[_Importer, str, bool], Generator[Distribution, None, None]]
_NSHandlerType: TypeAlias = Callable[[_Importer, str, str, types.ModuleType], str]

def declare_namespace(packageName: str) -> None: ...
def fixup_namespace_packages(path_item: str, parent=None) -> None: ...

class WorkingSet:
    entries: list[str]
    def __init__(self, entries: Iterable[str] | None = None) -> None: ...
    def require(self, *requirements: _NestedStr) -> Sequence[Distribution]: ...
    def run_script(self, requires: str, script_name: str) -> None: ...
    def iter_entry_points(self, group: str, name: str | None = None) -> Generator[EntryPoint, None, None]: ...
    def add_entry(self, entry: str) -> None: ...
    def __contains__(self, dist: Distribution) -> bool: ...
    def __iter__(self) -> Iterator[Distribution]: ...
    def find(self, req: Requirement) -> Distribution | None: ...
    def resolve(
        self,
        requirements: Iterable[Requirement],
        env: Environment | None = None,
        installer: _InstallerType | None = None,
        replace_conflicting: bool = False,
        extras=None,
    ) -> list[Distribution]: ...
    def add(self, dist: Distribution, entry: str | None = None, insert: bool = True, replace: bool = False) -> None: ...
    def subscribe(self, callback: Callable[[Distribution], object], existing: bool = True) -> None: ...
    def find_plugins(
        self, plugin_env: Environment, full_env: Environment | None = None, installer=None, fallback: bool = True
    ) -> tuple[list[Distribution], dict[Distribution, Exception]]: ...

working_set: WorkingSet

require = working_set.require
run_script = working_set.run_script
run_main = run_script
iter_entry_points = working_set.iter_entry_points
add_activation_listener = working_set.subscribe

class Environment:
    def __init__(
        self, search_path: Sequence[str] | None = None, platform: str | None = ..., python: str | None = ...
    ) -> None: ...
    def __getitem__(self, project_name: str) -> list[Distribution]: ...
    def __iter__(self) -> Iterator[str]: ...
    def add(self, dist: Distribution) -> None: ...
    def remove(self, dist: Distribution) -> None: ...
    def can_add(self, dist: Distribution) -> bool: ...
    def __add__(self, other: Distribution | Environment) -> Environment: ...
    def __iadd__(self, other: Distribution | Environment) -> Self: ...
    @overload
    def best_match(
        self, req: Requirement, working_set: WorkingSet, installer: None = None, replace_conflicting: bool = False
    ) -> Distribution: ...
    @overload
    def best_match(
        self, req: Requirement, working_set: WorkingSet, installer: Callable[[Requirement], _T], replace_conflicting: bool = False
    ) -> _T: ...
    @overload
    def obtain(self, requirement: Requirement, installer: None = None) -> None: ...
    @overload
    def obtain(self, requirement: Requirement, installer: Callable[[Requirement], _T]) -> _T: ...
    def scan(self, search_path: Sequence[str] | None = None) -> None: ...

def parse_requirements(strs: str | Iterable[str]) -> Generator[Requirement, None, None]: ...

class RequirementParseError(packaging_requirements.InvalidRequirement): ...

class Requirement(packaging_requirements.Requirement):
    unsafe_name: str
    project_name: str
    key: str
    extras: tuple[str, ...]  # type: ignore[assignment]  # incompatible override of attribute on base class
    specs: list[tuple[str, str]]
    def __init__(self, requirement_string: str) -> None: ...
    @staticmethod
    def parse(s: str | Iterable[str]) -> Requirement: ...
    def __contains__(self, item: Distribution | str | tuple[str, ...]) -> bool: ...
    def __eq__(self, other_requirement: object) -> bool: ...

def load_entry_point(dist: _EPDistType, group: str, name: str) -> Any: ...
def get_entry_info(dist: _EPDistType, group: str, name: str) -> EntryPoint | None: ...
@overload
def get_entry_map(dist: _EPDistType, group: None = None) -> dict[str, dict[str, EntryPoint]]: ...
@overload
def get_entry_map(dist: _EPDistType, group: str) -> dict[str, EntryPoint]: ...

class EntryPoint:
    pattern: ClassVar[Pattern[str]]
    name: str
    module_name: str
    attrs: tuple[str, ...]
    extras: tuple[str, ...]
    dist: Distribution | None
    def __init__(
        self,
        name: str,
        module_name: str,
        attrs: tuple[str, ...] = (),
        extras: tuple[str, ...] = (),
        dist: Distribution | None = None,
    ) -> None: ...
    @classmethod
    def parse(cls, src: str, dist: Distribution | None = None) -> EntryPoint: ...
    @classmethod
    def parse_group(cls, group: str, lines: str | Sequence[str], dist: Distribution | None = None) -> dict[str, EntryPoint]: ...
    @classmethod
    def parse_map(
        cls, data: dict[str, str | Sequence[str]] | str | Sequence[str], dist: Distribution | None = None
    ) -> dict[str, EntryPoint]: ...
    def load(self, require: bool = True, env: Environment | None = ..., installer: _InstallerType | None = ...) -> Any: ...
    def require(self, env: Environment | None = None, installer: _InstallerType | None = None) -> None: ...
    def resolve(self) -> Any: ...

def find_distributions(path_item: str, only: bool = False) -> Generator[Distribution, None, None]: ...
@overload
def get_distribution(dist: _D) -> _D: ...
@overload
def get_distribution(dist: _PkgReqType) -> Distribution: ...

EGG_DIST: int
BINARY_DIST: int
SOURCE_DIST: int
CHECKOUT_DIST: int
DEVELOP_DIST: int

def resource_exists(package_or_requirement: _PkgReqType, resource_name: str) -> bool: ...
def resource_stream(package_or_requirement: _PkgReqType, resource_name: str) -> IO[bytes]: ...
def resource_string(package_or_requirement: _PkgReqType, resource_name: str) -> bytes: ...
def resource_isdir(package_or_requirement: _PkgReqType, resource_name: str) -> bool: ...
def resource_listdir(package_or_requirement: _PkgReqType, resource_name: str) -> list[str]: ...
def resource_filename(package_or_requirement: _PkgReqType, resource_name: str) -> str: ...
def set_extraction_path(path: str) -> None: ...
def cleanup_resources(force: bool = False) -> list[str]: ...
@type_check_only
class _IResourceManager(Protocol):
    def resource_exists(self, package_or_requirement: _PkgReqType, resource_name: str) -> bool: ...
    def resource_stream(self, package_or_requirement: _PkgReqType, resource_name: str) -> IO[bytes]: ...
    def resource_string(self, package_or_requirement: _PkgReqType, resource_name: str) -> bytes: ...
    def resource_isdir(self, package_or_requirement: _PkgReqType, resource_name: str) -> bool: ...
    def resource_listdir(self, package_or_requirement: _PkgReqType, resource_name: str) -> list[str]: ...
    def resource_filename(self, package_or_requirement: _PkgReqType, resource_name: str) -> str: ...
    def set_extraction_path(self, path: str) -> None: ...
    def cleanup_resources(self, force: bool = ...) -> list[str]: ...
    def get_cache_path(self, archive_name: str, names: Iterable[str] = ...) -> str: ...
    def extraction_error(self) -> None: ...
    def postprocess(self, tempname: str, filename: str) -> None: ...

@overload
def get_provider(moduleOrReq: str) -> IResourceProvider: ...
@overload
def get_provider(moduleOrReq: Requirement) -> Distribution: ...

class IMetadataProvider(Protocol):
    def has_metadata(self, name: str) -> bool | None: ...
    def metadata_isdir(self, name: str) -> bool: ...
    def metadata_listdir(self, name: str) -> list[str]: ...
    def get_metadata(self, name: str) -> str: ...
    def get_metadata_lines(self, name: str) -> Generator[str, None, None]: ...
    def run_script(self, script_name: str, namespace: dict[str, Any]) -> None: ...

class ResolutionError(Exception): ...

class DistributionNotFound(ResolutionError):
    @property
    def req(self) -> Requirement: ...
    @property
    def requirers(self) -> set[str]: ...
    @property
    def requirers_str(self) -> str: ...
    def report(self) -> str: ...

class VersionConflict(ResolutionError):
    @property
    def dist(self) -> Any: ...
    @property
    def req(self) -> Any: ...
    def report(self) -> str: ...
    def with_context(self, required_by: set[Distribution | str]) -> VersionConflict: ...

class ContextualVersionConflict(VersionConflict):
    @property
    def required_by(self) -> set[Distribution | str]: ...

class UnknownExtra(ResolutionError): ...

class ExtractionError(Exception):
    manager: _IResourceManager
    cache_path: str
    original_error: Exception

class _Importer(importlib.abc.MetaPathFinder, importlib.abc.InspectLoader, metaclass=ABCMeta): ...

def register_finder(importer_type: type, distribution_finder: _DistFinderType) -> None: ...
def register_loader_type(loader_type: type, provider_factory: Callable[[types.ModuleType], IResourceProvider]) -> None: ...
def register_namespace_handler(importer_type: type, namespace_handler: _NSHandlerType) -> None: ...

class IResourceProvider(IMetadataProvider, Protocol):
    def get_resource_filename(self, manager: _IResourceManager, resource_name): ...
    def get_resource_stream(self, manager: _IResourceManager, resource_name): ...
    def get_resource_string(self, manager: _IResourceManager, resource_name): ...
    def has_resource(self, resource_name): ...
    def resource_isdir(self, resource_name): ...
    def resource_listdir(self, resource_name): ...

def invalid_marker(text) -> SyntaxError | Literal[False]: ...
def evaluate_marker(text, extra: Incomplete | None = None): ...

class NullProvider:
    egg_name: str | None
    egg_info: str | None
    loader: types._LoaderProtocol | None
    module_path: str | None

    def __init__(self, module) -> None: ...
    def get_resource_filename(self, manager: _IResourceManager, resource_name) -> str: ...
    def get_resource_stream(self, manager: _IResourceManager, resource_name) -> BytesIO: ...
    def get_resource_string(self, manager: _IResourceManager, resource_name): ...
    def has_resource(self, resource_name) -> bool: ...
    def has_metadata(self, name: str) -> bool | None: ...
    def get_metadata(self, name: str) -> str: ...
    def get_metadata_lines(self, name: str) -> Generator[str, None, None]: ...
    def resource_isdir(self, resource_name) -> bool: ...
    def metadata_isdir(self, name: str) -> bool: ...
    def resource_listdir(self, resource_name) -> list[str]: ...
    def metadata_listdir(self, name: str) -> list[str]: ...
    def run_script(self, script_name: str, namespace: dict[str, Any]) -> None: ...

# Doesn't actually extend NullProvider
class Distribution(NullProvider):
    PKG_INFO: ClassVar[str]
    location: str
    project_name: str
    @property
    def hashcmp(self) -> tuple[Incomplete, int, str, Incomplete | None, str, str]: ...
    def __hash__(self) -> int: ...
    def __lt__(self, other: Distribution) -> bool: ...
    def __le__(self, other: Distribution) -> bool: ...
    def __gt__(self, other: Distribution) -> bool: ...
    def __ge__(self, other: Distribution) -> bool: ...
    def __eq__(self, other: object) -> bool: ...
    def __ne__(self, other: object) -> bool: ...
    @property
    def key(self) -> str: ...
    @property
    def extras(self) -> list[str]: ...
    @property
    def version(self) -> str: ...
    @property
    def parsed_version(self) -> packaging_version.Version: ...
    py_version: str
    platform: str | None
    precedence: int
    def __init__(
        self,
        location: str | None = None,
        metadata: _MetadataType = None,
        project_name: str | None = None,
        version: str | None = None,
        py_version: str = ...,
        platform: str | None = None,
        precedence: int = 3,
    ) -> None: ...
    @classmethod
    def from_location(
        cls, location: str, basename: str, metadata: _MetadataType = None, **kw: str | None | int
    ) -> Distribution: ...
    @classmethod
    def from_filename(cls, filename: str, metadata: _MetadataType = None, **kw: str | None | int) -> Distribution: ...
    def activate(self, path: list[str] | None = None, replace: bool = False) -> None: ...
    def as_requirement(self) -> Requirement: ...
    def requires(self, extras: tuple[str, ...] = ()) -> list[Requirement]: ...
    def check_version_conflict(self) -> None: ...
    def has_version(self) -> bool: ...
    def clone(self, **kw: str | int | None) -> Requirement: ...
    def egg_name(self) -> str: ...  # type: ignore[override]  # supertype's egg_name is a variable, not a method
    def get_entry_info(self, group: str, name: str) -> EntryPoint | None: ...
    def insert_on(self, path, loc: Incomplete | None = None, replace: bool = False) -> None: ...
    @overload
    def get_entry_map(self, group: None = None) -> dict[str, dict[str, EntryPoint]]: ...
    @overload
    def get_entry_map(self, group: str) -> dict[str, EntryPoint]: ...
    def load_entry_point(self, group: str, name: str) -> Any: ...

class DistInfoDistribution(Distribution):
    PKG_INFO: ClassVar[Literal["METADATA"]]
    EQEQ: ClassVar[Pattern[str]]

class EggProvider(NullProvider):
    egg_root: str

class DefaultProvider(EggProvider): ...

class PathMetadata(DefaultProvider):
    egg_info: str
    module_path: str
    def __init__(self, path: str, egg_info: str) -> None: ...

class ZipProvider(EggProvider):
    eagers: list[str] | None
    zip_pre: str
    @property
    def zipinfo(self): ...

class EggMetadata(ZipProvider):
    loader: zipimport.zipimporter
    module_path: str
    def __init__(self, importer: zipimport.zipimporter) -> None: ...

class EmptyProvider(NullProvider):
    module_path: None
    def __init__(self) -> None: ...

empty_provider: EmptyProvider

class FileMetadata(EmptyProvider):
    def __init__(self, path: str) -> None: ...

class PEP440Warning(RuntimeWarning): ...

parse_version = packaging_version.Version

def yield_lines(iterable: _NestedStr) -> Generator[str, None, None]: ...
def split_sections(s: _NestedStr) -> Generator[tuple[str | None, list[str]], None, None]: ...
def safe_name(name: str) -> str: ...
def safe_version(version: str) -> str: ...
def safe_extra(extra: str) -> str: ...
def to_filename(name: str) -> str: ...
def get_build_platform() -> str: ...
def get_platform() -> str: ...
def get_supported_platform() -> str: ...
def compatible_platforms(provided: str | None, required: str | None) -> bool: ...
def get_default_cache() -> str: ...
def get_importer(path_item: str) -> _Importer: ...
def ensure_directory(path: str) -> None: ...
def normalize_path(filename: str) -> str: ...

class PkgResourcesDeprecationWarning(Warning): ...
