#!/bin/bash
./collect.py https://www.rediris.es/sir/shib1metadata.xml https://www.rediris.es/sir/shibsir1metadata.xml > es.md &
./collect.py https://haka.funet.fi/metadata/haka-metadata.xml > fi.md &
./collect.py https://services-federation.renater.fr/metadata/renater-metadata.xml > fr.md &
./collect.py http://aai.grnet.gr/metadata.xml > gr.md &
./collect.py http://metadata.eduid.hu/current/href.xml > hu.md &
./collect.py https://edugate.heanet.ie/edugate-federation-metadata-signed.xml > ie.md &
./collect.py https://www.idem.garr.it/docs/conf/signed-metadata.xml > it.md &
./collect.py https://metadata.gakunin.nii.ac.jp/gakunin-metadata.xml > jp.md &
./collect.py https://laife.lanet.lv/metadata/laife-metadata.xml > lv.md &
./collect.py http://md.swamid.se/md/swamid-2.0.xml  > se.md &
./collect.py http://md.incommon.org/InCommon/InCommon-metadata-fallback.xml > us.md &
./collect.py http://ds.aai.arnes.si/metadata/aai.arnes.si.signed.xml > si.md &
./collect.py https://directory.tuakiri.ac.nz/metadata/tuakiri-metadata-signed.xml > nz.md &
./collect.py https://caf-shibops.ca/CoreServices/cafshib_metadata_signed.xml > ca.md &
./collect.py http://geant.edugain.org/geant_metadata.xml > geant.md &
./collect.py https://federation.belnet.be/federation-metadata.xml > be.md &
./collect.py http://metadata.ukfederation.org.uk/ukfederation-metadata.xml > uk.md &
./collect.py https://wayf.surfnet.nl/federate/metadata > nl.md &
./collect.py http://metadata-rctsaai.fccn.pt/metadata/RCTSaai_metadata.xml > pt.md &
./collect.py https://login.aaiedu.hr/sso/module.php/aggregator/?id=aaieduhr_edugain > hr.md &
./collect.py https://metadata.feide.no/feide-edugain-metadata.xml > no.md &
./collect.py http://parichay.inflibnet.ac.in/metadata/infed.xml > in.md &
./collect.py http://cofre.reuna.cl/metadata/cofre-md.xml > cl.md &
./collect.py https://wayf.wayf.dk/saml2/idp/metadata.php https://wayf.wayf.dk/module.php/saml/sp/metadata.php/wayf.wayf.dk > dk.md &

wait

echo "done"