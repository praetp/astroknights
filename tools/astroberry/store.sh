#!/bin/bash 
set -xEeuo pipefail

REMOTE=astroberry.local
SRC=${1%/}

SSO_NAMES="sun mercury venus earth moon mars phobos deimos jupiter io europa ganymede callisto amalthea saturn mimas enceladus tethys dione rhea titan hyperion iapetus phoebe uranus miranda ariel umbriel titania oberon neptune triton nereid pluto charon"

HADS_NAMES="ad_cmi ag_pic al_cvn an_lyn be_lyn bm_for bo_lyn bq_psc bs_aqr cc_and dr_ari dv_scl dw_phe dw_vir dx_cet dx_ind eh_lib ek_cap fr_gru fs_cmi gp_and gt_cvn gw_uma ht_vul hu_cet ko_psc kp_lyn ku_cen kz_lac lp_car lr_psc ls_cet ls_psc np_lib np_lyn pt_com rs_gru ry_lep sz_lyn tw_aps v0337_ori v0341_leo v0343_aps v0358_mus v0360_aps v0367_cam v0377_boo v0390_cam v0393_car v0398_uma v0407_sge v0408_boo v0409_sge v0410_boo v0411_sge v0416_uma v0417_boo v0437_sge v0442_gem v0447_uma v0451_dra v0455_com v0457_peg v0460_and v0465_peg v0467_dra v0468_uma v0474_mon v0482_peg v0488_gem v0490_aqr v0494_vul v0495_uma v0506_aqr v0519_vul v0536_peg v0539_aur v0542_vul v0547_lac v0554_vel v0567_oph v0572_cam v0586_lac v0593_lyr v0594_dra v0595_cam v0601_vul v0611_cam v0613_ser v0643_ser v0645_ser v0670_and v0673_hya v0680_lac v0703_peg v0729_vir v0743_aur v0757_peg v0757_vir v0791_and v0792_cep v0799_aur v0831_tau v0839_lac v0878_cas v0889_aur v0965_cep v0973_cep v1004_per v1022_per v1078_per v1090_per v1128_cep v1132_cep v1221_cep v1290_cas v1338_cen v1421_cen v1425_tau v1429_cen v1441_her v1513_her v1535_her v1876_aql v1883_aql v1965_aql v2008_aql v2013_aql v2028_aql v2367_cyg v2455_cyg v2706_cyg v2771_cyg v3092_cyg v3186_cyg v3193_oph v3208_cyg v3363_oph v3364_oph v3368_oph v3423_oph v3424_oph v3441_oph v3446_oph v3541_oph v3583_oph v3658_oph v5505_sgr v6544_sgr v6616_sgr yz_boo zz_mic ai_vel sx_phe xx_cyg cy_aqr dy_her dy_peg vz_cnc v0927_her kz_hya v1162_ori cw_ser"

CATEGORY=DSO
SRC_LOWER=${SRC,,}
LEAD=${SRC_LOWER%%[_+ -]*}

case "$SRC" in
	C_[0-9][0-9][0-9][0-9]_*) CATEGORY=SSO ;;
esac

if [ "$CATEGORY" = "DSO" ]; then
	for n in $SSO_NAMES; do
		[ "$LEAD" = "$n" ] && CATEGORY=SSO && break
	done
fi

if [ "$CATEGORY" = "DSO" ]; then
	for h in $HADS_NAMES; do
		[ "$SRC_LOWER" = "$h" ] && CATEGORY=HADS && break
	done
fi

DEST=${DEST:-/astrophotography/projects/${CATEGORY}}


ASTROBERRY_UP=true
if ! ping -c 1 ${REMOTE} > /dev/null; then
	ASTROBERRY_UP=false
	read -p "${REMOTE} is not up. Continue anyway? (yes/no)" CONTINUE
	if [ $CONTINUE != "yes" ]; then
		exit 1
	fi
fi

read -p "OK to remove process directory ? (yes/no)" ANSWER
if [ $ANSWER = "yes" ]; then
	rm -rf ${SRC}/process
fi
OLDEST_LIGHT=$(find ${SRC}/Light -type f -printf '%TY-%Tm-%Td\n' | sort | head -n 1)
DEST_FULL=${DEST}/${SRC}/${OLDEST_LIGHT}

mkdir -p ${DEST_FULL}
echo "Moving files (this can take a while)"
mv ${SRC}/* ${DEST_FULL}
rmdir ${SRC}

if [ "$ASTROBERRY_UP" = "true" ]; then
	ssh ${REMOTE} "rm -rf /camera/${SRC}"
	echo "Removal on astroberry done"
fi

echo "Do not forget to update the database in kstars"
