pdf version available in docs/�est_map_documentation.pdf










west_map

Sean West*

April 14, 2015


Contents
1. Introduction	3
1.1 Function	3
1.2 Installation	3
1.2.1 Dependencies	3
1.2.2 How to install	3
2. BioMart structure and 'west_map'	5
2.1 BioMart	5
2.1.1 Database Structure	5
2.1.2 API Setup	5
2.1.3 Data Characteristics	5
2.2 'west_map'	6
2.2.1 Connection to BioMart	6
2.2.2 Retrieval from BioMart	6
2.2.3 Limitations and constraints	6
3. Using 'west_map' functionality	7
3.1 Functionality	7
3.2 Inputs	7
3.3 Examples	8
3.3.1 Task: Converting .dyn network file of Affymetrix coexpressions to HGNC Symbols	8
3.3.2 Task: Create a file with the start and end sequence positions within the human genome for a list of Entrez Ids (One column)	9
3.3.3 Task: Show list of all attributes available for the “ensembl” mart and the “hsapiens_gene_ensembl” datasets	9
3.3.4 Task: Show list of all available BioMart martservice	9
3.3.5 Task: Export list of filters to a file.txt	9
4. Using 'west_map' Python library	10
4.1 Directory structure	10
4.2 Useful Libraries	10
4.2.1 'biomart.control'	10
4.2.2 'map.control'	10
4.2.3 'map.contact'	10
4.3 Examples	11
4.3.1 Task: show attributes for “ensembl” and “hsapiens_gene_ensembl”	11
4.3.2 Task: obtain list of ids from second column in “input.txt”	11
4.3.3 Task: obtain conversion object (dictionary of lists) for previously obtained list	11
4.3.4 Task: export “output.txt” a converted file from “input.txt' in the previous example	11
5. Appendix	12
5.1 Available BioMart marts	12
5.2 Available BioMart datasets for “ensembl”	14
5.3 Attributes for “ensembl” and “hsapiens_gene_ensembl”	16


1.	Introduction

1.1	Function
	The purpose of 'west_map' is to extend the functional capability of BioMart to Python. BioMart, further described below, is designed to “facilitate the scientific discovery process” (www.biomart.org). Perhaps the most useful component of BioMart is the ability to map biological elements to each other through the BioMart API. This API, while setup for easy and widespread use, has a widespread selection of limited tools. 
	This tool, created for linux or as a set of Python 3 libraries, is focused on the quick mapping of biological elements through the API. Currently, its functionality includes file conversion and the creation of new map files given a list of Ids. Use 'west_map' if you have a file with Ids that need converted or if you want to create a map between two Id types. Since 'west_map' uses the BioMart database, the capabilities extend to current BioMart structure.
1.2	Installation
	The files are available on pypi.python.org after searching for “west_map”. Any further questions on access or updates to the package can be sent to the authors email on the title page. At the current state, there is no alternate URL, yet one is coming.
	The downloadable tarball houses the source code, documentation (including this document), test files, the license, and a version update file.
1.2.1 Dependencies
	The source code is written in Python 3.2 and has been tested successfully in Python 3.4 and Python 2.7. The non-'west_map' imports within the program include 'getopt', 'os', 'collections', 'itertools', 'sys', and 'requests'. Each of these are included within the standard Python libraries. Setuptools is required to install the package. For further setuptools documentation, see https://pypi.python.org/pypi/setuptools.
1.2.2	How to install
	After downloading the tarball, use standard 'setup.py' commands to install on the machine. For instance, if installing on a local linux account:
tar xzvf west_map-0.1.tar.gz
cd west_map-0.1
python setup.py install –user
	This will install in the ~/.local/bin directory and store the libraries in the ~/.local/lib. The path can be renamed to install anywhere, but the prefix must be manually changed in the setup.py command. To use the 'west_map' command in any directory make sure to add the /bin to PATH. Add to .bashrc if one would like this command to carry over to future sessions.
export PATH=$PATH:~/.local/bin

2.	BioMart structure and 'west_map'
2.1	BioMart
2.1.1	Database Structure
	The BioMart central portal uses a combination of 4 qualifiers to determine query results: a database (or mart), a dataset, filters, and attributes. The database is the highest level qualifier and determines the overall location that the information is coming from. The default database for 'west_map' is “ensembl” which corresponds to the Ensembl 78 Genes database. The dataset is a subset of the database and usually identifies the type of data being used. The default dataset is the “hsapiens_gene_ensembl” dataset under the “ensembl” database. Finally, filters are a list of qualifiers that describe the query values. They are dependent on the database and the dataset. Attributes are the qualifiers that the user would like to be returned. In 'west_map', the filter is automatically included within the mapping file, but not included in a converted file. 
	For conversion or mapping, all four qualifiers must be specified. For “--show_marts”, no qualifiers are necessary. For “--show_datasets”, marts must be specified. For “--show_filters” or “--show_attributes”, both a mart and a dataset must be specified (or defaults will be used).
2.1.2	API Setup
	The BioMart API has a REST API, SOAP API, and Java API. The processors available are TSV, CSV, and JSON. 'west_map' uses the REST API with XML queries. The XML query is created using Python string manipulation and submitted to the REST API using the Python “requests” package. The API 'west_map' response requires either a 200 or 400. In the first case, the response is processed. In the latter, the query is too long. So the query is cut in half and then resubmitted.
2.1.3	Data Characteristics
	When the data is returned by BioMart, it is represented in multiple patterns. In the case of REST API through 'west_map', the response-object text-attribute is a simple string, delineating a table through '\n' and '\t'. The Ids to be converted often have multiple values for an attribute or a set of attributes. The results are filter dependent and not attribute dependent. So, they will include multiple lines to reflect these multiple relationships. As BioMart retrieves its data via source databases, any incomplete data is a consequence of the individual data source, the improper structure of the query, or the Ids to be converted/mapped.
2.2	'west_map'
2.2.1	Connection to BioMart
	As stated above, 'west_map' connects to the BioMart REST API through XML Queries using the Python package “requests”. The connection is made through the sub-package 'west_map.biomart', through the module 'west_map.biomart.control' which submits user requests and data to either 'west_map.biomart.get_lists' (which gets available BioMart lists for marts, datasets, filters, and attributes) or 'west_map.biomart.query' (which iteratively sends XML queries requesting Id conversion).
2.2.2	Retrieval from BioMart
	The 'west_map.biomart.get_lists' object does not directly use the BioMart API. Rather it sends requests to either “http://www.biomart.org/biomart/martservice” or “http://www.biomart.org/biomart/martservice/marts” using parameters which return html text that is parsed within the 'get_lists' methods. 
	The 'west_map.biomart.query' formulates XML queries for the BioMart API in the following format:
	<Query client='biomartclient' processor='TSV' limit='-1' header='0'>
	<Dataset name='[dataset name]' config='[mart name]'>
	<Filter name='[filter name]'/>
	<Attribute name='[attribute name 1]'/>
	<Attribute name='[attribute name 2]'/>
	…
	</Dataset>
	</Query>
2.2.3	Limitations and constraints
	The 'west_map' package does not handle most API returned status codes (404, 405, 500). The mapping output is CSV, but the XML and input file handle can only use TSV. The “--show_datasets” command line argument uses parsing code written only for the “ensembl” 
3.	Using 'west_map' functionality
3.1	Functionality
	The package 'west_map' has a single command but two overall functionalities. In the first version, the package can convert a tab delimted text file with Ids to alternate BioMart Ids. In this case, the column with the Ids is specified by the user within the command line. If an Id corresponds to multiple Ids (or if there are multiple columns locations within a line, each with multiple corresponding Ids) additional lines are added where everything but the Ids are duplicated so that the exaustive product of the sets of new Ids are added. For instance, the mapping
	id1	newid-a	newid-b
	id2 	newid-c	newid-d	newid-e
will convert the line
	id1	id2	1.34	aerosol
to
	newid-a	newid-c	1.34	aerosol
	newid-a	newid-d	1.34	aerosol
	newid-a	newid-e	1.34	aerosol
	…	
	newid-b	newid-e	1.34	aerosol
Whereas the mapping function would output:
	id1,newid-a,newid-b
	id2,newid-c,newid-d,newid-e
3.2	Inputs
Required for Conversion or Mapping:
	-i	--input=		Input file where the ids are that need to be converted.
	-o	--output=		Name of the file where the converted Ids will be, regardless
					of version
	-d	--dataset=		Name of the BioMart datasets
	-f	--filter=		Name of the BioMart filter (singular in current version)
	-a	--attributes=		List of the names of the BioMart attributes, separated with ','
	-m	--mart=		Name of the BioMart mart
	-c	--columns=		List separated with ',' of the columns of the input file with the Ids
	-v	--version=		“convert” [default] or “map” to delineate function
Non-required:
	-h	--help
	-n	--header		Add to signify a single line header in the input file
	-r	--show_marts		List all BioMart marts (overrides mapping/conversion 
					functionality)
	-s	--show_datasets	List all BioMart datasets given a [-m, --mart] (overrides mapping/
					conversion functionality)
	-l	--show_filters		List all BioMart filters given [-m, --mart], [-d, --dataset] (overrides
					mapping/conversion functionality)
	-b	--show_attributes	List all BioMart attributes given [-m, --mart], [-d, --dataset]
					(overrides mapping/conversion functionality)
3.3 Examples
3.3.1 Task: Converting .dyn network file of Affymetrix coexpressions to HGNC Symbols
west_map --input=network.dyn --output=converted_network.dyn --mart=ensembl --dataset=hsapiens_gene_ensembl --filter=affy_hg_u133_v2 --attributes=hgnc_symbol --columns=1,2  --version=convert
Here, the input network is “network.dyn” and the output network is “converted_network.dyn”. In this example the network Ids from the original .dyn belong to H. Sapiens, so we use the “hsapiens_gene_ensembl” dataset for the “ensembl” mart. The Affymetrix arrays have multiple probesets, so it is important to pick a probeset that is representative of the MicroArray platform used.
3.3.2 Task: Create a file with the start and end sequence positions within the human genome for a list of Entrez Ids (One column)
west_map --input=entrez_ids.txt --output=mapping_file.txt --mart=ensembl --dataset=hsapiens_gene_ensembl --filter=gene_id --attributes=chromosome_name,start_position,end_position --columns=1 --version=map 
3.3.3 Task: Show list of all attributes available for the “ensembl” mart and the “hsapiens_gene_ensembl” datasets
west_map --mart=ensembl --dataset=hsapiens_gene_ensembl --show_attributes 
3.3.4 Task: Show list of all available BioMart martservice
west_map --show_marts 
3.3.5 Task: Export list of filters to a file.txt
west_map --mart=ensembl --dataset=hsapiens_gene_ensembl --show_filters > filters.txt
4.	Using 'west_map' Python library
4.1	Directory structure
4.2 Useful Libraries
4.2.1 'biomart.control'
biomart.control(mart, dataset, filters, attribute)
1. 'biomart.control.show_marts()' - Prints all BioMart available marts to stdout.
2. 'biomart.control.show_datasets()' - Prints all BioMart datasets for a given mart to stdout. Requires the initialization of 'biomart.control.mart'.
3. 'biomart.control.show_filters()' - Prints all BioMart filters for a given mart and dataset to stdout. Requires the initialization of 'biomart.control.mart' and 'biomart.control.dataset'.
4. 'biomart.control.show_attributes()' - Prints all BioMart attributes for a given mart and dataset to stdout. Requires the intialization of 'biomart.control.mart' and 'biomart.control.dataset'.
5. 'biomart.control.get_converstion(ids)' – Accepts a list of ids that correspond to self.filter. Returns a dictionary of lists where dictionary[id] = [list of corresponding ids]. Requires the intialization of 'biomart.control.mart', 'biomart.control.dataset', 'biomart.control.filters', and 'biomart.control.attribute'.
4.2.2 'map.control'
1. 'map.control.help()' - Prints directions to 'west_map' functionality to stdout.
4.2.3 'map.contact'
1. 'map.contact.parse(inputloc, columns, header)' – given an input file location (string), a list of columns (list of int), and a header flag (boolean), saves a non-redundant list of ids to convert as 'map.contact.ids'.
2. 'map.contact.export(inputloc, columns, header, outputloc, conversion)' – given an input file location (string), a list of columns (list of int), a header flag (boolean), an output file location (string), and a conversion object (dictionary of lists created from 'biomart.control.get_conversion(ids)'), exports an updated file with converted ids instead of original ids.
3. 'map.contact.mapping(inputloc, columns, header, outputloc, conversion)' – given (see previous), exports a comma separated mapping file for filter and attributes.
4.3 Examples
4.3.1 Task: show attributes for “ensembl” and “hsapiens_gene_ensembl”
import west_map
c = west_map.biomart.control(mart='ensembl', dataset='hsapiens_gene_ensembl')
c.show_attributes()
4.3.2 Task: obtain list of ids from second column in “input.txt”
import west_map
cont = west_map.map.contact()
# inputfile location, list of columns, boolean for header
ids = cont.parse('input.txt', [2], False)
4.3.3 Task: obtain conversion object (dictionary of lists) for previously obtained list
c = west_map.biomart.control(mart='ensembl', dataset='hsapiens_gene_ensembl', filters=['affy_u133_plus2'], attribute=['hgnc_symbol'])
conversion = c.get_conversion(ids) # “ids” from previous task
4.3.4 Task: export “output.txt” a converted file from “input.txt' in the previous example
# inputfile location, list of columns, boolean for header, output file location, conversion object
cont.export('input.txt', [2], False, 'output.txt', conversion)
5.	Appendix
5.1 Available BioMart marts
Breast_mart_69
BCCTB Bioinformatics Portal (UK and Ireland)
EMAGE browse repository
EMAGE BROWSE REPOSITORY
EMAGE gene expression
EMAGE GENE EXPRESSION
EMAP anatomy ontology
EMAP ANATOMY ONTOLOGY
ENSEMBL_MART_ONTOLOGY
Ontology
ENSEMBL_MART_PLANT
GRAMENE 40 ENSEMBL GENES (CSHL/CORNELL US)
ENSEMBL_MART_PLANT_SEQUENCE
Sequence
ENSEMBL_MART_PLANT_SNP
GRAMENE 40 VARIATION (CSHL/CORNELL US)
Eurexpress Biomart
EUREXPRESS (MRC EDINBURGH UK)
GermOnline
GERMONLINE
HapMap_rel27
HAPMAP 27 (NCBI US)
Hsmm_Hmec
Predictive models of gene regulation from processed high-throughput epigenomics data: Hsmm vs. Hmec
K562_Gm12878
Predictive models of gene regulation from processed high-throughput epigenomics data: K562 vs. Gm12878
Pancreas63
PANCREATIC EXPRESSION DATABASE (BARTS CANCER INSTITUTE UK)
Prod_BOFUB
Botrytis cinerea B0510, genes functional annotation 
Prod_BOTRYTISEDIT
Botrytis cinerea T4, genes functional annotation 
Prod_LMACULANSEDIT
Leptosphaeria maculans, genes functional annotation
Prod_POPLAR
Populus trichocarpa, genes functional annotation
Prod_POPLAR_V2
Populus trichocarpa, genes functional annotation V2.0
Prod_TOMATO
Tomato, stuctural and functional annotation
Prod_WHEAT
Wheat, stuctural annotation with Genetic maps (genetic markers..)
Public_MAIZE
Zea mays ZmB73, genes functional annotation
Public_OBIOMARTPUB
Multi-species: marker, QTL, SNP, gene, germplasm, phenotype, association, with Gene annotations
Public_TAIRV10
Arabidopsis Thaliana TAIRV10, genes functional annotation
Public_VITIS
Grapevine 8x, stuctural annotation with Genetic maps (genetic markers..)
Public_VITIS_12x
Grapevine 12x.0, stuctural and functional annotation with Genetic maps (genetic markers..)
Sigenae Oligo Annotation (Ensembl 56)
SIGENAE OLIGO ANNOTATION (ENSEMBL 56)
Sigenae Oligo Annotation (Ensembl 59)
SIGENAE OLIGO ANNOTATION (ENSEMBL 59)
Sigenae_Oligo_Annotation_Ensembl_61
SIGENAE OLIGO ANNOTATION (ENSEMBL 61)
WS220
WORMBASE 220 (CSHL US)
biblioDB
PARAMECIUM BIBLIOGRAPHY (CNRS FRANCE)
biomart
MGI (JACKSON LABORATORY US)
biomartDB
PARAMECIUM GENOME (CNRS FRANCE)
cg_mart_02
PROTEOMICS (UNIVERSITY OF CAMBRIDGE - UK)
ensembl
ENSEMBL GENES 79 (SANGER UK)
example
FANTOM5 phase1.1 (RIKEN CSLST Japan)
expression
VectorBase Expression
fungi_mart_26
ENSEMBL FUNGI 26 (EBI UK)
fungi_sequence_mart_26

fungi_variations_26
ENSEMBL FUNGI VARIATION 26 (EBI UK)
genomic_features
ENSEMBL GENOMIC FEATURES 79 (SANGER UK)
htgt
WTSI MOUSE GENETICS PROJECT (SANGER UK)
ikmc
IKMC GENES AND PRODUCTS (IKMC)
metazoa_genomic_features_mart_26

metazoa_mart_26
ENSEMBL METAZOA 26 (EBI UK)
metazoa_sequence_mart_26

metazoa_variations_26
ENSEMBL METAZOA VARIATION 26 (EBI UK)
metazome_mart
Metazome
metazome_sequence_mart
Sequences
msd
MSD (EBI UK)
oncomodules
INTOGEN ONCOMODULES
ontology
Ontology Mart
parasite_mart
ParaSite Mart (EBI UK)
parasite_sequences
ParaSite Mart Sequences
phytozome_mart
Phytozome
plants_mart_26
ENSEMBL PLANTS 26 (EBI UK)
plants_sequence_mart_26

plants_variations_26
ENSEMBL PLANTS VARIATION 26 (EBI UK)
pride
PRIDE (EBI UK)
prod-intermart_1
INTERPRO (EBI UK)
protists_mart_25
ENSEMBL PROTISTS 25 (EBI UK)
protists_sequence_mart_26

protists_variations_26
ENSEMBL PROTISTS VARIATION 26 (EBI UK)
regulation
ENSEMBL REGULATION 79 (SANGER UK)
sequence
ENSEMBL SEQUENCE 79 (SANGER UK)
sequence_mart
Sequences
snp
ENSEMBL VARIATION 79 (SANGER UK)
unimart
UNIPROT (EBI UK)
vb_gene_mart_1502
VectorBase Genes
vb_genomic_features_mart_1502
Genomic Features 1502
vb_ontology_mart_1502
Ontology Mart 1502
vb_sequence_mart_1502
VectorBase Sequence Mart
vb_snp_mart_1502
VectorBase Variation
vega
VEGA 59  (SANGER UK)

5.2 Available BioMart datasets for “ensembl”
dnovemcinctus_gene_ensembl
Dasypus novemcinctus genes (Dasnov3.0)
Dasnov3.0
2015-03-03 14:20:47
cjacchus_gene_ensembl
Callithrix jacchus genes (C_jacchus3.2.1)
C_jacchus3.2.1
2015-03-03 14:20:11
vpacos_gene_ensembl
Vicugna pacos genes (vicPac1)
vicPac1
2015-03-03 14:20:20
ggallus_gene_ensembl
Gallus gallus genes (Galgal4)
Galgal4
2015-03-03 14:20:51
tsyrichta_gene_ensembl
Tarsius syrichta genes (tarSyr1)
tarSyr1
2015-03-03 14:20:48
mlucifugus_gene_ensembl
Myotis lucifugus genes (myoLuc2)
myoLuc2
2015-03-03 14:21:21
nleucogenys_gene_ensembl
Nomascus leucogenys genes (Nleu1.0)
Nleu1.0
2015-03-03 14:20:36
amexicanus_gene_ensembl
Astyanax mexicanus genes (AstMex102)
AstMex102
2015-03-03 14:20:31
gaculeatus_gene_ensembl
Gasterosteus aculeatus genes (BROADS1)
BROADS1
2015-03-03 14:20:17
amelanoleuca_gene_ensembl
Ailuropoda melanoleuca genes (ailMel1)
ailMel1
2015-03-03 14:21:09
acarolinensis_gene_ensembl
Anolis carolinensis genes (AnoCar2.0)
AnoCar2.0
2015-03-03 14:20:41
sscrofa_gene_ensembl
Sus scrofa genes (Sscrofa10.2)
Sscrofa10.2
2015-03-03 14:20:29
mfuro_gene_ensembl
Mustela putorius furo genes (MusPutFur1.0)
MusPutFur1.0
2015-03-03 14:19:55
olatipes_gene_ensembl
Oryzias latipes genes (HdrR)
HdrR
2015-03-03 14:20:59
ogarnettii_gene_ensembl
Otolemur garnettii genes (OtoGar3)
OtoGar3
2015-03-03 14:20:37
psinensis_gene_ensembl
Pelodiscus sinensis genes (PelSin_1.0)
PelSin_1.0
2015-03-03 14:20:58
xtropicalis_gene_ensembl
Xenopus tropicalis genes (JGI4.2)
JGI4.2
2015-03-03 14:21:26
pmarinus_gene_ensembl
Petromyzon marinus genes (Pmarinus_7.0)
Pmarinus_7.0
2015-03-03 14:20:02
aplatyrhynchos_gene_ensembl
Anas platyrhynchos genes (BGI_duck_1.0)
BGI_duck_1.0
2015-03-03 14:19:59
csavignyi_gene_ensembl
Ciona savignyi genes (CSAV2.0)
CSAV2.0
2015-03-03 14:20:15
panubis_gene_ensembl
Papio anubis genes (PapAnu2.0)
PapAnu2.0
2015-03-03 14:21:31
oanatinus_gene_ensembl
Ornithorhynchus anatinus genes (OANA5)
OANA5
2015-03-03 14:21:16
xmaculatus_gene_ensembl
Xiphophorus maculatus genes (Xipmac4.4.2)
Xipmac4.4.2
2015-03-03 14:20:24
ecaballus_gene_ensembl
Equus caballus genes (EquCab2)
EquCab2
2015-03-03 14:20:34
ocuniculus_gene_ensembl
Oryctolagus cuniculus genes (OryCun2.0)
OryCun2.0
2015-03-03 14:20:53
cintestinalis_gene_ensembl
Ciona intestinalis genes (KH)
KH
2015-03-03 14:21:34
pcapensis_gene_ensembl
Procavia capensis genes (proCap1)
proCap1
2015-03-03 14:21:24
meugenii_gene_ensembl
Macropus eugenii genes (Meug_1.0)
Meug_1.0
2015-03-03 14:20:19
scerevisiae_gene_ensembl
Saccharomyces cerevisiae genes (R64-1-1)
R64-1-1
2015-03-03 14:21:30
pformosa_gene_ensembl
Poecilia formosa genes (PoeFor_5.1.2)
PoeFor_5.1.2
2015-03-03 14:21:04
oniloticus_gene_ensembl
Oreochromis niloticus genes (Orenil1.0)
Orenil1.0
2015-03-03 14:21:03
saraneus_gene_ensembl
Sorex araneus genes (sorAra1)
sorAra1
2015-03-03 14:21:11
pvampyrus_gene_ensembl
Pteropus vampyrus genes (pteVam1)
pteVam1
2015-03-03 14:20:43
gmorhua_gene_ensembl
Gadus morhua genes (gadMor1)
gadMor1
2015-03-03 14:21:28
oaries_gene_ensembl
Ovis aries genes (Oar_v3.1)
Oar_v3.1
2015-03-03 14:21:05
itridecemlineatus_gene_ensembl
Ictidomys tridecemlineatus genes (spetri2)
spetri2
2015-03-03 14:21:01
cporcellus_gene_ensembl
Cavia porcellus genes (cavPor3)
cavPor3
2015-03-03 14:21:25
drerio_gene_ensembl
Danio rerio genes (Zv9)
Zv9
2015-03-03 14:21:07
tnigroviridis_gene_ensembl
Tetraodon nigroviridis genes (TETRAODON8.0)
TETRAODON8.0
2015-03-03 14:19:56
lafricana_gene_ensembl
Loxodonta africana genes (loxAfr3)
loxAfr3
2015-03-03 14:21:19
etelfairi_gene_ensembl
Echinops telfairi genes (TENREC)
TENREC
2015-03-03 14:20:49
dmelanogaster_gene_ensembl
Drosophila melanogaster genes (BDGP6)
BDGP6
2015-03-03 14:21:14
rnorvegicus_gene_ensembl
Rattus norvegicus genes (Rnor_5.0)
Rnor_5.0
2015-03-03 14:20:56
fcatus_gene_ensembl
Felis catus genes (Felis_catus_6.2)
Felis_catus_6.2
2015-03-03 14:20:27
loculatus_gene_ensembl
Lepisosteus oculatus genes (LepOcu1)
LepOcu1
2015-03-03 14:19:58
eeuropaeus_gene_ensembl
Erinaceus europaeus genes (eriEur1)
eriEur1
2015-03-03 14:21:22
tbelangeri_gene_ensembl
Tupaia belangeri genes (tupBel1)
tupBel1
2015-03-03 14:20:21
cfamiliaris_gene_ensembl
Canis familiaris genes (CanFam3.1)
CanFam3.1
2015-03-03 14:20:40
mdomestica_gene_ensembl
Monodelphis domestica genes (monDom5)
monDom5
2015-03-03 14:20:30
mmusculus_gene_ensembl
Mus musculus genes (GRCm38.p3)
GRCm38.p3
2015-03-03 14:21:33
mmurinus_gene_ensembl
Microcebus murinus genes (micMur1)
micMur1
2015-03-03 14:19:53
choffmanni_gene_ensembl
Choloepus hoffmanni genes (choHof1)
choHof1
2015-03-03 14:20:54
falbicollis_gene_ensembl
Ficedula albicollis genes (FicAlb_1.4)
FicAlb_1.4
2015-03-03 14:20:04
ggorilla_gene_ensembl
Gorilla gorilla genes (gorGor3.1)
gorGor3.1
2015-03-03 14:20:25
mgallopavo_gene_ensembl
Meleagris gallopavo genes (UMD2)
UMD2
2015-03-03 14:20:10
hsapiens_gene_ensembl
Homo sapiens genes (GRCh38.p2)
GRCh38.p2
2015-03-03 14:20:14
lchalumnae_gene_ensembl
Latimeria chalumnae genes (LatCha1)
LatCha1
2015-03-03 14:20:57
csabaeus_gene_ensembl
Chlorocebus sabaeus genes (ChlSab1.1)
ChlSab1.1
2015-03-03 14:20:23
tguttata_gene_ensembl
Taeniopygia guttata genes (taeGut3.2.4)
taeGut3.2.4
2015-03-03 14:21:17
pabelii_gene_ensembl
Pongo abelii genes (PPYG2)
PPYG2
2015-03-03 14:20:32
ptroglodytes_gene_ensembl
Pan troglodytes genes (CHIMP2.1.4)
CHIMP2.1.4
2015-03-03 14:19:54
trubripes_gene_ensembl
Takifugu rubripes genes (FUGU4.0)
FUGU4.0
2015-03-03 14:20:45
sharrisii_gene_ensembl
Sarcophilus harrisii genes (DEVIL7.0)
DEVIL7.0
2015-03-03 14:20:38
oprinceps_gene_ensembl
Ochotona princeps genes (OchPri2.0)
OchPri2.0
2015-03-03 14:20:08
mmulatta_gene_ensembl
Macaca mulatta genes (MMUL_1)
MMUL_1
2015-03-03 14:20:01
btaurus_gene_ensembl
Bos taurus genes (UMD3.1)
UMD3.1
2015-03-03 14:20:42
celegans_gene_ensembl
Caenorhabditis elegans genes (WBcel235)
WBcel235
2015-03-03 14:20:07
dordii_gene_ensembl
Dipodomys ordii genes (dipOrd1)
dipOrd1
2015-03-03 14:21:20
ttruncatus_gene_ensembl
Tursiops truncatus genes (turTru1)
turTru1
2015-03-03 14:20:05

5.3 Attributes for “ensembl” and “hsapiens_gene_ensembl”
	Most of the following attributes can be used as filters as well (not anything organism specific other than H. sapiens).

ensembl_gene_id
Ensembl Gene ID
ensembl_transcript_id
Ensembl Transcript ID
ensembl_peptide_id
Ensembl Protein ID
ensembl_exon_id
Ensembl Exon ID
description
Description
chromosome_name
Chromosome Name
start_position
Gene Start (bp)
end_position
Gene End (bp)
strand
Strand
band
Band
transcript_start
Transcript Start (bp)
transcript_end
Transcript End (bp)
transcription_start_site
Transcription Start Site (TSS)
transcript_length
Transcript length
transcript_tsl
Transcript Support Level (TSL)
transcript_gencode_basic
GENCODE basic annotation
transcript_appris_pi
APPRIS principal isoform annotation
external_gene_name
Associated Gene Name
external_gene_source
Associated Gene Source
external_transcript_name
Associated Transcript Name
external_transcript_source_name
Associated Transcript Source
transcript_count
Transcript count
percentage_gc_content
% GC content
gene_biotype
Gene type
transcript_biotype
Transcript type
source
Source (gene)
transcript_source
Source (transcript)
status
Status (gene)
transcript_status
Status (transcript)
version
Version (gene)
transcript_version
Version (transcript)
phenotype_description
Phenotype description
source_name
Source name
study_external_id
Study External Reference
go_id
GO Term Accession
name_1006
GO Term Name
definition_1006
GO Term Definition
go_linkage_type
GO Term Evidence Code
namespace_1003
GO domain
goslim_goa_accession
GOSlim GOA Accession(s)
goslim_goa_description
GOSlim GOA Description
arrayexpress
ArrayExpress
chembl
ChEMBL ID(s)
clone_based_ensembl_gene_name
Clone based Ensembl gene name
clone_based_ensembl_transcript_name
Clone based Ensembl transcript name
clone_based_vega_gene_name
Clone based VEGA gene name
clone_based_vega_transcript_name
Clone based VEGA transcript name
ccds
CCDS ID
dbass3_id
Database of Aberrant 3' Splice Sites (DBASS3) IDs
dbass3_name
DBASS3 Gene Name
dbass5_id
Database of Aberrant 5' Splice Sites (DBASS5) IDs
dbass5_name
DBASS5 Gene Name
embl
EMBL (Genbank) ID
ens_hs_gene
Ensembl Human Gene IDs
ens_hs_transcript
Ensembl Human Transcript IDs
ens_hs_translation
Ensembl Human Translation IDs
ens_lrg_gene
LRG to Ensembl link gene
ens_lrg_transcript
LRG to Ensembl link transcript
entrezgene
EntrezGene ID
entrezgene_transcript_name
EntrezGene transcript name ID
hpa
Human Protein Atlas Antibody ID
ottg
VEGA gene ID(s) (OTTG)
ottt
VEGA transcript ID(s) (OTTT)
ottp
VEGA protein ID(s) (OTTP)
hgnc_id
HGNC ID(s)
hgnc_symbol
HGNC symbol
hgnc_transcript_name
HGNC transcript name
merops
MEROPS ID
pdb
PDB ID
mim_morbid_accession
MIM Morbid Accession
mim_morbid_description
MIM Morbid Description
mim_gene_accession
MIM Gene Accession
mim_gene_description
MIM Gene Description
mirbase_accession
miRBase Accession(s)
mirbase_id
miRBase ID(s)
mirbase_transcript_name
miRBase transcript name
protein_id
Protein (Genbank) ID
refseq_mrna
RefSeq mRNA [e.g. NM_001195597]
refseq_mrna_predicted
RefSeq mRNA predicted [e.g. XM_001125684]
refseq_ncrna
RefSeq ncRNA [e.g. NR_002834]
refseq_ncrna_predicted
RefSeq ncRNA predicted [e.g. XR_108264]
refseq_peptide
RefSeq Protein ID [e.g. NP_001005353]
refseq_peptide_predicted
RefSeq Predicted Protein ID [e.g. XP_001720922]
rfam
Rfam ID
rfam_transcript_name
Rfam transcript name
ucsc
UCSC ID
unigene
Unigene ID
uniparc
UniParc
uniprot_sptrembl
UniProt/TrEMBL Accession
uniprot_swissprot
UniProt/SwissProt ID
uniprot_swissprot_accession
UniProt/SwissProt Accession
uniprot_genename
UniProt Gene Name
uniprot_genename_transcript_name
Uniprot Genename Transcript Name
wikigene_name
WikiGene Name
wikigene_id
WikiGene ID
wikigene_description
WikiGene Description
efg_agilent_sureprint_g3_ge_8x60k
Agilent SurePrint G3 GE 8x60k probe
efg_agilent_sureprint_g3_ge_8x60k_v2
Agilent SurePrint G3 GE 8x60k v2 probe
efg_agilent_wholegenome_4x44k_v1
Agilent WholeGenome 4x44k v1 probe
efg_agilent_wholegenome_4x44k_v2
Agilent WholeGenome 4x44k v2 probe
affy_hc_g110
Affy HC G110 probeset
affy_hg_focus
Affy HG FOCUS probeset
affy_hg_u133_plus_2
Affy HG U133-PLUS-2 probeset
affy_hg_u133a_2
Affy HG U133A_2 probeset
affy_hg_u133a
Affy HG U133A probeset
affy_hg_u133b
Affy HG U133B probeset
affy_hg_u95av2
Affy HG U95AV2 probeset
affy_hg_u95b
Affy HG U95B probeset
affy_hg_u95c
Affy HG U95C probeset
affy_hg_u95d
Affy HG U95D probeset
affy_hg_u95e
Affy HG U95E probeset
affy_hg_u95a
Affy HG U95A probeset
affy_hugenefl
Affy HuGene FL probeset
affy_hta_2_0
Affy HTA-2_0 probeset
affy_huex_1_0_st_v2
Affy HuEx 1_0 st v2 probeset
affy_hugene_1_0_st_v1
Affy HuGene 1_0 st v1 probeset
affy_hugene_2_0_st_v1
Affy HuGene 2_0 st v1 probeset
affy_primeview
Affy primeview
affy_u133_x3p
Affy U133 X3P probeset
agilent_cgh_44b
Agilent CGH 44b probe
codelink
Codelink probe
illumina_humanwg_6_v1
Illumina HumanWG 6 v1 probe
illumina_humanwg_6_v2
Illumina HumanWG 6 v2 probe
illumina_humanwg_6_v3
Illumina HumanWG 6 v3 probe
illumina_humanht_12_v3
Illumina Human HT 12 V3 probe 
illumina_humanht_12_v4
Illumina Human HT 12 V4 probe 
illumina_humanref_8_v3
Illumina Human Ref 8 V3 probe
phalanx_onearray
Phalanx OneArray probe
family
Ensembl Protein Family ID(s)
family_description
Ensembl Family Description
pirsf
PIRSF SuperFamily ID
superfamily
Superfamily ID
smart
SMART ID
profile
PROFILE ID
prints
PRINTS ID
pfam
PFAM ID
tigrfam
TIGRFam ID
interpro
Interpro ID
interpro_short_description
Interpro Short Description
interpro_description
Interpro Description
low_complexity
Low complexity
transmembrane_domain
Transmembrane domain
signal_domain
Signal domain
ncoils
Ncoils
ensembl_gene_id
Ensembl Gene ID
ensembl_transcript_id
Ensembl Transcript ID
ensembl_peptide_id
Ensembl Protein ID
chromosome_name
Chromosome Name
start_position
Gene Start (bp)
end_position
Gene End (bp)
transcript_start
Transcript Start (bp)
transcript_end
Transcript End (bp)
transcription_start_site
Transcription Start Site (TSS)
transcript_length
Transcript length
strand
Strand
external_gene_name
Associated Gene Name
external_gene_source
Associated Gene Source
5_utr_start
5' UTR Start
5_utr_end
5' UTR End
3_utr_start
3' UTR Start
3_utr_end
3' UTR End
cds_length
CDS Length
transcript_count
Transcript count
description
Description
gene_biotype
Gene type
exon_chrom_start
Exon Chr Start (bp)
exon_chrom_end
Exon Chr End (bp)
is_constitutive
Constitutive Exon
rank
Exon Rank in Transcript
phase
phase
cdna_coding_start
cDNA coding start
cdna_coding_end
cDNA coding end
genomic_coding_start
Genomic coding start
genomic_coding_end
Genomic coding end
ensembl_exon_id
Ensembl Exon ID
cds_start
CDS Start
cds_end
CDS End
ensembl_gene_id
Ensembl Gene ID
ensembl_transcript_id
Ensembl Transcript ID
ensembl_peptide_id
Ensembl Protein ID
chromosome_name
Chromosome Name
start_position
Gene Start (bp)
end_position
Gene End (bp)
strand
Strand
band
Band
external_gene_name
Associated Gene Name
external_gene_source
Associated Gene Source
transcript_count
Transcript count
percentage_gc_content
% GC content
description
Description
vpacos_homolog_ensembl_gene
Alpaca Ensembl Gene ID
vpacos_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
vpacos_homolog_ensembl_peptide
Alpaca Ensembl Protein ID
vpacos_homolog_chromosome
Alpaca Chromosome Name
vpacos_homolog_chrom_start
Alpaca Chromosome Start (bp)
vpacos_homolog_chrom_end
Alpaca Chromosome End (bp)
vpacos_homolog_orthology_type
Homology Type
vpacos_homolog_subtype
Ancestor
vpacos_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
vpacos_homolog_perc_id
% Identity with respect to query gene
vpacos_homolog_perc_id_r1
% Identity with respect to Alpaca gene
pformosa_homolog_ensembl_gene
Amazon molly Ensembl Gene ID
pformosa_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
pformosa_homolog_ensembl_peptide
Amazon molly Ensembl Protein ID
pformosa_homolog_chromosome
Amazon molly Chromosome Name
pformosa_homolog_chrom_start
Amazon molly Chromosome Start (bp)
pformosa_homolog_chrom_end
Amazon molly Chromosome End (bp)
pformosa_homolog_orthology_type
Homology Type
pformosa_homolog_subtype
Ancestor
pformosa_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
pformosa_homolog_perc_id
% Identity with respect to query gene
pformosa_homolog_perc_id_r1
% Identity with respect to Amazon molly gene
acarolinensis_homolog_ensembl_gene
Anole Lizard Ensembl Gene ID
acarolinensis_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
acarolinensis_homolog_ensembl_peptide
Anole Lizard Ensembl Protein ID
acarolinensis_homolog_chromosome
Anole Lizard Chromosome Name
acarolinensis_homolog_chrom_start
Anole Lizard Chromosome Start (bp)
acarolinensis_homolog_chrom_end
Anole Lizard Chromosome End (bp)
acarolinensis_homolog_orthology_type
Homology Type
acarolinensis_homolog_subtype
Ancestor
acarolinensis_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
acarolinensis_homolog_perc_id
% Identity with respect to query gene
acarolinensis_homolog_perc_id_r1
% Identity with respect to Anole Lizard gene
acarolinensis_homolog_dn
dN
acarolinensis_homolog_ds
dS
dnovemcinctus_homolog_ensembl_gene
Armadillo Ensembl Gene ID
dnovemcinctus_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
dnovemcinctus_homolog_ensembl_peptide
Armadillo Ensembl Protein ID
dnovemcinctus_homolog_chromosome
Armadillo Chromosome Name
dnovemcinctus_homolog_chrom_start
Armadillo Chromosome Start (bp)
dnovemcinctus_homolog_chrom_end
Armadillo Chromosome End (bp)
dnovemcinctus_homolog_orthology_type
Homology Type
dnovemcinctus_homolog_subtype
Ancestor
dnovemcinctus_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
dnovemcinctus_homolog_perc_id
% Identity with respect to query gene
dnovemcinctus_homolog_perc_id_r1
% Identity with respect to Armadillo gene
dnovemcinctus_homolog_dn
dN
dnovemcinctus_homolog_ds
dS
gmorhua_homolog_ensembl_gene
Atlantic Cod Ensembl Gene ID
gmorhua_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
gmorhua_homolog_ensembl_protein
Atlantic Cod Ensembl Protein ID
gmorhua_homolog_chromosome
Atlantic Cod Chromosome Name
gmorhua_homolog_chrom_start
Atlantic Cod Chromosome Start (bp)
gmorhua_homolog_chrom_end
Atlantic Cod Chromosome End (bp)
gmorhua_homolog_orthology_type
Homology Type
gmorhua_homolog_subtype
Ancestor
gmorhua_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
gmorhua_homolog_perc_id
% Identity with respect to query gene
gmorhua_homolog_perc_id_r1
% Identity with respect to Atlantic Cod gene
ogarnettii_homolog_ensembl_gene
Bushbaby Ensembl Gene ID
ogarnettii_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
ogarnettii_homolog_ensembl_peptide
Bushbaby Ensembl Protein ID
ogarnettii_homolog_chromosome
Bushbaby Chromosome Name
ogarnettii_homolog_chrom_start
Bushbaby Chromosome Start (bp)
ogarnettii_homolog_chrom_end
Bushbaby Chromosome End (bp)
ogarnettii_homolog_orthology_type
Homology Type
ogarnettii_homolog_subtype
Ancestor
ogarnettii_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
ogarnettii_homolog_perc_id
% Identity with respect to query gene
ogarnettii_homolog_perc_id_r1
% Identity with respect to Bushbaby gene
ogarnettii_homolog_dn
dN
ogarnettii_homolog_ds
dS
celegans_homolog_chrom_start
Caenorhabditis elegans Chromosome Start (bp)
celegans_homolog_ensembl_gene
Caenorhabditis elegans Ensembl Gene ID
celegans_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
celegans_homolog_ensembl_peptide
Caenorhabditis elegans Ensembl Protein ID
celegans_homolog_chromosome
Caenorhabditis elegans Chromosome Name
celegans_homolog_chrom_end
Caenorhabditis elegans Chromosome End (bp)
celegans_homolog_orthology_type
Homology Type
celegans_homolog_subtype
Ancestor
celegans_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
celegans_homolog_perc_id
% Identity with respect to query gene
celegans_homolog_perc_id_r1
% Identity with respect to Caenorhabditis elegans gene
celegans_homolog_dn
dN
celegans_homolog_ds
dS
fcatus_homolog_ensembl_gene
Cat Ensembl Gene ID
fcatus_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
fcatus_homolog_ensembl_peptide
Cat Ensembl Protein ID
fcatus_homolog_chromosome
Cat Chromosome Name
fcatus_homolog_chrom_start
Cat Chromosome Start (bp)
fcatus_homolog_chrom_end
Cat Chromosome End (bp)
fcatus_homolog_orthology_type
Homology Type
fcatus_homolog_subtype
Ancestor
fcatus_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
fcatus_homolog_perc_id
% Identity with respect to query gene
fcatus_homolog_perc_id_r1
% Identity with respect to Cat gene
fcatus_homolog_dn
dN
fcatus_homolog_ds
dS
amexicanus_homolog_ensembl_gene
Cave fish Ensembl Gene ID
amexicanus_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
amexicanus_homolog_ensembl_peptide
Cave fish Ensembl Protein ID
amexicanus_homolog_chromosome
Cave fish Chromosome Name
amexicanus_homolog_chrom_start
Cave fish Chromosome Start (bp)
amexicanus_homolog_chrom_end
Cave fish Chromosome End (bp)
amexicanus_homolog_orthology_type
Homology Type
amexicanus_homolog_subtype
Ancestor
amexicanus_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
amexicanus_homolog_perc_id
% Identity with respect to query gene
amexicanus_homolog_perc_id_r1
% Identity with respect to Cave fish gene
ggallus_homolog_ensembl_gene
Chicken Ensembl Gene ID
ggallus_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
ggallus_homolog_ensembl_peptide
Chicken Ensembl Protein ID
ggallus_homolog_chromosome
Chicken Chromosome Name
ggallus_homolog_chrom_start
Chicken Chromosome Start (bp)
ggallus_homolog_chrom_end
Chicken Chromosome End (bp)
ggallus_homolog_orthology_type
Homology Type
ggallus_homolog_subtype
Ancestor
ggallus_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
ggallus_homolog_perc_id
% Identity with respect to query gene
ggallus_homolog_perc_id_r1
% Identity with respect to Chicken gene
ggallus_homolog_dn
dN
ggallus_homolog_ds
dS
ptroglodytes_homolog_ensembl_gene
Chimpanzee Ensembl Gene ID
ptroglodytes_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
ptroglodytes_homolog_ensembl_peptide
Chimpanzee Ensembl Protein ID
ptroglodytes_homolog_chromosome
Chimpanzee Chromosome Name
ptroglodytes_homolog_chrom_start
Chimpanzee Chromosome Start (bp)
ptroglodytes_homolog_chrom_end
Chimpanzee Chromosome End (bp)
ptroglodytes_homolog_orthology_type
Homology Type
ptroglodytes_homolog_subtype
Ancestor
ptroglodytes_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
ptroglodytes_homolog_perc_id
% Identity with respect to query gene
ptroglodytes_homolog_perc_id_r1
% Identity with respect to Chimpanzee gene
ptroglodytes_homolog_dn
dN
ptroglodytes_homolog_ds
dS
psinensis_homolog_ensembl_gene
Chinese softshell turtle Ensembl Gene ID
psinensis_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
psinensis_homolog_ensembl_peptide
Chinese softshell turtle Ensembl Protein ID
psinensis_homolog_chromosome
Chinese softshell turtle Chromosome Name
psinensis_homolog_chrom_start
Chinese softshell turtle Chromosome Start (bp)
psinensis_homolog_chrom_end
Chinese softshell turtle Chromosome End (bp)
psinensis_homolog_orthology_type
Homology Type
psinensis_homolog_subtype
Ancestor
psinensis_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
psinensis_homolog_perc_id
% Identity with respect to query gene
psinensis_homolog_perc_id_r1
% Identity with respect to Chinese softshell turtle gene
psinensis_homolog_dn
dN
psinensis_homolog_ds
dS
cintestinalis_homolog_ensembl_gene
Ciona intestinalis Ensembl Gene ID
cintestinalis_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
cintestinalis_homolog_ensembl_peptide
Ciona intestinalis Ensembl Protein ID
cintestinalis_homolog_chromosome
Ciona intestinalis Chromosome Name
cintestinalis_homolog_chrom_start
Ciona intestinalis Chromosome Start (bp)
cintestinalis_homolog_chrom_end
Ciona intestinalis Chromosome End (bp)
cintestinalis_homolog_orthology_type
Homology Type
cintestinalis_homolog_subtype
Ancestor
cintestinalis_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
cintestinalis_homolog_perc_id
% Identity with respect to query gene
cintestinalis_homolog_perc_id_r1
% Identity with respect to Ciona intestinalis gene
cintestinalis_homolog_dn
dN
cintestinalis_homolog_ds
dS
csavignyi_homolog_ensembl_gene
Ciona savignyi Ensembl Gene ID
csavignyi_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
csavignyi_homolog_ensembl_peptide
Ciona savignyi Ensembl Protein ID
csavignyi_homolog_chromosome
Ciona savignyi Chromosome Name
csavignyi_homolog_chrom_start
Ciona savignyi Chromosome Start (bp)
csavignyi_homolog_chrom_end
Ciona savignyi Chromosome End (bp)
csavignyi_homolog_orthology_type
Homology Type
csavignyi_homolog_subtype
Ancestor
csavignyi_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
csavignyi_homolog_perc_id
% Identity with respect to query gene
csavignyi_homolog_perc_id_r1
% Identity with respect to Ciona savignyi gene
csavignyi_homolog_dn
dN
csavignyi_homolog_ds
dS
lchalumnae_homolog_ensembl_gene
Coelacanth Ensembl Gene ID
lchalumnae_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
lchalumnae_homolog_ensembl_peptide
Coelacanth Ensembl Protein ID
lchalumnae_homolog_chromosome
Coelacanth Chromosome Name
lchalumnae_homolog_chrom_start
Coelacanth Chromosome Start (bp)
lchalumnae_homolog_chrom_end
Coelacanth Chromosome End (bp)
lchalumnae_homolog_orthology_type
Homology Type
lchalumnae_homolog_subtype
Ancestor
lchalumnae_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
lchalumnae_homolog_perc_id
% Identity with respect to query gene
lchalumnae_homolog_perc_id_r1
% Identity with respect to Coelacanth gene
saraneus_homolog_ensembl_gene
Common Shrew Ensembl Gene ID
saraneus_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
saraneus_homolog_ensembl_peptide
Common Shrew Ensembl Protein ID
saraneus_homolog_chromosome
Common Shrew Chromosome Name
saraneus_homolog_chrom_start
Common Shrew Chromosome Start (bp)
saraneus_homolog_chrom_end
Common Shrew Chromosome End (bp)
saraneus_homolog_orthology_type
Homology Type
saraneus_homolog_subtype
Ancestor
saraneus_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
saraneus_homolog_perc_id
% Identity with respect to query gene
saraneus_homolog_perc_id_r1
% Identity with respect to Common Shrew gene
btaurus_homolog_ensembl_gene
Cow Ensembl Gene ID
btaurus_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
btaurus_homolog_ensembl_peptide
Cow Ensembl Protein ID
btaurus_homolog_chromosome
Cow Chromosome Name
btaurus_homolog_chrom_start
Cow Chromosome Start (bp)
btaurus_homolog_chrom_end
Cow Chromosome End (bp)
btaurus_homolog_orthology_type
Homology Type
btaurus_homolog_subtype
Ancestor
btaurus_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
btaurus_homolog_perc_id
% Identity with respect to query gene
btaurus_homolog_perc_id_r1
% Identity with respect to Cow gene
btaurus_homolog_dn
dN
btaurus_homolog_ds
dS
cfamiliaris_homolog_ensembl_gene
Dog Ensembl Gene ID
cfamiliaris_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
cfamiliaris_homolog_ensembl_peptide
Dog Ensembl Protein ID
cfamiliaris_homolog_chromosome
Dog Chromosome Name
cfamiliaris_homolog_chrom_start
Dog Chromosome Start (bp)
cfamiliaris_homolog_chrom_end
Dog Chromosome End (bp)
cfamiliaris_homolog_orthology_type
Homology Type
cfamiliaris_homolog_subtype
Ancestor
cfamiliaris_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
cfamiliaris_homolog_perc_id
% Identity with respect to query gene
cfamiliaris_homolog_perc_id_r1
% Identity with respect to Dog gene
cfamiliaris_homolog_dn
dN
cfamiliaris_homolog_ds
dS
ttruncatus_homolog_ensembl_gene
Dolphin Ensembl Gene ID
ttruncatus_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
ttruncatus_homolog_ensembl_peptide
Dolphin Ensembl Protein ID
ttruncatus_homolog_chromosome
Dolphin Chromosome Name
ttruncatus_homolog_chrom_start
Dolphin Chromosome Start (bp)
ttruncatus_homolog_chrom_end
Dolphin Chromosome End (bp)
ttruncatus_homolog_orthology_type
Homology Type
ttruncatus_homolog_subtype
Ancestor
ttruncatus_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
ttruncatus_homolog_perc_id
% Identity with respect to query gene
ttruncatus_homolog_perc_id_r1
% Identity with respect to Dolphin gene
dmelanogaster_homolog_ensembl_gene
Drosophila Ensembl Gene ID
dmelanogaster_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
dmelanogaster_homolog_ensembl_peptide
Drosophila Ensembl Protein ID
dmelanogaster_homolog_chromosome
Drosophila Chromosome Name
dmelanogaster_homolog_chrom_start
Drosophila Chromosome Start (bp)
dmelanogaster_homolog_chrom_end
Drosophila Chromosome End (bp)
dmelanogaster_homolog_orthology_type
Homology Type
dmelanogaster_homolog_subtype
Ancestor
dmelanogaster_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
dmelanogaster_homolog_perc_id
% Identity with respect to query gene
dmelanogaster_homolog_perc_id_r1
% Identity with respect to Drosophila gene
dmelanogaster_homolog_dn
dN
dmelanogaster_homolog_ds
dS
aplatyrhynchos_homolog_ensembl_gene
Duck Ensembl Gene ID
aplatyrhynchos_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
aplatyrhynchos_homolog_ensembl_peptide
Duck Ensembl Protein ID
aplatyrhynchos_homolog_chromosome
Duck Chromosome Name
aplatyrhynchos_homolog_chrom_start
Duck Chromosome Start (bp)
aplatyrhynchos_homolog_chrom_end
Duck Chromosome End (bp)
aplatyrhynchos_homolog_orthology_type
Homology Type
aplatyrhynchos_homolog_subtype
Ancestor
aplatyrhynchos_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
aplatyrhynchos_homolog_perc_id
% Identity with respect to query gene
aplatyrhynchos_homolog_perc_id_r1
% Identity with respect to Duck gene
aplatyrhynchos_homolog_dn
dN
aplatyrhynchos_homolog_ds
dS
lafricana_homolog_ensembl_gene
Elephant Ensembl Gene ID
lafricana_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
lafricana_homolog_ensembl_peptide
Elephant Ensembl Protein ID
lafricana_homolog_chromosome
Elephant Chromosome Name
lafricana_homolog_chrom_start
Elephant Chromosome Start (bp)
lafricana_homolog_chrom_end
Elephant Chromosome End (bp)
lafricana_homolog_orthology_type
Homology Type
lafricana_homolog_subtype
Ancestor
lafricana_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
lafricana_homolog_perc_id
% Identity with respect to query gene
lafricana_homolog_perc_id_r1
% Identity with respect to Elephant gene
lafricana_homolog_dn
dN
lafricana_homolog_ds
dS
mfuro_homolog_ensembl_gene
Ferret Ensembl Gene ID
mfuro_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
mfuro_homolog_ensembl_peptide
Ferret Ensembl Protein ID
mfuro_homolog_chromosome
Ferret Chromosome Name
mfuro_homolog_chrom_start
Ferret Chromosome Start (bp)
mfuro_homolog_chrom_end
Ferret Chromosome End (bp)
mfuro_homolog_orthology_type
Homology Type
mfuro_homolog_subtype
Ancestor
mfuro_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
mfuro_homolog_perc_id
% Identity with respect to query gene
mfuro_homolog_perc_id_r1
% Identity with respect to Ferret gene
mfuro_homolog_dn
dN
mfuro_homolog_ds
dS
falbicollis_homolog_ensembl_gene
Flycatcher Ensembl Gene ID
falbicollis_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
falbicollis_homolog_ensembl_peptide
Flycatcher Ensembl Protein ID
falbicollis_homolog_chromosome
Flycatcher Chromosome Name
falbicollis_homolog_chrom_start
Flycatcher Chromosome Start (bp)
falbicollis_homolog_chrom_end
Flycatcher Chromosome End (bp)
falbicollis_homolog_orthology_type
Homology Type
falbicollis_homolog_subtype
Ancestor
falbicollis_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
falbicollis_homolog_perc_id
% Identity with respect to query gene
falbicollis_homolog_perc_id_r1
% Identity with respect to Flycatcher gene
falbicollis_homolog_dn
dN
falbicollis_homolog_ds
dS
trubripes_homolog_ensembl_gene
Fugu Ensembl Gene ID
trubripes_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
trubripes_homolog_ensembl_peptide
Fugu Ensembl Protein ID
trubripes_homolog_chromosome
Fugu Chromosome Name
trubripes_homolog_chrom_start
Fugu Chromosome Start (bp)
trubripes_homolog_chrom_end
Fugu Chromosome End (bp)
trubripes_homolog_orthology_type
Homology Type
trubripes_homolog_subtype
Ancestor
trubripes_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
trubripes_homolog_perc_id
% Identity with respect to query gene
trubripes_homolog_perc_id_r1
% Identity with respect to Fugu gene
trubripes_homolog_dn
dN
trubripes_homolog_ds
dS
nleucogenys_homolog_ensembl_gene
Gibbon Ensembl Gene ID
nleucogenys_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
nleucogenys_homolog_ensembl_peptide
Gibbon Ensembl Protein ID
nleucogenys_homolog_chromosome
Gibbon Chromosome Name
nleucogenys_homolog_chrom_start
Gibbon Chromosome Start (bp)
nleucogenys_homolog_chrom_end
Gibbon Chromosome End (bp)
nleucogenys_homolog_orthology_type
Homology Type
nleucogenys_homolog_subtype
Ancestor
nleucogenys_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
nleucogenys_homolog_perc_id
% Identity with respect to query gene
nleucogenys_homolog_perc_id_r1
% Identity with respect to Gibbon gene
nleucogenys_homolog_dn
dN
nleucogenys_homolog_ds
dS
ggorilla_homolog_ensembl_gene
Gorilla Ensembl Gene ID
ggorilla_homolog_canomical_transcript_protein
Canonical Protein or Transcript ID
ggorilla_homolog_ensembl_peptide
Gorilla Ensembl Protein ID
ggorilla_homolog_chromosome
Gorilla Chromosome Name
ggorilla_homolog_chrom_start
Gorilla Chromosome Start (bp)
ggorilla_homolog_chrom_end
Gorilla Chromosome End (bp)
ggorilla_homolog_orthology_type
Homology Type
ggorilla_homolog_subtype
Ancestor
ggorilla_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
ggorilla_homolog_perc_id
% Identity with respect to query gene
ggorilla_homolog_perc_id_r1
% Identity with respect to Gorilla gene
ggorilla_homolog_dn
dN
ggorilla_homolog_ds
dS
cporcellus_homolog_ensembl_gene
Guinea Pig Ensembl Gene ID
cporcellus_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
cporcellus_homolog_ensembl_peptide
Guinea Pig Ensembl Protein ID
cporcellus_homolog_chromosome
Guinea Pig Chromosome Name
cporcellus_homolog_chrom_start
Guinea Pig Chromosome Start (bp)
cporcellus_homolog_chrom_end
Guinea Pig Chromosome End (bp)
cporcellus_homolog_orthology_type
Homology Type
cporcellus_homolog_subtype
Ancestor
cporcellus_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
cporcellus_homolog_perc_id
% Identity with respect to query gene
cporcellus_homolog_perc_id_r1
% Identity with respect to Guinea Pig gene
cporcellus_homolog_dn
dN
cporcellus_homolog_ds
dS
eeuropaeus_homolog_ensembl_gene
Hedgehog Ensembl Gene ID
eeuropaeus_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
eeuropaeus_homolog_ensembl_peptide
Hedgehog Ensembl Protein ID
eeuropaeus_homolog_chromosome
Hedgehog Chromosome Name
eeuropaeus_homolog_chrom_start
Hedgehog Chromosome Start (bp)
eeuropaeus_homolog_chrom_end
Hedgehog Chromosome End (bp)
eeuropaeus_homolog_orthology_type
Homology Type
eeuropaeus_homolog_subtype
Ancestor
eeuropaeus_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
eeuropaeus_homolog_perc_id
% Identity with respect to query gene
eeuropaeus_homolog_perc_id_r1
% Identity with respect to Hedgehog gene
ecaballus_homolog_ensembl_gene
Horse Ensembl Gene ID
ecaballus_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
ecaballus_homolog_ensembl_peptide
Horse Ensembl Protein ID
ecaballus_homolog_chromosome
Horse Chromosome Name
ecaballus_homolog_chrom_start
Horse Chromosome Start (bp)
ecaballus_homolog_chrom_end
Horse Chromosome End (bp)
ecaballus_homolog_orthology_type
Homology Type
ecaballus_homolog_subtype
Ancestor
ecaballus_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
ecaballus_homolog_perc_id
% Identity with respect to query gene
ecaballus_homolog_perc_id_r1
% Identity with respect to Horse gene
ecaballus_homolog_dn
dN
ecaballus_homolog_ds
dS
dordii_homolog_ensembl_gene
Kangaroo Rat Ensembl Gene ID
dordii_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
dordii_homolog_ensembl_peptide
Kangaroo Rat Ensembl Protein ID
dordii_homolog_chromosome
Kangaroo Rat Chromosome Name
dordii_homolog_chrom_start
Kangaroo Rat Chromosome Start (bp)
dordii_homolog_chrom_end
Kangaroo Rat Chromosome End (bp)
dordii_homolog_orthology_type
Homology Type
dordii_homolog_subtype
Ancestor
dordii_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
dordii_homolog_perc_id
% Identity with respect to query gene
dordii_homolog_perc_id_r1
% Identity with respect to Kangaroo Rat gene
pmarinus_homolog_ensembl_gene
Lamprey Ensembl Gene ID
pmarinus_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
pmarinus_homolog_ensembl_peptide
Lamprey Ensembl Protein ID
pmarinus_homolog_chromosome
Lamprey Chromosome Name
pmarinus_homolog_chrom_start
Lamprey Chromosome Start (bp)
pmarinus_homolog_chrom_end
Lamprey Chromosome End (bp)
pmarinus_homolog_orthology_type
Homology Type
pmarinus_homolog_subtype
Ancestor
pmarinus_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
pmarinus_homolog_perc_id
% Identity with respect to query gene
pmarinus_homolog_perc_id_r1
% Identity with respect to Lamprey gene
etelfairi_homolog_ensembl_gene
Lesser hedgehog tenrec Ensembl Gene ID
etelfairi_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
etelfairi_homolog_ensembl_peptide
Lesser hedgehog tenrec Ensembl Protein ID
etelfairi_homolog_chromosome
Lesser hedgehog tenrec Chromosome Name
etelfairi_homolog_chrom_start
Lesser hedgehog tenrec Chromosome Start (bp)
etelfairi_homolog_chrom_end
Lesser hedgehog tenrec Chromosome End (bp)
etelfairi_homolog_orthology_type
Homology Type
etelfairi_homolog_subtype
Ancestor
etelfairi_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
etelfairi_homolog_perc_id
% Identity with respect to query gene
etelfairi_homolog_perc_id_r1
% Identity with respect to Lesser hedgehog tenrec gene
mmulatta_homolog_ensembl_gene
Macaque Ensembl Gene ID
mmulatta_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
mmulatta_homolog_ensembl_peptide
Macaque Ensembl Protein ID
mmulatta_homolog_chromosome
Macaque Chromosome Name
mmulatta_homolog_chrom_start
Macaque Chromosome Start (bp)
mmulatta_homolog_chrom_end
Macaque Chromosome End (bp)
mmulatta_homolog_orthology_type
Homology Type
mmulatta_homolog_subtype
Ancestor
mmulatta_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
mmulatta_homolog_perc_id
% Identity with respect to query gene
mmulatta_homolog_perc_id_r1
% Identity with respect to Macaque gene
mmulatta_homolog_dn
dN
mmulatta_homolog_ds
dS
cjacchus_homolog_ensembl_gene
Marmoset Ensembl Gene ID
cjacchus_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
cjacchus_homolog_ensembl_peptide
Marmoset Ensembl Protein ID
cjacchus_homolog_chromosome
Marmoset Chromosome Name
cjacchus_homolog_chrom_start
Marmoset Chromosome Start (bp)
cjacchus_homolog_chrom_end
Marmoset Chromosome End (bp)
cjacchus_homolog_orthology_type
Homology Type
cjacchus_homolog_subtype
Ancestor
cjacchus_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
cjacchus_homolog_perc_id
% Identity with respect to query gene
cjacchus_homolog_perc_id_r1
% Identity with respect to Marmoset gene
cjacchus_homolog_dn
dN
cjacchus_homolog_ds
dS
olatipes_homolog_ensembl_gene
Medaka Ensembl Gene ID
olatipes_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
olatipes_homolog_ensembl_peptide
Medaka Ensembl Protein ID
olatipes_homolog_chromosome
Medaka Chromosome Name
olatipes_homolog_chrom_start
Medaka Chromosome Start (bp)
olatipes_homolog_chrom_end
Medaka Chromosome End (bp)
olatipes_homolog_orthology_type
Homology Type
olatipes_homolog_subtype
Ancestor
olatipes_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
olatipes_homolog_perc_id
% Identity with respect to query gene
olatipes_homolog_perc_id_r1
% Identity with respect to Medaka gene
olatipes_homolog_dn
dN
olatipes_homolog_ds
dS
pvampyrus_homolog_ensembl_gene
Megabat Ensembl Gene ID
pvampyrus_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
pvampyrus_homolog_ensembl_peptide
Megabat Ensembl Protein ID
pvampyrus_homolog_chromosome
Megabat Chromosome Name
pvampyrus_homolog_chrom_start
Megabat Chromosome Start (bp)
pvampyrus_homolog_chrom_end
Megabat Chromosome End (bp)
pvampyrus_homolog_orthology_type
Homology Type
pvampyrus_homolog_subtype
Ancestor
pvampyrus_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
pvampyrus_homolog_perc_id
% Identity with respect to query gene
pvampyrus_homolog_perc_id_r1
% Identity with respect to Megabat gene
mlucifugus_homolog_ensembl_gene
Microbat Ensembl Gene ID
mlucifugus_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
mlucifugus_homolog_ensembl_peptide
Microbat Ensembl Protein ID
mlucifugus_homolog_chromosome
Microbat Chromosome Name
mlucifugus_homolog_chrom_start
Microbat Chromosome Start (bp)
mlucifugus_homolog_chrom_end
Microbat Chromosome End (bp)
mlucifugus_homolog_orthology_type
Homology Type
mlucifugus_homolog_subtype
Ancestor
mlucifugus_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
mlucifugus_homolog_perc_id
% Identity with respect to query gene
mlucifugus_homolog_perc_id_r1
% Identity with respect to Microbat gene
mlucifugus_homolog_dn
dN
mlucifugus_homolog_ds
dS
mmusculus_homolog_ensembl_gene
Mouse Ensembl Gene ID
mmusculus_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
mmusculus_homolog_ensembl_peptide
Mouse Ensembl Protein ID
mmusculus_homolog_chromosome
Mouse Chromosome Name
mmusculus_homolog_chrom_start
Mouse Chromosome Start (bp)
mmusculus_homolog_chrom_end
Mouse Chromosome End (bp)
mmusculus_homolog_orthology_type
Homology Type
mmusculus_homolog_subtype
Ancestor
mmusculus_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
mmusculus_homolog_perc_id
% Identity with respect to query gene
mmusculus_homolog_perc_id_r1
% Identity with respect to Mouse gene
mmusculus_homolog_dn
dN
mmusculus_homolog_ds
dS
mmurinus_homolog_ensembl_gene
Mouse Lemur Ensembl Gene ID
mmurinus_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
mmurinus_homolog_ensembl_peptide
Mouse Lemur Ensembl Protein ID
mmurinus_homolog_chromosome
Mouse Lemur Chromosome Name
mmurinus_homolog_chrom_start
Mouse Lemur Chromosome Start (bp)
mmurinus_homolog_chrom_end
Mouse Lemur Chromosome End (bp)
mmurinus_homolog_orthology_type
Homology Type
mmurinus_homolog_subtype
Ancestor
mmurinus_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
mmurinus_homolog_perc_id
% Identity with respect to query gene
mmurinus_homolog_perc_id_r1
% Identity with respect to Mouse Lemur gene
oniloticus_homolog_ensembl_gene
Nile tilapia Ensembl Gene ID
oniloticus_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
oniloticus_homolog_ensembl_peptide
Nile tilapia Ensembl Protein ID
oniloticus_homolog_chromosome
Nile tilapia Chromosome Name
oniloticus_homolog_chrom_start
Nile tilapia Chromosome Start (bp)
oniloticus_homolog_chrom_end
Nile tilapia Chromosome End (bp)
oniloticus_homolog_orthology_type
Homology Type
oniloticus_homolog_subtype
Ancestor
oniloticus_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
oniloticus_homolog_perc_id
% Identity with respect to query gene
oniloticus_homolog_perc_id_r1
% Identity with respect to Nile tilapia gene
panubis_homolog_ensembl_gene
Olive baboon Ensembl Gene ID
panubis_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
panubis_homolog_ensembl_peptide
Olive baboon Ensembl Protein ID
panubis_homolog_chromosome
Olive baboon Chromosome Name
panubis_homolog_chrom_start
Olive baboon Chromosome Start (bp)
panubis_homolog_chrom_end
Olive baboon Chromosome End (bp)
panubis_homolog_orthology_type
Homology Type
panubis_homolog_subtype
Ancestor
panubis_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
panubis_homolog_perc_id
% Identity with respect to query gene
panubis_homolog_perc_id_r1
% Identity with respect to Olive baboon gene
panubis_homolog_dn
dN
panubis_homolog_ds
dS
mdomestica_homolog_ensembl_gene
Opossum Ensembl Gene ID
mdomestica_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
mdomestica_homolog_ensembl_peptide
Opossum Ensembl Protein ID
mdomestica_homolog_chromosome
Opossum Chromosome Name
mdomestica_homolog_chrom_start
Opossum Chromosome Start (bp)
mdomestica_homolog_chrom_end
Opossum Chromosome End (bp)
mdomestica_homolog_orthology_type
Homology Type
mdomestica_homolog_subtype
Ancestor
mdomestica_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
mdomestica_homolog_perc_id
% Identity with respect to query gene
mdomestica_homolog_perc_id_r1
% Identity with respect to Opossum gene
mdomestica_homolog_dn
dN
mdomestica_homolog_ds
dS
pabelii_homolog_ensembl_gene
Orangutan Ensembl Gene ID
pabelii_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
pabelii_homolog_ensembl_peptide
Orangutan Ensembl Protein ID
pabelii_homolog_chromosome
Orangutan Chromosome Name
pabelii_homolog_chrom_start
Orangutan Chromosome Start (bp)
pabelii_homolog_chrom_end
Orangutan Chromosome End (bp)
pabelii_homolog_orthology_type
Homology Type
pabelii_homolog_subtype
Ancestor
pabelii_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
pabelii_homolog_perc_id
% Identity with respect to query gene
pabelii_homolog_perc_id_r1
% Identity with respect to Orangutan gene
pabelii_homolog_dn
dN
pabelii_homolog_ds
dS
amelanoleuca_homolog_ensembl_gene
Panda Ensembl Gene ID
amelanoleuca_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
amelanoleuca_homolog_ensembl_peptide
Panda Ensembl Protein ID
amelanoleuca_homolog_chromosome
Panda Chromosome Name
amelanoleuca_homolog_chrom_start
Panda Chromosome Start (bp)
amelanoleuca_homolog_chrom_end
Panda Chromosome End (bp)
amelanoleuca_homolog_orthology_type
Homology Type
amelanoleuca_homolog_subtype
Ancestor
amelanoleuca_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
amelanoleuca_homolog_perc_id
% Identity with respect to query gene
amelanoleuca_homolog_perc_id_r1
% Identity with respect to Panda gene
amelanoleuca_homolog_dn
dN
amelanoleuca_homolog_ds
dS
sscrofa_homolog_ensembl_gene
Pig Ensembl Gene ID
sscrofa_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
sscrofa_homolog_ensembl_peptide
Pig Ensembl Protein ID
sscrofa_homolog_chromosome
Pig Chromosome Name
sscrofa_homolog_chrom_start
Pig Chromosome Start (bp)
sscrofa_homolog_chrom_end
Pig Chromosome End (bp)
sscrofa_homolog_orthology_type
Homology Type
sscrofa_homolog_subtype
Ancestor
sscrofa_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
sscrofa_homolog_perc_id
% Identity with respect to query gene
sscrofa_homolog_perc_id_r1
% Identity with respect to Pig gene
sscrofa_homolog_dn
dN
sscrofa_homolog_ds
dS
oprinceps_homolog_ensembl_gene
Pika Ensembl Gene ID
oprinceps_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
oprinceps_homolog_ensembl_peptide
Pika Ensembl Protein ID
oprinceps_homolog_chromosome
Pika Chromosome Name
oprinceps_homolog_chrom_start
Pika Chromosome Start (bp)
oprinceps_homolog_chrom_end
Pika Chromosome End (bp)
oprinceps_homolog_orthology_type
Homology Type
oprinceps_homolog_subtype
Ancestor
oprinceps_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
oprinceps_homolog_perc_id
% Identity with respect to query gene
oprinceps_homolog_perc_id_r1
% Identity with respect to Pika gene
xmaculatus_homolog_ensembl_gene
Platyfish Ensembl Gene ID
xmaculatus_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
xmaculatus_homolog_ensembl_peptide
Platyfish Ensembl Protein ID
xmaculatus_homolog_chromosome
Platyfish Chromosome Name
xmaculatus_homolog_chrom_start
Platyfish Chromosome Start (bp)
xmaculatus_homolog_chrom_end
Platyfish Chromosome End (bp)
xmaculatus_homolog_orthology_type
Homology Type
xmaculatus_homolog_subtype
Ancestor
xmaculatus_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
xmaculatus_homolog_perc_id
% Identity with respect to query gene
xmaculatus_homolog_perc_id_r1
% Identity with respect to Platyfish gene
oanatinus_homolog_ensembl_gene
Platypus Ensembl Gene ID
oanatinus_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
oanatinus_homolog_ensembl_peptide
Platypus Ensembl Protein ID
oanatinus_homolog_chromosome
Platypus Chromosome Name
oanatinus_homolog_chrom_start
Platypus Chromosome Start (bp)
oanatinus_homolog_chrom_end
Platypus Chromosome End (bp)
oanatinus_homolog_orthology_type
Homology Type
oanatinus_homolog_subtype
Ancestor
oanatinus_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
oanatinus_homolog_perc_id
% Identity with respect to query gene
oanatinus_homolog_perc_id_r1
% Identity with respect to Platypus gene
oanatinus_homolog_dn
dN
oanatinus_homolog_ds
dS
ocuniculus_homolog_ensembl_gene
Rabbit Ensembl Gene ID
ocuniculus_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
ocuniculus_homolog_ensembl_peptide
Rabbit Ensembl Protein ID
ocuniculus_homolog_chromosome
Rabbit Chromosome Name
ocuniculus_homolog_chrom_start
Rabbit Chromosome Start (bp)
ocuniculus_homolog_chrom_end
Rabbit Chromosome End (bp)
ocuniculus_homolog_orthology_type
Homology Type
ocuniculus_homolog_subtype
Ancestor
ocuniculus_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
ocuniculus_homolog_perc_id
% Identity with respect to query gene
ocuniculus_homolog_perc_id_r1
% Identity with respect to Rabbit gene
ocuniculus_homolog_dn
dN
ocuniculus_homolog_ds
dS
rnorvegicus_homolog_ensembl_gene
Rat Ensembl Gene ID
rnorvegicus_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
rnorvegicus_homolog_ensembl_peptide
Rat Ensembl Protein ID
rnorvegicus_homolog_chromosome
Rat Chromosome Name
rnorvegicus_homolog_chrom_start
Rat Chromosome Start (bp)
rnorvegicus_homolog_chrom_end
Rat Chromosome End (bp)
rnorvegicus_homolog_orthology_type
Homology Type
rnorvegicus_homolog_subtype
Ancestor
rnorvegicus_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
rnorvegicus_homolog_perc_id
% Identity with respect to query gene
rnorvegicus_homolog_perc_id_r1
% Identity with respect to Rat gene
rnorvegicus_homolog_dn
dN
rnorvegicus_homolog_ds
dS
pcapensis_homolog_ensembl_gene
Rock Hyrax Ensembl Gene ID
pcapensis_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
pcapensis_homolog_ensembl_peptide
Rock Hyrax Ensembl Protein ID
pcapensis_homolog_chromosome
Rock Hyrax Chromosome Name
pcapensis_homolog_chrom_start
Rock Hyrax Chromosome Start (bp)
pcapensis_homolog_chrom_end
Rock Hyrax Chromosome End (bp)
pcapensis_homolog_orthology_type
Homology Type
pcapensis_homolog_subtype
Ancestor
pcapensis_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
pcapensis_homolog_perc_id
% Identity with respect to query gene
pcapensis_homolog_perc_id_r1
% Identity with respect to Rock Hyrax gene
oaries_homolog_ensembl_gene
Sheep Ensembl Gene ID
oaries_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
oaries_homolog_ensembl_peptide
Sheep Ensembl Protein ID
oaries_homolog_chromosome
Sheep Chromosome Name
oaries_homolog_chrom_start
Sheep Chromosome Start (bp)
oaries_homolog_chrom_end
Sheep Chromosome End (bp)
oaries_homolog_orthology_type
Homology Type
oaries_homolog_subtype
Ancestor
oaries_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
oaries_homolog_perc_id
% Identity with respect to query gene
oaries_homolog_perc_id_r1
% Identity with respect to Sheep gene
oaries_homolog_dn
dN
oaries_homolog_ds
dS
choffmanni_homolog_ensembl_gene
Sloth Ensembl Gene ID
choffmanni_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
choffmanni_homolog_ensembl_peptide
Sloth Ensembl Protein ID
choffmanni_homolog_chromosome
Sloth Chromosome Name
choffmanni_homolog_chrom_start
Sloth Chromosome Start (bp)
choffmanni_homolog_chrom_end
Sloth Chromosome End (bp)
choffmanni_homolog_orthology_type
Homology Type
choffmanni_homolog_subtype
Ancestor
choffmanni_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
choffmanni_homolog_perc_id
% Identity with respect to query gene
choffmanni_homolog_perc_id_r1
% Identity with respect to Sloth gene
loculatus_homolog_ensembl_gene
Spotted gar Ensembl Gene ID
loculatus_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
loculatus_homolog_ensembl_peptide
Spotted gar Ensembl Protein ID
loculatus_homolog_chromosome
Spotted gar Chromosome Name
loculatus_homolog_chrom_start
Spotted gar Chromosome Start (bp)
loculatus_homolog_chrom_end
Spotted gar Chromosome End (bp)
loculatus_homolog_orthology_type
Homology Type
loculatus_homolog_subtype
Ancestor
loculatus_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
loculatus_homolog_perc_id
% Identity with respect to query gene
loculatus_homolog_perc_id_r1
% Identity with respect to Spotted gar gene
itridecemlineatus_homolog_ensembl_gene
Squirrel Ensembl Gene ID
itridecemlineatus_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
itridecemlineatus_homolog_ensembl_peptide
Squirrel Ensembl Protein ID
itridecemlineatus_homolog_chromosome
Squirrel Chromosome Name
itridecemlineatus_homolog_chrom_start
Squirrel Chromosome Start (bp)
itridecemlineatus_homolog_chrom_end
Squirrel Chromosome End (bp)
itridecemlineatus_homolog_orthology_type
Homology Type
itridecemlineatus_homolog_subtype
Ancestor
itridecemlineatus_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
itridecemlineatus_homolog_perc_id
% Identity with respect to query gene
itridecemlineatus_homolog_perc_id_r1
% Identity with respect to Squirrel gene
itridecemlineatus_homolog_dn
dN
itridecemlineatus_homolog_ds
dS
gaculeatus_homolog_ensembl_gene
Stickleback Ensembl Gene ID
gaculeatus_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
gaculeatus_homolog_ensembl_peptide
Stickleback Ensembl Protein ID
gaculeatus_homolog_chromosome
Stickleback Chromosome Name
gaculeatus_homolog_chrom_start
Stickleback Chromosome Start (bp)
gaculeatus_homolog_chrom_end
Stickleback Chromosome End (bp)
gaculeatus_homolog_orthology_type
Homology Type
gaculeatus_homolog_subtype
Ancestor
gaculeatus_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
gaculeatus_homolog_perc_id
% Identity with respect to query gene
gaculeatus_homolog_perc_id_r1
% Identity with respect to Stickleback gene
gaculeatus_homolog_dn
dN
gaculeatus_homolog_ds
dS
tsyrichta_homolog_ensembl_gene
Tarsier Ensembl Gene ID
tsyrichta_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
tsyrichta_homolog_ensembl_peptide
Tarsier Ensembl Protein ID
tsyrichta_homolog_chromosome
Tarsier Chromosome Name
tsyrichta_homolog_chrom_start
Tarsier Chromosome Start (bp)
tsyrichta_homolog_chrom_end
Tarsier Chromosome End (bp)
tsyrichta_homolog_orthology_type
Homology Type
tsyrichta_homolog_subtype
Ancestor
tsyrichta_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
tsyrichta_homolog_perc_id
% Identity with respect to query gene
tsyrichta_homolog_perc_id_r1
% Identity with respect to Tarsier gene
sharrisii_homolog_ensembl_gene
Tasmanian Devil Ensembl Gene ID
sharrisii_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
sharrisii_homolog_ensembl_peptide
Tasmanian Devil Ensembl Protein ID
sharrisii_homolog_chromosome
Tasmanian Devil Chromosome Name
sharrisii_homolog_chrom_start
Tasmanian Devil Chromosome Start (bp)
sharrisii_homolog_chrom_end
Tasmanian Devil Chromosome End (bp)
sharrisii_homolog_orthology_type
Homology Type
sharrisii_homolog_subtype
Ancestor
sharrisii_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
sharrisii_homolog_perc_id
% Identity with respect to query gene
sharrisii_homolog_perc_id_r1
% Identity with respect to Tasmanian Devil gene
sharrisii_homolog_dn
dN
sharrisii_homolog_ds
dS
tnigroviridis_homolog_ensembl_gene
Tetraodon Ensembl Gene ID
tnigroviridis_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
tnigroviridis_homolog_ensembl_peptide
Tetraodon Ensembl Protein ID
tnigroviridis_homolog_chromosome
Tetraodon Chromosome Name
tnigroviridis_homolog_chrom_start
Tetraodon Chromosome Start (bp)
tnigroviridis_homolog_chrom_end
Tetraodon Chromosome End (bp)
tnigroviridis_homolog_orthology_type
Homology Type
tnigroviridis_homolog_subtype
Ancestor
tnigroviridis_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
tnigroviridis_homolog_perc_id
% Identity with respect to query gene
tnigroviridis_homolog_perc_id_r1
% Identity with respect to Tetraodon gene
tnigroviridis_homolog_dn
dN
tnigroviridis_homolog_ds
dS
tbelangeri_homolog_ensembl_gene
Tree Shrew Ensembl Gene ID
tbelangeri_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
tbelangeri_homolog_ensembl_peptide
Tree Shrew Ensembl Protein ID
tbelangeri_homolog_chromosome
Tree Shrew Chromosome Name
tbelangeri_homolog_chrom_start
Tree Shrew Chromosome Start (bp)
tbelangeri_homolog_chrom_end
Tree Shrew Chromosome End (bp)
tbelangeri_homolog_orthology_type
Homology Type
tbelangeri_homolog_subtype
Ancestor
tbelangeri_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
tbelangeri_homolog_perc_id
% Identity with respect to query gene
tbelangeri_homolog_perc_id_r1
% Identity with respect to Tree Shrew gene
mgallopavo_homolog_ensembl_gene
Turkey Ensembl Gene ID
mgallopavo_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
mgallopavo_homolog_ensembl_peptide
Turkey Ensembl Protein ID
mgallopavo_homolog_chromosome
Turkey Chromosome Name
mgallopavo_homolog_chrom_start
Turkey Chromosome Start (bp)
mgallopavo_homolog_chrom_end
Turkey Chromosome End (bp)
mgallopavo_homolog_orthology_type
Homology Type
mgallopavo_homolog_subtype
Ancestor
mgallopavo_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
mgallopavo_homolog_perc_id
% Identity with respect to query gene
mgallopavo_homolog_perc_id_r1
% Identity with respect to Turkey gene
mgallopavo_homolog_dn
dN
mgallopavo_homolog_ds
dS
csabaeus_homolog_ensembl_gene
Vervet-AGM Ensembl Gene ID
csabaeus_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
csabaeus_homolog_ensembl_peptide
Vervet-AGM Ensembl Protein ID
csabaeus_homolog_chromosome
Vervet-AGM Chromosome Name
csabaeus_homolog_chrom_start
Vervet-AGM Chromosome Start (bp)
csabaeus_homolog_chrom_end
Vervet-AGM Chromosome End (bp)
csabaeus_homolog_orthology_type
Homology Type
csabaeus_homolog_subtype
Ancestor
csabaeus_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
csabaeus_homolog_perc_id
% Identity with respect to query gene
csabaeus_homolog_perc_id_r1
% Identity with respect to Vervet-AGM gene
csabaeus_homolog_dn
dN
csabaeus_homolog_ds
dS
meugenii_homolog_ensembl_gene
Wallaby Ensembl Gene ID
meugenii_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
meugenii_homolog_ensembl_peptide
Wallaby Ensembl Protein ID
meugenii_homolog_chromosome
Wallaby Chromosome Name
meugenii_homolog_chrom_start
Wallaby Chromosome Start (bp)
meugenii_homolog_chrom_end
Wallaby Chromosome End (bp)
meugenii_homolog_orthology_type
Homology Type
meugenii_homolog_subtype
Ancestor
meugenii_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
meugenii_homolog_perc_id
% Identity with respect to query gene
meugenii_homolog_perc_id_r1
% Identity with respect to Wallaby gene
xtropicalis_homolog_ensembl_gene
Xenopus Ensembl Gene ID
xtropicalis_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
xtropicalis_homolog_ensembl_peptide
Xenopus Ensembl Protein ID
xtropicalis_homolog_chromosome
Xenopus Chromosome Name
xtropicalis_homolog_chrom_start
Xenopus Chromosome Start (bp)
xtropicalis_homolog_chrom_end
Xenopus Chromosome End (bp)
xtropicalis_homolog_orthology_type
Homology Type
xtropicalis_homolog_subtype
Ancestor
xtropicalis_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
xtropicalis_homolog_perc_id
% Identity with respect to query gene
xtropicalis_homolog_perc_id_r1
% Identity with respect to Xenopus gene
xtropicalis_homolog_dn
dN
xtropicalis_homolog_ds
dS
scerevisiae_homolog_ensembl_gene
Yeast Ensembl Gene ID
scerevisiae_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
scerevisiae_homolog_ensembl_peptide
Yeast Ensembl Protein ID
scerevisiae_homolog_chromosome
Yeast Chromosome Name
scerevisiae_homolog_chrom_start
Yeast Chromosome Start (bp)
scerevisiae_homolog_chrom_end
Yeast Chromosome End (bp)
scerevisiae_homolog_orthology_type
Homology Type
scerevisiae_homolog_subtype
Ancestor
scerevisiae_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
scerevisiae_homolog_perc_id
% Identity with respect to query gene
scerevisiae_homolog_perc_id_r1
% Identity with respect to Yeast gene
scerevisiae_homolog_dn
dN
scerevisiae_homolog_ds
dS
tguttata_homolog_ensembl_gene
Zebra Finch Ensembl Gene ID
tguttata_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
tguttata_homolog_ensembl_peptide
Zebra Finch Ensembl Protein ID
tguttata_homolog_chromosome
Zebra Finch Chromosome Name
tguttata_homolog_chrom_start
Zebra Finch Chromosome Start (bp)
tguttata_homolog_chrom_end
Zebra Finch Chromosome End (bp)
tguttata_homolog_orthology_type
Homology Type
tguttata_homolog_subtype
Ancestor
tguttata_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
tguttata_homolog_perc_id
% Identity with respect to query gene
tguttata_homolog_perc_id_r1
% Identity with respect to Zebra Finch gene
tguttata_homolog_dn
dN
tguttata_homolog_ds
dS
drerio_homolog_ensembl_gene
Zebrafish Ensembl Gene ID
drerio_homolog_canonical_transcript_protein
Canonical Protein or Transcript ID
drerio_homolog_ensembl_peptide
Zebrafish Ensembl Protein ID
drerio_homolog_chromosome
Zebrafish Chromosome Name
drerio_homolog_chrom_start
Zebrafish Chromosome Start (bp)
drerio_homolog_chrom_end
Zebrafish Chromosome End (bp)
drerio_homolog_orthology_type
Homology Type
drerio_homolog_subtype
Ancestor
drerio_homolog_orthology_confidence
Orthology confidence [0 low, 1 high]
drerio_homolog_perc_id
% Identity with respect to query gene
drerio_homolog_perc_id_r1
% Identity with respect to Zebrafish gene
drerio_homolog_dn
dN
drerio_homolog_ds
dS
hsapiens_paralog_ensembl_gene
Human Paralog Ensembl Gene ID
hsapiens_paralog_canonical_transcript_protein
Canonical Protein or Transcript ID
hsapiens_paralog_ensembl_peptide
Human Paralog Ensembl Protein ID
hsapiens_paralog_chromosome
Human Paralog Chromosome Name
hsapiens_paralog_chrom_start
Human Paralog Chr Start (bp)
hsapiens_paralog_chrom_end
Human Paralog Chr End (bp)
hsapiens_paralog_orthology_type
Homology Type
hsapiens_paralog_subtype
Ancestor
hsapiens_paralog_paralogy_confidence
Paralogy confidence [0 low, 1 high]
hsapiens_paralog_perc_id
% Identity with respect to query gene
hsapiens_paralog_perc_id_r1
% Identity with respect to Human gene
hsapiens_paralog_dn
dN
hsapiens_paralog_ds
dS
ensembl_gene_id
Ensembl Gene ID
ensembl_transcript_id
Ensembl Transcript ID
ensembl_peptide_id
Ensembl Protein ID
chromosome_name
Chromosome Name
start_position
Gene Start (bp)
end_position
Gene End (bp)
strand
Strand
band
Band
external_gene_name
Associated Gene Name
external_gene_source
Associated Gene Source
transcript_count
Transcript count
percentage_gc_content
% GC content
description
Description
variation_name
Variation Name
germ_line_variation_source
Variation Source
source_description
Variation source description
allele
Variant Alleles
validated
Evidence status
mapweight
Mapweight
minor_allele
Minor allele
minor_allele_freq
Minor allele frequency
minor_allele_count
Minor allele count
clinical_significance
Clinical significance
transcript_location
Transcript location (bp)
snp_chromosome_strand
Variation Chromosome Strand
peptide_location
Protein location (aa)
chromosome_location
Chromosome Location (bp)
polyphen_prediction_2076
PolyPhen prediction
polyphen_score_2076
PolyPhen score
sift_prediction_2076
SIFT prediction
sift_score_2076
SIFT score
distance_to_transcript_2076
Distance to transcript
cds_start_2076
CDS Start
cds_end_2076
CDS End
peptide_shift
Protein Allele
synonymous_status
Consequence Type (Transcript Variation)
allele_string_2076
Consequence specific allele
somatic_variation_name
Variation Name
somatic_source_name
Variation Source
somatic_source_description
Variation source description
somatic_allele
Variant Alleles
somatic_validated
Evidence status
somatic_mapweight
Mapweight
somatic_minor_allele
Minor allele
somatic_minor_allele_freq
Minor allele frequency
somatic_minor_allele_count
Minor allele count
somatic_clinical_significance
Clinical significance
somatic_transcript_location
Transcript location (bp)
somatic_snp_chromosome_strand
Variation Chromosome Strand
somatic_peptide_location
Protein location (aa)
somatic_chromosome_location
Chromosome Location (bp)
mart_transcript_variation_som__dm_polyphen_prediction_2076
PolyPhen prediction
mart_transcript_variation_som__dm_polyphen_score_2076
PolyPhen score
mart_transcript_variation_som__dm_sift_prediction_2076
SIFT prediction
mart_transcript_variation_som__dm_sift_score_2076
SIFT score
mart_transcript_variation_som__dm_distance_to_transcript_2076
Distance to transcript
somatic_cds_start_2076
CDS Start
somatic_cds_end_2076
CDS End
somatic_peptide_shift
Protein Allele
somatic_synonymous_status
Consequence Type (Transcript Variation)
mart_transcript_variation_som__dm_allele_string_2076
Consequence specific allele
transcript_exon_intron
Unspliced (Transcript)
gene_exon_intron
Unspliced (Gene)
transcript_flank
Flank (Transcript)
gene_flank
Flank (Gene)
coding_transcript_flank
Flank-coding region (Transcript)
coding_gene_flank
Flank-coding region (Gene)
5utr
5' UTR
3utr
3' UTR
gene_exon
Exon sequences
cdna
cDNA sequences
coding
Coding sequence
peptide
Protein
upstream_flank
upstream_flank
downstream_flank
downstream_flank
ensembl_gene_id
Ensembl Gene ID
description
Description
external_gene_name
Associated Gene Name
external_gene_source
Associated Gene Source
chromosome_name
Chromosome Name
start_position
Gene Start (bp)
end_position
Gene End (bp)
gene_biotype
Gene type
family
Ensembl Protein Family ID(s)
cdna_coding_start
CDS start (within cDNA)
cdna_coding_end
CDS end (within cDNA)
5_utr_start
5' UTR Start
5_utr_end
5' UTR End
3_utr_start
3' UTR Start
3_utr_end
3' UTR End
ensembl_transcript_id
Ensembl Transcript ID
ensembl_peptide_id
Ensembl Protein ID
transcript_biotype
Transcript type
strand
Strand
transcript_start
Transcript Start (bp)
transcript_end
Transcript End (bp)
transcription_start_site
Transcription Start Site (TSS)
transcript_length
Transcript length
cds_length
CDS Length
cds_start
CDS Start
cds_end
CDS End
ensembl_exon_id
Ensembl Exon ID
exon_chrom_start
Exon Chr Start (bp)
exon_chrom_end
Exon Chr End (bp)
strand
Strand
rank
Exon Rank in Transcript
phase
phase
cdna_coding_start
cDNA coding start
cdna_coding_end
cDNA coding end
genomic_coding_start
Genomic coding start
genomic_coding_end
Genomic coding end
is_constitutive
Constitutive Exon



