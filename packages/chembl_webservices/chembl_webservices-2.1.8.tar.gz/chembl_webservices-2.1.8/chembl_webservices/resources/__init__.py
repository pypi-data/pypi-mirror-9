__author__ = 'mnowotka'

from chembl_webservices.resources.activities import ActivityResource
from chembl_webservices.resources.assays import AssayResource
from chembl_webservices.resources.atc import AtcResource
from chembl_webservices.resources.binding_site import BindingSiteResource
from chembl_webservices.resources.bio_component import BiotherapeuticComponentsResource
from chembl_webservices.resources.cell_line import CellLineResource
from chembl_webservices.resources.docs import DocsResource
from chembl_webservices.resources.image import ImageResource
from chembl_webservices.resources.mechanism import MechanismResource
from chembl_webservices.resources.molecule import MoleculeResource
from chembl_webservices.resources.molecule_forms import MoleculeFormsResource
from chembl_webservices.resources.protein_class import ProteinClassResource
from chembl_webservices.resources.similarity import SimilarityResource
from chembl_webservices.resources.source import SourceResource
from chembl_webservices.resources.status import StatusResource
from chembl_webservices.resources.substructure import SubstructureResource
from chembl_webservices.resources.target import TargetResource
from chembl_webservices.resources.target_components import TargetComponentsResource
from chembl_webservices.resources.chembl_id import ChemblIdLookupResource

__all__ = [
    'ActivityResource',
    'AssayResource',
    'AtcResource',
    'BindingSiteResource',
    'BiotherapeuticComponentsResource',
    'CellLineResource',
    'DocsResource',
    'ImageResource',
    'MechanismResource',
    'MoleculeResource',
    'MoleculeFormsResource',
    'ProteinClassResource',
    'SimilarityResource',
    'SourceResource',
    'StatusResource',
    'SubstructureResource',
    'TargetResource',
    'TargetComponentsResource',
    'ChemblIdLookupResource'
]
