# -*- coding: utf-8 -*-
"""Testing class for pyicane package.

"""
from pyicane import pyicane
import unittest
import logging
import requests
from datetime import datetime
from collections import OrderedDict

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)
REQUESTS_LOG = logging.getLogger("requests")
REQUESTS_LOG.setLevel(logging.WARNING)


class TestGenericMethods(unittest.TestCase):
    # pylint: disable=R0904

    """ Test Case for metadata module methods """

    def setUp(self):
        self.node_digest_fields = 35

    def test_request(self):
        """ Test pyicane.request() """
        section_instance = pyicane.Section(pyicane.request('section/economy'))
        self.assertTrue(section_instance.title.encode("utf-8") == 'Economía')
        self.assertRaises(requests.exceptions.HTTPError,
                          pyicane.request, 'section/economic')

    def test_plain_metadata_model(self):
        """ Test pyicane.plain_metadata_model() """
        node_instance = pyicane.TimeSeries.get('quarterly-accounting-'
                                               'cantabria-base-2008-current-'
                                               'prices')
        node_digest = pyicane.node_digest_model(node_instance)
        self.assertTrue(len(node_digest) == self.node_digest_fields)
        self.assertTrue(node_digest[30] == 'Trimestral')

    def test_flatten_metadata(self):
        """ Test pyicane.flatten_metadata() """
        node_list = pyicane.TimeSeries.find_all('regional-data',
                                                'economy',
                                                'labour-market')
        first_record_name = 'Estadísticas de empleo y paro'
        second_record_uri_tag = 'active-population-survey-bases'
        records = pyicane.flatten_metadata(node_list)
        self.assertTrue(first_record_name == next(records)[1].encode("utf-8"))
        self.assertTrue(second_record_uri_tag == next(records)[19].
                        encode("utf-8"))

    def test_flatten_data(self):
        """ Test pyicane.flatten_data() """
        resource = requests.get('http://www.icane.es/data/api/municipal-'
                                'register-annual-review-municipality.json'
                                ).json(object_pairs_hook=OrderedDict)
        data = list(pyicane.flatten_data(resource))
        self.assertTrue(data[-1][3] == -0.55)
        self.assertTrue(data[0][3] == 2646.0)

    def test_add_query_string_params(self):
        """ Test pyicane.add_query_string_params() """
        self.assertTrue(pyicane.add_query_string_params('non-olap-native') ==
                        '?nodeType=non-olap-native')

        self.assertTrue(pyicane.add_query_string_params('non-olap-native',
                                                        'True') ==
                        '?nodeType=non-olap-native&inactive=True')

    def test_add_path_params(self):
        """ Test pyicane.add_path_params() """
        self.assertTrue(pyicane.add_path_params('economy') ==
                        '/economy')
        self.assertTrue(pyicane.add_path_params('economy', 'labour-market') ==
                        '/economy/labour-market')

        self.assertTrue(pyicane.add_path_params('economy', 'labour-market',
                                                'active-population-survey-'
                                                'bases'
                                                ) ==
                        '/economy/labour-market/active-population-survey-bases'
                        )


class TestCategory(unittest.TestCase):
    # pylint: disable=R0904
    """ Test Case for pyicane.Category class """

    def setUp(self):
        pass

    def test_category(self):
        """ Test pyicane.Category class"""
        self.assertRaises(ValueError, pyicane.Category, 'not a json object')
        self.assertTrue(pyicane.Category(
            pyicane.request('category/historical-data')).title.encode("utf-8")
            == 'Datos históricos')

    def test_get(self):
        """ Test pyicane.Category get()"""
        self.assertRaises(requests.exceptions.HTTPError,
                          pyicane.Category.get, 'regioal-data')
        self.assertEqual(pyicane.Category.get('regional-data').title,
                         'Datos regionales')
        self.assertEqual(pyicane.Category.get(3).uriTag, 'municipal-data')

        self.assertRaises(requests.exceptions.HTTPError,
                          pyicane.Category.get, 89)
        self.assertEqual(pyicane.Category.get(1).title, 'Datos regionales')

    def test_find_all(self):
        """ Test pyicane.Category find_all()"""
        categories = pyicane.Category.find_all()
        self.assertEqual(len(categories), 4)
        self.assertTrue(pyicane.Category.get('municipal-data') in categories)


class TestClass(unittest.TestCase):
    # pylint: disable=R0904
    """ Test Case for pyicane.Class class """

    def setUp(self):
        pass

    def test_get(self):
        """ Test pyicane.Class.get()"""
        self.assertEqual(pyicane.Class.get('time-series', 'es').fields[0].name,
                         'active')
        self.assertEqual(pyicane.Class.get('time-series', 'en').fields[1].name,
                         'apiUris')

    def test_find_all(self):
        """ Test pyicane.Class.find_all()"""
        self.assertEqual(pyicane.Class.find_all('en')[1].name, 'DataSet')
        self.assertEqual(pyicane.Class.find_all('en')[2].name, 'TimeSeries')


class TestData(unittest.TestCase):
    # pylint: disable=R0904
    """ Test Case for pyicane.Data class """

    def setUp(self):
        pass

    def test_get_last_updated(self):
        """ Test pyicane.Data.get_last_updated()"""
        self.assertTrue(datetime.strptime(pyicane.Data.get_last_updated(),
                                          '%d/%m/%Y'))

    def test_get_last_updated_millis(self):
        """ Test pyicane.Data.get_last_updated_millis()"""
        self.assertTrue(datetime.strptime(datetime.fromtimestamp(
            int(str(pyicane.Data.get_last_updated_millis())[0:-3])
        ).strftime('%d/%m/%Y'), '%d/%m/%Y'))


class TestDataProvider(unittest.TestCase):
    # pylint: disable=R0904
    """ Test Case for pyicane.DataProvider class """

    def setUp(self):
        pass

    def test_data_provider(self):
        """ Test pyicane.DataProvider class"""
        self.assertRaises(ValueError,
                          pyicane.DataProvider,
                          'not a json object')
        self.assertEqual(pyicane.DataProvider(
            pyicane.request('data-provider/1')).title.encode("utf-8"),
            'Instituto Nacional de Estadística')

    def test_get(self):
        """ Test pyicane.DataProvider.get()"""
        self.assertRaises(requests.exceptions.HTTPError,
                          pyicane.DataProvider.get, 'E0012120')
        self.assertEqual(pyicane.DataProvider.get('E00121204').acronym, 'INE')

        self.assertRaises(requests.exceptions.HTTPError,
                          pyicane.DataProvider.get, 999)
        self.assertEqual(pyicane.DataProvider.get(3).title.encode('utf-8'),
                         'Gobierno de España')

    def test_find_all(self):
        """ Test pyicane.DataProvider.find_all()"""
        data_providers = pyicane.DataProvider.find_all()
        self.assertTrue(len(data_providers) > 100)
        self.assertTrue(pyicane.DataProvider.get('20') in data_providers)


class TestDataSet(unittest.TestCase):
    # pylint: disable=R0904
    """ Test Case for pyicane.DataSet class """

    def setUp(self):
        pass

    def test_data_set(self):
        """ Test pyicane.DataSet class"""
        self.assertRaises(ValueError, pyicane.DataSet, 'not a json object')
        self.assertEqual(pyicane.DataSet(pyicane.request('data-set/87')).title,
                         'Empleo de las personas con discapacidad')

    def test_get(self):
        """ Test pyicane.DataSet.get()"""
        self.assertRaises(requests.exceptions.HTTPError,
                          pyicane.DataProvider.get, 'elections-autonomix')
        self.assertEqual(pyicane.DataSet.get('elections-autonomic').acronym,
                         'EAUTO')

        self.assertRaises(requests.exceptions.HTTPError,
                          pyicane.DataSet.get, 999)
        self.assertEqual(pyicane.DataSet.get(4).title, 'Aperturas de centros')

    def test_find_all(self):
        """ Test pyicane.DataSet.find_all()"""
        data_sets = pyicane.DataSet.find_all()
        self.assertTrue(len(data_sets) > 100)
        self.assertTrue(pyicane.DataSet.get('regional-accounts-1995')
                        in data_sets)


class TestLink(unittest.TestCase):
    # pylint: disable=R0904
    """ Test Case for pyicane.Link class """

    def setUp(self):
        pass

    def test_link(self):
        """ Test pyicane.Link class"""
        self.assertRaises(ValueError, pyicane.Link, 'not a json object')
        self.assertEqual(pyicane.Link(pyicane.request('link/472')).title,
                         'DBpedia')

    def test_get(self):
        """ Test pyicane.Link.get()"""
        self.assertRaises(requests.exceptions.HTTPError, pyicane.Link.get, 89)
        self.assertEqual(pyicane.Link.get(478).title, 'LEM')

    def test_find_all(self):
        """ Test pyicane.Link.find_all()"""
        links = pyicane.Link.find_all()
        self.assertTrue(len(links) > 200)
        self.assertTrue(pyicane.Link.get('873') in links)


class TestLinkType(unittest.TestCase):
    # pylint: disable=R0904
    """ Test Case for pyicane.LinkType class """

    def setUp(self):
        pass

    def test_link_type(self):
        """ Test pyicane.LinkType class"""
        self.assertRaises(ValueError, pyicane.LinkType, 'not a json object')
        self.assertEqual(pyicane.LinkType(pyicane.request('link-type/1')).
                         title, 'HTTP')

    def test_get(self):
        """ Test pyicane.LinkType.get()"""
        self.assertRaises(requests.exceptions.HTTPError,
                          pyicane.LinkType.get, 99)
        self.assertEqual(pyicane.LinkType.get(6).title, 'RDFS seeAlso')

    def test_find_all(self):
        """ Test pyicane.LinkType.find_all()"""
        link_types = pyicane.LinkType.find_all()
        self.assertTrue(len(link_types) == 8)
        self.assertTrue(pyicane.LinkType.get('4') in link_types)


class TestMeasure(unittest.TestCase):
    # pylint: disable=R0904
    """ Test Case for pyicane.Measure class """

    def setUp(self):
        pass

    def test_measure(self):
        """ Test pyicane.Measure class"""
        self.assertRaises(ValueError, pyicane.Measure, 'not a json object')
        self.assertEqual(pyicane.Measure(pyicane.request('measure/1')).title,
                         'Parados')

    def test_get(self):
        """ Test pyicane.Measure.get()"""
        self.assertRaises(requests.exceptions.HTTPError,
                          pyicane.Measure.get, 9999)
        self.assertEqual(pyicane.Measure.get(5742).code, 'CMestancia')

    def test_find_all(self):
        """ Test pyicane.Measure.find_all()"""
        measures = pyicane.Measure.find_all()
        self.assertTrue(len(measures) > 3000)
        self.assertTrue(pyicane.Measure.get('1503') in measures)


class TestMetadata(unittest.TestCase):
    # pylint: disable=R0904
    """ Test Case for pyicane.Metadata class """

    def setUp(self):
        pass

    def test_get_last_updated(self):
        """ Test pyicane.pyicane.get_last_updated()"""
        self.assertTrue(datetime.strptime(pyicane.Metadata.get_last_updated(),
                                          '%d/%m/%Y'))

    def test_get_last_updated_millis(self):
        """ Test pyicane.pyicane.get_last_updated_millis()"""
        self.assertTrue(datetime.strptime(datetime.fromtimestamp(
            int(str(pyicane.Metadata.get_last_updated_millis())
                [0:-3])).strftime('%d/%m/%Y'), '%d/%m/%Y'))


class TestNodeType(unittest.TestCase):
    # pylint: disable=R0904
    """ Test Case for pyicane.NodeType class """

    def setUp(self):
        pass

    def test_node_type(self):
        """ Test pyicane.NodeType class"""
        self.assertRaises(ValueError, pyicane.NodeType, 'not a json object')
        self.assertEqual(pyicane.NodeType(
            pyicane.request('node-type/1')).title.encode('utf-8'), 'Sección')

    def test_get(self):
        """ Test pyicane.NodeType.get()"""
        self.assertRaises(requests.exceptions.HTTPError,
                          pyicane.NodeType.get, 'documen')
        self.assertEqual(pyicane.NodeType.get('document').title, 'Documento')

        self.assertRaises(requests.exceptions.HTTPError,
                          pyicane.NodeType.get, 99)
        self.assertEqual(pyicane.NodeType.get(8).title.encode('utf-8'),
                         'Categoría')

    def test_find_all(self):
        """ Test pyicane.NodeType.find_all()"""
        node_types = pyicane.NodeType.find_all()
        self.assertTrue(len(node_types) >= 10)
        self.assertTrue(pyicane.NodeType.get('4') in node_types)


class TestPeriodicity(unittest.TestCase):
    # pylint: disable=R0904
    """ Test Case for pyicane.Periodicity class """

    def setUp(self):
        pass

    def test_periodicity(self):
        """ Test pyicane.Periodicity class"""
        self.assertRaises(ValueError, pyicane.Periodicity,
                          'not a json object')
        self.assertEqual(pyicane.Periodicity(
            pyicane.request('periodicity/annual')).title, 'Anual')

    def test_get(self):
        """ Test pyicane.Periodicity.get()"""
        self.assertRaises(requests.exceptions.HTTPError,
                          pyicane.Periodicity.get, 'montly')
        self.assertEqual(pyicane.Periodicity.get('monthly').title, 'Mensual')

        self.assertRaises(requests.exceptions.HTTPError,
                          pyicane.Periodicity.get, 89)
        self.assertEqual(pyicane.Periodicity.get(3).title, 'Trimestral')

    def test_find_all(self):
        """ Test pyicane.Periodicity.find_all()"""
        periodicities = pyicane.Periodicity.find_all()
        self.assertTrue(len(periodicities) == 12)
        self.assertTrue(pyicane.Periodicity.get('irregular') in periodicities)


class TestReferenceArea(unittest.TestCase):
    # pylint: disable=R0904
    """ Test Case for pyicane.ReferenceArea class """

    def setUp(self):
        pass

    def test_reference_area(self):
        """ Test pyicane.ReferenceArea class"""
        self.assertRaises(ValueError, pyicane.ReferenceArea,
                          'not a json object')
        self.assertEqual(pyicane.ReferenceArea(
            pyicane.request('reference-area/local')).title, 'Inframunicipal')

    def test_get(self):
        """ Test pyicane.ReferenceArea.get()"""
        self.assertRaises(requests.exceptions.HTTPError,
                          pyicane.ReferenceArea.get, 'regioal')
        self.assertEqual(pyicane.ReferenceArea.get('regional').title,
                         'Regional')

        self.assertRaises(requests.exceptions.HTTPError,
                          pyicane.ReferenceArea.get, 89)
        self.assertEqual(pyicane.ReferenceArea.get(3).title, 'Nacional')

    def test_find_all(self):
        """ Test pyicane.ReferenceArea.find_all()"""
        reference_areas = pyicane.ReferenceArea.find_all()
        self.assertTrue(len(reference_areas) >= 6)
        self.assertTrue(pyicane.ReferenceArea.get('municipal')
                        in reference_areas)


class TestSection(unittest.TestCase):
    # pylint: disable=R0904
    """ Test Case for pyicane.Section class"""

    def setUp(self):
        pass

    def test_section(self):
        """ Test pyicane.Section class"""
        self.assertRaises(ValueError, pyicane.Section, 'not a json object')
        self.assertEqual(pyicane.Section(
            pyicane.request('section/society')).title, 'Sociedad')

    def test_get(self):
        """ Test pyicane.Section.get()"""
        self.assertRaises(requests.exceptions.HTTPError,
                          pyicane.Section.get, 'economia')
        self.assertEqual(pyicane.Section.get('economy').title.encode('utf-8'),
                         'Economía')

        self.assertRaises(requests.exceptions.HTTPError,
                          pyicane.Section.get, 89)
        self.assertEqual(pyicane.Section.get(4).title,
                         'Territorio y Medio ambiente')

    def test_find_all(self):
        """ Test pyicane.Section.find_all()"""
        sections = pyicane.Section.find_all()
        self.assertTrue(len(sections) == 5)
        self.assertTrue(pyicane.Section.get('synthesis') in sections)

    def test_get_subsections(self):
        """ Test pyicane.Section.get_subsections()"""
        self.assertTrue(pyicane.Subsection.get(7) in
                        pyicane.Section.get(2).get_subsections())

    def test_get_subsection(self):
        """ Test pyicane.Section.get_subsection()"""
        with self.assertRaises(requests.exceptions.HTTPError):
            pyicane.Section.get('economy').get_subsection('lavour-market')
        self.assertEqual(pyicane.Section.get('economy').get_subsection(
            'labour-market').title, 'Mercado de Trabajo')


class TestSource(unittest.TestCase):
    # pylint: disable=R0904
    """ Test Case for pyicane.Source class"""

    def setUp(self):
        pass

    def test_source(self):
        """ Test pyicane.Source class"""
        self.assertRaises(ValueError, pyicane.Source,
                          'not a json object')
        self.assertEqual(pyicane.Source(
            pyicane.request('source/45')).label.encode('utf-8'),
            'Censo agrario. Instituto Nacional de Estadística (INE)')

    def test_get(self):
        """ Test pyicane.Source.get()"""
        self.assertRaises(requests.exceptions.HTTPError,
                          pyicane.Source.get, 8999)
        self.assertEqual(pyicane.Source.get(546).uri, 'http://www.ine.es')

    def test_find_all(self):
        """ Test pyicane.Source.find_all()"""
        sources = pyicane.Source.find_all()
        self.assertTrue(len(sources) > 500)
        self.assertTrue(pyicane.Source.get('457') in sources)


class TestSubsection(unittest.TestCase):
    # pylint: disable=R0904
    """ Test Case for pyicane.Subsection class"""

    def setUp(self):
        pass

    def test_subsection(self):
        """ Test pyicane.Subsection class"""
        self.assertRaises(ValueError, pyicane.Subsection,
                          'not a json object')
        self.assertEqual(pyicane.Subsection(
            pyicane.request('subsection/1')).title.encode('utf-8'),
            'Cifras de población')

    def test_get(self):
        """ Test pyicane.Subsection.get()"""
        self.assertRaises(requests.exceptions.HTTPError,
                          pyicane.Subsection.get, 99)
        self.assertEqual(pyicane.Subsection.get(13).title, 'Servicios')

    def test_find_all(self):
        """ Test pyicane.Subsection.find_all()"""
        subsections = pyicane.Subsection.find_all()
        self.assertTrue(len(subsections) > 20)
        self.assertTrue(pyicane.Subsection.get('6') in subsections)


class TestTimePeriod(unittest.TestCase):
    # pylint: disable=R0904
    """ Test Case for pyicane.TimePeriod class"""

    def setUp(self):
        pass

    def test_time_period(self):
        """ Test pyicane.TimePeriod class"""
        self.assertRaises(ValueError, pyicane.TimePeriod,
                          'not a json object')
        self.assertEqual(pyicane.TimePeriod(
            pyicane.request('time-period/593')).timeFormat, 'na')

    def test_get(self):
        """ Test pyicane.TimePeriod.get()"""
        self.assertRaises(requests.exceptions.HTTPError,
                          pyicane.TimePeriod.get, 9999)
        self.assertEqual(pyicane.TimePeriod.get(340).startYear, 1976)

    def test_find_all(self):
        """ Test pyicane.TimePeriod.find_all()"""
        time_periods = pyicane.TimePeriod.find_all()
        self.assertTrue(len(time_periods) > 300)
        self.assertTrue(pyicane.TimePeriod.get('426') in time_periods)


class TestTimeSeries(unittest.TestCase):
    # pylint: disable=R0904
    """ Test Case for pyicane.TimeSeries class"""

    def setUp(self):
        pass

    def test_time_series(self):
        """ Test pyicane.TimeSeries class"""
        self.assertRaises(ValueError, pyicane.TimeSeries,
                          'not a json object')
        self.assertEqual(pyicane.TimeSeries(
            pyicane.request('time-series/232')).title,
            'Afiliados medios mensuales en alta laboral')

    def test_get(self):
        """ Test pyicane.TimeSeries.get()"""
        self.assertRaises(requests.exceptions.HTTPError,
                          pyicane.TimeSeries.get, 'quarterly-account')
        self.assertEqual(pyicane.TimeSeries.get('quarterly-accounting-' +
                         'cantabria-base-2008-current-prices').title,
                         'Precios corrientes')

        self.assertRaises(requests.exceptions.HTTPError,
                          pyicane.TimeSeries.get, 9999)
        self.assertEqual(pyicane.TimeSeries.get(5036).title.encode("utf-8"),
                         'Nomenclátor Cantabria')

        self.assertRaises(requests.exceptions.HTTPError,
                          pyicane.TimeSeries.get, 32)
        self.assertEqual(pyicane.TimeSeries.get(32, inactive=True).uriTag,
                         'childbirths')

    def test_data_as_dataframe(self):
        """ Test pyicane.TimeSeries.data_as_dataframe()"""
        time_series = pyicane.TimeSeries.get('quarterly-accounting-' +
                                             'cantabria-base-2008-current-'
                                             'prices')
        data_frame = time_series.data_as_dataframe()
        self.assertTrue(len(data_frame) >= 2349)
        data_frame.to_csv('./trimestral.csv', sep='\t', encoding='utf-8')

    def test_metadata_as_dataframe(self):
        """ Test pyicane.TimeSeries.metadata_as_dataframe()"""
        time_series = pyicane.TimeSeries.get('quarterly-accounting-' +
                                             'cantabria-base-2008-current-'
                                             'prices')
        node_list = pyicane.TimeSeries.find_all('regional-data',
                                                'economy',
                                                'labour-market')
        dataframe = time_series.metadata_as_dataframe()
        metadata_array = []
        for node in node_list:
            metadata_array.append(node.metadata_as_dataframe())
        metadata_df = metadata_array[0].append(metadata_array[1:])
        self.assertTrue(len(metadata_df) >= 198)
        self.assertEqual('Precios corrientes', dataframe.iloc[0]['title'])
        self.assertEqual('ajuste,trimestre,sector',
                         dataframe.iloc[0]['automatizedTopics'])

    def test_get_parent(self):
        """ Test pyicane.TimeSeries.get_parent()"""
        self.assertEqual(pyicane.TimeSeries.get_parent('municipal-'
                                                       'terrain-series'),
                         pyicane.TimeSeries.get('municipal-terrain'))
        self.assertEqual(pyicane.TimeSeries.get_parent(4876),
                         pyicane.TimeSeries.get(4106))

    def test_get_parents(self):
        """ Test pyicane.TimeSeries.get_parents()"""
        self.assertTrue(pyicane.TimeSeries.get('municipal-terrain')
                        in pyicane.TimeSeries.get_parents('municipal-'
                                                          'terrain-series'))
        self.assertTrue(pyicane.TimeSeries.get(4106)
                        in pyicane.TimeSeries.get_parents(4876))

    def test_get_possible_subsections(self):
        """ Test pyicane.TimeSeries.get_possible_subsections()"""
        subsections = pyicane.TimeSeries.get_possible_subsections(
            'active-population-economic-sector-nace09')
        self.assertEqual(len(subsections), 1)
        self.assertTrue(pyicane.Subsection.get(7) in subsections)

    def test_get_by_category(self):
        """ Test pyicane.TimeSeries.get_by_category()"""
        time_series_list = pyicane.TimeSeries.find_all('historical-data')
        self.assertTrue(len(time_series_list) > 50)
        self.assertTrue(pyicane.TimeSeries.get('unemployment-employment')
                        in time_series_list)

    def test_get_by_category_and_section(self):
        """ Test pyicane.TimeSeries.get_by_category_and_section()"""
        data_set_list = pyicane.TimeSeries.find_all('municipal-data',
                                                    'society',
                                                    node_type_uri_tag='data-'
                                                                      'set')
        time_series_list = pyicane.TimeSeries.find_all('municipal-data',
                                                       'territory-environment',
                                                       node_type_uri_tag='time'
                                                       '-series')
        self.assertTrue(len(data_set_list) > 7)
        self.assertTrue(len(time_series_list) > 35)
        self.assertTrue(pyicane.TimeSeries.get('municipal-terrain-series')
                        in time_series_list)
        self.assertTrue(pyicane.TimeSeries.get('elections-municipal')
                        in data_set_list)

    def test_get_by_category_and_section_and_subsection(self):
        """ Test pyicane.TimeSeries.get_by_category_and_section_and_
        subsection()"""
        node_list = pyicane.TimeSeries.find_all('regional-data',
                                                'economy',
                                                'labour-market')
        node_list_all = pyicane.TimeSeries.find_all('regional-data',
                                                    'economy',
                                                    'labour-market',
                                                    inactive=True)
        time_series_list = pyicane.TimeSeries.find_all('regional-data',
                                                       'economy',
                                                       'labour-market',
                                                       node_type_uri_tag='time'
                                                       '-series')
        time_series_list_all = pyicane.TimeSeries.find_all(
            'regional-data', 'economy', 'labour-market',
            node_type_uri_tag='time-series', inactive=True)
        data_set_list = pyicane.TimeSeries.find_all('regional-data',
                                                    'society',
                                                    'living-standards',
                                                    node_type_uri_tag='data-'
                                                                      'set')
        self.assertTrue(len(time_series_list_all) >= len(time_series_list))
        self.assertTrue(len(node_list) >= 2)
        self.assertEqual(len(node_list), len(node_list_all))
        self.assertTrue(len(data_set_list) >= 3)
        self.assertTrue(len(time_series_list) >= 60)
        self.assertTrue(pyicane.TimeSeries.get('unemployment-benefits')
                        in data_set_list)
        self.assertTrue(pyicane.TimeSeries.get('active-population-aged-16-'
                                               'more-gender-age-group-activity'
                                               '-base-2011')
                        in time_series_list)
        self.assertTrue(pyicane.TimeSeries.get('employment-unemployment-'
                                               'statistics')
                        in node_list)

    def test_get_by_category_and_section_and_subsection_and_dataset(self):
        """ Test pyicane.TimeSeries.get_by_category_and_section_and_
            subsection_and_dataset()"""
        node_list = pyicane.TimeSeries.find_all('regional-data',
                                                'society',
                                                'living-standards',
                                                'unemployment-benefits')
        self.assertTrue(len(node_list) >= 2)
        self.assertTrue(pyicane.TimeSeries.get('unemployment-benefits-'
                                               'requests-beneficiaries-'
                                               'expenditures')
                        in node_list)

    def test_get_datasets(self):
        """ Test pyicane.TimeSeries.get_datasets()"""
        data_set_list = pyicane.TimeSeries.find_all_datasets(
            'regional-data', 'economy', 'labour-market')
        data_set_filtered_list = pyicane.TimeSeries.find_all(
            'regional-data', 'economy', 'labour-market',
            node_type_uri_tag='data-set')
        self.assertTrue(len(data_set_list) <= len(data_set_filtered_list))
        self.assertTrue(len(data_set_list) >= 3)
        self.assertTrue(pyicane.TimeSeries.get('labour-societies')
                        in data_set_list)

    def test_get_possible_time_series(self):
        """ Test pyicane.TimeSeries.get_possible_time_series()"""
        time_series_list = pyicane.TimeSeries.get_possible_time_series(
            'active-population-economic-sector-nace09')
        self.assertEqual(len(time_series_list), 1)
        self.assertTrue(pyicane.TimeSeries.get(5642) in time_series_list)


class TestUnifOfMeasure(unittest.TestCase):
    # pylint: disable=R0904
    """ Test Case for pyicane.UnitOfMeasure class"""

    def setUp(self):
        pass

    def test_unif_of_measure(self):
        """ Test pyicane.UnitOfMeasure class"""
        self.assertRaises(ValueError, pyicane.UnitOfMeasure,
                          'not a json object')
        self.assertEqual(pyicane.UnitOfMeasure(
            pyicane.request('unit-of-measure/1')).
            title.encode('utf-8'), 'Años')

    def test_get(self):
        """ Test pyicane.UnitOfMeasure.get()"""
        self.assertRaises(requests.exceptions.HTTPError,
                          pyicane.UnitOfMeasure.get, 9999)
        self.assertEqual(pyicane.UnitOfMeasure.get(320).title.encode('utf-8'),
                         'Número de bibliotecas y '
                         'Número de equipos de reproducción')

    def test_find_all(self):
        """ Test pyicane.UnitOfMeasure.find_all()"""
        units_of_measure = pyicane.UnitOfMeasure.find_all()
        self.assertTrue(len(units_of_measure) > 300)
        self.assertTrue(pyicane.UnitOfMeasure.get('45') in units_of_measure)


if __name__ == '__main__':
    unittest.main()
