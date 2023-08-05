# encoding: utf-8
# Copyright 2008–2012 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''Test data.
'''

import eke.knowledge.tests.base as ekeKnowledgeBase

_singlePublicationRDF = '''<?xml version="1.0" encoding="UTF-8"?><rdf:RDF  xmlns:_3="http://purl.org/dc/terms/" xmlns:_4="http://edrn.nci.nih.gov/rdf/schema.rdf#" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"><rdf:Description rdf:about="http://is.gd/pVKq"><rdf:type rdf:resource="http://edrn.nci.nih.gov/rdf/types.rdf#Publication"/><_3:title>Glazed Roast Chicken</_3:title><_3:description>Applying a glaze to a whole chicken can land you in a sweet mess.</_3:description><_4:abstract>Most glazed roast chicken recipes offer some variation on these instructions.</_4:abstract><_3:author>Kimball, C</_3:author><_3:author>Gavorick, M</_3:author><_4:year>2009</_4:year><_4:journal>Cook's Illustrated</_4:journal><_4:issue>March</_4:issue><_4:volume>12</_4:volume><_4:pmid>23319948</_4:pmid><_4:pubURL>http://is.gd/pVKq</_4:pubURL></rdf:Description></rdf:RDF>'''

_doublePublicationRDF = '''<?xml version="1.0" encoding="UTF-8"?><rdf:RDF  xmlns:_3="http://purl.org/dc/terms/" xmlns:_4="http://edrn.nci.nih.gov/rdf/schema.rdf#" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"><rdf:Description rdf:about="http://is.gd/pVKq"><rdf:type rdf:resource="http://edrn.nci.nih.gov/rdf/types.rdf#Publication"/><_3:title>Glazed Roast Chicken</_3:title><_3:description>Applying a glaze to a whole chicken can land you in a sweet mess.</_3:description><_4:abstract>Most glazed roast chicken recipes offer some variation on these instructions.</_4:abstract><_3:author>Kimball, C</_3:author><_3:author>Gavorick, M</_3:author><_4:year>2009</_4:year><_4:journal>Cook's Illustrated</_4:journal><_4:issue>March</_4:issue><_4:volume>12</_4:volume><_4:pmid>23319948</_4:pmid><_4:pubURL>http://is.gd/pVKq</_4:pubURL></rdf:Description><rdf:Description rdf:about="http://is.gd/q6mS"><rdf:type rdf:resource="http://edrn.nci.nih.gov/rdf/types.rdf#Publication"/><_3:title>Teriyaki Beef</_3:title><_3:description>This Japanese-American standard is synonymous with chewy, flavorless meat shellacked with saccharine-sweet sauce. To beef things up, we turned to a trick from the grill.</_3:description><_4:abstract>True Japanese teriyaki is as simple as it is restrained: Take a glossy, salty-sweet glaze made with soy sauce, sake, and mirin (sweet Japanese rice wine) and paint it over grilled fish to accent its delicately smoky flavor. Over time, beef and chicken were introduced and the dish morphed into the tired renditions now found at many Japanese-American restaurants: chewy, flavorless slivers of meat daubed with a thick, overly sweet sauce. We wanted juicy, charred steak embellished by a well-balanced, sweet and savory glaze that would be robust enough to stand up to the beef.</_4:abstract><_3:author>Kimball, C</_3:author><_3:author>Kythestra, Q</_3:author><_4:year>2009</_4:year><_4:journal>Cook's Illustrated</_4:journal><_4:issue>March</_4:issue><_4:volume>12</_4:volume><_4:pubURL>http://is.gd/q6mS</_4:pubURL><_4:pmid>21666252</_4:pmid></rdf:Description></rdf:RDF>'''

_morePublicationRDF = '''<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF xmlns:_3="http://purl.org/dc/terms/" xmlns:_4="http://edrn.nci.nih.gov/rdf/schema.rdf#" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
	<rdf:Description rdf:about="http://is.gd/4jH8Z">
		<rdf:type rdf:resource="http://edrn.nci.nih.gov/rdf/types.rdf#Publication"/>
		<_3:title>Sauteed Chicken Cutlets With Porcini Sauce</_3:title>
		<_3:description>For even more intense mushroom flavor, grind an additional half-ounce of dried porcini.</_3:description>
		<_4:abstract>Italians braise chicken for hours in a rich wine and mushroom sauce.</_4:abstract>
		<_3:author>Jone, WB</_3:author>
		<_4:year>2009</_4:year>
		<_4:journal>Cook's Illustrated</_4:journal>
		<_4:issue>March</_4:issue>
		<_4:volume>12</_4:volume>
		<_4:pmid>25392411</_4:pmid>
		<_4:pubURL>http://is.gd/4jH8Z</_4:pubURL>
	</rdf:Description>
	<rdf:Description rdf:about="http://is.gd/4jHbo">
		<rdf:type rdf:resource="http://edrn.nci.nih.gov/rdf/types.rdf#Publication"/>
		<_3:title>Sunday Gravy</_3:title>
		<_3:description>This over-the-top Italian-American tomato sauce typically calls for six cuts of meat.</_3:description>
		<_4:abstract>As our first step toward making this dish more manageable, ...</_4:abstract>
		<_3:author>Jone, AB</_3:author>
		<_4:year>2013</_4:year>
		<_4:journal>Cook's Illustrated</_4:journal>
		<_4:issue>April</_4:issue>
		<_4:volume>15</_4:volume>
		<_4:pmid>25381290</_4:pmid>
		<_4:pubURL>http://is.gd/4jHbo</_4:pubURL>
	</rdf:Description>
</rdf:RDF>'''

_yetMorePublicationRDF = '''<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF xmlns:_3="http://purl.org/dc/terms/" xmlns:_4="http://edrn.nci.nih.gov/rdf/schema.rdf#" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
	<rdf:Description rdf:about="http://is.gd/4jHmC">
		<rdf:type rdf:resource="http://edrn.nci.nih.gov/rdf/types.rdf#Publication"/>
		<_3:title>Chopped Salad</_3:title>
		<_3:description>We wanted complementary flavors and textures in every bite.</_3:description>
		<_4:abstract>Salting some of the vegetables to remove excess moisture was an important first step.</_4:abstract>
		<_3:author>Jonasi, ZB</_3:author>
		<_4:year>2009</_4:year>
		<_4:journal>Cook's Illustrated</_4:journal>
		<_4:issue>Octobary</_4:issue>
		<_4:volume>99</_4:volume>
		<_4:pmid>25379168</_4:pmid>
		<_4:pubURL>http://is.gd/4jHmC</_4:pubURL>
	</rdf:Description>
	<rdf:Description rdf:about="http://is.gd/4jHBS">
		<rdf:type rdf:resource="http://edrn.nci.nih.gov/rdf/types.rdf#Publication"/>
		<_3:title>Kalbi</_3:title>
		<_3:description>Koreans know how to take tough short ribs and transform them into tender barbecued beef</_3:description>
		<_4:abstract>Butchering the short ribs properly proved to be the most essential step.</_4:abstract>
		<_3:author>Jonefoo, QP</_3:author>
		<_4:year>2015</_4:year>
		<_4:journal>Cook's Illustrated</_4:journal>
		<_4:issue>Novembary</_4:issue>
		<_4:volume>16</_4:volume>
		<_4:pmid>25358803</_4:pmid>
		<_4:pubURL>http://is.gd/4jHBS</_4:pubURL>
	</rdf:Description>
</rdf:RDF>'''

_markedUpPublicationRDF = '''<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF xmlns:_3="http://purl.org/dc/terms/" xmlns:_4="http://edrn.nci.nih.gov/rdf/schema.rdf#" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    <rdf:Description rdf:about="http://cannibalism.com/book/1">
        <rdf:type rdf:resource="http://edrn.nci.nih.gov/rdf/types.rdf#Publication"/>
        <_3:title>How to &amp;#34;Serve&amp;#34; &lt;em&gt;Man&lt;/em&gt;</_3:title>
        <_3:description>Applying a glaze to a whole man can land you in a &lt;em&gt;sweet&lt;/em&gt; mess.</_3:description>
        <_4:abstract>&lt;em&gt;Most&lt;/em&gt; glazed man recipes offer some variation on these instructions&amp;#46;</_4:abstract>
        <_3:author>Voodoo, J</_3:author>
        <_4:year>2009</_4:year>
        <_4:journal>Cannibalism Illustrated</_4:journal>
        <_4:issue>March</_4:issue>
        <_4:volume>12</_4:volume>
        <_4:pmid>23319948</_4:pmid>
        <_4:pubURL>http://cannibalism.com/book/1/pdf</_4:pubURL>
    </rdf:Description>
</rdf:RDF>'''

def registerLocalTestData():
    ekeKnowledgeBase.registerTestData('/pubs/a', _singlePublicationRDF)
    ekeKnowledgeBase.registerTestData('/pubs/b', _doublePublicationRDF)
    ekeKnowledgeBase.registerTestData('/pubs/c', _morePublicationRDF)
    ekeKnowledgeBase.registerTestData('/pubs/d', _yetMorePublicationRDF)
    ekeKnowledgeBase.registerTestData('/pubs/e', _markedUpPublicationRDF)
