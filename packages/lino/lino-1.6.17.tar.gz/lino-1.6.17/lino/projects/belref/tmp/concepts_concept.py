# -*- coding: UTF-8 -*-
logger.info("Loading 12 objects to table concepts_concept...")
# fields: id, name, abbr, wikipedia, definition, is_jargon_domain
loader.save(create_concepts_concept(1,[u'Institut National de Statistique', u'Nationaal Instituut voor Statistiek', u'Nationales Institut f\xfcr Statistik'],[u'INS', u'NIS', u'NIS'],[u'', u'', u''],[u'', u'', u''],False))
loader.save(create_concepts_concept(2,[u'Direction g\xe9n\xe9rale Statistique et Information \xe9conomique', u'Algemene Directie Statistiek en Economische Informatie', u'Generaldirektion Statistik und Wirtschaftsinformation'],[u'DGSIE', u'ADSEI', u'GDSWI'],[u'', u'', u''],[u'', u'', u''],False))
loader.save(create_concepts_concept(3,[u'Registre National', u'Rijksregister', u'Nationalregister'],[u'RN', u'RR', u'NR'],[u'', u'', u''],[u'', u'', u''],False))
loader.save(create_concepts_concept(4,[u"Centre Public d'Action Sociale", u'Openbaar Centrum voor Maatschappelijk Welzijn', u'\xd6ffentliches Sozialhilfezentrum'],[u'CPAS', u'OCMW', u'\xd6SHZ'],[u'', u'', u''],[u'', u'', u''],True))
loader.save(create_concepts_concept(5,[u"Service d'insertion socio-professionnelle", u'Dienst Socio-Professionele Inschakeling', u'Dienst f\xfcr Sozial-Berufliche Eingliederung'],[u'SISP', u'DSPI', u'DSBE'],[u'', u'', u''],[u'', u'', u''],False))
loader.save(create_concepts_concept(6,[u"Projet Individualis\xe9 d'Int\xe9gration Sociale", u'', u'Vertrag zur Sozialen Eingliederung'],[u'PIIS', u'', u'VSE'],[u'', u'', u''],[u'', u'', u''],False))
loader.save(create_concepts_concept(7,[u"N\xb0 d'Identification de la S\xe9curit\xe9 Sociale", u'', u'Identifizierungsnummer der Sozialsicherheit'],[u'NISS', u'', u'INSS'],[u'', u'', u''],[u'', u'', u''],False))
loader.save(create_concepts_concept(8,[u'M\xe9diation de dettes', u'Schuldbemiddeling ', u'Schuldnerberatung'],[u'', u'', u''],[u'', u'', u''],[u'', u'', u''],False))
loader.save(create_concepts_concept(9,[u'Service Social', u'Sociale dienst', u'Sozialdienst'],[u'', u'', u''],[u'', u'', u''],[u'', u'', u''],False))
loader.save(create_concepts_concept(10,[u"Agence locale pour l'emploi", u'Plaatselijk werkgelegenheidsagentschap', u'Lokale Besch\xe4ftigungsagentur'],[u'ALE', u'PWA', u'LBA'],[u'', u'', u''],[u'', u'', u''],False))
loader.save(create_concepts_concept(11,[u"Office national de l'emploi", u'Rijksdienst voor Arbeidsvoorziening', u'Landesamt f\xfcr Arbeitsbeschaffung'],[u'ONEM', u'RVA', u'LfA'],[u'', u'', u''],[u'', u'', u''],False))
loader.save(create_concepts_concept(12,[u'Chef de m\xe9nage', u'Haushaltsvorstand', u'Haushaltsvorstand'],[u'', u'', u''],[u'', u'', u''],[u'', u'', u''],False))

loader.flush_deferred_objects()
