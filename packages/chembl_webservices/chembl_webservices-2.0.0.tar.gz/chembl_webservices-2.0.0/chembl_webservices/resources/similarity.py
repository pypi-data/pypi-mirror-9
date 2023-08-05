__author__ = 'mnowotka'

from tastypie.resources import ALL, ALL_WITH_RELATIONS
from tastypie import fields
from tastypie.exceptions import BadRequest
from tastypie.utils import trailing_slash
from django.conf.urls import url
from django.core.urlresolvers import NoReverseMatch
from django.core.exceptions import MultipleObjectsReturned
from chembl_webservices.resources.molecule import MoleculeResource
from chembl_core_model.models import CompoundMols
from chembl_core_model.models import MoleculeDictionary
try:
    from chembl_compatibility.models import MoleculeHierarchy
except ImportError:
    from chembl_core_model.models import MoleculeHierarchy

#-----------------------------------------------------------------------------------------------------------------------

class SimilarityResource(MoleculeResource):

    similarity = fields.DecimalField('similarity')

    class Meta(MoleculeResource.Meta):
        queryset = MoleculeDictionary.objects.all()
        resource_name = 'similarity'
        required_params = {'api_dispatch_detail' : ['smiles', 'similarity']}

#-----------------------------------------------------------------------------------------------------------------------

    def base_urls(self):

        return [
            url(r"^(?P<resource_name>%s)%s$" % (self._meta.resource_name, trailing_slash(),), self.wrap_view('dispatch_list'), name="dispatch_list"),
            url(r"^(?P<resource_name>%s)\.(?P<format>\w+)$" % self._meta.resource_name, self.wrap_view('dispatch_list'), name="dispatch_list"),
            url(r"^(?P<resource_name>%s)/schema%s$" % (self._meta.resource_name, trailing_slash(),), self.wrap_view('get_schema'), name="api_get_schema"),
            url(r"^(?P<resource_name>%s)/schema\.(?P<format>\w+)$" % self._meta.resource_name, self.wrap_view('get_schema'), name="api_get_schema"),
            url(r"^(?P<resource_name>%s)/(?P<chembl_id>[Cc][Hh][Ee][Mm][Bb][Ll]\d[\d]*)/(?P<similarity>\d[\d]*)%s$" % (self._meta.resource_name, trailing_slash(),), self.wrap_view('dispatch_list'), name="api_dispatch_detail"),
            url(r"^(?P<resource_name>%s)/(?P<chembl_id>[Cc][Hh][Ee][Mm][Bb][Ll]\d[\d]*)/(?P<similarity>\d[\d]*)\.(?P<format>\w+)$" % self._meta.resource_name, self.wrap_view('dispatch_list'), name="api_dispatch_detail"),
            url(r"^(?P<resource_name>%s)/(?P<standard_inchi_key>[A-Z]{14}-[A-Z]{10}-[A-Z])/(?P<similarity>\d[\d]*)%s$" % (self._meta.resource_name, trailing_slash(),), self.wrap_view('dispatch_list'), name="api_dispatch_detail"),
            url(r"^(?P<resource_name>%s)/(?P<standard_inchi_key>[A-Z]{14}-[A-Z]{10}-[A-Z])/(?P<similarity>\d[\d]*)\.(?P<format>\w+)$" % self._meta.resource_name, self.wrap_view('dispatch_list'), name="api_dispatch_detail"),
            url(r"^(?P<resource_name>%s)/(?P<smiles>[^jx/]+)/(?P<similarity>\d[\d]*)\.(?P<format>json|xml)$" % self._meta.resource_name, self.wrap_view('dispatch_list'), name="api_dispatch_detail"),
            url(r"^(?P<resource_name>%s)/(?P<smiles>[^jx/]+)/(?P<similarity>\d[\d]*)%s$" % (self._meta.resource_name, trailing_slash(),), self.wrap_view('dispatch_list'), name="api_dispatch_detail"),
        ]

#-----------------------------------------------------------------------------------------------------------------------

    def prepend_urls(self):
        return []

#-----------------------------------------------------------------------------------------------------------------------

    def obj_get_list(self, bundle, **kwargs):
        smiles = kwargs.pop('smiles', None)
        std_inchi_key = kwargs.pop('standard_inchi_key', None)
        chembl_id = kwargs.pop('chembl_id', None)

        if not smiles and not std_inchi_key and not chembl_id:
            raise BadRequest("Structure or identifier required.")

        similarity = kwargs.pop('similarity')
        if not similarity:
            raise BadRequest("Similarity parameter is required.")
        if not smiles:
            if chembl_id:
                mol_filters = {'chembl_id':chembl_id}
            else:
                mol_filters = {'compoundstructures__standard_inchi_key' : std_inchi_key}
            try:
                objects = self.apply_filters(bundle.request, mol_filters).values_list('compoundstructures__canonical_smiles',
                    flat=True)
                stringified_kwargs = ', '.join(["%s=%s" % (k, v) for k, v in mol_filters.items()])
                length = len(objects)
                if length <= 0:
                    raise self._meta.object_class.DoesNotExist("Couldn't find an instance of '%s' which matched '%s'." %
                                                               (self._meta.object_class.__name__, stringified_kwargs))
                elif length > 1:
                    raise MultipleObjectsReturned("More than '%s' matched '%s'." % (self._meta.object_class.__name__,
                                                                                    stringified_kwargs))
                smiles = objects[0]
            except ValueError:
                raise BadRequest("Invalid resource lookup data provided (mismatched type).")

        similar = CompoundMols.objects.similar_to(smiles, similarity).values_list('molecule_id', 'similarity')
        similarity_map = dict(similar)

        filters = {
            'chembl__entity_type':'COMPOUND',
            'compoundstructures__isnull' : False,
            'pk__in' : MoleculeHierarchy.objects.all().values_list('parent_molecule_id'),
            'compoundproperties__isnull' : False,
        }

        standard_filters, distinct = self.build_filters(filters=kwargs)

        filters.update(standard_filters)
        try:
            objects = self.get_object_list(bundle.request).filter(**filters).filter(pk__in=[sim[0] for sim in similar])
        except ValueError:
            raise BadRequest("Invalid resource lookup data provided (mismatched type).")
        if distinct:
            objects = objects.distinct()
        for obj in objects:
            obj.similarity = similarity_map[obj.pk]
        return self.authorized_read_list(objects, bundle)

#-----------------------------------------------------------------------------------------------------------------------

    def get_resource_uri(self, bundle_or_obj=None, url_name='dispatch_list'):
        if bundle_or_obj is not None:
            url_name = 'dispatch_detail'

        try:
            return self._build_reverse_url(url_name, kwargs=self.resource_uri_kwargs(bundle_or_obj))
        except NoReverseMatch:
            return ''

#-----------------------------------------------------------------------------------------------------------------------